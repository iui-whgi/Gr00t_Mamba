# Episode Replay Usage Guide

## Overview

The `replay_all_episodes.py` script allows you to replay all episodes from a LeRobot dataset one by one, with interactive controls for pausing, skipping, and stopping.

## Basic Usage

```bash
python replay_all_episodes.py \
    --dataset.repo_id=<dataset_id> \
    --robot.type=<robot_type> \
    --robot.port=<port> \
    --robot.id=<robot_id>
```

## Examples

### Replay all episodes from a dataset
```bash
python replay_all_episodes.py \
    --dataset.repo_id=aliberts/record-test \
    --robot.type=so100_follower \
    --robot.port=/dev/tty.usbmodem58760431541 \
    --robot.id=black
```

### Replay specific episode range
```bash
python replay_all_episodes.py \
    --dataset.repo_id=aliberts/record-test \
    --robot.type=so100_follower \
    --robot.port=/dev/tty.usbmodem58760431541 \
    --robot.id=black \
    --dataset.start_episode=5 \
    --dataset.end_episode=10
```

### Auto-advance between episodes
```bash
python replay_all_episodes.py \
    --dataset.repo_id=aliberts/record-test \
    --robot.type=so100_follower \
    --robot.port=/dev/tty.usbmodem58760431541 \
    --robot.id=black \
    --auto_advance=true \
    --episode_delay=3.0
```

## Interactive Controls

While the script is running, you can use these keyboard commands:

- `h` or `help` - Show available commands
- `p` or `pause` - Pause/resume current episode
- `n` or `next` - Move to next episode (if paused)
- `s` or `skip` - Skip current episode
- `q` or `quit` - Quit replay

## Configuration Options

### Dataset Options
- `--dataset.repo_id` - Dataset repository ID (required)
- `--dataset.root` - Local dataset root directory
- `--dataset.fps` - Frames per second (default: 30)
- `--dataset.start_episode` - Start episode index (default: 0)
- `--dataset.end_episode` - End episode index (default: -1 for all)

### Robot Options
- `--robot.type` - Robot type (e.g., so100_follower, so101_follower)
- `--robot.port` - Robot port (e.g., /dev/tty.usbmodem...)
- `--robot.id` - Robot identifier

### Replay Options
- `--play_sounds` - Use vocal synthesis (default: true)
- `--episode_delay` - Delay between episodes in seconds (default: 2.0)
- `--auto_advance` - Auto-advance to next episode (default: false)

## Features

- **Sequential Episode Replay**: Replays all episodes in order
- **Interactive Controls**: Pause, skip, or stop during replay
- **Progress Display**: Shows current episode and frame progress
- **Flexible Episode Selection**: Choose specific episode ranges
- **Auto-advance Mode**: Automatically move to next episode
- **Error Handling**: Graceful handling of connection issues
- **Timing Control**: Maintains proper FPS timing during replay

## Requirements

- LeRobot dataset with recorded episodes
- Compatible robot hardware
- Proper robot drivers and connections

