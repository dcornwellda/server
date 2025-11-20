"""
Read voltage from both Fluke 8845A and Keithley 2015 via FastAPI server
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def read_fluke_voltage():
    """Read voltage from Fluke 8845A"""
    print("\n" + "=" * 60)
    print("FLUKE 8845A")
    print("=" * 60)

    try:
        # Check status
        response = requests.get(f"{BASE_URL}/fluke/status", timeout=15)
        status = response.json()

        # Connect if needed
        if not status.get("connected", False):
            print("Connecting to Fluke...")
            connect_response = requests.post(
                f"{BASE_URL}/fluke/connect",
                json={"address": "COM5"}
            )
            connect_result = connect_response.json()
            if connect_result.get("status") == "error":
                print(f"ERROR: {connect_result.get('error')}")
                return None
            print(f"Connected: {connect_result.get('identification')}")
        else:
            print(f"Already connected: {status.get('identification')}")

        # Read voltage
        voltage_response = requests.post(f"{BASE_URL}/fluke/measure/voltage/dc", timeout=15)
        voltage_result = voltage_response.json()

        if "error" in voltage_result:
            print(f"ERROR: {voltage_result['error']}")
            return None
        else:
            value = voltage_result['value']
            print(f"\nDC Voltage: {value} V")
            return value

    except Exception as e:
        print(f"ERROR: {e}")
        return None

def read_keithley_voltage():
    """Read voltage from Keithley 2015"""
    print("\n" + "=" * 60)
    print("KEITHLEY 2015")
    print("=" * 60)

    try:
        # Check status
        response = requests.get(f"{BASE_URL}/keithley/status", timeout=15)
        status = response.json()

        # Connect if needed
        if not status.get("connected", False):
            print("Connecting to Keithley...")
            connect_response = requests.post(
                f"{BASE_URL}/keithley/connect",
                json={"address": "GPIB0::15::INSTR"}  # Update GPIB address if needed
            )
            connect_result = connect_response.json()
            if connect_result.get("status") == "error":
                print(f"ERROR: {connect_result.get('error')}")
                return None
            print(f"Connected: {connect_result.get('identification')}")
        else:
            print(f"Already connected: {status.get('identification')}")

        # Read voltage
        voltage_response = requests.post(f"{BASE_URL}/keithley/measure/voltage/dc", timeout=15)
        voltage_result = voltage_response.json()

        if "error" in voltage_result:
            print(f"ERROR: {voltage_result['error']}")
            return None
        else:
            value = voltage_result['value']
            print(f"\nDC Voltage: {value} V")
            return value

    except Exception as e:
        print(f"ERROR: {e}")
        return None

def main():
    print("\n" + "=" * 60)
    print("READING VOLTAGES FROM BOTH INSTRUMENTS")
    print("=" * 60)

    fluke_voltage = read_fluke_voltage()
    keithley_voltage = read_keithley_voltage()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if fluke_voltage is not None:
        print(f"Fluke 8845A:    {fluke_voltage} V")
    else:
        print("Fluke 8845A:    ERROR")

    if keithley_voltage is not None:
        print(f"Keithley 2015:  {keithley_voltage} V")
    else:
        print("Keithley 2015:  ERROR")

    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
