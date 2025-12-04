"""
Fall Detection System using MPU9250 IMU
Advanced fall detection with state machine and TTS alerts
"""

import time
import math
import threading
import logging
from enum import Enum
from collections import deque
from smbus2 import SMBus

logger = logging.getLogger(__name__)


class FallState(Enum):
    """Fall detection states"""
    NORMAL = "normal"
    FREEFALL = "freefall"
    IMPACT = "impact"
    LYING = "lying"


class MPU9250:
    """
    MPU9250 9-Axis IMU Interface
    Reads accelerometer, gyroscope, and magnetometer data
    """
    
    # I2C Configuration
    I2C_BUS = 1
    DEFAULT_ADDR = 0x68
    
    # Registers
    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H = 0x43
    TEMP_OUT_H = 0x41
    WHO_AM_I = 0x75
    
    # Scale factors
    ACCEL_SCALE = 16384.0  # LSB/g for ±2g range
    GYRO_SCALE = 131.0     # LSB/(°/s) for ±250°/s range
    
    def __init__(self, address=DEFAULT_ADDR, bus_number=I2C_BUS):
        """
        Initialize MPU9250
        
        Args:
            address: I2C address (0x68 or 0x69)
            bus_number: I2C bus number (1 for modern Pi)
        """
        self.address = address
        self.bus_number = bus_number
        self.bus = None
        
        self._initialize()
        logger.info(f"MPU9250 initialized at address 0x{address:02X}")
    
    def _initialize(self):
        """Initialize sensor"""
        self.bus = SMBus(self.bus_number)
        
        # Wake up device
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x00)
        time.sleep(0.1)
        
        # Set clock source
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x01)
        time.sleep(0.1)
    
    def _read_word(self, reg):
        """Read 16-bit signed word"""
        high = self.bus.read_byte_data(self.address, reg)
        low = self.bus.read_byte_data(self.address, reg + 1)
        value = (high << 8) | low
        
        if value >= 0x8000:
            value = -((65535 - value) + 1)
        
        return value
    
    def read_accel(self):
        """
        Read accelerometer data
        
        Returns:
            Tuple (ax, ay, az) in g units
        """
        ax = self._read_word(self.ACCEL_XOUT_H) / self.ACCEL_SCALE
        ay = self._read_word(self.ACCEL_XOUT_H + 2) / self.ACCEL_SCALE
        az = self._read_word(self.ACCEL_XOUT_H + 4) / self.ACCEL_SCALE
        return (ax, ay, az)
    
    def read_gyro(self):
        """
        Read gyroscope data
        
        Returns:
            Tuple (gx, gy, gz) in degrees/second
        """
        gx = self._read_word(self.GYRO_XOUT_H) / self.GYRO_SCALE
        gy = self._read_word(self.GYRO_XOUT_H + 2) / self.GYRO_SCALE
        gz = self._read_word(self.GYRO_XOUT_H + 4) / self.GYRO_SCALE
        return (gx, gy, gz)
    
    def read_temperature(self):
        """
        Read temperature
        
        Returns:
            Temperature in Celsius
        """
        temp_raw = self._read_word(self.TEMP_OUT_H)
        return (temp_raw / 333.87) + 21.0
    
    def cleanup(self):
        """Close I2C bus"""
        if self.bus:
            self.bus.close()
            logger.info("MPU9250 cleaned up")


