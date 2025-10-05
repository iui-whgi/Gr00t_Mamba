#!/usr/bin/env python3

"""
Demo script showing episode replay functionality.

This demonstrates how the episode replay system works without requiring
actual robot hardware or datasets.
"""

import time
import threading
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class MockAction:
    """Mock action data structure."""
    joint1: float
    joint2: float
    joint3: float
    joint4: float
    joint5: float
    joint6: float


class MockDataset:
    """Mock dataset for demonstration purposes."""
    
    def __init__(self, num_episodes: int = 5, frames_per_episode: int = 50):
        self.num_episodes = num_episodes
        self.frames_per_episode = frames_per_episode
        self.fps = 30
        
        # Create mock episode data
        self.episodes = []
        for ep_idx in range(num_episodes):
            episode = []
            for frame_idx in range(frames_per_episode):
                # Create mock action with some variation
                action = MockAction(
                    joint1=0.1 * frame_idx + ep_idx * 0.5,
                    joint2=0.2 * frame_idx + ep_idx * 0.3,
                    joint3=0.15 * frame_idx + ep_idx * 0.4,
                    joint4=0.25 * frame_idx + ep_idx * 0.2,
                    joint5=0.3 * frame_idx + ep_idx * 0.6,
                    joint6=0.05 * frame_idx + ep_idx * 0.1
                )
                episode.append(action)
            self.episodes.append(episode)
    
    def get_episode(self, episode_idx: int) -> List[MockAction]:
        """Get actions for a specific episode."""
        return self.episodes[episode_idx]


class MockRobot:
    """Mock robot for demonstration purposes."""
    
    def __init__(self):
        self.is_connected = False
        self.current_action = None
    
    def connect(self):
        """Simulate robot connection."""
        print("🤖 Connecting to robot...")
        time.sleep(1)  # Simulate connection time
        self.is_connected = True
        print("✅ Robot connected successfully!")
    
    def disconnect(self):
        """Simulate robot disconnection."""
        print("🤖 Disconnecting robot...")
        self.is_connected = False
        print("✅ Robot disconnected.")
    
    def send_action(self, action: MockAction):
        """Simulate sending action to robot."""
        self.current_action = action
        # Simulate some processing time
        time.sleep(0.01)


class EpisodeReplayer:
    """Episode replayer with interactive controls."""
    
    def __init__(self, dataset: MockDataset, robot: MockRobot):
        self.dataset = dataset
        self.robot = robot
        self.current_episode = 0
        self.is_paused = False
        self.should_stop = False
        self.input_thread = None
    
    def start_input_listener(self):
        """Start background thread for user input."""
        def input_listener():
            while not self.should_stop:
                try:
                    cmd = input().strip().lower()
                    if cmd == 'q' or cmd == 'quit':
                        self.should_stop = True
                        print("🛑 Stopping replay...")
                    elif cmd == 'p' or cmd == 'pause':
                        self.is_paused = not self.is_paused
                        status = "⏸️  paused" if self.is_paused else "▶️  resumed"
                        print(f"Replay {status}")
                    elif cmd == 'n' or cmd == 'next':
                        if self.is_paused:
                            self.is_paused = False
                            print("⏭️  Moving to next episode...")
                        else:
                            print("Already playing, use 'p' to pause first")
                    elif cmd == 's' or cmd == 'skip':
                        print("⏭️  Skipping current episode...")
                        break
                    elif cmd == 'h' or cmd == 'help':
                        self.print_help()
                    else:
                        print("❓ Unknown command. Type 'h' for help.")
                except EOFError:
                    break
                except KeyboardInterrupt:
                    self.should_stop = True
                    break
        
        self.input_thread = threading.Thread(target=input_listener, daemon=True)
        self.input_thread.start()
    
    def print_help(self):
        """Print available commands."""
        print("\n📋 Available commands:")
        print("  h, help  - Show this help")
        print("  p, pause - Pause/resume current episode")
        print("  n, next  - Move to next episode")
        print("  s, skip  - Skip current episode")
        print("  q, quit  - Quit replay")
        print()
    
    def replay_single_episode(self, episode_idx: int):
        """Replay a single episode."""
        print(f"\n{'='*50}")
        print(f"🎬 Replaying Episode {episode_idx + 1}/{self.dataset.num_episodes}")
        print(f"{'='*50}")
        
        actions = self.dataset.get_episode(episode_idx)
        num_frames = len(actions)
        
        print(f"📊 Episode {episode_idx} has {num_frames} frames")
        print(f"⏱️  FPS: {self.dataset.fps}")
        
        # Replay each frame
        for frame_idx in range(num_frames):
            if self.should_stop:
                print("🛑 Stopping replay...")
                return False
            
            # Handle pause
            while self.is_paused and not self.should_stop:
                time.sleep(0.1)
            
            if self.should_stop:
                return False
            
            start_frame_t = time.perf_counter()
            
            # Get action for this frame
            action = actions[frame_idx]
            
            # Send action to robot
            self.robot.send_action(action)
            
            # Show progress every 10 frames
            if frame_idx % 10 == 0:
                progress = (frame_idx + 1) / num_frames * 100
                print(f"\r🎯 Frame {frame_idx + 1}/{num_frames} ({progress:.1f}%) - "
                      f"Joints: [{action.joint1:.2f}, {action.joint2:.2f}, {action.joint3:.2f}, "
                      f"{action.joint4:.2f}, {action.joint5:.2f}, {action.joint6:.2f}]", 
                      end="", flush=True)
            
            # Maintain timing
            dt_s = time.perf_counter() - start_frame_t
            sleep_time = max(1 / self.dataset.fps - dt_s, 0)
            time.sleep(sleep_time)
        
        print(f"\n✅ Episode {episode_idx} completed!")
        return True
    
    def run(self):
        """Main replay loop."""
        try:
            # Connect robot
            self.robot.connect()
            
            if not self.robot.is_connected:
                raise ValueError("Robot is not connected!")
            
            # Start input listener
            self.start_input_listener()
            
            print(f"\n🎮 Starting episode replay...")
            print(f"📚 Dataset has {self.dataset.num_episodes} episodes")
            print(f"🎯 Type 'h' for help, 'q' to quit")
            
            # Replay each episode
            for episode_idx in range(self.dataset.num_episodes):
                if self.should_stop:
                    break
                
                # Show episode info
                print(f"\n📖 Episode {episode_idx + 1}/{self.dataset.num_episodes}")
                
                # Replay the episode
                success = self.replay_single_episode(episode_idx)
                
                if not success:
                    break
                
                # Delay between episodes (unless it's the last episode)
                if episode_idx < self.dataset.num_episodes - 1 and not self.should_stop:
                    print(f"\n⏳ Waiting 2 seconds before next episode...")
                    time.sleep(2)
            
            if not self.should_stop:
                print(f"\n{'='*60}")
                print("🎉 All episodes completed successfully!")
                print(f"📊 Replayed {self.dataset.num_episodes} episodes")
                print(f"{'='*60}")
            else:
                print("\n🛑 Replay stopped by user.")
                
        except Exception as e:
            print(f"❌ Error during replay: {e}")
        finally:
            if self.robot.is_connected:
                self.robot.disconnect()


def main():
    """Main function to demonstrate episode replay."""
    
    print("🎬 Episode Replay Demo")
    print("=" * 50)
    
    # Create mock dataset and robot
    dataset = MockDataset(num_episodes=3, frames_per_episode=30)
    robot = MockRobot()
    
    # Create and run replayer
    replayer = EpisodeReplayer(dataset, robot)
    replayer.run()


if __name__ == "__main__":
    main()

