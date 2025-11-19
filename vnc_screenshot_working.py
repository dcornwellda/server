"""Working VNC screenshot capture for Qt Embedded VNC Server

This script successfully captures screenshots from Qt Embedded Linux VNC servers
by using INCREMENTAL update requests, which is what TightVNC/RealVNC viewers do.

Key discoveries:
1. Qt Embedded VNC servers disconnect on non-incremental (full) update requests
2. They work fine with incremental update requests
3. The server sends the full screen on the first incremental request
"""

import socket
import struct
import time
from PIL import Image
import numpy as np
import sys

def capture_qt_vnc_screenshot(host="192.168.4.82", port=5900, save_path=None):
    """
    Capture screenshot from Qt Embedded Linux VNC Server

    Args:
        host: VNC server IP address
        port: VNC server port (default 5900 for display :0)
        save_path: Path to save screenshot (default: vnc_screenshot_<timestamp>.png)

    Returns:
        bool: True if successful, False otherwise
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)  # Increased timeout for slow connections

    try:
        print(f"Connecting to {host}:{port}...")

        # 1. Connect
        sock.connect((host, port))

        # 2. Version handshake
        version = sock.recv(12)
        if not version.startswith(b'RFB'):
            print("Error: Not a VNC server")
            return False
        sock.send(version)  # Echo same version

        # 3. Authentication
        auth = struct.unpack('>I', sock.recv(4))[0]
        if auth != 1:  # Only support no authentication
            print(f"Error: Authentication type {auth} not supported")
            return False

        # 4. ClientInit (shared desktop)
        sock.send(b'\x01')

        # 5. Receive ServerInit
        server_init = sock.recv(1024)
        width = struct.unpack('>H', server_init[0:2])[0]
        height = struct.unpack('>H', server_init[2:4])[0]
        print(f"Display size: {width}x{height}")

        # 6. Send SetEncodings (support Raw encoding only)
        encodings = struct.pack('>BBHi', 2, 0, 1, 0)  # Message type 2, 1 encoding (Raw)
        sock.send(encodings)

        # 7. Send INCREMENTAL update request (CRITICAL!)
        # This is the key - Qt VNC servers only work with incremental requests
        update_req = struct.pack('>BBHHHH', 3, 1, 0, 0, width, height)
        sock.send(update_req)

        # 8. Read the full framebuffer response
        print("Receiving screen data...")
        total_data = b''
        expected_size = 4 + 12 + (width * height * 2)  # Header + rect header + RGB565 pixels

        while len(total_data) < expected_size:
            chunk = sock.recv(8192)
            if not chunk:
                break
            total_data += chunk

            # Show progress
            percent = (len(total_data) / expected_size) * 100
            print(f"\rProgress: {percent:.1f}%", end='')

        print()  # New line after progress

        if len(total_data) < expected_size:
            print(f"Error: Only received {len(total_data)} of {expected_size} bytes")
            return False

        # 9. Parse and convert the framebuffer data
        msg_type = total_data[0]
        if msg_type != 0:  # FramebufferUpdate
            print(f"Error: Unexpected message type {msg_type}")
            return False

        num_rects = struct.unpack('>H', total_data[2:4])[0]
        if num_rects != 1:
            print(f"Warning: Expected 1 rectangle, got {num_rects}")

        # Parse rectangle header
        x = struct.unpack('>H', total_data[4:6])[0]
        y = struct.unpack('>H', total_data[6:8])[0]
        w = struct.unpack('>H', total_data[8:10])[0]
        h = struct.unpack('>H', total_data[10:12])[0]
        encoding = struct.unpack('>i', total_data[12:16])[0]

        if encoding != 0:  # Raw encoding
            print(f"Error: Unsupported encoding {encoding}")
            return False

        # Extract pixel data (RGB565 format)
        pixel_data = total_data[16:16 + (w * h * 2)]

        # Convert RGB565 to RGB888
        pixels = np.frombuffer(pixel_data, dtype='>u2').reshape((h, w))  # Back to big-endian
        r = ((pixels >> 11) & 0x1F) * 255 // 31
        g = ((pixels >> 5) & 0x3F) * 255 // 63
        b = (pixels & 0x1F) * 255 // 31

        # Create and save image
        rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
        img = Image.fromarray(rgb)

        # Save screenshot
        if save_path is None:
            save_path = f"vnc_screenshot_{int(time.time())}.png"

        img.save(save_path)
        print(f"Screenshot saved: {save_path}")

        sock.close()
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        try:
            sock.close()
        except:
            pass


def main():
    """Main function for command-line usage"""
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = "192.168.4.82"

    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    else:
        port = 5900

    print("Qt Embedded VNC Screenshot Capture")
    print("===================================")
    success = capture_qt_vnc_screenshot(host, port)

    if success:
        print("\nSuccess! Screenshot captured.")
        print("\nNote: This works because we use INCREMENTAL update requests,")
        print("which Qt Embedded VNC servers support (unlike full updates).")
    else:
        print("\nFailed to capture screenshot.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())