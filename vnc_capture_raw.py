"""Capture raw VNC protocol data to see what TightVNC/RealVNC do differently"""

import socket
import struct
import time
import binascii

def capture_vnc_protocol():
    """Connect and capture ALL data without sending update requests"""
    host = "192.168.4.82"
    port = 5900

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    try:
        # Connect
        sock.connect((host, port))
        print(f"Connected to {host}:{port}")

        # Get version
        version = sock.recv(12)
        print(f"Server: {version.decode('ascii').strip()}")

        # Send same version back
        sock.send(version)
        print("Sent version back")

        # Get auth
        auth_data = sock.recv(4)
        auth = struct.unpack('>I', auth_data)[0]
        print(f"Auth type: {auth}")

        # Send ClientInit with shared=1 (like TightVNC does)
        sock.send(b'\x01')
        print("Sent ClientInit (shared=1)")

        # Set non-blocking to capture all data
        sock.setblocking(0)

        print("\nWaiting for data from server...")
        print("="*50)

        total_data = b''
        start_time = time.time()
        last_data_time = start_time

        while time.time() - start_time < 5:  # Capture for 5 seconds
            try:
                data = sock.recv(65536)
                if data:
                    total_data += data
                    print(f"[{time.time()-start_time:.2f}s] Received {len(data)} bytes (total: {len(total_data)})")
                    last_data_time = time.time()

                    # Check if this looks like framebuffer data
                    if len(data) > 100:
                        print(f"  First 50 bytes: {binascii.hexlify(data[:50]).decode()}")
            except BlockingIOError:
                # No data available right now
                pass
            except Exception as e:
                print(f"Error: {e}")
                break

            # If no data for 2 seconds, send a gentle nudge
            if time.time() - last_data_time > 2:
                print("\nNo data for 2s, trying SetPixelFormat (like viewers do)...")
                # Send SetPixelFormat message (type 0)
                # This is what many viewers send after ServerInit
                # SetPixelFormat: type(1) + padding(3) + pixel_format(16)
                pixel_format = struct.pack(
                    '>BBBBBBBBHHHBBBxxx',
                    0,    # Message type: SetPixelFormat
                    0, 0, 0,  # Padding (3 bytes)
                    16,   # Bits per pixel
                    16,   # Depth
                    0,    # Big endian flag
                    1,    # True color flag
                    31,   # Red max (H = 2-byte value)
                    63,   # Green max (H = 2-byte value)
                    31,   # Blue max (H = 2-byte value)
                    11,   # Red shift
                    5,    # Green shift
                    0     # Blue shift
                    # xxx = 3 bytes padding automatically added
                )
                try:
                    sock.setblocking(1)
                    sock.send(pixel_format)
                    sock.setblocking(0)
                    print("Sent SetPixelFormat")
                except:
                    pass
                last_data_time = time.time()

        print("\n" + "="*50)
        print(f"Total data received: {len(total_data)} bytes")

        if len(total_data) > 24:
            # Parse ServerInit
            width = struct.unpack('>H', total_data[0:2])[0]
            height = struct.unpack('>H', total_data[2:4])[0]
            name_len = struct.unpack('>I', total_data[20:24])[0]

            server_init_size = 24 + name_len
            print(f"ServerInit size: {server_init_size} bytes")
            print(f"Display: {width}x{height}")

            if len(total_data) > server_init_size:
                remaining = total_data[server_init_size:]
                print(f"Data after ServerInit: {len(remaining)} bytes")

                if remaining:
                    print(f"First byte after ServerInit: 0x{remaining[0]:02x}")

                    # Check if it's a FramebufferUpdate (type 0)
                    if remaining[0] == 0:
                        print("This looks like a FramebufferUpdate message!")
                        if len(remaining) >= 4:
                            num_rects = struct.unpack('>H', remaining[2:4])[0]
                            print(f"Number of rectangles: {num_rects}")

                    # Save the data for analysis
                    with open("vnc_capture.bin", "wb") as f:
                        f.write(remaining)
                    print("Saved framebuffer data to vnc_capture.bin")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    capture_vnc_protocol()