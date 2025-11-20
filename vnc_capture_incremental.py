"""Capture VNC screen using INCREMENTAL updates (the working method!)"""

import socket
import struct
import time
from PIL import Image
import numpy as np

def capture_vnc_screen():
    """Capture screen using incremental updates like TightVNC/RealVNC do"""
    host = "192.168.4.82"
    port = 5900

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    try:
        # Connect and handshake
        sock.connect((host, port))
        version = sock.recv(12)
        sock.send(version)
        auth = struct.unpack('>I', sock.recv(4))[0]
        sock.send(b'\x01')  # ClientInit

        # Get ServerInit
        server_init = sock.recv(1024)
        width = struct.unpack('>H', server_init[0:2])[0]
        height = struct.unpack('>H', server_init[2:4])[0]
        print(f"Display: {width}x{height}, RGB565")

        # Send SetEncodings (support Raw encoding)
        encodings = struct.pack('>BBHi', 2, 0, 1, 0)  # Just Raw encoding
        sock.send(encodings)

        # Send INCREMENTAL update request
        update_req = struct.pack('>BBHHHH', 3, 1, 0, 0, width, height)
        sock.send(update_req)
        print("Requested incremental update...")

        # Read response - need to read full framebuffer
        # Header (4) + Rectangle header (12) + RGB565 pixels (480*272*2)
        total_data = b''
        expected_size = 4 + 12 + (width * height * 2)  # Full frame size
        print(f"Expecting ~{expected_size} bytes...")

        while len(total_data) < expected_size:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                total_data += chunk
                if len(total_data) % 50000 == 0 or len(total_data) >= expected_size:
                    print(f"  Read {len(total_data)} bytes...")
            except socket.timeout:
                print(f"  Timeout at {len(total_data)} bytes")
                break

        print(f"Received {len(total_data)} bytes total")

        if len(total_data) > 4:
            # Parse FramebufferUpdate
            msg_type = total_data[0]
            if msg_type == 0:  # FramebufferUpdate
                padding = total_data[1]
                num_rects = struct.unpack('>H', total_data[2:4])[0]
                print(f"FramebufferUpdate: {num_rects} rectangles")

                offset = 4
                for i in range(num_rects):
                    if offset + 12 <= len(total_data):
                        # Parse rectangle header
                        x = struct.unpack('>H', total_data[offset:offset+2])[0]
                        y = struct.unpack('>H', total_data[offset+2:offset+4])[0]
                        w = struct.unpack('>H', total_data[offset+4:offset+6])[0]
                        h = struct.unpack('>H', total_data[offset+6:offset+8])[0]
                        encoding = struct.unpack('>i', total_data[offset+8:offset+12])[0]

                        print(f"  Rectangle {i+1}: pos=({x},{y}) size={w}x{h} encoding={encoding}")

                        offset += 12

                        if encoding == 0:  # Raw encoding
                            # Calculate expected pixel data size
                            pixel_bytes = w * h * 2  # RGB565 = 2 bytes per pixel
                            print(f"    Expected {pixel_bytes} bytes of pixel data")

                            if offset + pixel_bytes <= len(total_data):
                                # Extract pixel data
                                pixel_data = total_data[offset:offset+pixel_bytes]
                                print(f"    Got {len(pixel_data)} bytes of pixel data")

                                # Convert RGB565 to image
                                if len(pixel_data) == pixel_bytes:
                                    # Parse RGB565 pixels
                                    pixels = np.frombuffer(pixel_data, dtype='>u2')
                                    pixels = pixels.reshape((h, w))

                                    # Extract RGB components
                                    r = ((pixels >> 11) & 0x1F) * 255 // 31
                                    g = ((pixels >> 5) & 0x3F) * 255 // 63
                                    b = (pixels & 0x1F) * 255 // 31

                                    # Create RGB image
                                    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
                                    img = Image.fromarray(rgb)

                                    # Save the rectangle
                                    filename = f"vnc_rect_{x}_{y}_{w}x{h}_{int(time.time())}.png"
                                    img.save(filename)
                                    print(f"    Saved: {filename}")

                                    # If this is full screen, save as main screenshot
                                    if x == 0 and y == 0 and w == width and h == height:
                                        main_file = f"vnc_screenshot_{int(time.time())}.png"
                                        img.save(main_file)
                                        print(f"    *** Full screen saved: {main_file} ***")

                                offset += pixel_bytes
                            else:
                                print(f"    Not enough data for pixels (need {pixel_bytes}, have {len(total_data)-offset})")

            # Save raw data for analysis
            with open("vnc_incremental_data.bin", "wb") as f:
                f.write(total_data)
            print(f"\nRaw data saved to vnc_incremental_data.bin")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sock.close()


if __name__ == "__main__":
    capture_vnc_screen()