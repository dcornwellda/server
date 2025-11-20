"""
Find the correct VISA library that matches Python architecture
"""

import sys
import os
import platform
import struct
import pyvisa

def check_python_architecture():
    """Determine if Python is 32-bit or 64-bit"""
    print("=" * 60)
    print("PYTHON ARCHITECTURE")
    print("=" * 60)

    bits = struct.calcsize("P") * 8
    print(f"Python version: {sys.version}")
    print(f"Python architecture: {bits}-bit")
    print(f"Platform: {platform.platform()}")

    return bits

def find_visa_libraries(bits):
    """Find all possible VISA libraries"""
    print("\n" + "=" * 60)
    print("SEARCHING FOR VISA LIBRARIES")
    print("=" * 60)

    # Possible VISA library locations
    if bits == 64:
        possible_paths = [
            # Keysight 64-bit
            r"C:\Windows\System32\agvisa32.dll",  # Despite name, in System32 on 64-bit
            r"C:\Program Files\IVI Foundation\VISA\Win64\agvisa\agbin\agvisa32.dll",
            r"C:\Program Files\IVI Foundation\VISA\Win64\Bin\visa64.dll",
            r"C:\Program Files\Keysight\IO Libraries Suite\bin\visa64.dll",
            # NI 64-bit
            r"C:\Windows\System32\nivisa64.dll",
            r"C:\Program Files\IVI Foundation\VISA\Win64\Bin\nivisa64.dll",
            # Generic 64-bit
            r"C:\Windows\System32\visa64.dll",
            r"C:\Program Files\IVI Foundation\VISA\Win64\Bin\visa64.dll",
        ]
    else:
        possible_paths = [
            # Keysight 32-bit
            r"C:\Windows\SysWOW64\agvisa32.dll",
            r"C:\Program Files (x86)\IVI Foundation\VISA\WinNT\agvisa\agbin\agvisa32.dll",
            r"C:\Program Files (x86)\Keysight\IO Libraries Suite\bin\agvisa32.dll",
            # NI 32-bit
            r"C:\Windows\SysWOW64\nivisa32.dll",
            r"C:\Program Files (x86)\IVI Foundation\VISA\WinNT\Bin\nivisa32.dll",
            # Generic 32-bit
            r"C:\Windows\SysWOW64\visa32.dll",
            r"C:\Program Files (x86)\IVI Foundation\VISA\WinNT\Bin\visa32.dll",
        ]

    found_libs = []
    print(f"\nLooking for {bits}-bit VISA libraries...\n")

    for path in possible_paths:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✓ Found: {path}")
            print(f"  Size: {size:,} bytes")
            found_libs.append(path)
        else:
            print(f"✗ Not found: {path}")

    return found_libs

def test_visa_library(lib_path):
    """Test if a VISA library works with PyVISA"""
    print(f"\n{'=' * 60}")
    print(f"TESTING: {lib_path}")
    print('=' * 60)

    try:
        print("  Creating ResourceManager...")
        rm = pyvisa.ResourceManager(lib_path)
        print(f"  ✓ Loaded: {rm.visalib}")

        print("  Scanning for resources...")
        resources = rm.list_resources()

        if resources:
            print(f"  ✓ Found {len(resources)} instrument(s):")
            for res in resources:
                print(f"      {res}")

            # Try to connect to GPIB0::23::INSTR
            if "GPIB0::23::INSTR" in resources:
                print(f"\n  Testing GPIB0::23::INSTR...")
                inst = rm.open_resource("GPIB0::23::INSTR")
                inst.timeout = 5000

                idn = inst.query("*IDN?").strip()
                print(f"  ✓ Connected: {idn}")

                inst.close()
                rm.close()
                return True, lib_path
        else:
            print("  ✗ No instruments found")

        rm.close()
        return False, lib_path

    except AttributeError as e:
        if "not found" in str(e):
            print(f"  ✗ Library architecture mismatch or incomplete VISA")
            print(f"     {str(e)[:80]}")
        else:
            print(f"  ✗ Error: {e}")
        return False, None

    except Exception as e:
        print(f"  ✗ Error: {str(e)[:100]}")
        return False, None

