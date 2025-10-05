#!/usr/bin/env python3

"""
Test robot connection on different ports.
"""

import serial
import time

def test_port(port):
    """Test if a port can be opened."""
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        print(f"✅ {port}: Connection successful")
        ser.close()
        return True
    except Exception as e:
        print(f"❌ {port}: {e}")
        return False

def main():
    print("🔍 Testing robot port connections...")
    print("=" * 50)
    
    ports_to_test = [
        "/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3",
        "/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3"
    ]
    
    working_ports = []
    
    for port in ports_to_test:
        if test_port(port):
            working_ports.append(port)
    
    print(f"\n📊 Results:")
    print(f"   Working ports: {working_ports}")
    
    if len(working_ports) >= 2:
        print(f"\n💡 Suggested configuration:")
        print(f"   Left arm: {working_ports[0]}")
        print(f"   Right arm: {working_ports[1]}")
    elif len(working_ports) == 1:
        print(f"\n⚠️  Only one port working: {working_ports[0]}")
        print("   Check if both robot arms are connected")
    else:
        print(f"\n❌ No working ports found!")
        print("   Make sure:")
        print("   - Robot is powered on")
        print("   - USB cables are connected")
        print("   - Try running with sudo: sudo python test_robot_connection.py")

if __name__ == "__main__":
    main()

