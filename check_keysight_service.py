"""
Check Keysight VISA service and provide installation instructions
"""

import subprocess
import os
import sys

def check_keysight_service():
    """Check if Keysight VISA service is running"""
    print("=" * 60)
    print("CHECKING KEYSIGHT VISA SERVICE")
    print("=" * 60)

    try:
        # Check for Keysight/Agilent services
        cmd = 'Get-Service | Where-Object {$_.DisplayName -like "*Keysight*" -or $_.DisplayName -like "*Agilent*" -or $_.DisplayName -like "*VISA*"} | Format-Table -AutoSize'
        result = subprocess.run(
            ['powershell', '-Command', cmd],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.stdout.strip():
            print("Found VISA-related services:\n")
            print(result.stdout)
            return True
        else:
            print("✗ No Keysight/Agilent VISA services found")
            return False

    except Exception as e:
        print(f"Could not check services: {e}")
        return None

def check_ivi_shared_components():
    """Check if IVI Shared Components are installed"""
    print("\n" + "=" * 60)
    print("CHECKING IVI SHARED COMPONENTS")
    print("=" * 60)

    ivi_paths = [
        r"C:\Program Files\IVI Foundation\VISA",
        r"C:\Program Files (x86)\IVI Foundation\VISA",
        r"C:\Program Files\IVI Foundation\IVI",
        r"C:\Program Files (x86)\IVI Foundation\IVI",
    ]

    found = False
    for path in ivi_paths:
        if os.path.exists(path):
            print(f"✓ Found: {path}")
            # List contents
            try:
                contents = os.listdir(path)
                print(f"  Contains: {', '.join(contents[:5])}")
            except:
                pass
            found = True

    if not found:
        print("✗ IVI Shared Components not found")

    return found

def check_keysight_installation():
    """Check Keysight IO Libraries installation"""
    print("\n" + "=" * 60)
    print("CHECKING KEYSIGHT IO LIBRARIES INSTALLATION")
    print("=" * 60)

    keysight_paths = [
        r"C:\Program Files\Keysight",
        r"C:\Program Files (x86)\Keysight",
        r"C:\Program Files\Agilent",
        r"C:\Program Files (x86)\Agilent",
    ]

    found = False
    for path in keysight_paths:
        if os.path.exists(path):
            print(f"✓ Found: {path}")
            try:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if 'visa' in file.lower() and file.endswith('.dll'):
                            full_path = os.path.join(root, file)
                            size = os.path.getsize(full_path)
                            print(f"  {file}: {size:,} bytes at {full_path}")
            except:
                pass
            found = True

    if not found:
        print("✗ Keysight IO Libraries not found in standard locations")

    return found

def provide_solution():
    """Provide step-by-step solution"""
    print("\n" + "=" * 60)
    print("SOLUTION")
    print("=" * 60)

    print("""
The problem is that Connection Expert can see your instrument, but PyVISA
cannot. This happens because Connection Expert uses its own VISA
implementation, while PyVISA tries to use the system VISA libraries.

You need to install the IVI Shared Components which allows all VISA
implementations to work together.

STEP-BY-STEP FIX:
================

Option 1: Install IVI Shared Components (Recommended)
------------------------------------------------------
1. Download IVI Shared Components from:
   https://www.ivifoundation.org/downloads/default.aspx

2. Look for "IVI Shared Components" (latest version)
   - Download the MSI installer
   - Install with default options

3. After installation, reboot your computer

4. The Keysight adapter should now be visible to all VISA libraries


Option 2: Use Keysight Connection Expert Python API (Alternative)
------------------------------------------------------------------
Instead of using PyVISA with VISA, use the Keysight Connection Expert
API directly through COM automation.

Install the pyvisa-py backend:
    pip install pyvisa-py

Or use the Keysight VISA Enabler that comes with IO Libraries Suite.


Option 3: Quick Workaround - Use subprocess (Temporary)
--------------------------------------------------------
Instead of using PyVISA, you could call Connection Expert's command-line
tools or use COM automation to control instruments. This is less elegant
but will work immediately.


RECOMMENDED ACTION:
===================
1. Download and install IVI Shared Components
2. Reboot computer
3. Run this command again: python test_gpib.py

If that doesn't work:
4. In Connection Expert, go to Tools → Options → VISA
5. Make sure "Export to IVI" or similar option is enabled
6. Restart the Keysight VISA Service (services.msc)
""")

def main():
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + "     KEYSIGHT VISA DIAGNOSTIC     " + " " * 21 + "║")
    print("╚" + "═" * 58 + "╝")

    service_ok = check_keysight_service()
    ivi_ok = check_ivi_shared_components()
    keysight_ok = check_keysight_installation()

    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print(f"{'Keysight Services:':<30} {'✓ Found' if service_ok else '✗ Not Found'}")
    print(f"{'IVI Shared Components:':<30} {'✓ Installed' if ivi_ok else '✗ Not Installed'}")
    print(f"{'Keysight IO Libraries:':<30} {'✓ Installed' if keysight_ok else '✗ Not Installed'}")

    provide_solution()

    # Open download page
    print("\n" + "=" * 60)
    print("Would you like to open the IVI Foundation download page?")
    print("=" * 60)
    response = input("Open in browser? (y/n): ").strip().lower()
    if response == 'y':
        import webbrowser
        webbrowser.open('https://www.ivifoundation.org/downloads/default.aspx')
        print("✓ Opened in browser")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