def try_ivi_shared_components():
    """Try using the @ivi backend"""
    print(f"\n{'=' * 60}")
    print("TESTING: @ivi (IVI Shared Components)")
    print('=' * 60)

    try:
        rm = pyvisa.ResourceManager('@ivi')
        print(f"  ✓ Loaded IVI backend")
        print(f"  Backend: {rm.visalib}")

        resources = rm.list_resources()

        if resources:
            print(f"  ✓ Found {len(resources)} instrument(s):")
            for res in resources:
                print(f"      {res}")

            if "GPIB0::23::INSTR" in resources:
                print(f"\n  Testing GPIB0::23::INSTR...")
                inst = rm.open_resource("GPIB0::23::INSTR")
                inst.timeout = 5000

                idn = inst.query("*IDN?").strip()
                print(f"  ✓ Connected: {idn}")

                inst.close()
                rm.close()
                return True, '@ivi'
        else:
            print("  ✗ No instruments found")

        rm.close()
        return False, '@ivi'

    except Exception as e:
        print(f"  ✗ Error: {str(e)[:100]}")
        return False, None

def main():
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + "     VISA LIBRARY ARCHITECTURE MATCHER     " + " " * 11 + "║")
    print("╚" + "═" * 58 + "╝")

    # Check Python architecture
    bits = check_python_architecture()

    # Find matching VISA libraries
    found_libs = find_visa_libraries(bits)

    if not found_libs:
        print("\n" + "!" * 60)
        print("ERROR: No matching VISA libraries found!")
        print("!" * 60)
        print("\nYou need to install Keysight IO Libraries Suite.")
        print("Make sure to install the version that matches your Python:")
        print(f"  - Your Python: {bits}-bit")
        print(f"  - Download from: https://www.keysight.com/")
        return False

    # Try @ivi first (this is the recommended approach)
    print("\n" + "=" * 60)
    print("ATTEMPTING CONNECTION WITH DIFFERENT VISA LIBRARIES")
    print("=" * 60)

    success, working_lib = try_ivi_shared_components()
    if success:
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"\nWorking VISA backend: {working_lib}")
        print("\nTo fix your code, use this in keithley2015.py:")
        print("\n" + "-" * 60)
        print("def connect(self):")
        print("    self.rm = pyvisa.ResourceManager('@ivi')")
        print("    self.instrument = self.rm.open_resource(self.resource_address)")
        print("-" * 60)
        return True

    # Try each library
    for lib_path in found_libs:
        success, working_lib = test_visa_library(lib_path)
        if success:
            print("\n" + "=" * 60)
            print("SUCCESS!")
            print("=" * 60)
            print(f"\nWorking VISA library: {working_lib}")
            print("\nTo fix your code, use this in keithley2015.py:")
            print("\n" + "-" * 60)
            print("def connect(self):")
            print(f"    self.rm = pyvisa.ResourceManager(r'{working_lib}')")
            print("    self.instrument = self.rm.open_resource(self.resource_address)")
            print("-" * 60)
            return True

    # Nothing worked
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING NEEDED")
    print("=" * 60)
    print("\nNo VISA library could connect to the instrument.")
    print("\nPossible issues:")
    print(f"  1. Python is {bits}-bit but Keysight IO Libraries is wrong version")
    print("  2. IVI Shared Components not installed")
    print("  3. Keysight VISA service not running")
    print("\nTry:")
    print("  1. Reinstall Keysight IO Libraries Suite")
    print(f"     Make sure to install {bits}-bit version")
    print("  2. Restart Keysight VISA service (services.msc)")
    print("  3. Reboot computer")

    return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
