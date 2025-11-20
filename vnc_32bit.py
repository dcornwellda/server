"""VNC capture in 32-bit format like TightVNC uses"""

import socket
import struct
import time
from PIL import Image
import numpy as np

def capture_32bit(host="192.168.4.82", port=5900):
    """Capture using 32-bit color format"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)

    try:
        print("Connecting...")
        sock.connect((host, port))

        # Handshake
        version = sock.recv(12)
        sock.send(version)
        sock.recv(4)  # auth
        sock.send(b'\x01')  # ClientInit

        # Get ServerInit
        server_init = sock.recv(1024)
        width = struct.unpack('>H', server_init[0:2])[0]
        height = struct.unpack('>H', server_init[2:4])[0]
        print(f"Display: {width}x{height}")

        # Try to set pixel format to 32-bit
        # SetPixelFormat message: type(1) + padding(3) + pixel_format(16)
        # Pixel format: bpp(1) + depth(1) + big_endian(1) + true_color(1) +
        #              r_max(2) + g_max(2) + b_max(2) + r_shift(1) + g_shift(1) + b_shift(1) + padding(3)

        # Try 32-bit RGBA format
        # Format: bpp(1) + depth(1) + big_endian(1) + true_color(1) + r_max(2) + g_max(2) + b_max(2) + r_shift(1) + g_shift(1) + b_shift(1)
        pixel_format_32bit = struct.pack(
            '>BBBBHHHBBB',
            32,   # Bits per pixel
            24,   # Depth
            0,    # Big endian? No
            1,    # True color
            255,  # Red max
            255,  # Green max
            255,  # Blue max
            16,   # Red shift
            8,    # Green shift
            0     # Blue shift
        )
        pixel_format_32bit += b'\x00\x00\x00'  # 3 bytes padding

        setpixel_msg = struct.pack('>BBBB', 0, 0, 0, 0) + pixel_format_32bit
        sock.send(setpixel_msg)
        print("Sent SetPixelFormat for 32-bit RGBA")

        # Set Raw encoding
        sock.send(struct.pack('>BBHi', 2, 0, 1, 0))
        print("Set Raw encoding")

        # Request incremental update for FULL screen
        sock.send(struct.pack('>BBHHHH', 3, 1, 0, 0, width, height))
        print("Requested screen update...")

        # Read all data
        total_data = b''
        expected_pixels_32bit = width * height * 4  # 32-bit = 4 bytes per pixel
        expected_total = 16 + expected_pixels_32bit

        print(f"Expecting {expected_total} bytes ({width}x{height}x4)...")

        while len(total_data) < expected_total:
            try:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                total_data += chunk
                percent = (len(total_data) / expected_total) * 100
                print(f"\rProgress: {percent:.1f}%", end='')
            except socket.timeout:
                print(f"\nTimeout at {len(total_data)} bytes")
                break

        print()
        print(f"Received {len(total_data)} bytes")

        # Process the data
        if len(total_data) >= 16:
            pixel_data = total_data[16:]

            # Try different 32-bit interpretations
            interpretations = {}

            # 1. RGBA (little-endian)
            if len(pixel_data) >= width * height * 4:
                pixels = np.frombuffer(pixel_data[:width * height * 4], dtype=np.uint8).reshape((height, width, 4))
                rgb = pixels[:, :, :3]  # Take RGB, ignore alpha
                interpretations['RGBA_LE'] = Image.fromarray(rgb)

            # 2. ARGB (little-endian)
            if len(pixel_data) >= width * height * 4:
                pixels = np.frombuffer(pixel_data[:width * height * 4], dtype=np.uint8).reshape((height, width, 4))
                rgb = pixels[:, :, 1:]  # Skip alpha, take RGB
                interpretations['ARGB_LE'] = Image.fromarray(rgb)

            # 3. BGRA (little-endian)
            if len(pixel_data) >= width * height * 4:
                pixels = np.frombuffer(pixel_data[:width * height * 4], dtype=np.uint8).reshape((height, width, 4))
                bgra = pixels[:, :, :3]
                rgb = bgra[:, :, [2, 1, 0]]  # Reverse to RGB
                interpretations['BGRA_LE'] = Image.fromarray(rgb)

            # Save all interpretations
            for name, img in interpretations.items():
                filename = f"vnc_32bit_{name}_{int(time.time())}.png"
                img.save(filename)
                print(f"Saved: {filename}")

            print("\nCheck which one looks correct!")

        sock.close()
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("VNC 32-bit Capture (TightVNC format)")
    print("="*50)
    capture_32bit()
