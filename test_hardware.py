"""
Hardware Test Script
Quick test to verify all connections are working
Run this BEFORE running main.py
"""

import machine
import time

print("\n" + "="*50)
print("HARDWARE TEST SCRIPT")
print("="*50 + "\n")

# Test 1: I2C Bus and OLED
print("TEST 1: I2C Bus and OLED Display")
print("-" * 40)
try:
    i2c = machine.I2C(0, sda=machine.Pin(4), scl=machine.Pin(5), freq=400000)
    devices = i2c.scan()
    print(f"✓ I2C initialized successfully")
    print(f"  Devices found: {[hex(d) for d in devices]}")
    
    if 0x3C in devices or 0x3D in devices:
        print("✓ OLED display detected!")
        
        # Try to initialize display
        from ssd1306 import SSD1306_I2C
        oled = SSD1306_I2C(128, 64, i2c)
        oled.text("Test OK!", 0, 0, 1)
        oled.text("OLED Working", 0, 16, 1)
        oled.show()
        print("✓ Display test passed!")
        time.sleep(2)
        oled.fill(0)
        oled.show()
    else:
        print("✗ OLED not found. Expected 0x3C or 0x3D")
        print("  Check wiring: SDA=GP4, SCL=GP5")
        
except Exception as e:
    print(f"✗ I2C Error: {e}")
    print("  Check connections!")

print()

# Test 2: Moisture Sensor
print("TEST 2: Moisture Sensor (PFM)")
print("-" * 40)
try:
    sensor_pin = machine.Pin(26, machine.Pin.IN, machine.Pin.PULL_DOWN)
    print("✓ Sensor pin (GP26) configured")
    
    # Count pulses for 2 seconds
    pulse_count = 0
    
    def count_pulse(pin):
        global pulse_count
        pulse_count += 1
    
    sensor_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=count_pulse)
    print("  Counting pulses for 2 seconds...")
    time.sleep(2)
    sensor_pin.irq(handler=None)
    
    frequency = pulse_count / 2
    print(f"✓ Measured frequency: {frequency:.2f} Hz")
    
    if frequency < 1:
        print("⚠ Very low frequency - check sensor is powered")
        print("  Is sensor connected to 3.3V?")
    elif frequency < 10:
        print("✓ Frequency looks good (dry range)")
    elif frequency < 35:
        print("✓ Frequency looks good (normal range)")
    else:
        print("⚠ Unusually high frequency - check wiring")
        
except Exception as e:
    print(f"✗ Sensor Error: {e}")

print()

# Test 3: Pin Availability
print("TEST 3: GPIO Pin Check")
print("-" * 40)
pins_to_check = {
    4: "I2C SDA",
    5: "I2C SCL", 
    26: "Sensor Signal",
    14: "Cal Button (optional)",
    15: "Confirm Button (optional)"
}

for pin_num, description in pins_to_check.items():
    try:
        pin = machine.Pin(pin_num, machine.Pin.IN)
        print(f"✓ GP{pin_num:2d} ({description:25s}) - Available")
    except Exception as e:
        print(f"✗ GP{pin_num:2d} ({description:25s}) - Error: {e}")

print()

# Test 4: Power
print("TEST 4: Power Supply")
print("-" * 40)
try:
    adc = machine.ADC(29)  # VSYS/3 on Pico
    raw = adc.read_u16()
    voltage = (raw / 65535) * 3.3 * 3  # Approximate VSYS
    print(f"✓ System voltage: ~{voltage:.2f}V")
    
    if voltage > 4.5:
        print("✓ USB powered - good!")
    elif voltage > 3.0:
        print("✓ Battery powered - OK")
    else:
        print("⚠ Low voltage detected")
        
except Exception as e:
    print(f"  Could not read voltage: {e}")

print()

# Summary
print("="*50)
print("HARDWARE TEST COMPLETE")
print("="*50)
print("\nNext steps:")
print("1. If all tests passed ✓ - Run main.py")
print("2. If OLED failed - Check I2C wiring")
print("3. If sensor failed - Check GP26 and power")
print("4. If frequency < 1Hz - Sensor not powered")
print("\nReady to grow! 🌱")
