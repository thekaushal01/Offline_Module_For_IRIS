"""
Ultrasonic Sensor Module using lgpio for Raspberry Pi 5
HC-SR04 distance measurement with filtering and monitoring
"""

import lgpio
import time
import threading
import logging
from typing import Optional, Callable
from collections import deque

logger = logging.getLogger(__name__)

# GPIO chip for Pi 5
GPIO_CHIP = 4  # /dev/gpiochip4

# Speed of sound in cm/s
SPEED_OF_SOUND = 34300


class UltrasonicSensor:
    """HC-SR04 Ultrasonic sensor with lgpio for Pi 5"""
    
    def __init__(self, trig_pin: int = 23, echo_pin: int = 24, gpio_chip: int = GPIO_CHIP):
        """
        Initialize ultrasonic sensor
        
        Args:
            trig_pin: GPIO pin for trigger (BCM numbering)
            echo_pin: GPIO pin for echo (BCM numbering, MUST be level-shifted!)
            gpio_chip: GPIO chip number (4 for Pi 5)
        """
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.gpio_chip = gpio_chip
        self.h = None
        
        # Measurement history for filtering
        self.history = deque(maxlen=5)
        
        # Initialize GPIO
        self._setup_gpio()
        
    def _setup_gpio(self):
        """Setup GPIO pins"""
        try:
            self.h = lgpio.gpiochip_open(self.gpio_chip)
            lgpio.gpio_claim_output(self.h, self.trig_pin)
            lgpio.gpio_claim_input(self.h, self.echo_pin)
            logger.info(f"✅ Ultrasonic sensor initialized (TRIG={self.trig_pin}, ECHO={self.echo_pin})")
        except Exception as e:
            logger.error(f"Failed to initialize ultrasonic sensor: {e}")
            raise
    
    def measure_distance_raw(self, max_distance_cm: float = 400) -> Optional[float]:
        """
        Single distance measurement
        
        Args:
            max_distance_cm: Maximum expected distance for timeout
            
        Returns:
            Distance in cm, or None if timeout/error
        """
        if self.h is None:
            return None
            
        try:
            # Send trigger pulse
            lgpio.gpio_write(self.h, self.trig_pin, 0)
            time.sleep(0.00002)
            lgpio.gpio_write(self.h, self.trig_pin, 1)
            time.sleep(0.00001)
            lgpio.gpio_write(self.h, self.trig_pin, 0)
            
            # Wait for echo
            timeout_s = (max_distance_cm * 2 / SPEED_OF_SOUND) + 0.005
            start_wait = time.time()
            
            # Wait for HIGH
            while lgpio.gpio_read(self.h, self.echo_pin) == 0:
                if (time.time() - start_wait) > timeout_s:
                    return None
            
            echo_start = time.time()
            
            # Wait for LOW
            while lgpio.gpio_read(self.h, self.echo_pin) == 1:
                if (time.time() - start_wait) > timeout_s:
                    return None
            
            echo_end = time.time()
            
            # Calculate distance
            pulse_duration = echo_end - echo_start
            distance_cm = (pulse_duration * SPEED_OF_SOUND) / 2.0
            
            # Validate range (2cm to 400cm)
            if 2 <= distance_cm <= 400:
                return distance_cm
            return None
            
        except Exception as e:
            logger.error(f"Error measuring distance: {e}")
            return None
    
    def measure_distance_filtered(self) -> Optional[float]:
        """
        Get filtered distance using median of last 5 readings
        
        Returns:
            Filtered distance in cm, or None
        """
        cm = self.measure_distance_raw()
        
        if cm is not None:
            self.history.append(cm)
        
        if len(self.history) >= 3:
            # Return median of history
            sorted_history = sorted(self.history)
            return sorted_history[len(sorted_history) // 2]
        elif len(self.history) > 0:
            return self.history[-1]
        
        return None
    
    def get_distance_feet(self) -> Optional[float]:
        """Get filtered distance in feet"""
        cm = self.measure_distance_filtered()
        if cm is not None:
            return cm / 30.48
        return None
    
    def get_distance_description(self, feet: Optional[float] = None) -> str:
        """
        Get TTS-friendly distance description
        
        Args:
            feet: Distance in feet (if None, will measure)
            
        Returns:
            Human-readable description
        """
        if feet is None:
            feet = self.get_distance_feet()
        
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
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        if self.h is not None:
            try:
                lgpio.gpiochip_close(self.h)
                logger.info("🔒 Ultrasonic sensor GPIO closed")
            except:
                pass
            self.h = None


class UltrasonicMonitor(threading.Thread):
    """Background thread for continuous distance monitoring"""
    
    def __init__(self, sensor: UltrasonicSensor, update_interval: float = 0.2):
        """
        Initialize monitor thread
        
        Args:
            sensor: UltrasonicSensor instance
            update_interval: Time between measurements in seconds
        """
        super().__init__(daemon=True)
        self.sensor = sensor
        self.update_interval = update_interval
        self.running = False
        self.callbacks = []
        self.last_distance = None
        self.distance_threshold = 1.0  # feet change threshold for callback
        
    def add_callback(self, callback: Callable[[float, str], None]):
        """
        Add callback for distance updates
        
        Args:
            callback: Function(distance_feet, description) called on significant change
        """
        self.callbacks.append(callback)
    
    def run(self):
        """Monitor loop"""
        self.running = True
        logger.info("🔊 Ultrasonic monitor started")
        
        while self.running:
            try:
                feet = self.sensor.get_distance_feet()
                
                if feet is not None:
                    # Check if significant change
                    if (self.last_distance is None or 
                        abs(feet - self.last_distance) >= self.distance_threshold):
                        
                        description = self.sensor.get_distance_description(feet)
                        
                        # Notify callbacks
                        for callback in self.callbacks:
                            try:
                                callback(feet, description)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")
                        
                        self.last_distance = feet
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(1.0)
        
        logger.info("🛑 Ultrasonic monitor stopped")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
