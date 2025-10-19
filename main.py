"""
Pimoroni Grow Moisture Sensor Display - WITH ICONS & NTP TIME
For Raspberry Pi Pico 2W with SSD1306 OLED
Author: Alex
Date: October 2025

Uses Phosphor icon bitmaps instead of custom drawing
Syncs time via NTP on startup

Hardware connections:
- Moisture Sensor (PFM signal): GP26 (Black wire)
- OLED SDA: GP4
- OLED SCL: GP5
- Sensor & OLED powered from 3.3V and GND

IMPORTANT: Capacitive moisture sensors have INVERSE frequency relationship:
- DRY (air) = HIGH frequency (~25-30 Hz)
- WET (water) = LOW frequency (~0-5 Hz)
"""

import machine
import time
import framebuf
from ssd1306 import SSD1306_I2C
from icon_bitmaps import DROP_EMPTY, DROP_HALF, DROP_FULL
import json
import network
import ntptime

# Hardware configuration
SENSOR_PIN = 26
I2C_SDA = 4
I2C_SCL = 5
I2C_FREQ = 400000
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64

# Timing configuration
MEASUREMENT_INTERVAL = 60  # seconds between readings
FREQUENCY_SAMPLE_TIME = 2  # seconds to measure pulse frequency

# Configuration files
CONFIG_FILE = 'moisture_config.json'
WIFI_CONFIG_FILE = 'wifi_config.json'

# Timezone offset for UK (GMT/BST)
# Set to 0 for GMT (winter) or 1 for BST (summer)
# MicroPython doesn't auto-detect DST, so you may need to adjust this
TIMEZONE_OFFSET = 0  # Hours offset from UTC

