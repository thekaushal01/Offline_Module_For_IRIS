#!/usr/bin/env python3
"""
HC-SR04 Ultrasonic Sensor Test Script (lgpio version for Raspberry Pi 5)
Measures distance to nearest obstacle using lgpio library
Converts to feet for visual assistance application
"""

import lgpio
import time
import sys
import argparse

# GPIO Pins (BCM numbering)
TRIG_PIN = 23  # GPIO23 (Physical pin 16)
ECHO_PIN = 24  # GPIO24 (Physical pin 18) - MUST be level-shifted to 3.3V!

# GPIO chip for Pi 5
GPIO_CHIP = 4  # /dev/gpiochip4 on Raspberry Pi 5

# Speed of sound in cm/s (at 20°C)
SPEED_OF_SOUND = 34300

def measure_distance_cm(h, max_distance_cm=400):
    """
    Measure distance using HC-SR04 ultrasonic sensor
    
    Args:
        h: lgpio chip handle
        max_distance_cm: Maximum expected distance (timeout calculation)
        
    Returns:
        Distance in centimeters, or None if timeout/error
    """
    try:
        # Send 10µs trigger pulse
        lgpio.gpio_write(h, TRIG_PIN, 0)
        time.sleep(0.00002)  # 20µs settle time
        lgpio.gpio_write(h, TRIG_PIN, 1)
        time.sleep(0.00001)  # 10µs pulse
        lgpio.gpio_write(h, TRIG_PIN, 0)
        
        # Wait for echo to go HIGH (with timeout)
        timeout_s = (max_distance_cm * 2 / SPEED_OF_SOUND) + 0.005  # Add 5ms margin
        start_wait = time.time()
        
        while lgpio.gpio_read(h, ECHO_PIN) == 0:
            if (time.time() - start_wait) > timeout_s:
                return None  # Timeout waiting for echo start
        
        echo_start = time.time()
        
        # Wait for echo to go LOW (with timeout)
        while lgpio.gpio_read(h, ECHO_PIN) == 1:
            if (time.time() - start_wait) > timeout_s:
                return None  # Timeout waiting for echo end
        
        echo_end = time.time()
        
        # Calculate distance
        pulse_duration = echo_end - echo_start
        distance_cm = (pulse_duration * SPEED_OF_SOUND) / 2.0
        
        return distance_cm
        
    except Exception as e:
        print(f"Error measuring distance: {e}")
        return None


def cm_to_feet(cm):
    """Convert centimeters to feet"""
    if cm is None:
        return None
    return cm / 30.48


def get_distance_description(feet):
    """
    Get human-readable distance description for TTS
    
    Args:
        feet: Distance in feet
        
    Returns:
        Human-readable string suitable for TTS
    """
    if feet is None:
        return "No obstacle detected"
    elif feet < 1.0:
        return f"Very close, less than 1 foot"
    elif feet < 3.0:
        return f"Obstacle at {feet:.1f} feet"
    elif feet < 6.0:
        return f"Object at {feet:.1f} feet ahead"
    elif feet < 10.0:
        return f"Clear path, obstacle {feet:.0f} feet away"
    else:
        return "Clear path ahead"


def print_header(duration):
    """Print test header"""
    print("=" * 60)
    print("🔊 HC-SR04 Ultrasonic Sensor Test (lgpio/Pi5)")
    print("=" * 60)
    print(f"TRIG Pin: GPIO{TRIG_PIN} (Physical pin 16)")
    print(f"ECHO Pin: GPIO{ECHO_PIN} (Physical pin 18) ⚠️ MUST be level-shifted!")
    print(f"Test duration: {duration} seconds")
    print("=" * 60)
    print("%" * 60)


def visualize_distance(feet, max_feet=13):
    """Create ASCII bar visualization of distance"""
    if feet is None:
        return "[TIMEOUT]"
    
    # Clamp to max range
    feet = min(feet, max_feet)
    bar_length = int((feet / max_feet) * 40)
    bar = "█" * bar_length + "░" * (40 - bar_length)
    return f"[{bar}] {feet:.2f}ft"


def run_single_test(h):
    """Run a single distance measurement"""
    print("\n" + "=" * 60)
    print("Single measurement test")
    print("=" * 60)
    
    cm = measure_distance_cm(h)
    feet = cm_to_feet(cm)
    
    if cm is not None:
        print(f"✅ Distance: {cm:.2f} cm ({feet:.2f} feet)")
        print(f"📢 TTS: {get_distance_description(feet)}")
        print(visualize_distance(feet))
    else:
        print("❌ No response - check wiring and voltage divider!")
    
    print("=" * 60)


def run_continuous_test(h, duration):
    """Run continuous distance measurements"""
    print("\nContinuous measurement mode")
    print("Press Ctrl+C to stop early\n")
    
    start_time = time.time()
    measurement_count = 0
    success_count = 0
    
    try:
        while (time.time() - start_time) < duration:
            cm = measure_distance_cm(h)
            feet = cm_to_feet(cm)
            measurement_count += 1
            
            if cm is not None:
                success_count += 1
                print(f"{visualize_distance(feet)} | {get_distance_description(feet)}")
            else:
                print("[TIMEOUT] No echo received - check sensor!")
            
            time.sleep(0.2)  # 5 measurements per second
            
    except KeyboardInterrupt:
        print("\n\n⏸️  Test stopped by user")
    
    # Print statistics
    elapsed = time.time() - start_time
    success_rate = (success_count / measurement_count * 100) if measurement_count > 0 else 0
    
    print("\n" + "=" * 60)
    print("📊 Test Statistics")
    print("=" * 60)
    print(f"Duration: {elapsed:.1f} seconds")
    print(f"Total measurements: {measurement_count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {measurement_count - success_count}")
    print(f"Success rate: {success_rate:.1f}%")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Test HC-SR04 ultrasonic sensor (Pi 5)')
    parser.add_argument('--duration', type=int, default=10,
                       help='Test duration in seconds (default: 10)')
    parser.add_argument('--single', action='store_true',
                       help='Run single measurement only')
    args = parser.parse_args()
    
    # Open GPIO chip
    try:
        h = lgpio.gpiochip_open(GPIO_CHIP)
        print(f"✅ Opened GPIO chip {GPIO_CHIP}")
    except Exception as e:
        print(f"❌ ERROR: Failed to open GPIO chip {GPIO_CHIP}")
        print(f"Error: {e}")
        print("\nMake sure you have lgpio installed:")
        print("  sudo apt-get install python3-lgpio")
        print("  pip install lgpio")
        return 1
    
    try:
        # Configure pins
        lgpio.gpio_claim_output(h, TRIG_PIN)
        lgpio.gpio_claim_input(h, ECHO_PIN)
        print(f"✅ Configured TRIG={TRIG_PIN}, ECHO={ECHO_PIN}")
        
        # Print header
        print_header(args.duration if not args.single else "single")
        
        # Run test
        if args.single:
            run_single_test(h)
        else:
            run_continuous_test(h, args.duration)
        
        print("\n✅ Test completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Cleanup
        lgpio.gpiochip_close(h)
        print("🔒 GPIO chip closed")


if __name__ == "__main__":
    sys.exit(main())
