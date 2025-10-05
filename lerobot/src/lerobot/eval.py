#!/usr/bin/env python

"""
GR00T Model Evaluation Script for bi_so101_follower Robot

This script provides the following functionality:
1. Connect to GR00T model server
2. Connect to bi_so101_follower robot
3. Control robot movement using actions received from server

Usage:
    python eval.py --server_host <server_IP> --server_port <port> --robot_config <robot_config_file>
"""

import argparse
import logging
import time
from typing import Any, Dict

import numpy as np
import requests
import json_numpy

from lerobot.robots.bi_so101_follower import BiSO101Follower
from lerobot.robots.bi_so101_follower.config_bi_so101_follower import BiSO101FollowerConfig

# Apply JSON numpy patch
json_numpy.patch()

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




class GR00TEvaluator:
    """
    Robot evaluation class using GR00T model
    """
    
    def __init__(self, server_host: str, server_port: int, robot_config: Dict[str, Any]):
        self.server_host = server_host
        self.server_port = server_port
        self.server_url = f"http://{server_host}:{server_port}"
        
        # Robot configuration
        robot_config_obj = BiSO101FollowerConfig(**robot_config)
        self.robot = BiSO101Follower(robot_config_obj)
        
        self.is_running = False
        
    def connect_robot(self) -> bool:
        """Connect to robot"""
        try:
            logger.info("Connecting to robot...")
            self.robot.connect(calibrate=True)
            
            if self.robot.is_connected:
                logger.info("Robot connected successfully!")
                return True
            else:
                logger.error("Failed to connect to robot")
                return False
                
        except Exception as e:
            logger.error(f"Error occurred while connecting to robot: {e}")
            return False
    
    def test_server_connection(self) -> bool:
        """Test server connection"""
        try:
            logger.info(f"Testing server connection: {self.server_url}")
            
            # Simple test request
            test_obs = {
                "video.ego_view": np.random.randint(0, 256, (1, 256, 256, 3), dtype=np.uint8),
                "state.left_arm": np.random.rand(1, 7),
                "state.right_arm": np.random.rand(1, 7),
                "state.left_hand": np.random.rand(1, 6),
                "state.right_hand": np.random.rand(1, 6),
                "state.waist": np.random.rand(1, 3),
                "annotation.human.action.task_description": ["Test task"],
            }
            
            response = requests.post(
                f"{self.server_url}/act", 
                json={"observation": test_obs},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Server connection successful!")
                return True
            else:
                logger.error(f"Server response error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Server connection test failed: {e}")
            return False
    
    def get_action_from_server(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Get action from server"""
        try:
            response = requests.post(
                f"{self.server_url}/act",
                json={"observation": observation},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get action from server: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Server communication error: {e}")
            return {}
    
    def observation_to_server_format(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        """Convert robot observation to server format"""
        # Convert to server expected format
        server_obs = {}
        
        # Video data (from camera)
        if "ego_view" in obs:
            server_obs["video.ego_view"] = obs["ego_view"]
        else:
            # Generate default video data (if no camera available)
            server_obs["video.ego_view"] = np.random.randint(0, 256, (1, 256, 256, 3), dtype=np.uint8)
        
        # Robot state data
        left_arm_pos = []
        right_arm_pos = []
        left_hand_pos = []
        right_hand_pos = []
        waist_pos = []
        
        # Extract joint positions from observation
        for key, value in obs.items():
            if key.startswith("left_") and key.endswith(".pos"):
                left_arm_pos.append(value)
            elif key.startswith("right_") and key.endswith(".pos"):
                right_arm_pos.append(value)
        
        # Fill with default values (adjust according to actual joint count)
        if len(left_arm_pos) < 7:
            left_arm_pos.extend([0.0] * (7 - len(left_arm_pos)))
        if len(right_arm_pos) < 7:
            right_arm_pos.extend([0.0] * (7 - len(right_arm_pos)))
        
        server_obs["state.left_arm"] = np.array([left_arm_pos[:7]])
        server_obs["state.right_arm"] = np.array([right_arm_pos[:7]])
        server_obs["state.left_hand"] = np.array([[0.0] * 6])  # Default value
        server_obs["state.right_hand"] = np.array([[0.0] * 6])  # Default value
        server_obs["state.waist"] = np.array([[0.0] * 3])  # Default value
        
        # Task description
        server_obs["annotation.human.action.task_description"] = ["Robot control task"]
        
        return server_obs
    
    def server_action_to_robot_format(self, server_action: Dict[str, Any]) -> Dict[str, Any]:
        """Convert server action to robot format"""
        robot_action = {}
        
        # Convert server action to robot format
        if "action.left_arm" in server_action:
            left_arm_actions = server_action["action.left_arm"][0]  # Use first timestep
            for i, pos in enumerate(left_arm_actions):
                robot_action[f"left_shoulder_pan.pos"] = pos if i == 0 else robot_action.get(f"left_shoulder_pan.pos", 0)
                robot_action[f"left_shoulder_lift.pos"] = pos if i == 1 else robot_action.get(f"left_shoulder_lift.pos", 0)
                robot_action[f"left_elbow_flex.pos"] = pos if i == 2 else robot_action.get(f"left_elbow_flex.pos", 0)
                robot_action[f"left_wrist_flex.pos"] = pos if i == 3 else robot_action.get(f"left_wrist_flex.pos", 0)
                robot_action[f"left_wrist_roll.pos"] = pos if i == 4 else robot_action.get(f"left_wrist_roll.pos", 0)
                robot_action[f"left_gripper.pos"] = pos if i == 5 else robot_action.get(f"left_gripper.pos", 0)
        
        if "action.right_arm" in server_action:
            right_arm_actions = server_action["action.right_arm"][0]  # Use first timestep
            for i, pos in enumerate(right_arm_actions):
                robot_action[f"right_shoulder_pan.pos"] = pos if i == 0 else robot_action.get(f"right_shoulder_pan.pos", 0)
                robot_action[f"right_shoulder_lift.pos"] = pos if i == 1 else robot_action.get(f"right_shoulder_lift.pos", 0)
                robot_action[f"right_elbow_flex.pos"] = pos if i == 2 else robot_action.get(f"right_elbow_flex.pos", 0)
                robot_action[f"right_wrist_flex.pos"] = pos if i == 3 else robot_action.get(f"right_wrist_flex.pos", 0)
                robot_action[f"right_wrist_roll.pos"] = pos if i == 4 else robot_action.get(f"right_wrist_roll.pos", 0)
                robot_action[f"right_gripper.pos"] = pos if i == 5 else robot_action.get(f"right_gripper.pos", 0)
        
        return robot_action
    
    def run_evaluation(self, duration: int = 60):
        """Run evaluation"""
        logger.info(f"Starting evaluation - running for {duration} seconds")
        self.is_running = True
        start_time = time.time()
        
        try:
            while self.is_running and (time.time() - start_time) < duration:
                # Collect robot observation
                obs = self.robot.get_observation()
                
                # Convert to server format
                server_obs = self.observation_to_server_format(obs)
                
                # Get action from server
                server_action = self.get_action_from_server(server_obs)
                
                if server_action:
                    # Convert to robot format
                    robot_action = self.server_action_to_robot_format(server_action)
                    
                    # Send action to robot
                    self.robot.send_action(robot_action)
                    
                    logger.info(f"Action sent successfully: {len(robot_action)} joints")
                else:
                    logger.warning("Failed to get action from server")
                
                # Wait briefly
                time.sleep(0.1)  # Run at 10Hz
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error occurred during evaluation: {e}")
        finally:
            self.is_running = False
            logger.info("Evaluation ended")
    
    def disconnect(self):
        """Disconnect"""
        if self.robot.is_connected:
            self.robot.disconnect()
            logger.info("Robot disconnected")


def main():
    parser = argparse.ArgumentParser(description="GR00T model evaluation for bi_so101_follower robot")
    
    parser.add_argument("--server_host", type=str, default="localhost", 
                       help="GR00T server host (default: localhost)")
    parser.add_argument("--server_port", type=int, default=5000, 
                       help="GR00T server port (default: 5000)")
    parser.add_argument("--duration", type=int, default=60, 
                       help="Evaluation duration in seconds (default: 60)")
    
    # Robot configuration
    parser.add_argument("--left_arm_port", type=str, default="/dev/ttyUSB0", 
                       help="Left arm port")
    parser.add_argument("--right_arm_port", type=str, default="/dev/ttyUSB1", 
                       help="Right arm port")
    parser.add_argument("--calibration_dir", type=str, default="~/.cache/huggingface/calibration/robots/bi_so101_follower", 
                       help="Calibration directory")
    
    args = parser.parse_args()
    
    # Robot configuration
    robot_config = {
        "id": "bi_so101_follower",
        "left_arm_port": args.left_arm_port,
        "right_arm_port": args.right_arm_port,
        "calibration_dir": args.calibration_dir,
        "left_arm_disable_torque_on_disconnect": True,
        "right_arm_disable_torque_on_disconnect": True,
        "left_arm_max_relative_target": 0.1,
        "right_arm_max_relative_target": 0.1,
        "left_arm_use_degrees": True,
        "right_arm_use_degrees": True,
        "cameras": {}  # Add camera configuration if needed
    }
    
    # Create evaluator
    evaluator = GR00TEvaluator(
        server_host=args.server_host,
        server_port=args.server_port,
        robot_config=robot_config
    )
    
    try:
        # Test server connection
        if not evaluator.test_server_connection():
            logger.error("Server connection failed. Exiting program.")
            return
        
        # Connect to robot
        if not evaluator.connect_robot():
            logger.error("Robot connection failed. Exiting program.")
            return
        
        # Run evaluation
        evaluator.run_evaluation(duration=args.duration)
        
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        evaluator.disconnect()


if __name__ == "__main__":
    main()