class WiFiManager:
    """Handles WiFi connection and NTP time sync"""
    
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.connected = False
        
    def load_credentials(self):
        """Load WiFi credentials from JSON file"""
        try:
            with open(WIFI_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config['ssid'], config['password']
        except Exception as e:
            print(f"Error loading WiFi config: {e}")
            return None, None
    
    def connect(self, timeout=10):
        """Connect to WiFi network"""
        ssid, password = self.load_credentials()
        
        if not ssid or not password:
            print("No WiFi credentials found")
            return False
        
        print(f"Connecting to WiFi '{ssid}'...")
        
        self.wlan.active(True)
        self.wlan.connect(ssid, password)
        
        # Wait for connection
        start_time = time.time()
        while not self.wlan.isconnected():
            if time.time() - start_time > timeout:
                print("WiFi connection timeout!")
                return False
            time.sleep(0.5)
            print(".", end="")
        
        print("\n✓ WiFi connected!")
        print(f"IP address: {self.wlan.ifconfig()[0]}")
        self.connected = True
        return True
    
    def sync_time(self, max_retries=3):
        """Sync time from NTP server"""
        if not self.connected:
            print("Not connected to WiFi, cannot sync time")
            return False
        
        print("Syncing time from NTP server...")
        
        for attempt in range(max_retries):
            try:
                ntptime.settime()
                
                # Get the current time and apply timezone offset
                current_time = time.localtime()
                print(f"✓ Time synced: {current_time[0]}-{current_time[1]:02d}-{current_time[2]:02d} "
                      f"{current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}")
                
                # Apply timezone offset if needed
                if TIMEZONE_OFFSET != 0:
                    print(f"Applying timezone offset: +{TIMEZONE_OFFSET} hours")
                    epoch_time = time.time()
                    adjusted_time = epoch_time + (TIMEZONE_OFFSET * 3600)
                    tm = time.localtime(adjusted_time)
                    # Note: Can't directly set with offset in MicroPython,
                    # but time.localtime() will use the system time
                
                return True
                
            except Exception as e:
                print(f"NTP sync attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        print("Failed to sync time after all retries")
        return False
    
    def disconnect(self):
        """Disconnect from WiFi to save power"""
        if self.connected:
            self.wlan.disconnect()
            self.wlan.active(False)
            self.connected = False
            print("WiFi disconnected")

class MoistureSensor:
    """Handles reading from Pimoroni Grow PFM moisture sensor"""
    
    def __init__(self, pin_number):
        self.pin = machine.Pin(pin_number, machine.Pin.IN, machine.Pin.PULL_DOWN)
        self.pulse_count = 0
        self.last_frequency = 0
        
    def count_pulse(self, pin):
        """Interrupt handler for counting pulses"""
        self.pulse_count += 1
    
    def read_frequency(self, sample_time=2):
        """
        Measure the pulse frequency from the sensor
        Returns frequency in Hz
        """
        self.pulse_count = 0
        
        # Set up interrupt on rising edge
        self.pin.irq(trigger=machine.Pin.IRQ_RISING, handler=self.count_pulse)
        
        # Count pulses for sample_time seconds
        time.sleep(sample_time)
        
        # Disable interrupt
        self.pin.irq(handler=None)
        
        # Calculate frequency
        frequency = self.pulse_count / sample_time
        self.last_frequency = frequency
        
        return frequency
    
    def read_moisture_percent(self, dry_freq, wet_freq):
        """
        Convert frequency to moisture percentage
        IMPORTANT: INVERSE relationship for capacitive sensors
        - Dry (air) = HIGH frequency
        - Wet (water) = LOW frequency
        """
        freq = self.read_frequency(FREQUENCY_SAMPLE_TIME)
        
        # Clamp frequency to calibration range (note: dry_freq > wet_freq)
        freq = max(min(freq, dry_freq), wet_freq)
        
        # Convert to percentage (0% = dry, 100% = wet)
        if dry_freq == wet_freq:
            return 0
        
        # INVERSE: higher freq = drier, so (dry_freq - freq) gives moisture
        moisture_percent = ((dry_freq - freq) / (dry_freq - wet_freq)) * 100
        return max(0, min(100, moisture_percent))  # Clamp to 0-100%

class MoistureDisplay:
    """Handles OLED display with Phosphor icon graphics"""
    
    def __init__(self, i2c):
        self.oled = SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, i2c)
        self.oled.contrast(255)
        
        # Create framebuffers for icons
        self.icon_empty = framebuf.FrameBuffer(DROP_EMPTY, 32, 32, framebuf.MONO_HLSB)
        self.icon_half = framebuf.FrameBuffer(DROP_HALF, 32, 32, framebuf.MONO_HLSB)
        self.icon_full = framebuf.FrameBuffer(DROP_FULL, 32, 32, framebuf.MONO_HLSB)
        
    def clear(self):
        """Clear the display"""
        self.oled.fill(0)
        self.oled.show()
    
    def get_icon_for_moisture(self, moisture_percent):
        """Select appropriate icon based on moisture level"""
        if moisture_percent < 34:
            return self.icon_empty  # 0-33%: Empty drop
        elif moisture_percent < 67:
            return self.icon_half   # 34-66%: Half drop
        else:
            return self.icon_full   # 67-100%: Full drop
    
    def show_moisture(self, moisture_percent, frequency):
        """Display moisture reading with Phosphor icon"""
        self.oled.fill(0)
        
        # Select and display appropriate icon
        icon = self.get_icon_for_moisture(moisture_percent)
        self.oled.blit(icon, 0, 16)  # Center vertically (64-32)/2 = 16
        
        # Display text on right side
        self.oled.text("Moisture", 40, 10, 1)
        
        # Large percentage display
        percent_text = "{:.0f}%".format(moisture_percent)
        self.oled.text(percent_text, 50, 28, 1)
        
        # Show frequency (for debugging/info)
        freq_text = "{:.1f}Hz".format(frequency)
        self.oled.text(freq_text, 45, 50, 1)
        
        self.oled.show()
    
    def show_message(self, line1, line2="", line3="", line4=""):
        """Display a multi-line message"""
        self.oled.fill(0)
        if line1:
            self.oled.text(line1, 0, 0, 1)
        if line2:
            self.oled.text(line2, 0, 16, 1)
        if line3:
            self.oled.text(line3, 0, 32, 1)
        if line4:
            self.oled.text(line4, 0, 48, 1)
        self.oled.show()
    
    def power_off(self):
        """Turn off display to save power"""
        self.oled.poweroff()
    
    def power_on(self):
        """Turn on display"""
        self.oled.poweron()

class Configuration:
    """Handles saving and loading calibration data"""
    
    def __init__(self, filename):
        self.filename = filename
        self.dry_freq = 27.0  # Default: typical dry reading (HIGH frequency)
        self.wet_freq = 5.0   # Default: typical wet reading (LOW frequency)
        self.load()
    
    def load(self):
        """Load configuration from file"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.dry_freq = data.get('dry_freq', 27.0)
                self.wet_freq = data.get('wet_freq', 5.0)
                print(f"Loaded config: dry={self.dry_freq}Hz, wet={self.wet_freq}Hz")
        except:
            print("No config file found, using defaults")
            self.save()  # Create default config file
    
    def save(self):
        """Save configuration to file"""
        data = {
            'dry_freq': self.dry_freq,
            'wet_freq': self.wet_freq
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f)
        print(f"Saved config: dry={self.dry_freq}Hz, wet={self.wet_freq}Hz")

def format_timestamp():
    """Format current time as readable string"""
    t = time.localtime()
    return f"{t[0]}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}"

def main():
    """Main program loop"""
    print("\n" + "="*50)
    print("Pimoroni Grow Moisture Monitor (with Icons)")
    print("="*50)
    
    # Initialize I2C for OLED
    print("Initializing I2C...")
    i2c = machine.I2C(0, sda=machine.Pin(I2C_SDA), scl=machine.Pin(I2C_SCL), freq=I2C_FREQ)
    print(f"I2C devices found: {i2c.scan()}")
    
    # Initialize display
    print("Initializing display...")
    display = MoistureDisplay(i2c)
    display.show_message("Grow Monitor", "Starting...", "", "")
    
    # Connect to WiFi and sync time
    print("\n--- WiFi & Time Sync ---")
    wifi = WiFiManager()
    
    display.show_message("Connecting", "to WiFi...", "", "")
    
    if wifi.connect(timeout=15):
        display.show_message("WiFi OK", "Syncing time...", "", "")
        time.sleep(1)
        
        if wifi.sync_time():
            display.show_message("Time synced!", format_timestamp(), "", "")
            time.sleep(2)
        else:
            display.show_message("Time sync", "failed", "", "Continuing...")
            time.sleep(2)
        
        # Disconnect WiFi to save power (we only needed it for time sync)
        wifi.disconnect()
    else:
        display.show_message("WiFi failed", "Time not set", "", "Continuing...")
        print("Warning: Could not sync time, timestamps will be incorrect")
        time.sleep(2)
    
    # Initialize sensor
    print("\nInitializing sensor...")
    sensor = MoistureSensor(SENSOR_PIN)
    
    # Load configuration
    print("Loading configuration...")
    config = Configuration(CONFIG_FILE)
    
    display.show_message("Ready!", "", "", "")
    time.sleep(1)
    
    # Main monitoring loop
    print("\n=== STARTING MONITORING ===")
    print(f"Current time: {format_timestamp()}")
    print(f"Update interval: {MEASUREMENT_INTERVAL} seconds")
    print(f"Icon switching:")
    print(f"  0-33%:  Empty drop (slash)")
    print(f"  34-66%: Half drop")
    print(f"  67-100%: Full drop")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Take reading
            timestamp = format_timestamp()
            print(f"[{timestamp}] Taking reading...")
            moisture = sensor.read_moisture_percent(config.dry_freq, config.wet_freq)
            frequency = sensor.last_frequency
            
            print(f"Frequency: {frequency:.2f} Hz")
            print(f"Moisture: {moisture:.1f}%")
            
            # Determine which icon
            if moisture < 34:
                icon_name = "EMPTY"
            elif moisture < 67:
                icon_name = "HALF"
            else:
                icon_name = "FULL"
            print(f"Displaying: {icon_name} drop icon")
            
            # Update display
            display.power_on()
            display.show_moisture(moisture, frequency)
            
            # Keep display on for 10 seconds then power off to save energy
            time.sleep(10)
            display.power_off()
            
            # Wait until next reading
            print(f"Sleeping for {MEASUREMENT_INTERVAL} seconds...\n")
            time.sleep(MEASUREMENT_INTERVAL - 10)  # Account for 10s display time
            
    except KeyboardInterrupt:
        print("\n\nStopping monitoring...")
        display.clear()
        display.show_message("Monitor", "Stopped", "", "")
        time.sleep(2)
        display.clear()
        print("Goodbye!")

if __name__ == "__main__":
    main()
