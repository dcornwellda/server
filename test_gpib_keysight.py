"""
GPIB Connection Test for Keysight/Agilent 82357B Adapter
Tests connection to Keithley 2015 at GPIB address 23
"""

import pyvisa
import sys

def test_gpib_connection():
    """Test GPIB connection using Keysight backend"""

    print("=" * 60)
    print("GPIB Connection Test (Keysight 82357B)")
    print("=" * 60)

    try:
        # Try Keysight backend first
        print("\n[1/5] Trying Keysight VISA backend...")
        try:
            rm = pyvisa.ResourceManager('visa://keysight')
            print("✓ Using Keysight VISA backend")
        except:
            print("  Keysight backend not found, trying default...")
            rm = pyvisa.ResourceManager()
            print("✓ Using default VISA backend")

        # List available backends
        print("\n[2/5] Available VISA implementations:")
        try:
            backends = pyvisa.highlevel.list_backends()
            for backend in backends:
                print(f"    - {backend}")
        except:
            print("    - Default backend")

        # List all resources
        print("\n[3/5] Scanning for instruments...")
        resources = rm.list_resources()
        print(f"✓ Found {len(resources)} instrument(s):")
        for res in resources:
            print(f"    - {res}")

        # Connect to Keithley at address 23
        address = "GPIB0::23::INSTR"
        print(f"\n[4/5] Connecting to {address}...")

        if address not in resources:
            print(f"✗ ERROR: {address} not found")
            print("\nTroubleshooting:")
            print("  - Check GPIB address on Keithley (should be set to 23)")
            print("  - Verify GPIB cable is connected")
            print("  - Open Keysight Connection Expert to verify adapter")
            return False

        instrument = rm.open_resource(address)
        instrument.timeout = 5000
        print(f"✓ Connected to {address}")

        # Query instrument identification
        print("\n[5/5] Reading instrument identification...")
        idn = instrument.query("*IDN?").strip()
        print(f"✓ Instrument ID: {idn}")

        # Test measurement
        print("\n[BONUS] Testing DC voltage measurement...")
        instrument.write("*RST")
        instrument.write("FUNC 'VOLT:DC'")
        instrument.write("VOLT:DC:RANG:AUTO ON")
        voltage = float(instrument.query("READ?"))
        print(f"✓ Measured voltage: {voltage:.6f} V")

        # Close connection
        instrument.close()
        rm.close()

        print("\n" + "=" * 60)
        print("SUCCESS: Keysight 82357B adapter is working!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting Steps:")
        print("  1. Install Keysight IO Libraries Suite")
        print("     https://www.keysight.com/us/en/lib/software-detail/")
        print("     computer-software/io-libraries-suite-downloads-2175637.html")
        print("  2. Open Keysight Connection Expert")
        print("  3. Verify 82357B adapter is detected")
        print("  4. Check GPIB cable connections")
        print("  5. Verify Keithley is powered on")
        print("  6. Set GPIB address to 23 on Keithley")
        return False

if __name__ == "__main__":
    success = test_gpib_connection()
    sys.exit(0 if success else 1)
