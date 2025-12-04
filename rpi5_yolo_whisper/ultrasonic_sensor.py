"""
Ultrasonic Distance Sensor Module
HC-SR04 interface using pigpio for accurate timing
Provides distance measurements in feet with filtering
"""

import pigpio
import time
import threading
import logging
from collections import deque

logger = logging.getLogger(__name__)


class UltrasonicSensor:
    """
    HC-SR04 Ultrasonic Distance Sensor Interface
    
    Features:
    - Accurate timing using pigpio library
    - Median filtering for stable readings
    - Automatic outlier rejection
    - Thread-safe operation
    """
    
    def __init__(self, trig_pin=23, echo_pin=24, max_distance_cm=400):
        """
        Initialize ultrasonic sensor
        
        Args:
            trig_pin: GPIO pin for trigger (default: 23)
            echo_pin: GPIO pin for echo (default: 24, MUST be level-shifted!)
            max_distance_cm: Maximum detection range (default: 400cm/13ft)
        """
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.max_distance_cm = max_distance_cm
        
        # Initialize pigpio
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpio daemon not running. Start with: sudo systemctl start pigpiod")
        
        # Configure pins
        self.pi.set_mode(self.trig_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.echo_pin, pigpio.INPUT)
        self.pi.write(self.trig_pin, 0)
        
        # Median filter buffer (stores last N readings)
        self.filter_size = 5
        self.distance_buffer = deque(maxlen=self.filter_size)
        
        # Speed of sound in cm/µs
        self.speed_of_sound = 0.0343  # cm/µs at 20°C
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info(f"UltrasonicSensor initialized (TRIG=GPIO{trig_pin}, ECHO=GPIO{echo_pin})")
    
    def measure_distance_raw(self):
        """
        Take a single distance measurement
        
        Returns:
            Distance in centimeters, or None if timeout/error
        """
        with self.lock:
            # Send 10µs trigger pulse
            self.pi.write(self.trig_pin, 0)
            time.sleep(0.00002)  # 20µs settle
            self.pi.write(self.trig_pin, 1)
            time.sleep(0.00001)  # 10µs pulse
            self.pi.write(self.trig_pin, 0)
            
            # Calculate timeout based on max distance
            timeout_us = (self.max_distance_cm * 2 / (self.speed_of_sound * 100)) + 5000
            start_wait = time.time()
            
            # Wait for echo start (HIGH)
            while self.pi.read(self.echo_pin) == 0:
                if (time.time() - start_wait) > (timeout_us / 1e6):
                    logger.warning("Ultrasonic timeout waiting for echo start")
                    return None
            
            echo_start = self.pi.get_current_tick()
            
            # Wait for echo end (LOW)
            while self.pi.read(self.echo_pin) == 1:
                if (time.time() - start_wait) > (timeout_us / 1e6):
                    logger.warning("Ultrasonic timeout waiting for echo end")
                    return None
            
            echo_end = self.pi.get_current_tick()
            
            # Calculate distance
            pulse_duration = pigpio.tickDiff(echo_start, echo_end)  # µs
            distance = (pulse_duration * self.speed_of_sound) / 2.0  # cm
            
            # Validate range
            if distance < 2 or distance > self.max_distance_cm:
                return None
            
            return distance
    
    def measure_distance_filtered(self):
        """
        Get filtered distance measurement using median filter
        
        Returns:
            Distance in centimeters, or None if no valid reading
        """
        # Take measurement
        distance = self.measure_distance_raw()
        
        if distance is not None:
            self.distance_buffer.append(distance)
        
        # Return median of buffer
        if len(self.distance_buffer) >= 3:
            sorted_buffer = sorted(self.distance_buffer)
            return sorted_buffer[len(sorted_buffer) // 2]
        elif len(self.distance_buffer) > 0:
            return self.distance_buffer[-1]
        else:
            return None
    
    def get_distance_feet(self):
        """
        Get distance in feet with filtering
        
        Returns:
            Distance in feet, or None if no reading
        """
        cm = self.measure_distance_filtered()
        if cm is None:
            return None
        return cm / 30.48
    
    def get_distance_description(self, feet=None):
        """
        Get human-readable distance description for TTS
        
        Args:
            feet: Distance in feet (if None, takes new measurement)
            
        Returns:
            String description suitable for speech
        """
        if feet is None:
            feet = self.get_distance_feet()
        
        if feet is None:
            return "No obstacle detected"
        elif feet < 0.5:
            return "Obstacle very close, less than half a foot"
        elif feet < 1.0:
            return f"Obstacle very close, less than 1 foot"
        elif feet < 2.0:
            return f"Obstacle at {feet:.1f} feet"
        elif feet < 5.0:
            return f"Obstacle at {int(round(feet))} feet"
        elif feet < 10.0:
            return f"Obstacle ahead at {int(round(feet))} feet"
        else:
            return "Path clear, over 10 feet"
    
    def cleanup(self):
        """Release GPIO resources"""
        if self.pi.connected:
            self.pi.set_mode(self.trig_pin, pigpio.INPUT)
            self.pi.stop()
            logger.info("UltrasonicSensor cleaned up")


class UltrasonicMonitor(threading.Thread):
    """
    Background thread for continuous ultrasonic monitoring
    Provides callbacks when distance changes significantly
    """
    
    def __init__(self, sensor, update_interval=0.2, distance_change_threshold=1.0):
        """
        Initialize monitoring thread
        
        Args:
            sensor: UltrasonicSensor instance
            update_interval: Measurement interval in seconds
            distance_change_threshold: Minimum change in feet to trigger callback
        """
        super().__init__(daemon=True)
        self.sensor = sensor
        self.update_interval = update_interval
        self.distance_change_threshold = distance_change_threshold
        
        self.running = False
        self.last_distance = None
        self.callbacks = []
    
    def add_callback(self, callback):
        """
        Add callback function to be called when distance changes
        
        Args:
            callback: Function(distance_feet, description) to call
        """
        self.callbacks.append(callback)
    
    def run(self):
        """Main monitoring loop"""
        self.running = True
        logger.info("UltrasonicMonitor started")
        
        while self.running:
            try:
                # Get current distance
                distance_feet = self.sensor.get_distance_feet()
                
                # Check for significant change
                if distance_feet is not None:
                    if (self.last_distance is None or 
                        abs(distance_feet - self.last_distance) >= self.distance_change_threshold):
                        
                        description = self.sensor.get_distance_description(distance_feet)
                        
                        # Notify callbacks
                        for callback in self.callbacks:
                            try:
                                callback(distance_feet, description)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")
                        
                        self.last_distance = distance_feet
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"UltrasonicMonitor error: {e}")
                time.sleep(1)
        
        logger.info("UltrasonicMonitor stopped")
    
    def stop(self):
        """Stop monitoring thread"""
        self.running = False


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    
    try:
        sensor = UltrasonicSensor()
        
        print("Testing ultrasonic sensor for 10 seconds...")
        print("Move objects in front of sensor to see readings\n")
        
        for i in range(50):
            distance_cm = sensor.measure_distance_raw()
            if distance_cm:
                feet = distance_cm / 30.48
                desc = sensor.get_distance_description(feet)
                print(f"[{i+1}] {distance_cm:.1f} cm ({feet:.2f} ft) - {desc}")
            else:
                print(f"[{i+1}] No reading")
            
            time.sleep(0.2)
        
        sensor.cleanup()
        
    except KeyboardInterrupt:
        print("\nStopped")
    except Exception as e:
        print(f"Error: {e}")
