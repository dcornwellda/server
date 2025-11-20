"""
Debug test for Keithley 2015 - shows exactly what's happening
"""

import serial
import time

PORT = 'COM3'
BAUDRATE = 9600

print("Debug Test for Keithley 2015")
print("=" * 60)

try:
    # Open serial port
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUDRATE,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=5  # 5 second timeout
    )

    print(f"✓ Opened port {PORT}")
    time.sleep(0.5)

    # Test 1: Get ID
    print("\nTest 1: Sending *IDN?")
    ser.write(b'*IDN?\n')
    print("  Waiting for response...")
    response = ser.readline()
    print(f"  Response: {response}")
    print(f"  Decoded: {response.decode('ascii').strip()}")

    # Test 2: Clear and reset
    print("\nTest 2: Clearing and resetting")
    ser.write(b'*CLS\n')
    time.sleep(0.5)
    ser.write(b'*RST\n')
    print("  Sent *CLS and *RST")
    time.sleep(2)

    # Test 3: Configure for DC voltage
    print("\nTest 3: Configure DC voltage")
    ser.write(b'CONF:VOLT:DC\n')
    print("  Sent CONF:VOLT:DC")
    time.sleep(0.5)

    # Test 4: Try to read
    print("\nTest 4: Attempting to read measurement")
    ser.write(b'READ?\n')
    print("  Sent READ?")
    print("  Waiting for response (5 second timeout)...")

    start_time = time.time()
    response = ser.readline()
    elapsed = time.time() - start_time

    if response:
        print(f"  ✓ Got response in {elapsed:.2f} seconds")
        print(f"  Raw bytes: {response}")
        print(f"  Decoded: {response.decode('ascii').strip()}")
        try:
            value = float(response.decode('ascii').strip())
            print(f"  Value: {value} V")
        except:
            print("  Could not convert to float")
    else:
        print(f"  ✗ No response after {elapsed:.2f} seconds (TIMEOUT)")
        print("  Checking what's in the buffer...")
        waiting = ser.in_waiting
        print(f"  Bytes in buffer: {waiting}")
        if waiting > 0:
            data = ser.read(waiting)
            print(f"  Buffer contents: {data}")

    # Test 5: Check errors
    print("\nTest 5: Checking for errors")
    ser.write(b'SYST:ERR?\n')
    time.sleep(0.2)
    error = ser.readline()
    print(f"  Error queue: {error.decode('ascii').strip()}")

    # Test 6: Try alternative read method
    print("\nTest 6: Try INIT + FETCH method")
    ser.write(b'INIT\n')
    print("  Sent INIT (start measurement)")
    time.sleep(2)  # Wait for measurement to complete
    ser.write(b'FETC?\n')
    print("  Sent FETC? (fetch result)")
    response = ser.readline()
    if response:
        print(f"  Response: {response.decode('ascii').strip()}")
    else:
        print("  No response")

    ser.close()
    print("\n✓ Test complete, port closed")

except serial.SerialException as e:
    print(f"\n✗ Serial error: {e}")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
