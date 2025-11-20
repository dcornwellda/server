"""
Quick Start Example for Keithley 2015 Control
"""

from keithley_2015 import Keithley2015
import time

# CONFIGURATION - Update these for your setup
PORT = 'COM3'        # Your serial port (check Device Manager on Windows)
BAUDRATE = 9600      # Must match instrument settings (typically 9600)

def main():
    print("Keithley 2015 Control Example")
    print("=" * 50)

    try:
        # Connect to the meter
        dmm = Keithley2015(PORT, BAUDRATE)
        print(f"Connected to port {PORT}")

        # Get instrument ID
        id_string = dmm.get_id()
        print(f"Instrument: {id_string}\n")

        # Make it beep to confirm connection
        dmm.beep()

        # Example 1: Measure DC Voltage
        print("Example 1: DC Voltage Measurement")
        print("-" * 50)
        dmm.configure_dc_voltage(range_val='AUTO')
        for i in range(3):
            voltage = dmm.read()
            print(f"  Reading {i+1}: {voltage:.6f} V")
            time.sleep(0.5)

        # Example 2: Measure Resistance
        print("\nExample 2: Resistance Measurement")
        print("-" * 50)
        dmm.configure_resistance(range_val='AUTO')
        resistance = dmm.read()
        print(f"  Resistance: {resistance:.3f} Ohms")

        # Example 3: Measure AC Voltage
        print("\nExample 3: AC Voltage Measurement")
        print("-" * 50)
        dmm.configure_ac_voltage(range_val='AUTO')
        ac_voltage = dmm.read()
        print(f"  AC Voltage: {ac_voltage:.6f} V")

        # Example 4: Display custom text
        print("\nExample 4: Display Custom Text")
        print("-" * 50)
        dmm.display_text("HELLO!")
        print("  'HELLO!' displayed on meter for 2 seconds")
        time.sleep(2)
        dmm.display_clear()

        # Check for errors
        print("\nChecking for errors...")
        errors = dmm.check_errors()
        if not errors:
            print("  No errors detected!")

        # Close connection
        dmm.close()
        print("\nConnection closed successfully")

    except Exception as e:
        print(f"\nError occurred: {e}")
        print("\nTroubleshooting tips:")
        print(f"  1. Verify the serial port is correct (current: {PORT})")
        print("     - Check Windows Device Manager > Ports (COM & LPT)")
        print(f"  2. Verify the baud rate matches instrument (current: {BAUDRATE})")
        print("     - Check instrument menu: MENU > INTERFACE > RS232")
        print("  3. Ensure no other software is using the port")
        print("  4. Check cable connection")

if __name__ == '__main__':
    main()