class FallDetector:
    """
    Advanced Fall Detection System
    
    Uses multi-stage detection:
    1. Freefall detection (low g)
    2. Impact detection (high g)
    3. Lying detection (orientation change)
    """
    
    def __init__(self, imu, tts_callback=None):
        """
        Initialize fall detector
        
        Args:
            imu: MPU9250 instance
            tts_callback: Function(message) to call for speech output
        """
        self.imu = imu
        self.tts_callback = tts_callback
        
        # Thresholds (tunable based on user)
        self.freefall_threshold = 0.5      # g
        self.impact_threshold = 2.5        # g
        self.lying_threshold = 0.7         # g
        self.rotation_threshold = 150      # deg/s
        
        # Timing thresholds
        self.freefall_duration_min = 0.3   # seconds
        self.impact_duration_max = 0.5     # seconds
        self.lying_duration_min = 1.0      # seconds
        
        # State machine
        self.state = FallState.NORMAL
        self.state_start_time = time.time()
        
        # History buffers
        self.accel_history = deque(maxlen=100)  # Last 2 seconds at 50Hz
        self.gyro_history = deque(maxlen=100)
        
        # Fall event tracking
        self.last_fall_time = 0
        self.fall_cooldown = 30  # seconds before re-detection
        
        logger.info("FallDetector initialized")
    
    @staticmethod
    def magnitude(x, y, z):
        """Calculate vector magnitude"""
        return math.sqrt(x*x + y*y + z*z)
    
    def update(self, ax, ay, az, gx, gy, gz):
        """
        Update fall detection with new sensor data
        
        Args:
            ax, ay, az: Acceleration in g
            gx, gy, gz: Rotation in deg/s
            
        Returns:
            True if fall detected, False otherwise
        """
        # Calculate magnitudes
        accel_mag = self.magnitude(ax, ay, az)
        gyro_mag = self.magnitude(gx, gy, gz)
        
        # Add to history
        self.accel_history.append(accel_mag)
        self.gyro_history.append(gyro_mag)
        
        current_time = time.time()
        time_in_state = current_time - self.state_start_time
        
        # State machine
        if self.state == FallState.NORMAL:
            # Check for freefall (sudden low g)
            if accel_mag < self.freefall_threshold:
                self._transition_to(FallState.FREEFALL)
                logger.debug("Freefall detected")
        
        elif self.state == FallState.FREEFALL:
            # Check for impact (sudden high g after freefall)
            if accel_mag > self.impact_threshold:
                if time_in_state > self.freefall_duration_min:
                    self._transition_to(FallState.IMPACT)
                    logger.debug("Impact detected")
                else:
                    # Too short, false alarm
                    self._transition_to(FallState.NORMAL)
            
            # Timeout if freefall too long
            elif time_in_state > 1.0:
                self._transition_to(FallState.NORMAL)
        
        elif self.state == FallState.IMPACT:
            # Check for lying down (low g, low rotation)
            if (accel_mag < self.lying_threshold and 
                gyro_mag < 50 and 
                time_in_state > self.impact_duration_max):
                
                self._transition_to(FallState.LYING)
                logger.debug("Lying detected")
            
            # Timeout if no lying detected
            elif time_in_state > 2.0:
                self._transition_to(FallState.NORMAL)
        
        elif self.state == FallState.LYING:
            # Confirm fall if lying persists
            if time_in_state > self.lying_duration_min:
                # Check cooldown
                if (current_time - self.last_fall_time) > self.fall_cooldown:
                    self.last_fall_time = current_time
                    self._on_fall_detected()
                    self._transition_to(FallState.NORMAL)
                    return True
                else:
                    # In cooldown, reset
                    self._transition_to(FallState.NORMAL)
            
            # If person gets up quickly, false alarm
            elif accel_mag > 1.2 or gyro_mag > 100:
                logger.debug("Person got up, false alarm")
                self._transition_to(FallState.NORMAL)
        
        return False
    
    def _transition_to(self, new_state):
        """Transition to new state"""
        self.state = new_state
        self.state_start_time = time.time()
    
    def _on_fall_detected(self):
        """Handle fall detection event"""
        logger.warning("🚨 FALL DETECTED!")
        
        if self.tts_callback:
            try:
                self.tts_callback("Fall detected! Are you okay?")
            except Exception as e:
                logger.error(f"TTS callback error: {e}")
    
    def simple_fall_check(self, ax, ay, az, gx, gy, gz):
        """
        Simple fall detection (single-stage, less reliable)
        
        Returns:
            True if sudden impact or rotation detected
        """
        accel_mag = self.magnitude(ax, ay, az)
        gyro_mag = self.magnitude(gx, gy, gz)
        
        # Check cooldown
        if (time.time() - self.last_fall_time) < self.fall_cooldown:
            return False
        
        # Detect high-g impact OR rapid rotation
        if accel_mag > self.impact_threshold or gyro_mag > self.rotation_threshold:
            self.last_fall_time = time.time()
            self._on_fall_detected()
            return True
        
        return False


class FallMonitor(threading.Thread):
    """
    Background thread for continuous fall monitoring
    """
    
    def __init__(self, detector, sample_rate=50):
        """
        Initialize monitoring thread
        
        Args:
            detector: FallDetector instance
            sample_rate: Sampling rate in Hz (default: 50)
        """
        super().__init__(daemon=True)
        self.detector = detector
        self.sample_rate = sample_rate
        self.sample_interval = 1.0 / sample_rate
        
        self.running = False
        self.fall_callbacks = []
    
    def add_fall_callback(self, callback):
        """
        Add callback for fall events
        
        Args:
            callback: Function() to call when fall detected
        """
        self.fall_callbacks.append(callback)
    
    def run(self):
        """Main monitoring loop"""
        self.running = True
        logger.info(f"FallMonitor started (sample rate: {self.sample_rate}Hz)")
        
        while self.running:
            try:
                # Read sensors
                ax, ay, az = self.detector.imu.read_accel()
                gx, gy, gz = self.detector.imu.read_gyro()
                
                # Update fall detection
                fall_detected = self.detector.update(ax, ay, az, gx, gy, gz)
                
                if fall_detected:
                    # Notify callbacks
                    for callback in self.fall_callbacks:
                        try:
                            callback()
                        except Exception as e:
                            logger.error(f"Fall callback error: {e}")
                
                time.sleep(self.sample_interval)
                
            except Exception as e:
                logger.error(f"FallMonitor error: {e}")
                time.sleep(1)
        
        logger.info("FallMonitor stopped")
    
    def stop(self):
        """Stop monitoring thread"""
        self.running = False


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    
    def test_tts(message):
        print(f"🗣️  TTS: {message}")
    
    try:
        imu = MPU9250()
        detector = FallDetector(imu, tts_callback=test_tts)
        
        print("Testing fall detection for 30 seconds...")
        print("Try shaking or rotating the sensor quickly\n")
        
        for i in range(1500):  # 30 seconds at 50Hz
            ax, ay, az = imu.read_accel()
            gx, gy, gz = imu.read_gyro()
            
            accel_mag = detector.magnitude(ax, ay, az)
            gyro_mag = detector.magnitude(gx, gy, gz)
            
            fall = detector.update(ax, ay, az, gx, gy, gz)
            
            if i % 50 == 0:  # Print every second
                status = "🚨 FALL!" if fall else f"State: {detector.state.value}"
                print(f"[{i/50:.0f}s] {status} | a={accel_mag:.2f}g g={gyro_mag:.1f}°/s")
            
            time.sleep(0.02)
        
        imu.cleanup()
        
    except KeyboardInterrupt:
        print("\nStopped")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
