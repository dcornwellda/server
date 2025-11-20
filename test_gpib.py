"""
Quick GPIB Connection Test Script
Tests connection to Keithley 2015 at GPIB address 23
"""

import pyvisa
import sys

def test_gpib_connection():
    """Test GPIB connection to Keithley 2015"""

    print("=" * 60)
    print("GPIB Connection Test")
    print("=" * 60)

    try:
        # Step 1: Create resource manager
        print("\n[1/4] Creating VISA Resource Manager...")
        rm = pyvisa.ResourceManager()
        print("✓ Resource Manager created")

        # Step 2: List all resources
        print("\n[2/4] Scanning for instruments...")
        resources = rm.list_resources()
        print(f"✓ Found {len(resources)} instrument(s):")
        for res in resources:
            print(f"    - {res}")

        # Step 3: Connect to Keithley at address 23
        address = "GPIB0::23::INSTR"
        print(f"\n[3/4] Connecting to {address}...")

        if address not in resources:
            print(f"✗ ERROR: {address} not found in available resources")
            print("\nAvailable resources:")
            for res in resources:
                print(f"    - {res}")
            return False

        instrument = rm.open_resource(address)
        instrument.timeout = 5000  # 5 second timeout
        print(f"✓ Connected to {address}")

        # Step 4: Query instrument identification
        print("\n[4/4] Reading instrument identification...")
        idn = instrument.query("*IDN?").strip()
        print(f"✓ Instrument ID: {idn}")

        # Optional: Test a simple measurement
        print("\n[BONUS] Testing DC voltage measurement...")
        instrument.write("FUNC 'VOLT:DC'")
        instrument.write("VOLT:DC:RANG:AUTO ON")
        voltage = float(instrument.query("READ?"))
        print(f"✓ Measured voltage: {voltage:.6f} V")

        # Close connection
        instrument.close()
        rm.close()

        print("\n" + "=" * 60)
        print("SUCCESS: GPIB connection is working!")
        print("=" * 60)
        return True

    except pyvisa.errors.VisaIOError as e:
        print(f"\n✗ VISA Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check that NI-VISA is installed")
        print("  2. Verify GPIB cable connections")
        print("  3. Check that Keithley is powered on")
        print("  4. Verify GPIB address is set to 23 on the instrument")
        return False

    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = test_gpib_connection()
    sys.exit(0 if success else 1)
