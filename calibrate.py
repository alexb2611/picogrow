"""
Manual Calibration Script (Button-less) - FIXED VERSION
For Pimoroni Grow Moisture Monitor
Author: Alex
Date: October 2025

IMPORTANT: Capacitive sensors have INVERSE frequency relationship!
- DRY (air) = HIGH frequency (~20-30 Hz)
- WET (water) = LOW frequency (~0-5 Hz)

This script provides a button-less calibration process with plenty of time
to move the sensor between dry and wet conditions.
"""

import machine
import time
from ssd1306 import SSD1306_I2C
import json

# Hardware configuration
SENSOR_PIN = 26
I2C_SDA = 4
I2C_SCL = 5
I2C_FREQ = 400000
CONFIG_FILE = 'moisture_config.json'

# Timing - adjust these if you need more/less time
PREP_TIME = 10  # Seconds to prepare sensor between measurements
SAMPLE_TIME = 3  # Seconds to measure frequency (for accuracy)

class MoistureSensor:
    """Handles reading from Pimoroni Grow PFM moisture sensor"""
    
    def __init__(self, pin_number):
        self.pin = machine.Pin(pin_number, machine.Pin.IN, machine.Pin.PULL_DOWN)
        self.pulse_count = 0
        self.last_frequency = 0
        
    def count_pulse(self, pin):
        """Interrupt handler for counting pulses"""
        self.pulse_count += 1
    
    def read_frequency(self, sample_time=3):
        """Measure the pulse frequency from the sensor"""
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

class MoistureDisplay:
    """Simple display handler"""
    
    def __init__(self, i2c):
        self.oled = SSD1306_I2C(128, 64, i2c)
        self.oled.contrast(255)
    
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

def countdown_timer(display, seconds, message):
    """Show a countdown on the display"""
    for i in range(seconds, 0, -1):
        display.show_message(
            message,
            "",
            f"{i} seconds...",
            "Get ready!"
        )
        print(f"{message} - {i} seconds remaining...")
        time.sleep(1)

def save_config(dry_freq, wet_freq):
    """Save calibration values to file"""
    data = {
        'dry_freq': dry_freq,
        'wet_freq': wet_freq
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)
    print(f"\nCalibration saved to {CONFIG_FILE}")
    print(f"  Dry: {dry_freq:.2f} Hz (HIGH frequency - in air)")
    print(f"  Wet: {wet_freq:.2f} Hz (LOW frequency - in water)")

