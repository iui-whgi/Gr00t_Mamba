#!/usr/bin/env python3

"""
Test script to demonstrate episode replay functionality without requiring robot hardware.

This script loads a LeRobot dataset and shows how to iterate through episodes.
"""

import time
from lerobot.datasets.lerobot_dataset import LeRobotDataset


def test_dataset_loading():
    """Test loading a dataset and showing episode information."""
    
    # Try to load a test dataset
    try:
        print("Loading test dataset...")
        dataset = LeRobotDataset("lerobot/test")
        
        print(f"\n{'='*60}")
        print(f"Dataset: {dataset.repo_id}")
        print(f"Total episodes: {dataset.num_episodes}")
        print(f"Total frames: {dataset.num_frames}")
        print(f"FPS: {dataset.fps}")
        print(f"Features: {list(dataset.features.keys())}")
        print(f"{'='*60}\n")
        
        # Show episode information
        for ep_idx in range(min(5, dataset.num_episodes)):  # Show first 5 episodes
            ep_start = dataset.episode_data_index["from"][ep_idx].item()
            ep_end = dataset.episode_data_index["to"][ep_idx].item()
            ep_length = ep_end - ep_start
            
            print(f"Episode {ep_idx}: frames {ep_start}-{ep_end-1} (length: {ep_length})")
        
        if dataset.num_episodes > 5:
            print(f"... and {dataset.num_episodes - 5} more episodes")
        
        return dataset
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None


def simulate_episode_replay(dataset, episode_idx):
    """Simulate replaying an episode (without actual robot control)."""
    
    print(f"\n{'='*40}")
    print(f"Simulating Episode {episode_idx + 1}/{dataset.num_episodes}")
    print(f"{'='*40}")
    
    # Load specific episode
    episode_dataset = LeRobotDataset(
        dataset.repo_id, 
        root=dataset.root, 
        episodes=[episode_idx]
    )
    
    actions = episode_dataset.hf_dataset.select_columns("action")
    num_frames = episode_dataset.num_frames
    
    print(f"Episode {episode_idx} has {num_frames} frames")
    print(f"Action names: {episode_dataset.features['action']['names']}")
    
    # Simulate replaying each frame
    for frame_idx in range(min(10, num_frames)):  # Show first 10 frames
        action_array = actions[frame_idx]["action"]
        action = {}
        for i, name in enumerate(episode_dataset.features["action"]["names"]):
            action[name] = action_array[i]
        
        print(f"Frame {frame_idx + 1}: {action}")
        time.sleep(0.1)  # Simulate timing
    
    if num_frames > 10:
        print(f"... and {num_frames - 10} more frames")
    
    print(f"Episode {episode_idx} simulation completed!")


def main():
    """Main function to test episode replay functionality."""
    
    print("Testing Episode Replay Functionality")
    print("=" * 50)
    
    # Load dataset
    dataset = test_dataset_loading()
    
    if dataset is None:
        print("Could not load dataset. Exiting.")
        return
    
    # Simulate replaying a few episodes
    num_episodes_to_test = min(3, dataset.num_episodes)
    
    for ep_idx in range(num_episodes_to_test):
        simulate_episode_replay(dataset, ep_idx)
        
        if ep_idx < num_episodes_to_test - 1:
            print(f"\nWaiting 2 seconds before next episode...")
            time.sleep(2)
    
    print(f"\n{'='*60}")
    print("Episode replay simulation completed!")
    print(f"Tested {num_episodes_to_test} episodes out of {dataset.num_episodes} total")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

