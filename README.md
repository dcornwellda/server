# Remote Instrument Control Server

A FastAPI-based REST API server for controlling and monitoring test instruments remotely:
- **Keithley 2015 THD Multimeter** (via GPIB)
- **QA402 Audio Analyzer** (via REST API proxy)

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Usage](#api-usage)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)

## ✨ Features

### Keithley 2015 Multimeter
- DC/AC Voltage measurements
- DC/AC Current measurements
- 2-wire and 4-wire resistance measurements
- Auto-ranging and manual range selection
- Full SCPI command support

### QA402 Audio Analyzer
- Frequency response analysis
- Time domain waveforms
- THD (Total Harmonic Distortion) measurement
- RMS voltage measurement
- Peak frequency detection
- Output signal generator control
- Configurable sample rates and buffer sizes

## 🔧 Prerequisites

### Hardware
- **Windows PC** (remote instrument PC)
- **Keithley 2015** connected via:
  - NI GPIB-USB-HS adapter, or
  - USB, or
  - Serial port
- **QA402 Audio Analyzer** with USB connection

### Software on Remote PC
1. **NI-VISA** (for GPIB/USB/Serial communication)
   - Download from: https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html
   - Install the runtime (free)

2. **Python 3.8 or newer**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

3. **QA402 Application**
   - Must be installed and running
   - Default API endpoint: http://localhost:9402

## 📥 Installation

### Step 1: Copy Files
Copy the entire `instrument_server` folder to your remote PC.

Recommended location: `H:\instrument_server\`

### Step 2: Install Python Dependencies
Open Command Prompt and navigate to the server directory:

```cmd
cd H:\instrument_server
pip install -r requirements.txt
```

This installs:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `pyvisa` - Instrument communication
- `requests` - HTTP client for QA402

### Step 3: Find Your Instrument Address
Before running the server, identify your Keithley's VISA address:

```cmd
python
>>> import pyvisa
>>> rm = pyvisa.ResourceManager()
>>> print(rm.list_resources())
```

You should see something like:
```
('GPIB0::15::INSTR', 'USB0::0x05E6::0x2015::...')
```

Note the address for your Keithley 2015 (e.g., `GPIB0::15::INSTR`)

## 🚀 Quick Start

### Starting the Server

1. **Start QA402 Application** (if using QA402)
2. **Open Command Prompt** in the server directory:

```cmd
cd H:\instrument_server
python main.py
```

You should see:
```
============================================================
Remote Instrument Control Server
============================================================

Starting server...
Server will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

Instruments:
  - Keithley 2015 Multimeter
  - QA402 Audio Analyzer

Press CTRL+C to stop the server
============================================================
```

### Accessing from Local PC

Open a web browser and navigate to:
```
http://<remote-pc-ip>:8000/docs
```

Replace `<remote-pc-ip>` with your remote PC's IP address.

## 📖 API Usage

### Interactive Documentation

The server provides interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Basic Workflow

#### Keithley 2015

1. **Connect to instrument**:
   ```
   POST /keithley/connect
   Body: {"address": "GPIB0::15::INSTR"}
   ```

2. **Check status**:
   ```
   GET /keithley/status
   ```

3. **Measure DC voltage**:
   ```
   POST /keithley/measure/voltage/dc
   Body: {"range_value": null}  # null = auto-range
   ```

4. **Measure resistance (4-wire)**:
   ```
   POST /keithley/measure/resistance/4wire
   Body: {"range_value": 1000}  # 1kΩ range
   ```

#### QA402 Audio Analyzer

1. **Connect to QA402**:
   ```
   POST /qa402/connect
   Body: {"base_url": "http://localhost:9402"}
   ```

2. **Configure acquisition**:
   ```
   POST /qa402/configure/acquisition
   Body: {
     "sample_rate": 48000,
     "buffer_size": 8192,
     "input_range": 18
   }
   ```

3. **Configure generator**:
   ```
   POST /qa402/configure/generator
   Body: {
     "frequency_hz": 1000,
     "level_dbv": -10,
     "enabled": true
   }
   ```

4. **Run acquisition**:
   ```
   POST /qa402/acquisition/run
   ```

5. **Get THD measurement**:
   ```
   POST /qa402/data/thd
   Body: {"channel": "left"}
   ```

### Python Client Example

```python
import requests

BASE_URL = "http://192.168.1.100:8000"  # Replace with your remote PC IP

# Connect to Keithley
response = requests.post(
    f"{BASE_URL}/keithley/connect",
    json={"address": "GPIB0::15::INSTR"}
)
print(response.json())

# Measure DC voltage
response = requests.post(
    f"{BASE_URL}/keithley/measure/voltage/dc",
    json={"range_value": None}
)
result = response.json()
print(f"Voltage: {result['value']} {result['unit']}")

# QA402: Get THD
response = requests.post(
    f"{BASE_URL}/qa402/data/thd",
    json={"channel": "left"}
)
result = response.json()
print(f"THD: {result['thd_db']} dB")
```

## 🔍 Troubleshooting

### Keithley Connection Issues

**Problem**: "Not connected to instrument"
- Check that NI-VISA is installed
- Verify GPIB address using `list_resources()`
- Check cable connections
- Try running NI MAX (Measurement & Automation Explorer) to test connection

**Problem**: "VISA not found"
```cmd
pip install pyvisa-py
```

### QA402 Connection Issues

**Problem**: "QA402 not connected"
- Ensure QA402 application is running
- Check that API is enabled in QA402 settings
- Verify http://localhost:9402 is accessible

**Problem**: "Connection refused"
- Restart QA402 application
- Check firewall settings

### Network Access Issues

**Problem**: Can't access from local PC
- Check Windows Firewall on remote PC
- Allow port 8000 in firewall:
  ```cmd
  netsh advfirewall firewall add rule name="Instrument Server" dir=in action=allow protocol=TCP localport=8000
  ```
- Verify both PCs are on the same network

## 🏗️ Architecture

```
instrument_server/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── api/                    # API route definitions
│   ├── keithley_routes.py # Keithley 2015 endpoints
│   └── qa402_routes.py    # QA402 endpoints
├── services/               # Business logic layer
│   ├── keithley_service.py
│   └── qa402_service.py
├── devices/                # Device drivers
│   ├── keithley2015.py    # Keithley VISA driver
│   └── qa402.py           # QA402 REST API client
└── docs/                   # Documentation
```

### Design Principles

- **Layered Architecture**: Separation of API, business logic, and device drivers
- **RESTful API**: Standard HTTP methods and JSON responses
- **Error Handling**: Comprehensive error messages and status codes
- **Auto-Documentation**: Interactive Swagger UI documentation
- **CORS Enabled**: Accessible from any client application

## 📝 Additional Notes

### Security Considerations

This server is designed for use on a trusted local network. For production use:
- Configure CORS to allow only specific origins
- Add authentication (API keys, JWT tokens)
- Use HTTPS with SSL certificates
- Implement rate limiting

### Performance

- GPIB communication: ~10-50 measurements/second
- QA402 API: Limited by acquisition time
- Network latency: Typically < 50ms on LAN

### Customization

To add new measurement functions:
1. Add method to device driver (`devices/`)
2. Add business logic to service (`services/`)
3. Add API endpoint to routes (`api/`)

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check VISA and QA402 documentation

---

**Version**: 1.0.0  
**Last Updated**: November 2024
