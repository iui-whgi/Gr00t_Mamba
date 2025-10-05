sudo chmod 666 /dev/ttyACM*

python src/lerobot/record.py \
    --robot.type=bi_so101_follower \
    --robot.id=dual_so101 \
    --robot.left_arm_port=/dev/ttyACM0 \
    --robot.right_arm_port=/dev/ttyACM1 \
    --robot.cameras='{
        "left": {"type": "opencv", "index_or_path": 2, "width": 640, "height": 480, "fps": 30},
        "top": {"type": "opencv", "index_or_path": 6, "width": 640, "height": 480, "fps": 30},
        "right": {"type": "opencv", "index_or_path": 4, "width": 640, "height": 480, "fps": 30},
        "front": {"type": "opencv", "index_or_path": 0, "width": 640, "height": 480, "fps": 30}
    }' \
    --teleop.type=bi_so101_leader \
    --teleop.id=dual_leader_so101 \
    --teleop.left_arm_port=/dev/ttyACM2 \
    --teleop.right_arm_port=/dev/ttyACM3 \
    --dataset.repo_id=JisooSong/sandwich_596to600_vhlv \
    --dataset.num_episodes=5 \
    --dataset.single_task="Stack the sandwich in the order of vagel, ham, lettuce, and vagel" \
    --dataset.root=/home/son/lerobotjs/datasets/sandwich_596to602_vhlv