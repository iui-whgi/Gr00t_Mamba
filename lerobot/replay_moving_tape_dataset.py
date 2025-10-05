#!/usr/bin/env python3

"""
Replay episodes from the moving-tape-dataset-20250915_153200 dataset.

This script loads the dataset and replays episodes with interactive controls.
"""

import time
import threading
from lerobot.datasets.lerobot_dataset import LeRobotDataset


class DatasetEpisodeReplayer:
    def __init__(self, dataset_path, root_path):
        self.dataset_path = dataset_path
        self.root_path = root_path
        self.dataset = None
        self.current_episode = 0
        self.is_paused = False
        self.should_stop = False
        self.input_thread = None
        
    def load_dataset(self):
        """Load the dataset."""
        print("📚 Loading dataset...")
        try:
            self.dataset = LeRobotDataset(
                self.dataset_path, 
                root=self.root_path,
                download_videos=False
            )
            print(f"✅ Dataset loaded successfully!")
            print(f"   Episodes: {self.dataset.num_episodes}")
            print(f"   Frames: {self.dataset.num_frames}")
            print(f"   FPS: {self.dataset.fps}")
            print(f"   Robot type: {self.dataset.meta.robot_type}")
            print(f"   Action features: {self.dataset.features['action']['names']}")
            return True
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            return False
    
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
        print(f"\n{'='*60}")
        print(f"🎬 Replaying Episode {episode_idx + 1}/{self.dataset.num_episodes}")
        print(f"{'='*60}")
        
        # Load specific episode
        episode_dataset = LeRobotDataset(
            self.dataset_path, 
            root=self.root_path,
            episodes=[episode_idx],
            download_videos=False
        )
        
        actions = episode_dataset.hf_dataset.select_columns("action")
        num_frames = episode_dataset.num_frames
        
        print(f"📊 Episode {episode_idx} has {num_frames} frames")
        print(f"⏱️  FPS: {self.dataset.fps}")
        print(f"🤖 Robot type: {episode_dataset.meta.robot_type}")
        
        # Show action names
        action_names = episode_dataset.features["action"]["names"]
        print(f"🎯 Action joints: {len(action_names)} joints")
        for i, name in enumerate(action_names):
            print(f"   {i+1:2d}. {name}")
        
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
            action_array = actions[frame_idx]["action"]
            action = {}
            for i, name in enumerate(action_names):
                action[name] = action_array[i]
            
            # Simulate sending action to robot (in real implementation, this would be robot.send_action(action))
            # For now, we'll just display the action values
            if frame_idx % 10 == 0:  # Show every 10th frame
                progress = (frame_idx + 1) / num_frames * 100
                print(f"\r🎯 Frame {frame_idx + 1}/{num_frames} ({progress:.1f}%) - "
                      f"Left arm: [{action['left_shoulder_pan.pos']:.3f}, {action['left_shoulder_lift.pos']:.3f}, {action['left_elbow_flex.pos']:.3f}] "
                      f"Right arm: [{action['right_shoulder_pan.pos']:.3f}, {action['right_shoulder_lift.pos']:.3f}, {action['right_elbow_flex.pos']:.3f}]", 
                      end="", flush=True)
            
            # Maintain timing
            dt_s = time.perf_counter() - start_frame_t
            sleep_time = max(1 / self.dataset.fps - dt_s, 0)
            time.sleep(sleep_time)
        
        print(f"\n✅ Episode {episode_idx} completed!")
        return True
    
    def run(self, start_episode=0, end_episode=None, auto_advance=False, episode_delay=2.0):
        """Main replay loop."""
        try:
            # Load dataset
            if not self.load_dataset():
                return
            
            # Set episode range
            if end_episode is None:
                end_episode = self.dataset.num_episodes - 1
            else:
                end_episode = min(end_episode, self.dataset.num_episodes - 1)
            
            # Start input listener
            self.start_input_listener()
            
            print(f"\n🎮 Starting episode replay...")
            print(f"📚 Will replay episodes {start_episode} to {end_episode} ({end_episode - start_episode + 1} episodes)")
            print(f"🎯 Type 'h' for help, 'q' to quit")
            
            # Replay each episode
            for episode_idx in range(start_episode, end_episode + 1):
                if self.should_stop:
                    break
                
                # Show episode info
                print(f"\n📖 Episode {episode_idx + 1}/{self.dataset.num_episodes} (Dataset episode {episode_idx})")
                
                # Replay the episode
                success = self.replay_single_episode(episode_idx)
                
                if not success:
                    break
                
                # Delay between episodes (unless it's the last episode)
                if episode_idx < end_episode and not self.should_stop:
                    if auto_advance:
                        print(f"\n⏳ Waiting {episode_delay}s before next episode...")
                        time.sleep(episode_delay)
                    else:
                        print("Press Enter to continue to next episode, or type a command...")
                        # Wait for user input or command
                        while not self.should_stop:
                            time.sleep(0.1)
                            if not self.is_paused:
                                break
            
            if not self.should_stop:
                print(f"\n{'='*60}")
                print("🎉 All episodes completed successfully!")
                print(f"📊 Replayed episodes {start_episode} to {end_episode}")
                print(f"{'='*60}")
            else:
                print("\n🛑 Replay stopped by user.")
                
        except Exception as e:
            print(f"❌ Error during replay: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function to replay the moving tape dataset."""
    
    print("🎬 Moving Tape Dataset Episode Replay")
    print("=" * 50)
    
    # Dataset configuration
    dataset_path = "JisooSong/moving-tape-dataset-20250915_153200"
    root_path = "./src/lerobot/datasets/multi_dataset_cache"
    
    # Create and run replayer
    replayer = DatasetEpisodeReplayer(dataset_path, root_path)
    
    # Replay first 3 episodes with auto-advance
    replayer.run(
        start_episode=0,
        end_episode=2,  # First 3 episodes (0, 1, 2)
        auto_advance=True,
        episode_delay=1.0
    )


if __name__ == "__main__":
    main()

