"""Get VNC server info without requesting screenshots (won't hang)"""

import socket
import struct

def get_vnc_info(host="192.168.4.82", port=5900):
    """Connect to VNC and get display info only"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        # Connect
        sock.connect((host, port))
        print(f"[OK] Connected to {host}:{port}")

        # Get protocol version
        version = sock.recv(12).decode('ascii').strip()
        print(f"[OK] Server version: {version}")

        # Send our version
        sock.send(b"RFB 003.003\n")

        # Get auth type
        auth = struct.unpack('>I', sock.recv(4))[0]
        if auth == 1:
            print("[OK] No authentication required")
        else:
            print(f"[FAIL] Authentication type {auth} not supported")
            return

        # Send ClientInit (shared=1)
        sock.send(b'\x01')

        # Receive ServerInit
        server_init = sock.recv(1024)

        # Parse display info
        width = struct.unpack('>H', server_init[0:2])[0]
        height = struct.unpack('>H', server_init[2:4])[0]

        # Parse pixel format
        bpp = server_init[4]
        depth = server_init[5]

        # Parse desktop name
        name_length = struct.unpack('>I', server_init[20:24])[0]
        if len(server_init) >= 24 + name_length:
            desktop_name = server_init[24:24+name_length].decode('ascii', errors='ignore')
        else:
            desktop_name = "Unknown"

        print("\n" + "="*50)
        print("VNC SERVER INFORMATION:")
        print("="*50)
        print(f"Display Size: {width} x {height} pixels")
        print(f"Pixel Format: {bpp} bits per pixel, depth {depth}")
        print(f"Desktop Name: {desktop_name}")
        print("="*50)

        print("\n[WARNING] This server does not support screenshot capture")
        print("It's a Qt Embedded VNC server with limited functionality")

    except Exception as e:
        print(f"[FAIL] Error: {e}")
    finally:
        sock.close()
        print("\n[OK] Connection closed")

if __name__ == "__main__":
    get_vnc_info()