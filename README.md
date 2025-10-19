# 🌱 Pimoroni Grow Moisture Monitor

**Smart soil moisture monitoring with Raspberry Pi Pico 2W**

A complete MicroPython project for monitoring plant soil moisture using Pimoroni Grow capacitive sensors, with a beautiful Phosphor icon-based OLED display, WiFi time sync, and professional data logging.

![Project Status](https://img.shields.io/badge/status-working-brightgreen)
![Hardware](https://img.shields.io/badge/hardware-Pico_2W-red)
![License](https://img.shields.io/badge/license-MIT-blue)

Created by **Alex** • Bramford, Ipswich, UK • October 2025. #builtwithclaude

---

## 📋 Table of Contents

- [Features](#-features)
- [Hardware Requirements](#-hardware-requirements)
- [Quick Start](#-quick-start-5-minutes)
- [Detailed Setup](#-detailed-setup)
- [Wiring Guide](#-wiring-guide)
- [Calibration](#-calibration)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Technical Details](#-technical-details)
- [Future Enhancements](#-future-enhancements)

---

## ✨ Features

✅ **Professional Phosphor Icons** - Beautiful drop icons (empty/half/full)  
✅ **WiFi Time Sync** - Automatic NTP time synchronization  
✅ **Power Efficient** - Display sleeps between readings, WiFi only on at startup  
✅ **Accurate Calibration** - Button-less 30-second calibration process  
✅ **Inverse Frequency Logic** - Correctly handles capacitive sensor behavior  
✅ **Clean Display** - Moisture %, frequency, and icon status  
✅ **Timestamped Readings** - Know exactly when each reading was taken  
✅ **Easy Configuration** - JSON-based settings  

---

## 🛠️ Hardware Requirements

### Essential Components:
- **Raspberry Pi Pico 2W** (or Pico W)
- **Pimoroni Grow Moisture Sensor** (capacitive PFM type)
- **SSD1306 OLED Display** (128x64, I2C, usually 0x3C address)
- **JST to Dupont cables** (for sensor connection)
- **USB cable** (for power and programming)

### Optional:
- Power bank (for portable operation)
- Breadboard and jumper wires
- Case/enclosure

### Where to Buy:
- **Pico 2W**: [Pimoroni](https://shop.pimoroni.com), [The Pi Hut](https://thepihut.com)
- **Grow Sensor**: [Pimoroni Grow Kit](https://shop.pimoroni.com/products/grow)
- **OLED Display**: Most electronics retailers (check I2C address is 0x3C)

---

## 🚀 Quick Start (5 Minutes)

### 1. Wire It Up

```
OLED Display:
  VCC → Pico Pin 36 (3.3V)
  GND → Pico Pin 38 (GND)
  SDA → Pico Pin 6 (GP4)
  SCL → Pico Pin 7 (GP5)

Moisture Sensor (JST Cable):
  Blue wire   → Pico Pin 38 (GND)
  Black wire  → Pico Pin 31 (GP26)
  Green wire  → Pico Pin 36 (3.3V)
```

**IMPORTANT**: Your JST cable colors (left to right looking at connector):
- **Blue (left)** = GND
- **Black (middle)** = Signal
- **Green (right)** = VCC (3.3V)

### 2. Install MicroPython

1. Download [MicroPython for Pico 2W](https://micropython.org/download/RPI_PICO2/)
2. Hold **BOOTSEL** button on Pico while plugging in USB
3. Copy `.uf2` file to Pico drive
4. Pico will reboot automatically

### 3. Upload Files

Using Thonny IDE or similar:
1. **`main.py`** → Save to Pico
2. **`icon_bitmaps.py`** → Save to Pico  
3. **`ssd1306.py`** → Save to Pico
4. **`wifi_config.json`** → Save to Pico (edit with your WiFi details)

### 4. Create WiFi Config

Create `wifi_config.json` on the Pico:
```json
{
    "ssid": "YOUR_WIFI_NAME",
    "password": "YOUR_WIFI_PASSWORD"
}
```

### 5. Calibrate

Run `calibrate.py` (or import it in REPL):
```python
import calibrate
```

Follow the on-screen instructions:
1. **30 seconds** to hold sensor in air (dry calibration)
2. **30 seconds** to put sensor in water (wet calibration)
3. Done! Values saved automatically

### 6. Run!

Reset the Pico or run:
```python
import main
```

Display will show moisture with Phosphor icon! 🎉

---

## 📖 Detailed Setup

### Step 1: Hardware Assembly

#### Pin Connections:

| Component | Pico Pin | GPIO | Description |
|-----------|----------|------|-------------|
| OLED VCC | 36 | 3.3V | Power (shared) |
| OLED GND | 38 | GND | Ground (shared) |
| OLED SDA | 6 | GP4 | I2C Data |
| OLED SCL | 7 | GP5 | I2C Clock |
| Sensor GND | 38 | GND | Ground |
| Sensor Signal | 31 | GP26 | PFM Output |
| Sensor VCC | 36 | 3.3V | Power |

#### JST Connector Pinout:

Looking at the front of the JST connector (where wires enter):
```
   [1]   [2]   [3]
   Blue  Black Green
   GND   OUT   VDD
```

**Safety Check**:
- Blue (left) = GND → Pin 38 ✓
- Black (middle) = Signal → Pin 31 ✓
- Green (right) = 3.3V → Pin 36 ✓

**⚠️ CRITICAL**: Wrong polarity could damage your Pico! Triple-check before powering on.

### Step 2: Software Installation

#### Install MicroPython:
1. Visit [micropython.org/download](https://micropython.org/download/RPI_PICO2/)
2. Download latest `.uf2` for Pico 2W
3. Hold BOOTSEL, plug USB, release BOOTSEL
4. Drag `.uf2` to RPI-RP2 drive
5. Wait for reboot (drive disappears)

#### Upload Project Files:

Using **Thonny IDE** (recommended):
1. Install Thonny: [thonny.org](https://thonny.org)
2. Tools → Options → Interpreter → MicroPython (Raspberry Pi Pico)
3. File → Open each file, then File → Save As → Raspberry Pi Pico
4. Upload in this order:
   - `ssd1306.py` (display driver)
   - `icon_bitmaps.py` (Phosphor icons)
   - `main.py` (main program)
   - `calibrate.py` (calibration helper)
   - `wifi_config.json` (your WiFi details)

Using **mpremote** (command line):
```bash
mpremote cp ssd1306.py :
mpremote cp icon_bitmaps.py :
mpremote cp main.py :
mpremote cp calibrate.py :
mpremote cp wifi_config.json :
```

### Step 3: WiFi Configuration

Create or edit `wifi_config.json` on the Pico:
```json
{
    "ssid": "YOUR_NETWORK_NAME",
    "password": "YOUR_PASSWORD"
}
```

**Notes**:
- Pico 2W only supports **2.4GHz WiFi** (not 5GHz)
- WiFi connects at startup for NTP time sync only
- WiFi disconnects after sync to save power
- Network must allow NTP traffic (port 123)

### Step 4: Timezone Configuration

Edit `main.py` if you're not in the UK:
```python
TIMEZONE_OFFSET = 0  # UK GMT (winter)
# TIMEZONE_OFFSET = 1  # UK BST (summer)
# TIMEZONE_OFFSET = -5  # US Eastern
# TIMEZONE_OFFSET = 1  # Central European
```

---

## 🔌 Wiring Guide

### Visual Diagram:

```
    ┌─────────────────────┐
    │  Raspberry Pi Pico  │
    │       2W            │
    └─────────────────────┘
           ║     ║
    3.3V(36)   GND(38)
        ║       ║
        ╚═══╦═══╝
            ║
    ┌───────────────┐
    │ SSD1306 OLED  │
    │  VCC  GND     │
    │  SDA  SCL     │
    └───┬───┬───────┘
        │   │
      GP4 GP5
       (6) (7)
       
    ┌─────────────────────┐
    │  Moisture Sensor    │
    │  (via JST cable)    │
    └─────────────────────┘
      Blue Black Green
       │     │     │
      GND   GP26  3.3V
      (38)  (31)  (36)
```

### Connection Steps:

1. **Power off** Pico (unplug USB)
2. Connect **OLED first**:
   - VCC (red) → Pin 36
   - GND (black) → Pin 38
   - SDA (blue/white) → Pin 6
   - SCL (yellow/green) → Pin 7
3. Connect **Sensor via JST**:
   - Plug JST into sensor
   - Blue → Pin 38 (GND)
   - Black → Pin 31 (GP26)
   - Green → Pin 36 (3.3V)
4. **Triple-check** all connections
5. Use the safety checklist below
6. Power on

### Safety Checklist:

Before powering on, verify:
- [ ] Blue wire → GND (Pin 38) ✓
- [ ] Black wire → GP26 (Pin 31) ✓
- [ ] Green wire → 3.3V (Pin 36) ✓
- [ ] JST fully seated in sensor ✓
- [ ] No wire strands touching ✓
- [ ] OLED connections correct ✓
- [ ] Dupont connectors fully on pins ✓

---

## 🎯 Calibration

### Why Calibrate?

Capacitive sensors vary by:
- Soil type (clay, sand, loam)
- Soil mineral content
- Temperature
- Individual sensor characteristics

Calibration ensures accurate 0-100% readings for YOUR setup.

### Understanding Sensor Behavior:

**CRITICAL**: Capacitive sensors have **INVERSE** frequency relationship:
- **DRY (air) = HIGH frequency** (~20-30 Hz)
- **WET (water) = LOW frequency** (~0-5 Hz)

More moisture = Higher capacitance = Lower frequency

### Automatic Calibration:

Run the calibration script:
```python
import calibrate
```

**Process**:
1. Display shows "STEP 1: Remove sensor, Hold in AIR"
2. **30-second countdown** (plenty of time to prepare)
3. Measures DRY frequency (expect 20-30 Hz)
4. Display shows "STEP 2: Put sensor in WATER"
5. **30-second countdown** (move sensor to water/wet soil)
6. Measures WET frequency (expect 0-5 Hz)
7. Validates and saves automatically

**Total time**: ~1 minute

### Calibration Tips:

**For DRY reading**:
- Hold sensor completely in air
- Don't touch the sensing plates
- Keep steady during 3-second measurement
- Expected: 20-30 Hz

**For WET reading**:
- Submerge in glass of water, OR
- Push into very saturated soil
- Ensure sensor past the line marked on it
- Keep steady during 3-second measurement
- Expected: 0-5 Hz

### Validation:

Script automatically checks:
- ✓ Dry freq > Wet freq (correct inverse relationship)
- ✓ Dry freq in reasonable range (>15 Hz)
- ✓ Wet freq in reasonable range (<10 Hz)

If validation fails, script will warn you and suggest trying again.

### Recalibration:

Recalibrate when:
- Changing to different soil type
- Readings seem inaccurate
- After several months of use
- Replacing sensor

Just run `import calibrate` again!

### Manual Calibration (Advanced):

If needed, edit `moisture_config.json` directly:
```json
{
  "dry_freq": 27.33,
  "wet_freq": 0.33
}
```

---

## 📱 Usage

### Normal Operation:

Once calibrated, the system runs automatically:

**On Startup** (~15 seconds):
1. Connects to WiFi
2. Syncs time via NTP
3. Disconnects WiFi (saves power)
4. Loads calibration
5. Starts monitoring

**Every 60 Seconds**:
1. Measures soil moisture (2 seconds)
2. Calculates percentage (0-100%)
3. Displays icon + percentage (10 seconds)
4. Powers off display
5. Sleeps (48 seconds)

### Reading the Display:

```
┌─────────────────────────┐
│     Moisture            │
│ [ICON]   45%            │
│          18.3Hz         │
└─────────────────────────┘
```

**Icon indicates**:
- 🌑 **Empty (slash)**: 0-33% - Needs water!
- 💧 **Half filled**: 34-66% - Moderate  
- 💦 **Full**: 67-100% - Well watered

**Percentage**: Exact moisture level

**Frequency**: Raw sensor reading (for debugging)

### Console Output:

```
==================================================
Pimoroni Grow Moisture Monitor (with Icons)
==================================================
Initializing I2C...
I2C devices found: [60]
Initializing display...

--- WiFi & Time Sync ---
Connecting to WiFi 'YOUR_NETWORK'...
✓ WiFi connected!
IP address: 192.168.1.123
Syncing time from NTP server...
✓ Time synced: 2025-10-19 14:23:45
WiFi disconnected

=== STARTING MONITORING ===
Current time: 2025-10-19 14:23:47
Update interval: 60 seconds

[2025-10-19 14:23:47] Taking reading...
Frequency: 18.50 Hz
Moisture: 32.7%
Displaying: EMPTY drop icon
Sleeping for 60 seconds...
```

### Power Consumption:

| Mode | Current Draw | Notes |
|------|--------------|-------|
| WiFi active | ~100-150mA | First 15 seconds only |
| Display on | ~30-40mA | 10 seconds per minute |
| Display off | ~20mA | 50 seconds per minute |
| Average | ~25mA | Over full cycle |

**Battery life estimate**:
- 2000mAh power bank: ~80 hours (3+ days)
- 10000mAh power bank: ~400 hours (16+ days)

---

## ⚙️ Configuration

### Adjusting Update Interval:

Edit `main.py`:
```python
MEASUREMENT_INTERVAL = 60  # Change to desired seconds
# MEASUREMENT_INTERVAL = 300  # 5 minutes
# MEASUREMENT_INTERVAL = 1800  # 30 minutes
```

### Changing Pin Assignments:

Edit `main.py`:
```python
SENSOR_PIN = 26    # Sensor signal pin
I2C_SDA = 4        # OLED SDA
I2C_SCL = 5        # OLED SCL
```

### Icon Switching Thresholds:

Edit `main.py` in the `MoistureDisplay` class:
```python
def get_icon_for_moisture(self, moisture_percent):
    if moisture_percent < 34:  # ← Adjust threshold
        return self.icon_empty
    elif moisture_percent < 67:  # ← Adjust threshold
        return self.icon_half
    else:
        return self.icon_full
```

Example adjustments:
- More sensitive: `< 25` and `< 60` (changes sooner)
- Less sensitive: `< 40` and `< 75` (changes later)

### Display Settings:

```python
I2C_FREQ = 400000  # I2C clock speed (try 100000 if issues)
FREQUENCY_SAMPLE_TIME = 2  # Seconds to measure (2-5)
DISPLAY_WIDTH = 128  # Don't change
DISPLAY_HEIGHT = 64  # Don't change
```

### WiFi Settings:

Keep WiFi connected (not recommended for battery):
```python
# Comment out this line in main():
# wifi.disconnect()
```

---

## 🐛 Troubleshooting

### Display Not Working:

**Symptoms**: Black screen, no output

**Checks**:
1. Verify wiring: SDA=GP4, SCL=GP5, VCC=3.3V, GND=GND
2. Check I2C address:
   ```python
   import machine
   i2c = machine.I2C(0, sda=machine.Pin(4), scl=machine.Pin(5))
   print(i2c.scan())  # Should show [60] which is 0x3C
   ```
3. If shows different address, edit `ssd1306.py`:
   ```python
   # Change address to your display's address
   self.addr = 0x3C  # or 0x3D
   ```
4. Try lower I2C frequency in `main.py`:
   ```python
   I2C_FREQ = 100000  # Instead of 400000
   ```

### Sensor Reading Issues:

**Always 0% or 100%**:
- Calibration needed or wrong
- Run `import calibrate` again
- Check `moisture_config.json` has sensible values

**Erratic readings**:
- Sensor not properly inserted in soil
- JST connector loose
- Sensor corroded (replace if old)
- Try recalibrating

**No frequency reading** (0.00 Hz):
- Check black wire → GP26
- Verify sensor powered (green wire → 3.3V)
- Test sensor by touching plates (frequency should change)

### WiFi Issues:

**"WiFi connection timeout"**:
- Wrong SSID/password in `wifi_config.json`
- Router out of range
- 5GHz network (Pico only supports 2.4GHz)
- Router has MAC filtering enabled

**"NTP sync failed"**:
- WiFi not connected
- Firewall blocking port 123
- System continues anyway, timestamps will be wrong

### Import Errors:

**"No module named 'icon_bitmaps'"**:
- Forgot to upload `icon_bitmaps.py`
- Upload it to root directory of Pico

**"No module named 'ssd1306'"**:
- Forgot to upload `ssd1306.py`
- Upload display driver

**"No module named 'network'"**:
- Using regular Pico (no WiFi)
- Need Pico W or Pico 2W for WiFi features

### Calibration Issues:

**"ERROR: Dry <= Wet"**:
- You measured backwards! 
- DRY should be HIGH frequency (20-30 Hz)
- WET should be LOW frequency (0-5 Hz)
- Run calibration again carefully

**Very low dry frequency** (<15 Hz):
- Sensor might not be powered properly
- Check green wire to 3.3V
- Sensor might be faulty

**Very high wet frequency** (>10 Hz):
- Sensor not actually wet
- Ensure fully submerged in water
- Check sensor isn't damaged

### Time/Date Wrong:

**Off by 1 hour**:
- Daylight saving time issue
- Adjust `TIMEZONE_OFFSET` in `main.py`:
  ```python
  TIMEZONE_OFFSET = 0  # GMT
  # or
  TIMEZONE_OFFSET = 1  # BST
  ```

**Completely wrong time**:
- NTP sync failed at startup
- Check WiFi works
- Reboot to retry sync

### Still Having Issues?

Run the hardware test:
```python
import test_hardware
```

This will check:
- ✓ I2C bus communication
- ✓ OLED display response
- ✓ Sensor pulse detection
- ✓ All GPIO pins accessible
- ✓ Power supply voltage

---

## 🔧 Technical Details

### How PFM Sensors Work:

**PFM = Pulse Frequency Modulation**

The Pimoroni Grow uses a capacitive sensing technique:
1. Sensor plates form a capacitor
2. Water/moisture changes capacitance
3. Oscillator circuit frequency depends on capacitance
4. More moisture → Higher capacitance → **Lower frequency**
5. Less moisture → Lower capacitance → **Higher frequency**

**Key Insight**: The relationship is **INVERSE**!
- Not like resistive sensors (more moisture = more conductivity)
- Capacitive: more moisture = lower frequency

### Advantages Over Resistive Sensors:

✅ **No corrosion** - No exposed electrodes in soil  
✅ **Long lifetime** - Can last years  
✅ **More accurate** - Less affected by soil minerals  
✅ **Digital output** - Easy to interface (no ADC needed)  
✅ **Low power** - Only draws current during measurement  

### Frequency Ranges:

Typical ranges for most soils:
- **Air**: 25-30 Hz
- **Very dry soil**: 20-25 Hz
- **Dry soil**: 15-20 Hz
- **Moist soil**: 10-15 Hz
- **Wet soil**: 5-10 Hz
- **Saturated/water**: 0-5 Hz

Your specific ranges will vary - hence calibration!

### I2C Communication:

**SSD1306 Display**:
- Standard I2C protocol
- 7-bit address: Usually 0x3C (sometimes 0x3D)
- Clock speed: 100kHz-400kHz
- Built-in frame buffer (1KB for 128x64 display)

### Icons & Display:

**Phosphor Icons**:
- Open source icon library
- Converted to 32x32 pixel bitmaps
- Stored as byte arrays
- Rendered using `framebuf` module

**Display format**:
- Monochrome (1-bit per pixel)
- 128 × 64 pixels
- Vertical byte addressing
- Buffer size: 1024 bytes (128 × 64 / 8)

### File Structure:

```
/
├── main.py               # Main program (auto-runs)
├── calibrate.py          # Calibration helper
├── icon_bitmaps.py       # Phosphor icon data (128 bytes each)
├── ssd1306.py           # OLED driver (from Micropython)
├── wifi_config.json     # Your WiFi credentials
└── moisture_config.json # Auto-generated calibration (42 bytes)
```

### Memory Usage:

- **Main program**: ~15KB
- **Icon bitmaps**: ~0.4KB (3 × 128 bytes)
- **Display driver**: ~8KB
- **Total**: ~25KB of 264KB flash
- **RAM usage**: ~10KB during operation

Plenty of room for expansion!

---

## 🚀 Future Enhancements

Ideas for extending this project:

### Hardware Additions:
- [ ] Add more sensors (Pico can handle 3+ sensors)
- [ ] Temperature/humidity sensor (BME280)
- [ ] Light sensor (for indoor/outdoor detection)
- [ ] Soil temperature (DS18B20)
- [ ] Pump control relay (automatic watering)
- [ ] Battery monitoring (ADC on VSYS)
- [ ] Solar charging circuit

### Software Features:
- [ ] Data logging to SD card
- [ ] Web dashboard (built-in web server)
- [ ] MQTT publishing to Home Assistant
- [ ] Telegram/Discord notifications
- [ ] Historical graphs
- [ ] Multiple plant profiles
- [ ] Watering schedules
- [ ] Weather API integration
- [ ] Battery level display

### Advanced Features:
- [ ] Machine learning (predict watering needs)
- [ ] Soil conductivity measurement
- [ ] pH sensor integration
- [ ] NPK sensor (nitrogen/phosphorus/potassium)
- [ ] Camera for plant growth timelapse
- [ ] Voice alerts (DFPlayer Mini)

Want to implement any of these? Just ask! 🌱

---

## 📁 Project Files

### Essential Files (upload to Pico):
- **`main.py`** - Main program with monitoring loop
- **`icon_bitmaps.py`** - Phosphor drop icons (empty/half/full)
- **`ssd1306.py`** - OLED display driver
- **`wifi_config.json`** - Your WiFi credentials

### Helper Files (optional):
- **`calibrate.py`** - Standalone calibration script
- **`test_hardware.py`** - Hardware testing utility

### Generated Files (auto-created):
- **`moisture_config.json`** - Calibration values

### Documentation:
- **`README.md`** - This file!

---

## 📚 Resources & References

### Official Documentation:
- [MicroPython Docs](https://docs.micropython.org/)
- [Raspberry Pi Pico Datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf)
- [RP2040 Datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)

### Hardware:
- [Pimoroni Grow Tutorial](https://learn.pimoroni.com/tutorial/hel/assembling-grow)
- [SSD1306 Datasheet](https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf)
- [Pico Pinout](https://pico.pinout.xyz/)

### Libraries Used:
- `machine` - Hardware abstraction (built-in)
- `time` - Timing functions (built-in)
- `framebuf` - Frame buffer for icons (built-in)
- `network` - WiFi networking (built-in on Pico W/2W)
- `ntptime` - NTP client (built-in)
- `json` - JSON parsing (built-in)

### Icons:
- [Phosphor Icons](https://phosphoricons.com/) - Open source icon family

---

## 🤝 Contributing

Found a bug? Have an improvement? 

This project is open for contributions:
- Report issues
- Suggest features
- Submit improvements
- Share your builds!

---

## 📝 License

MIT License - Free to use and modify!

If you build something cool with this, please share it with the community! 🌍

---

## 👨‍💻 Author

**Alex**  
📍 Bramford, Ipswich, UK  
📅 October 2025  
🌱 Happy Growing!

---

## 🙏 Acknowledgments

- Pimoroni for the excellent Grow sensors
- MicroPython community for the robust platform
- Phosphor Icons team for beautiful open-source icons
- Everyone who helped test and improve this project

---

## 📊 Project Stats

- **Lines of Code**: ~600 (main.py + supporting files)
- **Development Time**: Built iteratively with improvements
- **Sensors Supported**: 1 (easily expandable to 3+)
- **Power Consumption**: ~25mA average
- **Cost**: ~£15-20 for complete setup

---

**Now go monitor some plants! 🌱💧**

*Questions? Issues? Just ask!*
