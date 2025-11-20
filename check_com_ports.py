"""
Check available COM ports and their status
"""
import serial.tools.list_ports

def main():
    print("=" * 60)
    print("Available COM Ports")
    print("=" * 60)

    ports = serial.tools.list_ports.comports()

    if not ports:
        print("No COM ports found!")
    else:
        for port in ports:
            print(f"\nPort: {port.device}")
            print(f"  Description: {port.description}")
            print(f"  Manufacturer: {port.manufacturer}")
            print(f"  Hardware ID: {port.hwid}")

            # Try to open it
            try:
                ser = serial.Serial(port.device, timeout=1)
                ser.close()
                print(f"  Status: AVAILABLE (can be opened)")
            except serial.SerialException as e:
                print(f"  Status: IN USE or ERROR ({str(e)})")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
