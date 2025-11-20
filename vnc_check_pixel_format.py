"""Check the actual pixel format sent by the VNC server"""

import socket
import struct

def check_pixel_format(host="192.168.4.82", port=5900):
    """Get and decode the pixel format from the VNC server"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        # Connect and handshake
        sock.connect((host, port))
        version = sock.recv(12)
        print(f"Server version: {version.decode('ascii').strip()}")
        sock.send(version)

        auth = struct.unpack('>I', sock.recv(4))[0]
        print(f"Auth type: {auth}")

        sock.send(b'\x01')  # ClientInit

        # Get ServerInit - contains pixel format
        server_init = sock.recv(1024)

        # Parse framebuffer dimensions
        width = struct.unpack('>H', server_init[0:2])[0]
        height = struct.unpack('>H', server_init[2:4])[0]

        print(f"\nFramebuffer: {width}x{height}")
        print("\nPIXEL FORMAT FROM SERVER:")
        print("-" * 40)

        # Parse pixel format (starts at byte 4)
        fmt = server_init[4:20]

        bits_per_pixel = fmt[0]
        depth = fmt[1]
        big_endian = fmt[2]
        true_color = fmt[3]
        red_max = struct.unpack('>H', fmt[4:6])[0]
        green_max = struct.unpack('>H', fmt[6:8])[0]
        blue_max = struct.unpack('>H', fmt[8:10])[0]
        red_shift = fmt[10]
        green_shift = fmt[11]
        blue_shift = fmt[12]

        print(f"Bits per pixel: {bits_per_pixel}")
        print(f"Depth: {depth}")
        print(f"Big endian: {big_endian} ({'Yes' if big_endian else 'No'})")
        print(f"True color: {true_color} ({'Yes' if true_color else 'No'})")
        print(f"Red max: {red_max} (0x{red_max:04X})")
        print(f"Green max: {green_max} (0x{green_max:04X})")
        print(f"Blue max: {blue_max} (0x{blue_max:04X})")
        print(f"Red shift: {red_shift}")
        print(f"Green shift: {green_shift}")
        print(f"Blue shift: {blue_shift}")

        # Determine the actual format
        print("\n" + "="*50)
        print("ACTUAL FORMAT ANALYSIS:")
        print("="*50)

        if bits_per_pixel == 16:
            if red_max == 31 and green_max == 63 and blue_max == 31:
                if red_shift == 11 and green_shift == 5 and blue_shift == 0:
                    print("FORMAT: Standard RGB565")
                    print("Layout: RRRRRGGGGGGBBBBB")
                elif red_shift == 0 and green_shift == 5 and blue_shift == 11:
                    print("FORMAT: BGR565 (reversed)")
                    print("Layout: BBBBBGGGGGGRRRRR")
                else:
                    print(f"FORMAT: Custom 565 with shifts R:{red_shift} G:{green_shift} B:{blue_shift}")
            elif red_max == 15 and green_max == 15 and blue_max == 15:
                print("FORMAT: RGB444 or RGBA4444")
            else:
                print(f"FORMAT: Unknown 16-bit format")

        # Show how to extract colors correctly
        print("\nCORRECT EXTRACTION CODE:")
        print("-" * 40)

        if big_endian:
            print("pixels = np.frombuffer(data, dtype='>u2')")
        else:
            print("pixels = np.frombuffer(data, dtype='<u2')")

        print(f"r = ((pixels >> {red_shift}) & 0x{red_max:X}) * 255 // {red_max}")
        print(f"g = ((pixels >> {green_shift}) & 0x{green_max:X}) * 255 // {green_max}")
        print(f"b = ((pixels >> {blue_shift}) & 0x{blue_max:X}) * 255 // {blue_max}")

        sock.close()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_pixel_format()