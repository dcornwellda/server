"""Test incremental framebuffer updates"""

import socket
import struct
import time

def test_incremental():
    host = "192.168.4.82"
    port = 5900

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        # Connect
        sock.connect((host, port))
        print(f"Connected to {host}:{port}")

        # Handshake
        version = sock.recv(12)
        print(f"Server: {version.decode('ascii').strip()}")
        sock.send(version)

        # Auth
        auth = struct.unpack('>I', sock.recv(4))[0]
        if auth != 1:
            print(f"Auth failed: {auth}")
            return

        # ClientInit
        sock.send(b'\x01')

        # ServerInit
        server_init = sock.recv(1024)
        width = struct.unpack('>H', server_init[0:2])[0]
        height = struct.unpack('>H', server_init[2:4])[0]
        print(f"Display: {width}x{height}")

        print("\nTrying different update request types...")

        # Try incremental update (might work better)
        print("1. Sending incremental update request...")
        # Type=3, incremental=1 (not 0), x=0, y=0, w=width, h=height
        update_req = struct.pack('>BBHHHH', 3, 1, 0, 0, width, height)
        sock.send(update_req)

        # Wait for response
        sock.settimeout(2)
        try:
            data = sock.recv(1024)
            print(f"   Received {len(data)} bytes")
        except socket.timeout:
            print("   No response (timeout)")
        except:
            print("   Connection closed by server")

        # Try small region update
        print("2. Sending small region update request...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.recv(12)  # version
        sock.send(b'RFB 003.003\n')
        sock.recv(4)  # auth
        sock.send(b'\x01')  # ClientInit
        server_init = sock.recv(1024)

        # Request just a 10x10 region
        update_req = struct.pack('>BBHHHH', 3, 0, 0, 0, 10, 10)
        sock.send(update_req)

        sock.settimeout(2)
        try:
            data = sock.recv(1024)
            print(f"   Received {len(data)} bytes")
        except socket.timeout:
            print("   No response (timeout)")
        except:
            print("   Connection closed by server")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    test_incremental()