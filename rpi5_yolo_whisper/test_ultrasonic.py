#!/usr/bin/env python3
"""
HC-SR04 Ultrasonic Sensor Test Script
Measures distance to nearest obstacle using pigpio library
Converts to feet for visual assistance application
"""

import pigpio
import time
import sys

# GPIO Pins (BCM numbering)
TRIG_PIN = 23  # GPIO23 (Physical pin 16)
ECHO_PIN = 24  # GPIO24 (Physical pin 18) - MUST be level-shifted to 3.3V!

# Speed of sound in cm/s (at 20°C)
SPEED_OF_SOUND = 34300

def measure_distance_cm(pi, max_distance_cm=400):
    """
    Measure distance using HC-SR04 ultrasonic sensor
    
    Args:
        pi: pigpio.pi() instance
        max_distance_cm: Maximum expected distance (timeout calculation)
        
    Returns:
        Distance in centimeters, or None if timeout/error
    """
    # Ensure pins are configured
    pi.set_mode(TRIG_PIN, pigpio.OUTPUT)
    pi.set_mode(ECHO_PIN, pigpio.INPUT)
    
    # Send 10µs trigger pulse
    pi.write(TRIG_PIN, 0)
    time.sleep(0.00002)  # 20µs settle time
    pi.write(TRIG_PIN, 1)
    time.sleep(0.00001)  # 10µs pulse
    pi.write(TRIG_PIN, 0)
    
    # Wait for echo to go HIGH (with timeout)
    timeout_us = (max_distance_cm * 2 / SPEED_OF_SOUND) * 1e6 + 5000  # Add 5ms margin
    start_wait = time.time()
    
    while pi.read(ECHO_PIN) == 0:
        if (time.time() - start_wait) > (timeout_us / 1e6):
            return None  # Timeout waiting for echo start
    
    echo_start_tick = pi.get_current_tick()
    
    # Wait for echo to go LOW (with timeout)
    while pi.read(ECHO_PIN) == 1:
        if (time.time() - start_wait) > (timeout_us / 1e6):
            return None  # Timeout waiting for echo end
    
    echo_end_tick = pi.get_current_tick()
    
    # Calculate distance
    # tickDiff handles 32-bit tick wraparound
    pulse_duration_us = pigpio.tickDiff(echo_start_tick, echo_end_tick)
    
    # Distance = (Time × Speed of Sound) / 2
    # pulse_duration_us is in microseconds
    distance_cm = (pulse_duration_us / 1e6) * SPEED_OF_SOUND / 2.0
    
    return distance_cm


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
        String description suitable for TTS announcement
    """
    if feet is None:
        return "No obstacle detected"
    elif feet < 1.0:
        return f"Obstacle very close, less than 1 foot"
    elif feet < 3.0:
        return f"Obstacle at {feet:.1f} feet"
    elif feet < 6.0:
        return f"Obstacle at {int(feet)} feet"
    elif feet < 10.0:
        return f"Obstacle ahead at {int(feet)} feet"
    else:
        return f"Clear, over {int(feet)} feet"


def test_ultrasonic(duration_sec=30):
    """
    Test HC-SR04 sensor continuously
    
    Args:
        duration_sec: How long to run test (seconds)
    """
    print("=" * 60)
    print("🔊 HC-SR04 Ultrasonic Sensor Test")
    print("=" * 60)
    print(f"TRIG Pin: GPIO{TRIG_PIN} (Physical pin 16)")
    print(f"ECHO Pin: GPIO{ECHO_PIN} (Physical pin 18) ⚠️ MUST be level-shifted!")
    print(f"Test duration: {duration_sec} seconds")
    print("=" * 60)
    
    # Connect to pigpio daemon
    pi = pigpio.pi()
    
    if not pi.connected:
        print("❌ ERROR: pigpio daemon not running!")
        print("Start it with: sudo systemctl start pigpiod")
        sys.exit(1)
    
    print("✅ Connected to pigpio daemon")
    print("\nMeasuring distances (Ctrl+C to stop)...\n")
    
    try:
        start_time = time.time()
        measurement_count = 0
        total_valid = 0
        
        while (time.time() - start_time) < duration_sec:
            measurement_count += 1
            
            # Take measurement
            distance_cm = measure_distance_cm(pi)
            
            if distance_cm is None:
                print(f"[{measurement_count:3d}] ❌ No reading (timeout or out of range)")
            else:
                total_valid += 1
                distance_ft = cm_to_feet(distance_cm)
                distance_in = distance_ft * 12
                description = get_distance_description(distance_ft)
                
                # Visual representation
                bars = min(int(distance_ft * 2), 40)  # Scale for display
                bar_display = "█" * bars
                
                print(f"[{measurement_count:3d}] 📏 {distance_cm:6.1f} cm | "
                      f"{distance_ft:5.2f} ft | {distance_in:5.1f} in")
                print(f"      {bar_display}")
                print(f"      🗣️  TTS: \"{description}\"")
                print()
            
            # Measurement rate: ~5Hz (200ms interval)
            time.sleep(0.2)
        
        # Summary statistics
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        print(f"Total measurements: {measurement_count}")
        print(f"Valid readings: {total_valid}")
        print(f"Success rate: {(total_valid/measurement_count*100):.1f}%")
        
        if total_valid < measurement_count * 0.8:
            print("\n⚠️  Warning: Low success rate!")
            print("Troubleshooting:")
            print("  - Check ECHO pin voltage divider (5V → 3.3V)")
            print("  - Verify wiring connections")
            print("  - Ensure no obstacles within 2cm (too close)")
            print("  - Try adding 10µF capacitor between VCC and GND")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test stopped by user")
    
    finally:
        # Cleanup
        pi.set_mode(TRIG_PIN, pigpio.INPUT)  # Set to input to avoid driving
        pi.stop()
        print("✅ GPIO cleaned up")


def single_measurement():
    """Take a single distance measurement and display result"""
    pi = pigpio.pi()
    
    if not pi.connected:
        print("❌ pigpio daemon not running!")
        return
    
    print("Taking measurement...")
    distance_cm = measure_distance_cm(pi)
    
    if distance_cm is None:
        print("❌ No reading")
    else:
        distance_ft = cm_to_feet(distance_cm)
        description = get_distance_description(distance_ft)
        print(f"✅ Distance: {distance_cm:.1f} cm ({distance_ft:.2f} ft)")
        print(f"   TTS: \"{description}\"")
    
    pi.stop()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test HC-SR04 ultrasonic sensor on Raspberry Pi"
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=30,
        help='Test duration in seconds (default: 30)'
    )
    parser.add_argument(
        '--single',
        action='store_true',
        help='Take single measurement instead of continuous test'
    )
    
    args = parser.parse_args()
    
    if args.single:
        single_measurement()
    else:
        test_ultrasonic(args.duration)
