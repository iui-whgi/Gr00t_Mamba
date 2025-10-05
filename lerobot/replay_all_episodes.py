#!/usr/bin/env python3

"""
Replay all episodes from a robot arm dataset one by one.

This script loads a LeRobot dataset and replays each episode sequentially,
allowing the user to control playback with keyboard inputs.

Usage:
    python replay_all_episodes.py --dataset.repo_id=<dataset_id> --robot.type=<robot_type> --robot.port=<port>

Example:
    python replay_all_episodes.py \
        --dataset.repo_id=aliberts/record-test \
        --robot.type=so100_follower \
        --robot.port=/dev/tty.usbmodem58760431541 \
        --robot.id=black
"""

import logging
import time
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from pprint import pformat

import draccus

from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.robots import (
    Robot,
    RobotConfig,
    make_robot_from_config,
)
from lerobot.utils.robot_utils import busy_wait
from lerobot.utils.utils import (
    init_logging,
    log_say,
)


@dataclass
class DatasetReplayConfig:
    # Dataset identifier. By convention it should match '{hf_username}/{dataset_name}' (e.g. `lerobot/test`).
    repo_id: str
    # Root directory where the dataset will be stored (e.g. 'dataset/path').
    root: str | Path | None = None
    # Limit the frames per second. By default, uses the policy fps.
    fps: int = 30
    # Start from a specific episode (0-indexed)
    start_episode: int = 0
    # End at a specific episode (0-indexed, -1 for all episodes)
    end_episode: int = -1


@dataclass
class ReplayAllConfig:
    robot: RobotConfig
    dataset: DatasetReplayConfig
    # Use vocal synthesis to read events.
    play_sounds: bool = True
    # Delay between episodes in seconds
    episode_delay: float = 2.0
    # Auto-advance to next episode (False to wait for user input)
    auto_advance: bool = False


