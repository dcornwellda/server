"""
Test GPIB connection using Keysight VISA backend explicitly
"""

import pyvisa
import sys
import os

def find_keysight_visa():
    """Find Keysight VISA DLL path"""
    print("=" * 60)
    print("FINDING KEYSIGHT VISA LIBRARY")
    print("=" * 60)

    # Common Keysight VISA DLL locations
    possible_paths = [
        r"C:\Windows\System32\agvisa32.dll",
        r"C:\Windows\SysWOW64\agvisa32.dll",
        r"C:\Program Files\IVI Foundation\VISA\WinNT\agvisa\agbin\agvisa32.dll",
        r"C:\Program Files (x86)\IVI Foundation\VISA\WinNT\agvisa\agbin\agvisa32.dll",
        r"C:\Program Files\Keysight\IO Libraries Suite\bin\agvisa32.dll",
        r"C:\Program Files (x86)\Keysight\IO Libraries Suite\bin\agvisa32.dll",
    ]

    found_paths = []
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✓ Found: {path}")
            found_paths.append(path)

    if not found_paths:
        print("✗ Keysight VISA DLL not found in standard locations")
        return None

    return found_paths[0]

def test_with_keysight_visa(visa_path=None):
    """Test connection using Keysight VISA explicitly"""
    print("\n" + "=" * 60)
    print("TESTING WITH KEYSIGHT VISA")
    print("=" * 60)

    try:
        # Try to use Keysight VISA explicitly
        if visa_path:
            print(f"\nUsing VISA library: {visa_path}")
            rm = pyvisa.ResourceManager(visa_path)
        else:
            print("\nTrying default backend...")
            rm = pyvisa.ResourceManager()

        print(f"Backend: {rm.visalib}")

        # List resources
        print("\nScanning for instruments...")
        resources = rm.list_resources()

        print(f"✓ Found {len(resources)} instrument(s):")
        for res in resources:
            print(f"    - {res}")

        if not resources:
            print("\n✗ No instruments found with this backend")
            return False

        # Try to connect to GPIB0::23::INSTR
        address = "GPIB0::23::INSTR"
        if address in resources:
            print(f"\n✓ {address} found! Connecting...")
            inst = rm.open_resource(address)
            inst.timeout = 5000

            # Get ID
            idn = inst.query("*IDN?").strip()
            print(f"✓ Instrument ID: {idn}")

            # Test measurement
            print("\nTesting DC voltage measurement...")
            inst.write("*RST")
            inst.write("FUNC 'VOLT:DC'")
            inst.write("VOLT:DC:RANG:AUTO ON")
            voltage = float(inst.query("READ?"))
            print(f"✓ Measured voltage: {voltage:.6f} V")

            inst.close()
            rm.close()

            print("\n" + "=" * 60)
            print("SUCCESS!")
            print("=" * 60)
            return True
        else:
            print(f"\n✗ {address} not in resource list")
            return False

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_code_with_solution(visa_path):
    """Show how to update the code"""
    print("\n" + "=" * 60)
    print("HOW TO FIX YOUR CODE")
    print("=" * 60)

    print("\nYou need to specify the Keysight VISA library explicitly.")
    print("\nIn your keithley2015.py, update the __init__ method:")
    print("\n" + "-" * 60)
    print("OLD CODE:")
    print("-" * 60)
    print("""
def connect(self):
    self.rm = pyvisa.ResourceManager()
    self.instrument = self.rm.open_resource(self.resource_address)
""")

    print("\n" + "-" * 60)
    print("NEW CODE:")
    print("-" * 60)
    print(f"""
def connect(self):
    # Use Keysight VISA explicitly
    self.rm = pyvisa.ResourceManager(r'{visa_path}')
    self.instrument = self.rm.open_resource(self.resource_address)
""")
    print("-" * 60)

def main():
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + "     KEYSIGHT VISA BACKEND TEST     " + " " * 18 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    # Find Keysight VISA
    visa_path = find_keysight_visa()

    if not visa_path:
        print("\nCannot find Keysight VISA DLL.")
        print("Make sure Keysight IO Libraries Suite is installed.")
        return False

    # Test with Keysight VISA
    success = test_with_keysight_visa(visa_path)

    if success:
        update_code_with_solution(visa_path)
        return True
    else:
        print("\n" + "=" * 60)
        print("TROUBLESHOOTING")
        print("=" * 60)
        print("\nEven with Keysight VISA, the instrument was not found.")
        print("\nTry these steps:")
        print("  1. Close Connection Expert")
        print("  2. Disconnect and reconnect the GPIB cable")
        print("  3. Power cycle the Keithley 2015")
        print("  4. Restart the Keysight VISA service:")
        print("     - Open Services (services.msc)")
        print("     - Find 'Keysight VISA Service'")
        print("     - Restart it")
        print("  5. Run this script again")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
