"""CORRECTED VNC screenshot capture with proper little-endian RGB565 conversion"""

import socket
import struct
import time
from PIL import Image
import numpy as np
import sys

def capture_vnc_screenshot_corrected(host="192.168.4.82", port=5900, save_path=None):
    """
    Capture screenshot with CORRECT pixel format (little-endian RGB565)
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    try:
        print(f"Connecting to {host}:{port}...")

        # Connect and handshake
        sock.connect((host, port))
        version = sock.recv(12)
        sock.send(version)

        auth = struct.unpack('>I', sock.recv(4))[0]
        if auth != 1:
            print(f"Error: Authentication type {auth} not supported")
            return False

        sock.send(b'\x01')  # ClientInit

        # Get ServerInit and parse pixel format
        server_init = sock.recv(1024)
        width = struct.unpack('>H', server_init[0:2])[0]
        height = struct.unpack('>H', server_init[2:4])[0]

        # Parse pixel format to confirm
        pixel_format = server_init[4:20]
        bits_per_pixel = pixel_format[0]
        depth = pixel_format[1]
        big_endian_flag = pixel_format[2]
        true_color = pixel_format[3]
        red_max = struct.unpack('>H', pixel_format[4:6])[0]
        green_max = struct.unpack('>H', pixel_format[6:8])[0]
        blue_max = struct.unpack('>H', pixel_format[8:10])[0]
        red_shift = pixel_format[10]
        green_shift = pixel_format[11]
        blue_shift = pixel_format[12]

        print(f"Display: {width}x{height}")
        print(f"Pixel format: {bits_per_pixel}bpp, big_endian={big_endian_flag}")
        print(f"Color shifts: R={red_shift}, G={green_shift}, B={blue_shift}")

        # Send SetEncodings
        sock.send(struct.pack('>BBHi', 2, 0, 1, 0))

        # Send INCREMENTAL update request
        sock.send(struct.pack('>BBHHHH', 3, 1, 0, 0, width, height))

        # Read full framebuffer
        print("Receiving screen data...")
        total_data = b''
        expected_size = 4 + 12 + (width * height * 2)

        while len(total_data) < expected_size:
            chunk = sock.recv(8192)
            if not chunk:
                break
            total_data += chunk
            percent = (len(total_data) / expected_size) * 100
            print(f"\rProgress: {percent:.1f}%", end='')

        print()  # New line

        if len(total_data) < expected_size:
            print(f"Error: Only received {len(total_data)} of {expected_size} bytes")
            return False

        # Extract pixel data
        pixel_data = total_data[16:16 + (width * height * 2)]

        # CORRECT CONVERSION - Use LITTLE ENDIAN as reported by server!
        if big_endian_flag:
            # Server says big endian
            pixels = np.frombuffer(pixel_data, dtype='>u2').reshape((height, width))
        else:
            # Server says little endian (our case!)
            pixels = np.frombuffer(pixel_data, dtype='<u2').reshape((height, width))

        # Extract RGB with correct bit shifts from server
        r = ((pixels >> red_shift) & red_max) * 255 // red_max
        g = ((pixels >> green_shift) & green_max) * 255 // green_max
        b = ((pixels >> blue_shift) & blue_max) * 255 // blue_max

        # Create image
        rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
        img = Image.fromarray(rgb)

        # Save
        if save_path is None:
            save_path = f"vnc_screenshot_correct_{int(time.time())}.png"

        img.save(save_path)
        print(f"Screenshot saved: {save_path}")

        # Also save a version with contrast adjustment for better black
        # This helps if there's still slight color tinting
        img_enhanced = Image.fromarray(rgb)

        # Convert to LAB for better black point correction
        from PIL import ImageOps
        img_enhanced = ImageOps.autocontrast(img_enhanced, cutoff=2)

        enhanced_path = save_path.replace('.png', '_enhanced.png')
        img_enhanced.save(enhanced_path)
        print(f"Enhanced version saved: {enhanced_path}")

        sock.close()
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            sock.close()
        except:
            pass


def main():
    print("CORRECTED Qt Embedded VNC Screenshot Capture")
    print("=============================================")
    print("Using LITTLE ENDIAN format as reported by server")
    print()

    success = capture_vnc_screenshot_corrected()

    if success:
        print("\nSuccess! Black text should now appear correctly black.")
        print("Check both the normal and enhanced versions.")
    else:
        print("\nFailed to capture screenshot.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())