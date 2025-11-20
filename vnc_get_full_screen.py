"""Get FULL screen by continuing to read after the first half"""

import socket
import struct
import time
from PIL import Image
import numpy as np

def capture_full_screen(host="192.168.4.82", port=5900):
    """
    Capture full screen - server sends it in two chunks
    """

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

        # Set Raw encoding
        sock.send(struct.pack('>BBHi', 2, 0, 1, 0))

        # Request incremental update
        sock.send(struct.pack('>BBHHHH', 3, 1, 0, 0, width, height))
        print("Requested screen update...")

        # Read data in chunks - DON'T STOP at 50%!
        total_data = b''
        expected_total = 16 + (width * height * 2)  # Header + all pixels

        print(f"Reading {expected_total} bytes...")

        # Set non-blocking after initial data
        first_chunk = True

        while len(total_data) < expected_total:
            try:
                if first_chunk:
                    # First read with longer timeout
                    chunk = sock.recv(65536)
                    first_chunk = False
                else:
                    # Continue reading with shorter timeout
                    sock.settimeout(2)
                    chunk = sock.recv(65536)

                if chunk:
                    total_data += chunk
                    percent = (len(total_data) / expected_total) * 100
                    print(f"\rProgress: {percent:.1f}% ({len(total_data)}/{expected_total} bytes)", end='')

                    # Don't break at 50%! Keep reading!
                    if len(total_data) >= expected_total:
                        break
                else:
                    # No more data, but maybe server will send more
                    time.sleep(0.1)

            except socket.timeout:
                # Maybe we need to send another request for the second half
                if len(total_data) >= 130576 and len(total_data) < expected_total:
                    print(f"\nGot first half ({len(total_data)} bytes), requesting more...")

                    # Try sending another incremental request
                    sock.settimeout(10)
                    sock.send(struct.pack('>BBHHHH', 3, 1, 0, 0, width, height))
                    continue
                else:
                    print(f"\nTimeout at {len(total_data)} bytes")
                    break

        print()  # New line
        print(f"Total received: {len(total_data)} bytes")

        # Process what we got
        if len(total_data) >= 16:
            pixel_data = total_data[16:]
            pixels_available = len(pixel_data) // 2  # 2 bytes per pixel

            if pixels_available > 0:
                # Calculate how much of the screen we can show
                rows = min(pixels_available // width, height)
                pixels_to_use = rows * width * 2

                # Big-endian RGB565 (as you confirmed works best)
                pixels = np.frombuffer(pixel_data[:pixels_to_use], dtype='>u2').reshape((rows, width))
                r = ((pixels >> 11) & 0x1F) * 255 // 31
                g = ((pixels >> 5) & 0x3F) * 255 // 63
                b = (pixels & 0x1F) * 255 // 31
                rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)

                # If we only got part of the screen, create full image with white bottom
                if rows < height:
                    print(f"Got {rows}/{height} rows, padding the rest...")
                    full_img = np.ones((height, width, 3), dtype=np.uint8) * 255  # White background
                    full_img[:rows, :, :] = rgb
                    rgb = full_img

                img = Image.fromarray(rgb)
                filename = f"vnc_fullscreen_attempt_{int(time.time())}.png"
                img.save(filename)
                print(f"Saved: {filename}")

                # Also save with sharpening filter
                from PIL import ImageFilter, ImageEnhance

                # Sharpen
                img_sharp = img.filter(ImageFilter.SHARPEN)
                sharpener = ImageEnhance.Sharpness(img_sharp)
                img_sharp = sharpener.enhance(2.0)

                # Increase contrast for black text
                enhancer = ImageEnhance.Contrast(img_sharp)
                img_sharp = enhancer.enhance(1.5)

                filename_sharp = f"vnc_fullscreen_sharp_{int(time.time())}.png"
                img_sharp.save(filename_sharp)
                print(f"Sharpened version: {filename_sharp}")

        sock.close()
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Attempting to capture FULL screen")
    print("="*50)
    capture_full_screen()