class EpisodeReplayer:
    def __init__(self, cfg: ReplayAllConfig):
        self.cfg = cfg
        self.robot = None
        self.dataset = None
        self.current_episode = cfg.dataset.start_episode
        self.total_episodes = 0
        self.is_paused = False
        self.should_stop = False
        self.input_thread = None
        
    def setup_robot_and_dataset(self):
        """Initialize robot and dataset connections."""
        init_logging()
        logging.info(pformat(asdict(self.cfg)))
        
        # Setup robot
        self.robot = make_robot_from_config(self.cfg.robot)
        self.robot.connect()
        
        if not self.robot.is_connected:
            raise ValueError("Robot is not connected!")
        
        # Load dataset
        self.dataset = LeRobotDataset(
            self.cfg.dataset.repo_id, 
            root=self.cfg.dataset.root
        )
        
        # Determine episode range
        self.total_episodes = self.dataset.num_episodes
        start_ep = self.cfg.dataset.start_episode
        end_ep = self.cfg.dataset.end_episode if self.cfg.dataset.end_episode >= 0 else self.total_episodes - 1
        
        # Validate episode range
        if start_ep >= self.total_episodes:
            raise ValueError(f"Start episode {start_ep} is >= total episodes {self.total_episodes}")
        if end_ep >= self.total_episodes:
            end_ep = self.total_episodes - 1
        if start_ep > end_ep:
            raise ValueError(f"Start episode {start_ep} > end episode {end_ep}")
        
        self.current_episode = start_ep
        self.end_episode = end_ep
        
        print(f"\n{'='*60}")
        print(f"Dataset: {self.cfg.dataset.repo_id}")
        print(f"Total episodes in dataset: {self.total_episodes}")
        print(f"Will replay episodes: {start_ep} to {end_ep} ({end_ep - start_ep + 1} episodes)")
        print(f"Robot type: {self.cfg.robot.type}")
        print(f"FPS: {self.dataset.fps}")
        print(f"{'='*60}\n")
        
    def start_input_listener(self):
        """Start a background thread to listen for user input."""
        def input_listener():
            while not self.should_stop:
                try:
                    cmd = input().strip().lower()
                    if cmd == 'q' or cmd == 'quit':
                        self.should_stop = True
                        print("Stopping replay...")
                    elif cmd == 'p' or cmd == 'pause':
                        self.is_paused = not self.is_paused
                        status = "paused" if self.is_paused else "resumed"
                        print(f"Replay {status}")
                    elif cmd == 'n' or cmd == 'next':
                        if self.is_paused:
                            self.is_paused = False
                            print("Moving to next episode...")
                        else:
                            print("Already playing, use 'p' to pause first")
                    elif cmd == 's' or cmd == 'skip':
                        print("Skipping current episode...")
                        break
                    elif cmd == 'h' or cmd == 'help':
                        self.print_help()
                    else:
                        print("Unknown command. Type 'h' for help.")
                except EOFError:
                    break
                except KeyboardInterrupt:
                    self.should_stop = True
                    break
        
        self.input_thread = threading.Thread(target=input_listener, daemon=True)
        self.input_thread.start()
    
    def print_help(self):
        """Print available commands."""
        print("\nAvailable commands:")
        print("  h, help  - Show this help")
        print("  p, pause - Pause/resume current episode")
        print("  n, next  - Move to next episode")
        print("  s, skip  - Skip current episode")
        print("  q, quit  - Quit replay")
        print()
    
    def replay_single_episode(self, episode_idx: int):
        """Replay a single episode."""
        print(f"\n{'='*40}")
        print(f"Replaying Episode {episode_idx + 1}/{self.total_episodes}")
        print(f"{'='*40}")
        
        # Load specific episode
        episode_dataset = LeRobotDataset(
            self.cfg.dataset.repo_id, 
            root=self.cfg.dataset.root, 
            episodes=[episode_idx]
        )
        
        actions = episode_dataset.hf_dataset.select_columns("action")
        num_frames = episode_dataset.num_frames
        
        print(f"Episode {episode_idx} has {num_frames} frames")
        
        if self.cfg.play_sounds:
            log_say(f"Replaying episode {episode_idx}", blocking=True)
        
        # Replay each frame
        for frame_idx in range(num_frames):
            if self.should_stop:
                print("Stopping replay...")
                return False
                
            # Handle pause
            while self.is_paused and not self.should_stop:
                time.sleep(0.1)
            
            if self.should_stop:
                return False
            
            start_frame_t = time.perf_counter()
            
            # Get action for this frame
            action_array = actions[frame_idx]["action"]
            action = {}
            for i, name in enumerate(episode_dataset.features["action"]["names"]):
                action[name] = action_array[i]
            
            # Send action to robot
            self.robot.send_action(action)
            
            # Maintain timing
            dt_s = time.perf_counter() - start_frame_t
            busy_wait(1 / self.dataset.fps - dt_s)
            
            # Show progress every 10 frames
            if frame_idx % 10 == 0:
                progress = (frame_idx + 1) / num_frames * 100
                print(f"\rFrame {frame_idx + 1}/{num_frames} ({progress:.1f}%)", end="", flush=True)
        
        print(f"\nEpisode {episode_idx} completed!")
        return True
    
    def run(self):
        """Main replay loop."""
        try:
            self.setup_robot_and_dataset()
            self.start_input_listener()
            
            print("Starting episode replay...")
            print("Type 'h' for help, 'q' to quit")
            
            # Replay each episode
            for episode_idx in range(self.current_episode, self.end_episode + 1):
                if self.should_stop:
                    break
                
                # Show episode info
                print(f"\nEpisode {episode_idx + 1}/{self.total_episodes} (Dataset episode {episode_idx})")
                
                # Replay the episode
                success = self.replay_single_episode(episode_idx)
                
                if not success:
                    break
                
                # Delay between episodes (unless it's the last episode)
                if episode_idx < self.end_episode and not self.should_stop:
                    if self.cfg.auto_advance:
                        print(f"Waiting {self.cfg.episode_delay}s before next episode...")
                        time.sleep(self.cfg.episode_delay)
                    else:
                        print("Press Enter to continue to next episode, or type a command...")
                        # Wait for user input or command
                        while not self.should_stop:
                            time.sleep(0.1)
                            if not self.is_paused:
                                break
            
            if not self.should_stop:
                print(f"\n{'='*60}")
                print("All episodes completed successfully!")
                print(f"Replayed episodes {self.current_episode} to {self.end_episode}")
                print(f"{'='*60}")
            else:
                print("\nReplay stopped by user.")
                
        except Exception as e:
            print(f"Error during replay: {e}")
            logging.error(f"Replay error: {e}", exc_info=True)
        finally:
            if self.robot and self.robot.is_connected:
                self.robot.disconnect()
                print("Robot disconnected.")


@draccus.wrap()
def replay_all_episodes(cfg: ReplayAllConfig):
    """Replay all episodes from a dataset."""
    replayer = EpisodeReplayer(cfg)
    replayer.run()


def main():
    """Main entry point."""
    replay_all_episodes()


if __name__ == "__main__":
    main()
