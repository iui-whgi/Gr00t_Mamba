#!/bin/bash

sudo chmod 666 /dev/ttyACM*

lerobot-calibrate \
    --teleop.type=bi_so101_leader \
    --teleop.left_arm_port=/dev/ttyACM2 \
    --teleop.right_arm_port=/dev/ttyACM3 \
    --teleop.id=dual_leader_so101

# lerobot-calibrate \
#     --robot.type=bi_so101_follower \
#     --robot.left_arm_port=/dev/ttyACM0 \
#     --robot.right_arm_port=/dev/ttyACM1 \
#     --robot.id=dual_so101