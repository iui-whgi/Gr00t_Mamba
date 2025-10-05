#!/usr/bin/env python
"""
Simplified dataset merging utility for LeRobot datasets.

This script provides a much simpler approach to merging datasets by:
1. Loading datasets individually
2. Extracting all frames from each dataset
3. Creating a new dataset with all frames
4. Saving and uploading the result
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from lerobot.datasets.lerobot_dataset import LeRobotDataset

def find_datasets():
    """Find available moving-tape datasets"""
    possible_paths = [
        ".",
        "~/lerobotjs/datasets",
        os.path.expanduser("~/lerobotjs/datasets"),
        "/home/son/lerobotjs/datasets",
    ]
    
    datasets = []
    for path in possible_paths:
        expanded_path = os.path.expanduser(path)
        if os.path.exists(expanded_path):
            print(f"Checking path: {expanded_path}")
            for item in os.listdir(expanded_path):
                item_path = os.path.join(expanded_path, item)
                if item.startswith('moving-tape-dataset') and os.path.isdir(item_path):
                    info_path = os.path.join(item_path, 'meta', 'info.json')
                    if os.path.exists(info_path):
                        try:
                            with open(info_path, 'r') as f:
                                info = json.load(f)
                            datasets.append((item, item_path, info))
                            print(f"✓ Found: {item} ({info.get('total_episodes', '?')} episodes)")
                        except Exception as e:
                            print(f"✗ Error reading {item}: {e}")
    
    return datasets

def create_merged_dataset(datasets, output_path):
    """Create a merged dataset from multiple datasets"""
    
    if not datasets:
        print("No datasets found!")
        return None
    
    print(f"\nCreating merged dataset from {len(datasets)} datasets...")
    
    # Use first dataset as template
    first_dataset_path = datasets[0][1]
    first_dataset = LeRobotDataset(first_dataset_path)
    
    print(f"Template dataset: {first_dataset_path}")
    print(f"  FPS: {first_dataset.fps}")
    print(f"  Features: {list(first_dataset.features.keys())}")
    print(f"  Camera keys: {first_dataset.camera_keys}")
    
    # Create new dataset
    merged_dataset = LeRobotDataset.create(
        repo_id="JisooSong/cookingbot",
        fps=first_dataset.fps,
        features=first_dataset.features,
        root=output_path,
        robot_type=first_dataset.meta.robot_type,
        use_videos=len(first_dataset.meta.video_keys) > 0
    )
    
    print(f"Created merged dataset at: {merged_dataset.root}")
    
    # Process each dataset
    total_episodes = 0
    total_frames = 0
    
    for i, (dataset_name, dataset_path, info) in enumerate(datasets):
        print(f"\nProcessing dataset {i+1}/{len(datasets)}: {dataset_name}")
        
        try:
            # Load dataset
            dataset = LeRobotDataset(dataset_path)
            print(f"  Episodes: {dataset.num_episodes}")
            print(f"  Frames: {dataset.num_frames}")
            
            # Process each episode
            for ep_idx in range(dataset.num_episodes):
                print(f"    Episode {ep_idx + 1}/{dataset.num_episodes}")
                
                # Get episode frame range
                ep_start = dataset.episode_data_index["from"][ep_idx].item()
                ep_end = dataset.episode_data_index["to"][ep_idx].item()
                
                print(f"      Frames: {ep_start} to {ep_end-1} ({ep_end - ep_start} frames)")
                
                # Create new episode buffer
                merged_dataset.episode_buffer = merged_dataset.create_episode_buffer(
                    episode_index=merged_dataset.num_episodes
                )
                
                # Process each frame in the episode
                for frame_idx in range(ep_start, ep_end):
                    try:
                        # Get frame data
                        frame_data = dataset[frame_idx]
                        
                        # Extract task
                        task = frame_data.get('task', 'default_task')
                        
                        # Prepare frame data (exclude metadata)
                        new_frame_data = {}
                        for key, value in frame_data.items():
                            if key in ['episode_index', 'index', 'frame_index', 'timestamp', 
                                     'task_index', 'task', 'dataset_index']:
                                continue
                            
                            # Handle image dimension conversion if needed
                            if 'images' in key and hasattr(value, 'shape') and len(value.shape) == 3:
                                if value.shape[0] == 3:  # (3, H, W) -> (H, W, 3)
                                    import torch
                                    import numpy as np
                                    if isinstance(value, torch.Tensor):
                                        value = value.permute(1, 2, 0)
                                    elif isinstance(value, np.ndarray):
                                        value = value.transpose(1, 2, 0)
                                    else:
                                        value = np.array(value)
                                        if value.shape[0] == 3:
                                            value = value.transpose(1, 2, 0)
                            
                            new_frame_data[key] = value
                        
                        # Add frame to merged dataset
                        merged_dataset.add_frame(new_frame_data, task)
                        
                    except Exception as frame_error:
                        print(f"      ⚠ Frame {frame_idx} error: {frame_error}")
                        continue
                
                # Save episode
                try:
                    merged_dataset.save_episode()
                    print(f"      ✓ Episode saved")
                    total_episodes += 1
                    total_frames += (ep_end - ep_start)
                except Exception as save_error:
                    print(f"      ✗ Episode save failed: {save_error}")
                    continue
                    
        except Exception as dataset_error:
            print(f"  ✗ Dataset {dataset_name} failed: {dataset_error}")
            continue
    
    print(f"\nMerge completed!")
    print(f"  Total episodes: {total_episodes}")
    print(f"  Total frames: {total_frames}")
    print(f"  Dataset episodes: {merged_dataset.num_episodes}")
    print(f"  Dataset frames: {merged_dataset.num_frames}")
    
    return merged_dataset

def main():
    """Main function"""
    print("Simple Dataset Merger")
    print("=" * 50)
    
    # Find datasets
    datasets = find_datasets()
    
    if not datasets:
        print("No datasets found!")
        return
    
    print(f"\nFound {len(datasets)} datasets:")
    for i, (name, path, info) in enumerate(datasets):
        print(f"  {i+1}. {name} ({info.get('total_episodes', '?')} episodes)")
    
    # Ask which datasets to merge
    if len(datasets) == 1:
        selected = [0]
    else:
        print(f"\nWhich datasets to merge? (enter numbers separated by commas, or 'all' for all)")
        choice = input("Choice: ").strip()
        
        if choice.lower() == 'all':
            selected = list(range(len(datasets)))
        else:
            try:
                selected = [int(x.strip()) - 1 for x in choice.split(',')]
                selected = [x for x in selected if 0 <= x < len(datasets)]
            except:
                print("Invalid choice, using all datasets")
                selected = list(range(len(datasets)))
    
    selected_datasets = [datasets[i] for i in selected]
    print(f"\nSelected {len(selected_datasets)} datasets for merging")
    
    # Create output directory
    output_dir = os.path.expanduser("~/lerobotjs/datasets")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create merged dataset
    merged_dataset = create_merged_dataset(selected_datasets, output_dir)
    
    if merged_dataset is None:
        print("Failed to create merged dataset!")
        return
    
    # Upload to hub
    print(f"\nUploading to HuggingFace Hub...")
    try:
        merged_dataset.push_to_hub(
            tags=["robotics", "manipulation", "merged-dataset", "moving-tape"],
            private=False,
            push_videos=True
        )
        print(f"✓ Upload successful!")
        print(f"URL: https://huggingface.co/datasets/JisooSong/cookingbot")
    except Exception as upload_error:
        print(f"✗ Upload failed: {upload_error}")
        print(f"Dataset saved locally at: {merged_dataset.root}")

if __name__ == "__main__":
    main()
