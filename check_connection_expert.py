"""
Check what Connection Expert sees vs PyVISA
"""

import pyvisa
import time

def check_all_backends():
    """Try all possible backends to find instruments"""
    print("=" * 60)
    print("SCANNING WITH DIFFERENT BACKENDS")
    print("=" * 60)

    backends = [
        ('@ivi', 'IVI/Default'),
        ('@py', 'PyVISA-py'),
        ('@ni', 'NI-VISA'),
        ('@sim', 'Simulated'),
        ('', 'System Default')
    ]

    all_resources = {}

    for backend, name in backends:
        print(f"\n[{name}]")
        try:
            if backend:
                rm = pyvisa.ResourceManager(backend)
            else:
                rm = pyvisa.ResourceManager()

            print(f"  Backend path: {rm.visalib}")
            resources = rm.list_resources()

            if resources:
                print(f"  ✓ Found {len(resources)} instrument(s):")
                for res in resources:
                    print(f"      - {res}")
                all_resources[name] = resources
            else:
                print(f"  ✗ No instruments found")

            rm.close()

        except Exception as e:
            print(f"  ✗ Error: {str(e)[:60]}")

    return all_resources

def check_gpib_addresses():
    """Try to scan common GPIB addresses manually"""
    print("\n" + "=" * 60)
    print("MANUAL GPIB ADDRESS SCAN")
    print("=" * 60)
    print("Trying to connect to different GPIB addresses...")

    try:
        rm = pyvisa.ResourceManager()
        print(f"Using: {rm.visalib}\n")

        found = []

        # Try addresses 0-30
        for addr in range(0, 31):
            address = f"GPIB0::{addr}::INSTR"
            try:
                print(f"  Trying {address}...", end=" ")
                inst = rm.open_resource(address)
                inst.timeout = 1000  # Short timeout for quick scan

                # Try to get ID
                try:
                    idn = inst.query("*IDN?").strip()
                    print(f"✓ FOUND: {idn[:50]}")
                    found.append((address, idn))
                except:
                    print(f"✓ Device responds (no *IDN)")
                    found.append((address, "Unknown device"))

                inst.close()

            except pyvisa.errors.VisaIOError as e:
                if "VI_ERROR_RSRC_NFOUND" in str(e):
                    print("✗ Not found")
                elif "VI_ERROR_TMO" in str(e):
                    print("✓ Device found but timeout")
                    found.append((address, "Device found (timeout)"))
                else:
                    print(f"✗ Error: {str(e)[:30]}")
            except Exception as e:
                print(f"✗ {str(e)[:30]}")

            time.sleep(0.1)  # Small delay between attempts

        rm.close()

        print("\n" + "=" * 60)
        print("SCAN RESULTS")
        print("=" * 60)

        if found:
            print(f"\n✓ Found {len(found)} device(s):")
            for addr, idn in found:
                print(f"    {addr}: {idn}")
            return found
        else:
            print("\n✗ No GPIB devices found")
            print("\nTroubleshooting:")
            print("  1. Check if Keithley is powered ON")
            print("  2. Verify GPIB cable is connected")
            print("  3. Check GPIB address setting on Keithley front panel")
            print("  4. In Connection Expert, try 'Scan for Instruments'")
            return []

    except Exception as e:
        print(f"\n✗ Error during scan: {e}")
        return []

def check_visa_info():
    """Get detailed VISA information"""
    print("\n" + "=" * 60)
    print("VISA SYSTEM INFORMATION")
    print("=" * 60)

    try:
        rm = pyvisa.ResourceManager()

        print(f"VISA Library: {rm.visalib}")

        try:
            # Try to get more info
            print(f"\nSession: {rm.session}")
        except:
            pass

        try:
            # List all resources with query
            print(f"\nResource query: {rm.list_resources_info()}")
        except:
            pass

        rm.close()

    except Exception as e:
        print(f"Error: {e}")

def main():
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " CONNECTION EXPERT vs PyVISA COMPARISON " + " " * 11 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    # Check VISA info
    check_visa_info()

    # Try different backends
    resources = check_all_backends()

    # Manual GPIB scan
    found_devices = check_gpib_addresses()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if found_devices:
        print("\n✓ SUCCESS: Found GPIB devices!")
        print("\nUpdate your code to use this address:")
        for addr, idn in found_devices:
            print(f"  {addr}")
    else:
        print("\n✗ No GPIB devices detected by PyVISA")
        print("\nWhat to check in Connection Expert:")
        print("  1. Is GPIB0 interface visible?")
        print("  2. Are any instruments listed under GPIB0?")
        print("  3. Right-click GPIB0 → 'Scan for Instruments'")
        print("  4. If you see instruments there, note their addresses")
        print("\nPhysical checks:")
        print("  1. Keithley 2015 powered ON?")
        print("  2. GPIB cable connected to both ends?")
        print("  3. Check GPIB address on Keithley (Menu → Communication)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScan cancelled.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
