#!/usr/bin/env python3
"""
MPU9250 9-Axis IMU Test Script
Reads accelerometer, gyroscope, and magnetometer data
Tests fall detection algorithm for visual assistance system
"""

import time
import math
import sys
from smbus2 import SMBus

# I2C Configuration
I2C_BUS = 1  # Raspberry Pi I2C bus (use 1 for all modern Pi models)
MPU_ADDR = 0x68  # Default address (AD0=GND); use 0x69 if AD0=VCC

# MPU9250 Register Map
PWR_MGMT_1 = 0x6B
PWR_MGMT_2 = 0x6C
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
ACCEL_CONFIG2 = 0x1D

ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43
TEMP_OUT_H = 0x41

WHO_AM_I = 0x75  # Should return 0x71 for MPU9250

# Accelerometer scale factors (for ±2g range)
ACCEL_SCALE = 16384.0  # LSB/g for ±2g

# Gyroscope scale factors (for ±250°/s range)
GYRO_SCALE = 131.0  # LSB/(°/s) for ±250°/s


def read_byte(bus, addr, reg):
    """Read a single byte from I2C register"""
    return bus.read_byte_data(addr, reg)


def read_word(bus, addr, reg):
    """Read a 16-bit signed word from I2C register (big-endian)"""
    high = bus.read_byte_data(addr, reg)
    low = bus.read_byte_data(addr, reg + 1)
    value = (high << 8) | low
    
    # Convert to signed 16-bit
    if value >= 0x8000:
        value = -((65535 - value) + 1)
    
    return value