def main():
    """Manual calibration with timed intervals"""
    print("\n" + "="*60)
    print("MANUAL CALIBRATION - Button-less Version (FIXED)")
    print("="*60)
    print("\nIMPORTANT: Capacitive sensors have INVERSE frequency!")
    print("  - Dry (air) = HIGH frequency (~20-30 Hz)")
    print("  - Wet (water) = LOW frequency (~0-5 Hz)")
    print(f"\nThis script will guide you through calibration with")
    print(f"{PREP_TIME} seconds between each measurement.\n")
    
    # Initialize hardware
    print("Initializing hardware...")
    i2c = machine.I2C(0, sda=machine.Pin(I2C_SDA), scl=machine.Pin(I2C_SCL), freq=I2C_FREQ)
    display = MoistureDisplay(i2c)
    sensor = MoistureSensor(SENSOR_PIN)
    
    display.show_message("CALIBRATION", "Starting...", "", "")
    time.sleep(2)
    
    # ========================================
    # STEP 1: DRY CALIBRATION
    # ========================================
    print("\n" + "="*60)
    print("STEP 1: DRY CALIBRATION (expect HIGH frequency)")
    print("="*60)
    print("\nINSTRUCTIONS:")
    print("1. Remove sensor from soil completely")
    print("2. Hold sensor in AIR (not touching anything wet)")
    print("3. Keep sensor steady during measurement")
    print(f"\nYou have {PREP_TIME} seconds to prepare...")
    print("Starting countdown NOW!\n")
    
    display.show_message("STEP 1:", "Remove sensor", "Hold in AIR", "")
    
    # Countdown to dry measurement
    countdown_timer(display, PREP_TIME, "DRY - Hold in air")
    
    # Take dry measurement
    display.show_message("Measuring...", "DRY reading", "Hold still!", "")
    print("\nMeasuring DRY frequency...")
    print("(Hold sensor steady in air)")
    
    dry_freq = sensor.read_frequency(SAMPLE_TIME)
    
    print(f"\n✓ DRY frequency measured: {dry_freq:.2f} Hz")
    
    display.show_message("DRY Reading:", f"{dry_freq:.1f} Hz", "(HIGH freq)", "Step 1 done!")
    time.sleep(3)
    
    # ========================================
    # STEP 2: WET CALIBRATION
    # ========================================
    print("\n" + "="*60)
    print("STEP 2: WET CALIBRATION (expect LOW frequency)")
    print("="*60)
    print("\nINSTRUCTIONS:")
    print("1. Place sensor in a glass/cup of water, OR")
    print("2. Push sensor into VERY wet/saturated soil")
    print("3. Make sure sensor is fully submerged/surrounded")
    print(f"\nYou have {PREP_TIME} seconds to prepare...")
    print("Starting countdown NOW!\n")
    
    display.show_message("STEP 2:", "Put sensor", "in WATER", "")
    
    # Countdown to wet measurement
    countdown_timer(display, PREP_TIME, "WET - Put in water")
    
    # Take wet measurement
    display.show_message("Measuring...", "WET reading", "Hold still!", "")
    print("\nMeasuring WET frequency...")
    print("(Sensor should be in water/very wet soil)")
    
    wet_freq = sensor.read_frequency(SAMPLE_TIME)
    
    print(f"\n✓ WET frequency measured: {wet_freq:.2f} Hz")
    
    display.show_message("WET Reading:", f"{wet_freq:.1f} Hz", "(LOW freq)", "Step 2 done!")
    time.sleep(3)
    
    # ========================================
    # VALIDATION & SAVE
    # ========================================
    print("\n" + "="*60)
    print("CALIBRATION RESULTS")
    print("="*60)
    print(f"\nDry frequency:  {dry_freq:.2f} Hz (should be HIGH)")
    print(f"Wet frequency:  {wet_freq:.2f} Hz (should be LOW)")
    print(f"Difference:     {dry_freq - wet_freq:.2f} Hz")
    
    # Validate results - DRY should be HIGHER than WET!
    if wet_freq >= dry_freq:
        print("\n⚠️  ERROR: Dry frequency should be HIGHER than wet!")
        print("    Capacitive sensors have INVERSE relationship:")
        print("    - Dry (air) = HIGH frequency")
        print("    - Wet (water) = LOW frequency")
        print(f"    Got: Dry={dry_freq:.1f}Hz, Wet={wet_freq:.1f}Hz")
        print("    Something went wrong - try again!")
        display.show_message("ERROR!", "Dry <= Wet", "Try again", "")
        time.sleep(5)
        return
    
    if dry_freq < 15:
        print("\n⚠️  WARNING: Dry frequency seems low (<15 Hz)")
        print("    Expected ~20-30 Hz for sensor in air")
        print("    Was the sensor actually in air?")
        display.show_message("WARNING!", "Low dry freq", "Check setup", "")
        time.sleep(5)
    
    if wet_freq > 10:
        print("\n⚠️  WARNING: Wet frequency seems high (>10 Hz)")
        print("    Expected ~0-5 Hz for sensor in water")
        print("    Was the sensor actually submerged?")
        display.show_message("WARNING!", "High wet freq", "Check setup", "")
        time.sleep(5)
    
    # Save configuration
    print("\nSaving calibration...")
    save_config(dry_freq, wet_freq)
    
    display.show_message("Calibration", "COMPLETE!", "", "Saved!")
    time.sleep(3)
    
    # ========================================
    # FINAL SUMMARY
    # ========================================
    print("\n" + "="*60)
    print("✓ CALIBRATION COMPLETE!")
    print("="*60)
    print(f"\nYour calibration values:")
    print(f"  Dry: {dry_freq:.2f} Hz  (HIGH - sensor in air)")
    print(f"  Wet: {wet_freq:.2f} Hz  (LOW - sensor in water)")
    print(f"  Range: {dry_freq - wet_freq:.2f} Hz")
    print(f"\nThese values are saved to: {CONFIG_FILE}")
    print("\nHow the sensor works:")
    print("  - More moisture = Lower frequency")
    print("  - Less moisture = Higher frequency")
    print("  - This is INVERSE relationship (capacitance-based)")
    print("\nExpected moisture readings:")
    print(f"  Air/Very dry:     ~{dry_freq:.0f}Hz = 0-10%")
    print(f"  Dry soil:         ~{(dry_freq+wet_freq)/2:.0f}Hz = 30-50%")
    print(f"  Moist soil:       ~{(wet_freq + (dry_freq-wet_freq)*0.3):.0f}Hz = 60-80%")
    print(f"  Wet/Saturated:    ~{wet_freq:.0f}Hz = 90-100%")
    print("\nYou can now run the main monitoring program!")
    print("="*60 + "\n")
    
    display.show_message("Ready to", "monitor!", "", "Run main.py")
    time.sleep(3)
    display.oled.fill(0)
    display.oled.show()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCalibration cancelled by user")
    except Exception as e:
        print(f"\n\nError during calibration: {e}")
        import sys
        sys.print_exception(e)
