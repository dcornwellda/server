"""
Comprehensive GPIB Diagnostic Tool
Helps identify why instruments are not being detected
"""

import sys

def check_pyvisa():
    """Check PyVISA installation and backends"""
    print("\n" + "=" * 60)
    print("STEP 1: Checking PyVISA Installation")
    print("=" * 60)

    try:
        import pyvisa
        print(f"✓ PyVISA version: {pyvisa.__version__}")
        return True
    except ImportError:
        print("✗ PyVISA not installed")
        print("  Run: pip install pyvisa")
        return False

def check_visa_backends():
    """Check available VISA backends"""
    print("\n" + "=" * 60)
    print("STEP 2: Checking VISA Backends")
    print("=" * 60)

    import pyvisa

    # Try to list all available backends
    try:
        backends = pyvisa.highlevel.list_backends()
        print(f"✓ Found {len(backends)} VISA backend(s):")
        for backend in backends:
            print(f"    - {backend}")
        return len(backends) > 0
    except:
        print("  Could not enumerate backends")

    # Try specific backends
    print("\nTrying specific backends:")

    backends_to_try = [
        ('@ivi', 'IVI/VISA.NET (Keysight/NI)'),
        ('@py', 'PyVISA-py (Pure Python)'),
        ('@ni', 'NI-VISA'),
        ('@keysight', 'Keysight VISA'),
        ('', 'Default')
    ]

    working_backends = []
    for backend, name in backends_to_try:
        try:
            if backend:
                rm = pyvisa.ResourceManager(backend)
            else:
                rm = pyvisa.ResourceManager()
            print(f"  ✓ {name:30} - WORKING")
            working_backends.append((backend, name))
            rm.close()
        except Exception as e:
            print(f"  ✗ {name:30} - {str(e)[:40]}")

    return len(working_backends) > 0

def check_visa_library():
    """Check for VISA library installation"""
    print("\n" + "=" * 60)
    print("STEP 3: Checking VISA Library Installation")
    print("=" * 60)

    import pyvisa

    try:
        rm = pyvisa.ResourceManager()
        print(f"✓ VISA library found: {rm.visalib}")

        # Try to get VISA library info
        try:
            info = rm.visalib.get_library_paths()
            print(f"  Library path: {info}")
        except:
            pass

        rm.close()
        return True
    except Exception as e:
        print(f"✗ No VISA library found: {e}")
        print("\nYou need to install ONE of these:")
        print("  Option 1: Keysight IO Libraries Suite (recommended for 82357B)")
        print("            https://www.keysight.com/us/en/lib/software-detail/")
        print("            computer-software/io-libraries-suite-downloads-2175637.html")
        print("\n  Option 2: NI-VISA")
        print("            https://www.ni.com/en-us/support/downloads/drivers/")
        print("            download.ni-visa.html")
        print("\n  Option 3: PyVISA-py (software only, no adapter drivers)")
        print("            pip install pyvisa-py")
        return False

def check_usb_devices():
    """Check for USB devices (Keysight adapter)"""
    print("\n" + "=" * 60)
    print("STEP 4: Checking USB Devices")
    print("=" * 60)

    try:
        import subprocess
        # Use PowerShell to check for the specific USB device
        cmd = 'Get-PnpDevice | Where-Object {$_.InstanceId -like "*VID_0957*"} | Format-List'
        result = subprocess.run(
            ['powershell', '-Command', cmd],
            capture_output=True,
            text=True,
            timeout=5
        )

        if 'VID_0957' in result.stdout:
            print("✓ Agilent/Keysight USB device detected")
            print(result.stdout[:500])

            if 'OK' in result.stdout:
                print("\n✓ Device status: OK (Driver installed)")
                return True
            elif 'Error' in result.stdout or 'Unknown' in result.stdout:
                print("\n✗ Device status: ERROR (Driver not working)")
                return False
        else:
            print("✗ Keysight 82357B USB adapter not detected")
            print("\nCheck:")
            print("  1. Is the USB cable connected?")
            print("  2. Is the adapter powered? (LED should be on)")
            print("  3. Try a different USB port")
            return False

    except Exception as e:
        print(f"  Could not check USB devices: {e}")
        return None

def check_resources():
    """Scan for VISA resources"""
    print("\n" + "=" * 60)
    print("STEP 5: Scanning for Instruments")
    print("=" * 60)

    import pyvisa

    try:
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()

        if len(resources) == 0:
            print("✗ No instruments found")
            print("\nPossible reasons:")
            print("  1. Keithley is not powered on")
            print("  2. GPIB cable not connected")
            print("  3. GPIB adapter not recognized (check Step 4)")
            print("  4. GPIB address mismatch")
            return False
        else:
            print(f"✓ Found {len(resources)} instrument(s):")
            for res in resources:
                print(f"    - {res}")
            return True

    except Exception as e:
        print(f"✗ Error scanning: {e}")
        return False

def check_keysight_connection_expert():
    """Check if Keysight Connection Expert is installed"""
    print("\n" + "=" * 60)
    print("STEP 6: Checking Keysight Tools")
    print("=" * 60)

    import os

    # Common installation paths
    paths = [
        r"C:\Program Files\Keysight\IO Libraries Suite",
        r"C:\Program Files (x86)\Keysight\IO Libraries Suite",
        r"C:\Program Files\Agilent\IO Libraries Suite",
        r"C:\Program Files (x86)\Agilent\IO Libraries Suite"
    ]

    for path in paths:
        if os.path.exists(path):
            print(f"✓ Keysight IO Libraries found at: {path}")
            print("\nNext steps:")
            print("  1. Open 'Keysight Connection Expert' from Start menu")
            print("  2. Check if your 82357B adapter appears")
            print("  3. Check if GPIB0::23::INSTR is listed")
            return True

    print("✗ Keysight IO Libraries not found")
    print("\nPlease install:")
    print("  Keysight IO Libraries Suite")
    print("  https://www.keysight.com/us/en/lib/software-detail/")
    print("  computer-software/io-libraries-suite-downloads-2175637.html")
    return False

def main():
    """Run all diagnostics"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "GPIB DIAGNOSTIC TOOL" + " " * 23 + "║")
    print("╚" + "═" * 58 + "╝")

    results = {
        "PyVISA": check_pyvisa(),
        "Backends": check_visa_backends(),
        "VISA Library": check_visa_library(),
        "USB Device": check_usb_devices(),
        "Resources": check_resources(),
        "Keysight Tools": check_keysight_connection_expert()
    }

    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)

    for test, result in results.items():
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⚠ UNKNOWN"
        print(f"{status:10} {test}")

    # Provide recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)

    if not results["VISA Library"]:
        print("\n1. INSTALL KEYSIGHT IO LIBRARIES SUITE")
        print("   This is the most important step!")
        print("   Download from: https://www.keysight.com/us/en/lib/")
        print("   software-detail/computer-software/")
        print("   io-libraries-suite-downloads-2175637.html")

    if results["USB Device"] is False:
        print("\n2. CHECK USB CONNECTION")
        print("   - Reconnect the Keysight 82357B adapter")
        print("   - Try a different USB port")
        print("   - Check if LED is lit on the adapter")

    if results["VISA Library"] and not results["Resources"]:
        print("\n3. CHECK INSTRUMENT CONNECTION")
        print("   - Power on the Keithley 2015")
        print("   - Verify GPIB cable is connected")
        print("   - Check GPIB address on Keithley (should be 23)")
        print("   - Open Keysight Connection Expert to verify")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDiagnostic cancelled.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
