"""
Quick test script to read voltage from Fluke 8845A via FastAPI server
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("=" * 60)
    print("Reading Fluke 8845A Voltage")
    print("=" * 60)

    # Check status
    print("\n1. Checking Fluke connection status...")
    try:
        response = requests.get(f"{BASE_URL}/fluke/status")
        status = response.json()
        print(f"   Status: {json.dumps(status, indent=2)}")

        # If not connected, connect
        if not status.get("connected", False):
            print("\n2. Fluke not connected. Connecting...")
            connect_response = requests.post(
                f"{BASE_URL}/fluke/connect",
                json={"address": "COM5"}  # Change COM port if needed
            )
            connect_result = connect_response.json()
            print(f"   Connection result: {json.dumps(connect_result, indent=2)}")

            if connect_result.get("status") == "error":
                print(f"\n   ERROR: Failed to connect - {connect_result.get('error')}")
                print("   Check that:")
                print("   - Fluke 8845A is connected to COM5 (or update address)")
                print("   - NI-VISA is installed")
                print("   - Instrument is powered on")
                return
        else:
            print("   Fluke is already connected!")

        # Read DC voltage
        print("\n3. Reading DC voltage...")
        voltage_response = requests.post(f"{BASE_URL}/fluke/measure/voltage/dc")
        voltage_result = voltage_response.json()

        if "error" in voltage_result:
            print(f"   ERROR: {voltage_result['error']}")
        else:
            print(f"\n   Measurement successful!")
            print(f"   Type: {voltage_result['measurement_type']}")
            print(f"   Value: {voltage_result['value']} {voltage_result['unit']}")
            print(f"   Range: {voltage_result['range']}")

    except requests.exceptions.ConnectionError:
        print("\n   ERROR: Cannot connect to server at http://localhost:8000")
        print("   Make sure the FastAPI server is running:")
        print("   python main.py")
    except Exception as e:
        print(f"\n   ERROR: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
