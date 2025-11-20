# Keithley 2015 Serial Control

Python library for controlling the Keithley 2015 Multimeter via RS-232 serial port.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Your Instrument

On the Keithley 2015, configure the RS-232 settings:

1. Press **MENU** button
2. Navigate to **INTERFACE**
3. Select **RS232**
4. Configure settings:
   - **Baud Rate**: 9600 (or match your preference)
   - **Data Bits**: 8
   - **Parity**: None
   - **Stop Bits**: 1
   - **Flow Control**: None
   - **Terminator**: LF (Line Feed)

### 3. Find Your Serial Port

**Windows:**
- Open Device Manager
- Expand "Ports (COM & LPT)"
- Note the COM port number (e.g., COM3, COM4)

**Linux:**
- Typically `/dev/ttyUSB0` or `/dev/ttyS0`
- Run `ls /dev/tty*` to list available ports

### 4. Update Configuration

Edit `example_usage.py` and set your port:

```python
PORT = 'COM3'        # Change to your port
BAUDRATE = 9600      # Match your instrument settings
```

### 5. Run Example

```bash
python example_usage.py
```

## Usage Examples

### Basic Measurement

```python
from keithley_2015 import Keithley2015

# Connect to meter
dmm = Keithley2015('COM3', baudrate=9600)

# Get instrument ID
print(dmm.get_id())

# Measure DC voltage
dmm.configure_dc_voltage(range_val='AUTO')
voltage = dmm.read()
print(f"Voltage: {voltage} V")

# Close connection
dmm.close()
```

### Using Context Manager

```python
from keithley_2015 import Keithley2015

with Keithley2015('COM3', baudrate=9600) as dmm:
    dmm.configure_dc_voltage()
    voltage = dmm.read()
    print(f"Voltage: {voltage} V")
```

### Different Measurement Types

```python
# DC Voltage (auto-range)
dmm.configure_dc_voltage(range_val='AUTO')
voltage = dmm.read()

# AC Voltage (fixed 10V range)
dmm.configure_ac_voltage(range_val=10)
ac_voltage = dmm.read()

# DC Current
dmm.configure_dc_current(range_val='AUTO')
current = dmm.read()

# 2-wire Resistance
dmm.configure_resistance(range_val='AUTO')
resistance = dmm.read()

# 4-wire Resistance
dmm.configure_fresistance(range_val='AUTO')
resistance = dmm.read()

# Frequency
dmm.configure_frequency()
frequency = dmm.read()
```

### Continuous Monitoring

```python
import time

with Keithley2015('COM3') as dmm:
    dmm.configure_dc_voltage()

    for i in range(10):
        voltage = dmm.read()
        timestamp = time.strftime("%H:%M:%S")
        print(f"{timestamp} - Voltage: {voltage:.6f} V")
        time.sleep(1)
```

## Available Methods

### Connection
- `__init__(port, baudrate, timeout)` - Initialize connection
- `close()` - Close connection

### Basic Commands
- `write(command)` - Send SCPI command
- `query(command)` - Send command and get response
- `reset()` - Reset to defaults
- `clear()` - Clear status
- `get_id()` - Get instrument ID

### Configuration
- `configure_dc_voltage(range_val, resolution)`
- `configure_ac_voltage(range_val, resolution)`
- `configure_dc_current(range_val, resolution)`
- `configure_ac_current(range_val, resolution)`
- `configure_resistance(range_val, resolution)` - 2-wire
- `configure_fresistance(range_val, resolution)` - 4-wire
- `configure_frequency()`
- `configure_period()`

### Measurements
- `read()` - Trigger and read measurement
- `fetch()` - Fetch last measurement
- `initiate()` - Start measurement

### Display
- `display_on()` - Turn display on
- `display_off()` - Turn off (faster measurements)
- `display_text(text)` - Show custom text
- `display_clear()` - Clear custom text

### Trigger
- `set_trigger_source(source)` - Set trigger source
- `trigger()` - Send software trigger

### Utility
- `beep()` - Make instrument beep
- `get_error()` - Get error from queue
- `check_errors()` - Check all errors
- `local()` - Return to local control
- `remote()` - Set remote control

## Troubleshooting

### "Could not open port"
- Check port name is correct
- Close other programs using the port
- Check cable connection
- Try unplugging and reconnecting

### "Timeout" or No Response
- Verify baud rate matches instrument
- Check instrument is in remote mode
- Verify terminator settings (should be LF)
- Try increasing timeout parameter

### Incorrect Readings
- Allow settling time between measurements
- Check proper measurement function selected
- Verify input connections
- Check for grounding issues

## SCPI Command Reference

You can also send raw SCPI commands:

```python
dmm.write('*RST')              # Reset
dmm.write('CONF:VOLT:DC 10')   # Configure DC voltage, 10V range
response = dmm.query('READ?')  # Read measurement
```

Common SCPI commands for Keithley 2015:
- `*IDN?` - Identification
- `*RST` - Reset
- `*CLS` - Clear status
- `READ?` - Trigger and read
- `CONF:VOLT:DC` - Configure DC voltage
- `CONF:CURR:DC` - Configure DC current
- `CONF:RES` - Configure resistance
- `SYST:ERR?` - Query error

## License

This code is provided as-is for controlling Keithley instruments.
