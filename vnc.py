"""
VNC Client for Qt Embedded Linux VNC Server
Direct socket implementation using 32-bit RGBA format with INCREMENTAL update requests
"""

import socket
import struct
import time
from typing import Optional, Tuple
import io
import base64
import numpy as np
from PIL import Image
import sys


class VNCClient:
    """VNC client for Qt Embedded Linux VNC Server"""

    def __init__(self, host: str = "192.168.4.82", port: int = 5900, password: Optional[str] = None):
        """
        Initialize VNC client

        Args:
            host: VNC server hostname or IP
            port: VNC server port (default 5900)
            password: VNC password (if required, currently not used)
        """
        self.host = host
        self.port = port
        self.password = password
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.width = 480
        self.height = 272

    def connect(self) -> bool:
        """
        Connect to VNC server and perform handshake

        Returns:
            True if connection successful
        """
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)

            # Connect
            self.socket.connect((self.host, self.port))

            # VNC Handshake: Version
            version = self.socket.recv(12)
            if not version.startswith(b'RFB'):
                raise ConnectionError("Not a VNC server")
            self.socket.send(version)

            # VNC Handshake: Authentication
            auth_data = self.socket.recv(4)
            auth_type = struct.unpack('>I', auth_data)[0]
            if auth_type != 1:
                raise ConnectionError(f"Authentication type {auth_type} not supported (no password auth)")
            self.socket.send(b'\x01')  # No authentication

            # Get ServerInit
            server_init = self.socket.recv(1024)
            self.width = struct.unpack('>H', server_init[0:2])[0]
            self.height = struct.unpack('>H', server_init[2:4])[0]

            # Set Pixel Format to 32-bit RGBA (little-endian)
            # The server will convert from its native RGB565 to our requested format
            pixel_format = struct.pack(
                '>BBBBHHHBBB',
                32,   # Bits per pixel
                24,   # Depth
                0,    # Big endian flag (0 = little endian)
                1,    # True color flag
                255,  # Red max
                255,  # Green max
                255,  # Blue max
                0,    # Red shift (little-endian: RGBA)
                8,    # Green shift
                16    # Blue shift
            )
            pixel_format += b'\x00\x00\x00'  # Padding

            setpixel_msg = struct.pack('>BBBB', 0, 0, 0, 0) + pixel_format
            self.socket.send(setpixel_msg)

            # Set Encodings - support Raw only
            encodings = struct.pack('>BBHi', 2, 0, 1, 0)  # Raw encoding (type 0)
            self.socket.send(encodings)

            self.connected = True
            return True

        except Exception as e:
            self.connected = False
            raise ConnectionError(f"Failed to connect to VNC server: {str(e)}")

    def disconnect(self):
        """Disconnect from VNC server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        self.socket = None

    def is_connected(self) -> bool:
        """Check if connected to VNC server"""
        return self.connected and self.socket is not None

    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get screen dimensions

        Returns:
            Tuple of (width, height)
        """
        return (self.width, self.height)

    def _capture_frame(self) -> bytes:
        """
        Capture one frame from the VNC server using 32-bit RGBA format

        Returns:
            PNG image as bytes
        """
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected to VNC server")

        try:
            # Send INCREMENTAL update request (CRITICAL!)
            # Qt VNC servers only work with incremental requests, not full updates
            update_req = struct.pack('>BBHHHH', 3, 1, 0, 0, self.width, self.height)
            self.socket.send(update_req)

            # Read the response with 30 second timeout
            self.socket.settimeout(30)
            total_data = b''
            expected_size = 4 + 12 + (self.width * self.height * 4)  # Header + rect header + 32-bit pixels

            while len(total_data) < expected_size:
                chunk = self.socket.recv(65536)
                if not chunk:
                    raise RuntimeError("Connection closed by server")
                total_data += chunk

                # Show progress
                percent = (len(total_data) / expected_size) * 100
                print(f"\rProgress: {percent:.1f}%", end='', file=sys.stderr)

            print(file=sys.stderr)  # New line after progress

            if len(total_data) < expected_size:
                raise RuntimeError(f"Incomplete frame: received {len(total_data)} of {expected_size} bytes")

            # Parse the response
            msg_type = total_data[0]
            if msg_type != 0:  # FramebufferUpdate
                raise RuntimeError(f"Expected FramebufferUpdate (0), got {msg_type}")

            num_rects = struct.unpack('>H', total_data[2:4])[0]
            if num_rects != 1:
                raise RuntimeError(f"Expected 1 rectangle, got {num_rects}")

            # Parse rectangle header
            x = struct.unpack('>H', total_data[4:6])[0]
            y = struct.unpack('>H', total_data[6:8])[0]
            w = struct.unpack('>H', total_data[8:10])[0]
            h = struct.unpack('>H', total_data[10:12])[0]
            encoding = struct.unpack('>i', total_data[12:16])[0]

            if encoding != 0:  # Raw encoding
                raise RuntimeError(f"Unsupported encoding {encoding}")

            # Extract pixel data (32-bit RGBA little-endian)
            pixel_data = total_data[16:16 + (w * h * 4)]

            # Convert RGBA to RGB
            # RGBA little-endian: bytes are R, G, B, A
            rgba = np.frombuffer(pixel_data, dtype=np.uint8).reshape((h, w, 4))
            rgb = rgba[:, :, :3]  # Drop alpha channel

            # Create RGB image
            img = Image.fromarray(rgb)

            # Save to PNG bytes
            output = io.BytesIO()
            img.save(output, format='PNG')
            return output.getvalue()

        except socket.timeout:
            # Connection timed out - likely server issue or connection lost
            self.connected = False
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            raise RuntimeError("Timeout waiting for framebuffer data - connection may have been closed by server")
        except Exception as e:
            # On any other error, try to close the connection
            self.connected = False
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            raise RuntimeError(f"Screenshot capture failed: {str(e)}")

    def screenshot(self, width: Optional[int] = None, height: Optional[int] = None) -> bytes:
        """
        Capture screenshot from VNC server

        Args:
            width: Screen width (optional, auto-detect)
            height: Screen height (optional, auto-detect)

        Returns:
            PNG image as bytes
        """
        # Capture raw frame
        image_bytes = self._capture_frame()

        # If specific dimensions requested, resize if needed
        if width and height and (width != self.width or height != self.height):
            img = Image.open(io.BytesIO(image_bytes))
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            output = io.BytesIO()
            img.save(output, format='PNG')
            return output.getvalue()

        return image_bytes

    def screenshot_base64(self) -> str:
        """
        Capture screenshot and return as base64 string

        Returns:
            Base64 encoded PNG image
        """
        image_bytes = self.screenshot()
        return base64.b64encode(image_bytes).decode('utf-8')

    def mouse_move(self, x: int, y: int):
        """
        Move mouse to absolute position

        Args:
            x: X coordinate
            y: Y coordinate
        """
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected to VNC server")

        try:
            # PointerEvent message: type(1) + button_mask(1) + x(2) + y(2)
            msg = struct.pack('>BBHH', 6, 0, x, y)  # Type 6 = PointerEvent, no buttons pressed
            self.socket.send(msg)
        except Exception as e:
            raise RuntimeError(f"Mouse move failed: {str(e)}")

    def mouse_click(self, x: Optional[int] = None, y: Optional[int] = None, button: int = 1):
        """
        Click mouse button at position

        Args:
            x: X coordinate (None to click at current position)
            y: Y coordinate (None to click at current position)
            button: Mouse button (1=left, 2=middle, 3=right)
        """
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected to VNC server")

        try:
            # Move mouse first if coordinates given
            if x is not None and y is not None:
                self.mouse_move(x, y)

            # Convert button number to bitmask
            button_mask = 1 << (button - 1)

            # Send mouse down
            msg = struct.pack('>BBHH', 6, button_mask, x or 0, y or 0)
            self.socket.send(msg)

            # Small delay
            time.sleep(0.05)

            # Send mouse up
            msg = struct.pack('>BBHH', 6, 0, x or 0, y or 0)
            self.socket.send(msg)

        except Exception as e:
            raise RuntimeError(f"Mouse click failed: {str(e)}")

    def mouse_down(self, button: int = 1):
        """Press mouse button down"""
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected to VNC server")

        try:
            button_mask = 1 << (button - 1)
            msg = struct.pack('>BBHH', 6, button_mask, 0, 0)
            self.socket.send(msg)
        except Exception as e:
            raise RuntimeError(f"Mouse down failed: {str(e)}")

    def mouse_up(self, button: int = 1):
        """Release mouse button"""
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected to VNC server")

        try:
            msg = struct.pack('>BBHH', 6, 0, 0, 0)
            self.socket.send(msg)
        except Exception as e:
            raise RuntimeError(f"Mouse up failed: {str(e)}")

    def key_press(self, key: str):
        """
        Press a key

        Args:
            key: Key to press
        """
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected to VNC server")

        # This is a simplified implementation
        # In a real implementation, you would need to map characters to keysym values
        # For now, we'll just raise NotImplementedError
        raise NotImplementedError("Key press not yet implemented for direct socket VNC client")
