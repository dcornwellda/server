# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based REST API server for remote control of laboratory test instruments:
- **Keithley 2015 THD Multimeter** - GPIB/USB/Serial communication via PyVISA
- **QA402 Audio Analyzer** - REST API proxy to localhost application

The server enables remote measurement and control over a local network, with interactive Swagger documentation at `/docs`.

## Development Commands

### Running the Server

```bash
# Start the server (listens on all interfaces at port 8000)
python main.py

# Server will be available at:
# - Local: http://localhost:8000
# - Network: http://<ip-address>:8000
# - API Docs: http://localhost:8000/docs
```

### Installing Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Or use the provided setup script (Windows)
setup.bat
```

### Testing Instruments

```bash
# Find available VISA instruments (Keithley)
python
>>> import pyvisa
>>> rm = pyvisa.ResourceManager()
>>> print(rm.list_resources())

# Verify QA402 API is accessible
# Open browser to: http://localhost:9402
```

## Architecture

This codebase follows a **three-tier layered architecture**:

### 1. Device Layer (`*.py` in root)
- **keithley2015.py** - Low-level VISA/SCPI driver for Keithley 2015
  - Handles GPIB communication via PyVISA
  - Direct SCPI command interface
  - Connection management and timeout handling
- **qa402.py** - HTTP client wrapper for QA402 REST API
  - Proxies requests to QA402 application (localhost:9402)
  - The QA402 desktop app must be running for this to work

### 2. Service Layer (`*_service.py` in root)
- **keithley_service.py** - Business logic for Keithley operations
  - Singleton instance: `keithley_service`
  - Connection state management
  - Measurement orchestration and error handling
- **qa402_service.py** - Business logic for QA402 operations
  - Singleton instance: `qa402_service`
  - Configuration management
  - Data aggregation methods

### 3. API Layer (`*_routes.py` in root)
- **keithley_routes.py** - REST endpoints for Keithley (`/keithley/*`)
  - Pydantic models for request/response validation
  - FastAPI router with prefix `/keithley`
- **qa402_routes.py** - REST endpoints for QA402 (`/qa402/*`)
  - Pydantic models for request/response validation
  - FastAPI router with prefix `/qa402`

### Application Entry Point
- **main.py** - FastAPI app initialization
  - CORS enabled (allow all origins - production needs restriction)
  - Router registration
  - Uvicorn server configuration (host=0.0.0.0, port=8000)

## Important Implementation Details

### Connection Management
- **Both services use singleton patterns** - one global instance per service
- **State is maintained in memory** - no persistent storage
- **Connections must be explicitly established** via `/connect` endpoints before measurements
- **Keithley** - Connection persists until `/disconnect` or server restart
- **QA402** - HTTP client created on connect, communicates with localhost:9402

### Measurement Workflow

**Keithley 2015:**
1. POST `/keithley/connect` with VISA address (e.g., "GPIB0::15::INSTR")
2. GET `/keithley/status` to verify connection
3. POST `/keithley/measure/voltage/dc` (or other measurement endpoints)
   - Optional `range_value` parameter (null = auto-range)
4. POST `/keithley/disconnect` when done

**QA402:**
1. Ensure QA402 desktop application is running
2. POST `/qa402/connect` with base_url (default: http://localhost:9402)
3. POST `/qa402/configure/acquisition` - Set sample rate, buffer size, input range
4. POST `/qa402/configure/generator` - Set frequency, level, enable/disable
5. POST `/qa402/acquisition/run` - Trigger measurement
6. POST `/qa402/data/thd` or other data endpoints to retrieve results

### Error Handling
- Service layer catches exceptions and returns error dictionaries
- Routes check for `"error"` key and raise HTTPException with 500 status
- Connection errors use 503 status for QA402
- Validation errors handled by Pydantic (automatic 422 responses)

### File Organization
The repository has a **flat structure** - all Python modules are in the root directory:
- No separate `api/`, `services/`, `devices/` folders despite documentation suggesting this
- Import paths reflect flat structure (e.g., `from services.keithley_service import ...` won't work)
- Actual imports: `from keithley_service import keithley_service`

## Key Constraints and Requirements

### Hardware Dependencies
- **NI-VISA** must be installed on the system for Keithley communication
- **Keithley 2015** must be physically connected via GPIB/USB/Serial
- **QA402 desktop application** must be running for QA402 endpoints to work

### Network Configuration
- Server listens on `0.0.0.0:8000` (all interfaces)
- **Windows Firewall** may block port 8000 - use provided firewall rule in docs
- CORS allows all origins (`allow_origins=["*"]`) - restrict for production

### Valid Parameter Ranges

**Keithley Voltage Ranges:**
- DC: 0.2, 2, 20, 200, 1000V
- AC: 0.2, 2, 20, 200, 750V

**Keithley Current Ranges:**
- DC/AC: 0.02, 0.2, 2A

**Keithley Resistance Ranges:**
- 200, 2000, 20000, 200000, 2000000, 20000000Ω

**QA402 Sample Rates:**
- 48000 or 192000 Hz only

**QA402 Input Ranges:**
- 0, 6, 12, 18, 24, 30, 36, 42 dBV

**QA402 Output Level:**
- -100 to 18 dBV

## Development Guidelines

### Adding New Measurement Functions
1. Add method to device driver (e.g., `keithley2015.py`)
2. Add wrapper method to service (e.g., `keithley_service.py`)
3. Create Pydantic request model if needed (in routes file)
4. Add API endpoint to routes (e.g., `keithley_routes.py`)
5. FastAPI auto-generates documentation at `/docs`

### Modifying Existing Endpoints
- Request/response models use Pydantic - changes automatically update docs
- Service methods return dictionaries (not Pydantic models)
- Routes convert service responses to JSON automatically

### Testing Endpoints
- Use interactive docs at `http://localhost:8000/docs`
- "Try it out" feature executes requests directly
- Python client example available in `example_client.py`

## Common Pitfalls

1. **QA402 connection fails** - Desktop application must be running first
2. **Keithley connection fails** - Check VISA address with `list_resources()`
3. **Import errors** - Remember flat structure, no nested folders
4. **Measurement before connect** - Will raise `ConnectionError` from service layer
5. **Invalid ranges** - Pydantic won't validate, but device will fail - add validation if needed
6. **Timeout errors** - QA402 acquisitions can take time, max_wait=10s in `run_single_acquisition()`

## External References

- QA402 API Documentation: https://github.com/QuantAsylum/QA40x/wiki/QA40x-API
- PyVISA Documentation: https://pyvisa.readthedocs.io/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- NI-VISA Download: https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html
