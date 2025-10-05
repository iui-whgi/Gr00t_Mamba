#!/usr/bin/env python3

"""
Find available robot ports for SO101 bimanual robot.

This script helps identify the correct USB ports for your robot arms.
"""

import serial.tools.list_ports
import subprocess
import os


def find_robot_ports():
    """Find available robot ports."""
    print("🔍 Searching for robot ports...")
    print("=" * 50)
    
    # Method 1: List all serial ports
    print("📡 Available serial ports:")
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("   No serial ports found!")
        return []
    
    for i, port in enumerate(ports):
        print(f"   {i+1}. {port.device} - {port.description}")
        if port.vid and port.pid:
            print(f"      VID: {port.vid:04X}, PID: {port.pid:04X}")
    
    # Method 2: Check common robot ports
    print("\n🤖 Checking common robot ports:")
    common_ports = [
        "/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3",
        "/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3",
        "/dev/tty.usbmodem*", "/dev/tty.usbserial*"
    ]
    
    available_ports = []
    for port_pattern in common_ports:
        if "*" in port_pattern:
            # Use glob to find matching ports
            import glob
            matching_ports = glob.glob(port_pattern)
            for port in matching_ports:
                if os.path.exists(port):
                    available_ports.append(port)
                    print(f"   ✅ {port}")
        else:
            if os.path.exists(port_pattern):
                available_ports.append(port_pattern)
                print(f"   ✅ {port_pattern}")
            else:
                print(f"   ❌ {port_pattern}")
    
    # Method 3: Check for Dynamixel devices
    print("\n🔧 Checking for Dynamixel devices:")
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'dynamixel' in line.lower() or 'robotis' in line.lower():
                    print(f"   🤖 {line}")
                elif 'usb' in line.lower() and 'serial' in line.lower():
                    print(f"   📡 {line}")
        else:
            print("   ❌ Could not run lsusb")
    except Exception as e:
        print(f"   ❌ Error running lsusb: {e}")
    
    # Method 4: Check dmesg for recent USB connections
    print("\n📋 Recent USB connections (last 20 lines):")
    try:
        result = subprocess.run(['dmesg', '|', 'tail', '-20'], 
                              shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'usb' in line.lower() and ('tty' in line.lower() or 'serial' in line.lower()):
                    print(f"   📡 {line}")
        else:
            print("   ❌ Could not check dmesg")
    except Exception as e:
        print(f"   ❌ Error checking dmesg: {e}")
    
    return available_ports


def suggest_robot_config(available_ports):
    """Suggest robot configuration based on available ports."""
    print("\n💡 Suggested robot configuration:")
    print("=" * 50)
    
    if len(available_ports) >= 2:
        print("✅ Found enough ports for bimanual robot!")
        print(f"   Left arm port: {available_ports[0]}")
        print(f"   Right arm port: {available_ports[1]}")
        print()
        print("Update your script with these ports:")
        print(f"robot_config = BiSO101FollowerConfig(")
        print(f"    left_arm_port='{available_ports[0]}',")
        print(f"    right_arm_port='{available_ports[1]}',")
        print(f"    id='bimanual_so101'")
        print(f")")
    elif len(available_ports) == 1:
        print("⚠️  Only found one port. You might need:")
        print("   - Connect both robot arms")
        print("   - Check USB cables")
        print("   - Install robot drivers")
        print(f"   Available port: {available_ports[0]}")
    else:
        print("❌ No robot ports found. Please check:")
        print("   - Robot is powered on")
        print("   - USB cables are connected")
        print("   - Robot drivers are installed")
        print("   - Try different USB ports")


def main():
    """Main function to find robot ports."""
    print("🔍 Robot Port Finder for SO101 Bimanual Robot")
    print("=" * 60)
    
    available_ports = find_robot_ports()
    suggest_robot_config(available_ports)
    
    print("\n📚 Next steps:")
    print("1. Update the ports in replay_with_real_robot.py")
    print("2. Make sure robot is powered on and connected")
    print("3. Run: python replay_with_real_robot.py")


if __name__ == "__main__":
    main()