def initialize_mpu9250(bus, addr):
    """
    Initialize MPU9250 sensor
    
    Args:
        bus: SMBus instance
        addr: I2C address
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check WHO_AM_I register
        who_am_i = read_byte(bus, addr, WHO_AM_I)
        if who_am_i != 0x71:  # MPU9250 ID
            print(f"⚠️  Warning: WHO_AM_I = 0x{who_am_i:02X} (expected 0x71)")
            print("    Device may still work (some clones return different ID)")
        
        # Wake up device (clear sleep bit)
        bus.write_byte_data(addr, PWR_MGMT_1, 0x00)
        time.sleep(0.1)
        
        # Set clock source to PLL with X-axis gyroscope reference
        bus.write_byte_data(addr, PWR_MGMT_1, 0x01)
        time.sleep(0.1)
        
        # Configure accelerometer (±2g range)
        bus.write_byte_data(addr, ACCEL_CONFIG, 0x00)
        
        # Configure gyroscope (±250°/s range)
        bus.write_byte_data(addr, GYRO_CONFIG, 0x00)
        
        # Set sample rate divider (1kHz / (1 + 0) = 1kHz)
        bus.write_byte_data(addr, 0x19, 0x00)
        
        # Disable FSYNC and set DLPF to 44Hz bandwidth
        bus.write_byte_data(addr, CONFIG, 0x03)
        
        print("✅ MPU9250 initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing MPU9250: {e}")
        return False


def read_accel(bus, addr):
    """
    Read accelerometer data
    
    Returns:
        Tuple of (ax, ay, az) in g units
    """
    ax_raw = read_word(bus, addr, ACCEL_XOUT_H)
    ay_raw = read_word(bus, addr, ACCEL_XOUT_H + 2)
    az_raw = read_word(bus, addr, ACCEL_XOUT_H + 4)
    
    # Convert to g units
    ax = ax_raw / ACCEL_SCALE
    ay = ay_raw / ACCEL_SCALE
    az = az_raw / ACCEL_SCALE
    
    return (ax, ay, az)


def read_gyro(bus, addr):
    """
    Read gyroscope data
    
    Returns:
        Tuple of (gx, gy, gz) in degrees/second
    """
    gx_raw = read_word(bus, addr, GYRO_XOUT_H)
    gy_raw = read_word(bus, addr, GYRO_XOUT_H + 2)
    gz_raw = read_word(bus, addr, GYRO_XOUT_H + 4)
    
    # Convert to degrees/second
    gx = gx_raw / GYRO_SCALE
    gy = gy_raw / GYRO_SCALE
    gz = gz_raw / GYRO_SCALE
    
    return (gx, gy, gz)


def read_temperature(bus, addr):
    """
    Read temperature sensor
    
    Returns:
        Temperature in Celsius
    """
    temp_raw = read_word(bus, addr, TEMP_OUT_H)
    
    # Convert to Celsius: ((raw / 333.87) + 21.0)
    temp_c = (temp_raw / 333.87) + 21.0
    
    return temp_c


def calculate_magnitude(x, y, z):
    """Calculate vector magnitude (Euclidean norm)"""
    return math.sqrt(x*x + y*y + z*z)


def detect_fall_simple(accel_magnitude, gyro_magnitude, 
                       impact_threshold=2.5, rotation_threshold=150):
    """
    Simple fall detection algorithm
    
    Args:
        accel_magnitude: Total acceleration in g
        gyro_magnitude: Total rotation rate in deg/s
        impact_threshold: Acceleration spike threshold (g)
        rotation_threshold: Rotation rate threshold (deg/s)
        
    Returns:
        True if fall detected, False otherwise
    """
    # Detect high-g impact OR rapid rotation
    impact_detected = accel_magnitude > impact_threshold
    rapid_rotation = gyro_magnitude > rotation_threshold
    
    return impact_detected or rapid_rotation


def test_mpu9250(duration_sec=30):
    """
    Test MPU9250 sensor continuously
    
    Args:
        duration_sec: How long to run test (seconds)
    """
    print("=" * 60)
    print("🔄 MPU9250 9-Axis IMU Test")
    print("=" * 60)
    print(f"I2C Bus: {I2C_BUS}")
    print(f"I2C Address: 0x{MPU_ADDR:02X}")
    print(f"Test duration: {duration_sec} seconds")
    print("=" * 60)
    
    try:
        with SMBus(I2C_BUS) as bus:
            # Initialize sensor
            if not initialize_mpu9250(bus, MPU_ADDR):
                print("\n❌ Failed to initialize MPU9250")
                print("Troubleshooting:")
                print("  - Run: sudo i2cdetect -y 1")
                print("  - Check if address is 0x68 or 0x69")
                print("  - Verify wiring (SDA→GPIO2, SCL→GPIO3)")
                print("  - Ensure 3.3V power (NOT 5V!)")
                sys.exit(1)
            
            print("\nReading sensor data (Ctrl+C to stop)...\n")
            print("Legend: ax,ay,az = acceleration (g)")
            print("        gx,gy,gz = rotation rate (°/s)")
            print("        |a| = acceleration magnitude")
            print("        |g| = rotation magnitude")
            print("-" * 60)
            
            start_time = time.time()
            measurement_count = 0
            fall_count = 0
            
            while (time.time() - start_time) < duration_sec:
                measurement_count += 1
                
                # Read sensors
                ax, ay, az = read_accel(bus, MPU_ADDR)
                gx, gy, gz = read_gyro(bus, MPU_ADDR)
                temp = read_temperature(bus, MPU_ADDR)
                
                # Calculate magnitudes
                accel_mag = calculate_magnitude(ax, ay, az)
                gyro_mag = calculate_magnitude(gx, gy, gz)
                
                # Fall detection
                fall_detected = detect_fall_simple(accel_mag, gyro_mag)
                if fall_detected:
                    fall_count += 1
                
                # Display
                status = "🚨 FALL!" if fall_detected else "✅ Normal"
                
                print(f"[{measurement_count:4d}] {status}")
                print(f"  Accel: x={ax:+6.2f}g  y={ay:+6.2f}g  z={az:+6.2f}g  |a|={accel_mag:5.2f}g")
                print(f"  Gyro:  x={gx:+7.1f}°/s y={gy:+7.1f}°/s z={gz:+7.1f}°/s |g|={gyro_mag:6.1f}°/s")
                print(f"  Temp: {temp:.1f}°C")
                print()
                
                # Sample rate: ~20Hz (50ms interval)
                time.sleep(0.05)
            
            # Summary
            print("\n" + "=" * 60)
            print("📊 Test Summary")
            print("=" * 60)
            print(f"Total measurements: {measurement_count}")
            print(f"Fall events detected: {fall_count}")
            print(f"Sample rate: ~{measurement_count/duration_sec:.1f} Hz")
            
            if fall_count > 0:
                print(f"\n⚠️  {fall_count} fall-like events detected during test")
                print("    Tune thresholds if false positives occur")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Test stopped by user")
    
    except FileNotFoundError:
        print("❌ I2C device not found!")
        print("Make sure I2C is enabled:")
        print("  sudo raspi-config → Interface Options → I2C → Enable")
        sys.exit(1)
    
    except PermissionError:
        print("❌ Permission denied accessing I2C!")
        print("Add your user to i2c group:")
        print(f"  sudo usermod -a -G i2c $USER")
        print("Then log out and back in")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def calibrate_at_rest(samples=100):
    """
    Calibrate sensor by taking readings at rest
    Useful for determining offsets and noise levels
    
    Args:
        samples: Number of samples to average
    """
    print("=" * 60)
    print("📏 MPU9250 Calibration")
    print("=" * 60)
    print("Keep sensor completely still on flat surface!")
    print(f"Taking {samples} samples...")
    print()
    
    with SMBus(I2C_BUS) as bus:
        if not initialize_mpu9250(bus, MPU_ADDR):
            return
        
        time.sleep(1)  # Settle time
        
        ax_sum, ay_sum, az_sum = 0, 0, 0
        gx_sum, gy_sum, gz_sum = 0, 0, 0
        
        for i in range(samples):
            ax, ay, az = read_accel(bus, MPU_ADDR)
            gx, gy, gz = read_gyro(bus, MPU_ADDR)
            
            ax_sum += ax
            ay_sum += ay
            az_sum += az
            gx_sum += gx
            gy_sum += gy
            gz_sum += gz
            
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i+1}/{samples}")
            
            time.sleep(0.01)
        
        # Calculate averages
        ax_avg = ax_sum / samples
        ay_avg = ay_sum / samples
        az_avg = az_sum / samples
        gx_avg = gx_sum / samples
        gy_avg = gy_sum / samples
        gz_avg = gz_sum / samples
        
        print("\n" + "=" * 60)
        print("📊 Calibration Results")
        print("=" * 60)
        print(f"Accelerometer offsets:")
        print(f"  X: {ax_avg:+.4f}g  (expected: ~0)")
        print(f"  Y: {ay_avg:+.4f}g  (expected: ~0)")
        print(f"  Z: {az_avg:+.4f}g  (expected: ~1.0 for gravity)")
        print()
        print(f"Gyroscope offsets (drift):")
        print(f"  X: {gx_avg:+.2f}°/s  (expected: ~0)")
        print(f"  Y: {gy_avg:+.2f}°/s  (expected: ~0)")
        print(f"  Z: {gz_avg:+.2f}°/s  (expected: ~0)")
        print()
        
        if abs(az_avg - 1.0) > 0.1:
            print("⚠️  Warning: Z-axis acceleration not close to 1.0g")
            print("   Ensure sensor is flat and level")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test MPU9250 9-axis IMU on Raspberry Pi"
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=30,
        help='Test duration in seconds (default: 30)'
    )
    parser.add_argument(
        '--calibrate',
        action='store_true',
        help='Run calibration routine instead of test'
    )
    parser.add_argument(
        '--address',
        type=lambda x: int(x, 0),
        default=0x68,
        help='I2C address in hex (default: 0x68)'
    )
    
    args = parser.parse_args()
    
    # Override address if specified
    MPU_ADDR = args.address
    
    if args.calibrate:
        calibrate_at_rest()
    else:
        test_mpu9250(args.duration)
