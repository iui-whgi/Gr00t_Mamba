#!/bin/bash

sudo chmod 666 /dev/ttyACM*

# huggingface-cli login

# HF_USER=$(huggingface-cli whoami | head -n 1)
HF_USER="JisooSong"  # 임시로 사용자명 설정
echo $HF_USER

# 작업 디렉토리를 LeRobot 루트로 변경

# 수정된 명령어 - 현재 LeRobot 코드베이스와 호환
python ~/lerobot/src/lerobot/record.py \
    --robot.type=bi_so101_follower \
    --robot.id="dual_so101" \
    --robot.left_arm_port=/dev/ttyACM0 \
    --robot.right_arm_port=/dev/ttyACM1 \
    --robot.cameras='{
        "left": {"type": "opencv", "index_or_path": 0, "width": 640, "height": 480, "fps": 30},
        "top": {"type": "opencv", "index_or_path": 2, "width": 640, "height": 480, "fps": 30},
        "right": {"type": "opencv", "index_or_path": 4, "width": 640, "height": 480, "fps": 30}
    }' \
    --teleop.type=bi_so101_leader \
    --teleop.id="dual_leader_so101" \
    --teleop.left_arm_port=/dev/ttyACM2 \
    --teleop.right_arm_port=/dev/ttyACM3 \
    --dataset.repo_id=${HF_USER}/moving-tape-dataset \
    --dataset.num_episodes=5 \
    --dataset.single_task="Clap twice" \
    --dataset.root=/home/son/lerobotjs/datasets/moving-tape-dataset-$(date +%Y%m%d_%H%M%S)