"""VNC capture using the exact format RealVNC shows"""

import socket
import struct
import time
from PIL import Image
import numpy as np

def capture_like_realvnc(host="192.168.4.82", port=5900):
    """
    Capture using RealVNC's confirmed settings:
    - Little-endian RGB565
    - Force Raw encoding (not Hextile)
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)

    try:
        print("Connecting (using RealVNC format)...")
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

        # IMPORTANT: Set encodings to force RAW (not Hextile)
        # We only support Raw encoding (type 0)
        encodings_msg = struct.pack(
            '>BBH',
            2,    # SetEncodings message type
            0,    # Padding
            1     # Number of encodings (just Raw)
        )
        # Add Raw encoding type (0)
        encodings_msg += struct.pack('>i', 0)  # Raw = 0
        sock.send(encodings_msg)
        print("Forced Raw encoding (not Hextile)")

        # Request incremental update
        update_req = struct.pack('>BBHHHH', 3, 1, 0, 0, width, height)
        sock.send(update_req)
        print("Requested screen update...")

        # Read ALL data - keep reading until we have enough
        total_data = b''
        expected_header = 16  # FramebufferUpdate header + rectangle header
        expected_pixels = width * height * 2  # RGB565 pixels
        expected_total = expected_header + expected_pixels

        print(f"Expecting {expected_total} bytes total...")

        # First, read enough to get the header
        while len(total_data) < expected_header:
            chunk = sock.recv(4096)
            if not chunk:
                break
            total_data += chunk

        # Check if this is Raw encoding
        if len(total_data) >= 16:
            encoding = struct.unpack('>i', total_data[12:16])[0]
            if encoding != 0:
                print(f"WARNING: Server sent encoding {encoding} (not Raw)")
                # Try to continue anyway

        # Continue reading until we have all pixel data
        sock.settimeout(5)  # Shorter timeout for remaining data
        while len(total_data) < expected_total:
            try:
                chunk = sock.recv(8192)
                if not chunk:
                    break
                total_data += chunk
                percent = (len(total_data) / expected_total) * 100
                print(f"\rProgress: {percent:.1f}%", end='')
            except socket.timeout:
                print(f"\nTimeout at {len(total_data)} bytes")
                break

        print()  # New line
        print(f"Received {len(total_data)} bytes")

        if len(total_data) >= expected_total:
            # Extract pixel data
            pixel_data = total_data[16:16 + expected_pixels]

            # LITTLE-ENDIAN RGB565 (as confirmed by RealVNC)
            pixels = np.frombuffer(pixel_data, dtype='<u2').reshape((height, width))

            # Standard RGB565 extraction
            r = ((pixels >> 11) & 0x1F) * 255 // 31
            g = ((pixels >> 5) & 0x3F) * 255 // 63
            b = (pixels & 0x1F) * 255 // 31

            # Create image
            rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
            img = Image.fromarray(rgb)

            # Save
            filename = f"vnc_realvnc_format_{int(time.time())}.png"
            img.save(filename)
            print(f"Screenshot saved: {filename}")

            # Also try byte-swapped version for comparison
            pixels_swap = np.frombuffer(pixel_data, dtype='>u2').reshape((height, width))
            r2 = ((pixels_swap >> 11) & 0x1F) * 255 // 31
            g2 = ((pixels_swap >> 5) & 0x3F) * 255 // 63
            b2 = (pixels_swap & 0x1F) * 255 // 31
            rgb2 = np.stack([r2, g2, b2], axis=-1).astype(np.uint8)
            img2 = Image.fromarray(rgb2)
            filename2 = f"vnc_bigendian_compare_{int(time.time())}.png"
            img2.save(filename2)
            print(f"Big-endian version for comparison: {filename2}")

            print("\nCheck both images:")
            print("- vnc_realvnc_format_*.png (little-endian as per RealVNC)")
            print("- vnc_bigendian_compare_*.png (big-endian for comparison)")

            sock.close()
            return True
        else:
            print(f"Not enough data (need {expected_total}, got {len(total_data)})")

            # Save what we got for analysis
            with open("vnc_partial_data.bin", "wb") as f:
                f.write(total_data)
            print("Partial data saved to vnc_partial_data.bin")

            sock.close()
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    print("VNC Capture using RealVNC-confirmed format")
    print("=" * 50)
    print("Format: Little-endian RGB565 (16bpp)")
    print("=" * 50)
    print()

    capture_like_realvnc()