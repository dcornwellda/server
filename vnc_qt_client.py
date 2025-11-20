"""Custom VNC client for Qt Embedded Linux VNC Server

This server has quirks:
- Disconnects when FramebufferUpdateRequest is sent
- May push updates automatically without requests
- Uses RGB565 format (16bpp)
"""

import socket
import struct
import time
from PIL import Image
import numpy as np

class QtVNCClient:
    def __init__(self, host, port=5900):
        self.host = host
        self.port = port
        self.sock = None
        self.width = None
        self.height = None
        self.pixel_format = None
        self.desktop_name = None

    def connect(self):
        """Connect and perform VNC handshake"""
        try:
            # Connect to server
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")

            # Read server version
            version = self.sock.recv(12)
            print(f"Server version: {version.decode('ascii').strip()}")

            # Send client version (use same version)
            self.sock.send(version)
            print("Sent client version")

            # Read authentication type
            auth_data = self.sock.recv(4)
            auth_type = struct.unpack('>I', auth_data)[0]
            print(f"Auth type: {auth_type}")

            if auth_type != 1:
                print("Authentication required or failed")
                return False

            # Send ClientInit (shared=1)
            self.sock.send(b'\x01')
            print("Sent ClientInit")

            # Read ServerInit
            server_init = self.sock.recv(1024)  # Read enough for ServerInit

            # Parse dimensions
            self.width = struct.unpack('>H', server_init[0:2])[0]
            self.height = struct.unpack('>H', server_init[2:4])[0]
            print(f"Framebuffer: {self.width}x{self.height}")

            # Parse pixel format (starts at byte 4)
            bits_per_pixel = server_init[4]
            depth = server_init[5]
            big_endian = server_init[6]
            true_color = server_init[7]

            if true_color:
                r_max = struct.unpack('>H', server_init[8:10])[0]
                g_max = struct.unpack('>H', server_init[10:12])[0]
                b_max = struct.unpack('>H', server_init[12:14])[0]
                r_shift = server_init[14]
                g_shift = server_init[15]
                b_shift = server_init[16]

                self.pixel_format = {
                    'bpp': bits_per_pixel,
                    'depth': depth,
                    'big_endian': big_endian,
                    'r_max': r_max,
                    'g_max': g_max,
                    'b_max': b_max,
                    'r_shift': r_shift,
                    'g_shift': g_shift,
                    'b_shift': b_shift
                }
                print(f"Pixel format: RGB565 ({r_max},{g_max},{b_max})")

            # Parse desktop name
            name_length = struct.unpack('>I', server_init[20:24])[0]
            if len(server_init) >= 24 + name_length:
                self.desktop_name = server_init[24:24+name_length].decode('ascii', errors='ignore')
                print(f"Desktop: '{self.desktop_name}'")

            # Important: Set socket to non-blocking to check for pushed data
            self.sock.setblocking(0)

            return True

        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def check_for_data(self, timeout=2):
        """Check if server pushed any data (without requesting it)"""
        import select

        print(f"Waiting {timeout}s for any pushed data from server...")
        ready, _, _ = select.select([self.sock], [], [], timeout)

        if ready:
            try:
                # Try to read any available data
                data = self.sock.recv(65536)  # Read up to 64KB
                print(f"Received {len(data)} bytes of data!")
                return data
            except BlockingIOError:
                print("No data available")
                return None
        else:
            print("No data pushed by server")
            return None

    def try_passive_capture(self):
        """Try to capture screen without sending update request"""
        print("\n--- Passive Capture Attempt ---")

        # Check if server pushes any initial data
        data = self.check_for_data(timeout=3)

        if data:
            # Try to parse as framebuffer update
            if len(data) > 0 and data[0] == 0:  # FramebufferUpdate message type
                print("Received FramebufferUpdate message!")
                # In a real implementation, parse the rectangles here
                return data

        print("No framebuffer data received passively")
        return None

    def send_key_event(self, key, down=True):
        """Send a key event (might trigger screen update)"""
        try:
            # Key event: type(1) + down(1) + padding(2) + key(4)
            msg = struct.pack('>BBHI', 4, 1 if down else 0, 0, key)
            self.sock.send(msg)
            print(f"Sent key event: {key} ({'down' if down else 'up'})")
            return True
        except Exception as e:
            print(f"Failed to send key event: {e}")
            return False

    def send_pointer_event(self, x, y, buttons=0):
        """Send a pointer event (might trigger screen update)"""
        try:
            # Pointer event: type(1) + buttons(1) + x(2) + y(2)
            msg = struct.pack('>BBHH', 5, buttons, x, y)
            self.sock.send(msg)
            print(f"Sent pointer event: ({x},{y}) buttons={buttons}")
            return True
        except Exception as e:
            print(f"Failed to send pointer event: {e}")
            return False

    def disconnect(self):
        """Close the connection"""
        if self.sock:
            try:
                self.sock.close()
                print("Disconnected")
            except:
                pass


def test_qt_vnc():
    """Test the Qt VNC server"""
    client = QtVNCClient("192.168.4.82")

    if not client.connect():
        print("Failed to connect")
        return

    # Try passive capture (no update request)
    data = client.try_passive_capture()

    # Try sending events to trigger updates
    print("\n--- Trying to trigger updates with events ---")

    # Send a harmless key event (space key)
    client.send_key_event(0x20, down=True)
    time.sleep(0.1)
    client.send_key_event(0x20, down=False)

    # Check for response
    data = client.check_for_data(timeout=1)

    # Try pointer movement
    client.send_pointer_event(240, 136)  # Center of 480x272 screen

    # Check for response
    data = client.check_for_data(timeout=1)

    # Disconnect
    client.disconnect()

    print("\n" + "="*60)
    print("CONCLUSION:")
    print("Qt Embedded VNC Server (480x272, RGB565) is limited:")
    print("- Closes connection on FramebufferUpdateRequest")
    print("- Doesn't push updates automatically")
    print("- May need special client or different approach")
    print("="*60)


if __name__ == "__main__":
    test_qt_vnc()