#!/usr/bin/env python
"""
Direct dataset merging by copying parquet files.

This is the simplest possible approach - just copy the parquet files
from multiple datasets into a single merged dataset.
"""

import os
import json
import shutil
from pathlib import Path
import pandas as pd

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

def merge_datasets_direct(datasets, output_path):
    """Merge datasets by directly copying and renumbering parquet files"""
    
    if not datasets:
        print("No datasets found!")
        return False
    
    print(f"\nMerging {len(datasets)} datasets directly...")
    
    # Create output directory structure
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    meta_dir = output_path / "meta"
    data_dir = output_path / "data" / "chunk-000"
    videos_dir = output_path / "videos" / "chunk-000"
    
    meta_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    videos_dir.mkdir(parents=True, exist_ok=True)
    
    # Use first dataset as template for metadata
    first_dataset_path = Path(datasets[0][1])
    first_info_path = first_dataset_path / "meta" / "info.json"
    
    with open(first_info_path, 'r') as f:
        template_info = json.load(f)
    
    # Initialize merged dataset info
    merged_info = template_info.copy()
    merged_info.update({
        "total_episodes": 0,
        "total_frames": 0,
        "total_tasks": 0,
        "total_videos": 0,
        "splits": {"train": "0:0"}
    })
    
    # Process each dataset
    episode_counter = 0
    frame_counter = 0
    all_tasks = set()
    all_episodes = []
    all_episodes_stats = []
    
    for i, (dataset_name, dataset_path, info) in enumerate(datasets):
        print(f"\nProcessing dataset {i+1}/{len(datasets)}: {dataset_name}")
        
        dataset_path = Path(dataset_path)
        
        # Load episodes info
        episodes_path = dataset_path / "meta" / "episodes.jsonl"
        if episodes_path.exists():
            with open(episodes_path, 'r') as f:
                episodes = [json.loads(line) for line in f]
        else:
            episodes = []
        
        # Load tasks info
        tasks_path = dataset_path / "meta" / "tasks.jsonl"
        if tasks_path.exists():
            with open(tasks_path, 'r') as f:
                tasks = [json.loads(line) for line in f]
                for task in tasks:
                    all_tasks.add(task.get('task', 'default_task'))
        
        # Load episodes stats
        episodes_stats_path = dataset_path / "meta" / "episodes_stats.jsonl"
        if episodes_stats_path.exists():
            with open(episodes_stats_path, 'r') as f:
                episodes_stats = [json.loads(line) for line in f]
        else:
            episodes_stats = []
        
        # Process each episode
        for ep_idx, episode in enumerate(episodes):
            print(f"  Episode {ep_idx + 1}/{len(episodes)}")
            
            # Copy parquet file
            old_parquet = dataset_path / "data" / "chunk-000" / f"episode_{episode['episode_index']:06d}.parquet"
            new_parquet = data_dir / f"episode_{episode_counter:06d}.parquet"
            
            if old_parquet.exists():
                shutil.copy2(old_parquet, new_parquet)
                print(f"    Copied parquet: {old_parquet.name} -> {new_parquet.name}")
                
                # Update episode info
                new_episode = episode.copy()
                new_episode['episode_index'] = episode_counter
                all_episodes.append(new_episode)
                
                # Update frame counter
                frame_counter += episode['length']
                episode_counter += 1
                
                # Copy video files if they exist
                if 'videos' in template_info and template_info['videos']:
                    old_videos_dir = dataset_path / "videos" / "chunk-000"
                    if old_videos_dir.exists():
                        for video_key in template_info.get('video_keys', []):
                            old_video_dir = old_videos_dir / video_key
                            new_video_dir = videos_dir / video_key
                            new_video_dir.mkdir(exist_ok=True)
                            
                            old_video_file = old_video_dir / f"episode_{episode['episode_index']:06d}.mp4"
                            new_video_file = new_video_dir / f"episode_{episode_counter-1:06d}.mp4"
                            
                            if old_video_file.exists():
                                shutil.copy2(old_video_file, new_video_file)
                                print(f"    Copied video: {old_video_file.name} -> {new_video_file.name}")
            else:
                print(f"    ⚠ Parquet file not found: {old_parquet}")
    
    # Update merged info
    merged_info.update({
        "total_episodes": episode_counter,
        "total_frames": frame_counter,
        "total_tasks": len(all_tasks),
        "total_videos": episode_counter * len(template_info.get('video_keys', [])),
        "splits": {"train": f"0:{episode_counter}"}
    })
    
    # Save merged info
    with open(meta_dir / "info.json", 'w') as f:
        json.dump(merged_info, f, indent=2)
    
    # Save episodes
    with open(meta_dir / "episodes.jsonl", 'w') as f:
        for episode in all_episodes:
            f.write(json.dumps(episode) + '\n')
    
    # Save tasks
    with open(meta_dir / "tasks.jsonl", 'w') as f:
        for i, task in enumerate(sorted(all_tasks)):
            f.write(json.dumps({"task_index": i, "task": task}) + '\n')
    
    # Save episodes stats (if available)
    if all_episodes_stats:
        with open(meta_dir / "episodes_stats.jsonl", 'w') as f:
            for stats in all_episodes_stats:
                f.write(json.dumps(stats) + '\n')
    
    # Create empty stats.json
    with open(meta_dir / "stats.json", 'w') as f:
        json.dump({}, f)
    
    print(f"\n✓ Direct merge completed!")
    print(f"  Total episodes: {episode_counter}")
    print(f"  Total frames: {frame_counter}")
    print(f"  Total tasks: {len(all_tasks)}")
    print(f"  Output path: {output_path}")
    
    return True

def main():
    """Main function"""
    print("Direct Dataset Merger")
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
    output_dir = os.path.expanduser("~/lerobotjs/datasets/JisooSong-cookingbot")
    
    # Remove existing output if it exists
    if os.path.exists(output_dir):
        print(f"Removing existing output: {output_dir}")
        shutil.rmtree(output_dir)
    
    # Merge datasets
    success = merge_datasets_direct(selected_datasets, output_dir)
    
    if success:
        print(f"\n🎉 Merge successful!")
        print(f"Dataset saved at: {output_dir}")
        print(f"You can now upload it manually or use the LeRobot upload tools.")
    else:
        print(f"\n❌ Merge failed!")

if __name__ == "__main__":
    main()
