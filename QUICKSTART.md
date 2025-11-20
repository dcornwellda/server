# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Check

- [ ] Windows PC with instruments connected
- [ ] NI-VISA installed
- [ ] Python 3.8+ installed
- [ ] QA402 application installed (if using QA402)

## Installation Steps

### 1. Install Dependencies

Open Command Prompt in the `instrument_server` folder:

```cmd
pip install -r requirements.txt
```

### 2. Find Your Keithley Address

```cmd
python
>>> import pyvisa
>>> rm = pyvisa.ResourceManager()
>>> print(rm.list_resources())
```

Note the address (e.g., `GPIB0::15::INSTR`)

### 3. Start the Server

```cmd
python main.py
```

Server starts at: `http://localhost:8000`

### 4. Open Documentation

Open browser: http://localhost:8000/docs

## First Measurement

### Test Keithley Connection

1. In the API docs, find **POST /keithley/connect**
2. Click "Try it out"
3. Enter your address:
   ```json
   {
     "address": "GPIB0::15::INSTR"
   }
   ```
4. Click "Execute"

### Measure DC Voltage

1. Find **POST /keithley/measure/voltage/dc**
2. Click "Try it out"
3. Use default settings (auto-range)
4. Click "Execute"
5. See result:
   ```json
   {
     "measurement_type": "DC Voltage",
     "value": 5.023,
     "unit": "V",
     "range": "auto"
   }
   ```

### Test QA402 (if available)

1. **Start QA402 application first!**
2. Find **POST /qa402/connect**
3. Click "Try it out", then "Execute"
4. If connected, try **POST /qa402/data/thd**

## Access from Remote PC

From your local PC, open:
```
http://<remote-pc-ip>:8000/docs
```

Replace `<remote-pc-ip>` with the IP address of your instrument PC.

## Python Client Example

```python
import requests

# Replace with your server IP
BASE_URL = "http://192.168.1.100:8000"

# Connect to Keithley
requests.post(
    f"{BASE_URL}/keithley/connect",
    json={"address": "GPIB0::15::INSTR"}
)

# Measure voltage
response = requests.post(
    f"{BASE_URL}/keithley/measure/voltage/dc",
    json={"range_value": None}
)
print(response.json())
```

## Common Issues

### "Module not found: pyvisa"
```cmd
pip install pyvisa
```

### "Keithley not found"
- Check VISA address with `list_resources()`
- Verify cable connection
- Install/reinstall NI-VISA

### "QA402 not connected"
- Make sure QA402 application is running
- Check http://localhost:9402 in browser

### "Can't access from other PC"
Allow port 8000 in Windows Firewall:
```cmd
netsh advfirewall firewall add rule name="Instrument Server" dir=in action=allow protocol=TCP localport=8000
```

## Next Steps

- Read full documentation in README.md
- Explore all API endpoints at `/docs`
- Try the example client: `example_client.py`
- Customize for your specific measurements

## Getting Help

1. Check README.md for detailed info
2. Review API docs at `/docs`
3. Test with NI MAX or QA402 application directly

---

**Need more help?** See the full README.md file.
