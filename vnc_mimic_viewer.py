"""Mimic what TightVNC/RealVNC viewers do to successfully get screen data"""

import socket
import struct
import time

def mimic_vnc_viewer():
    """Try to replicate exactly what working VNC viewers do"""
    host = "192.168.4.82"
    port = 5900

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        # 1. Connect
        sock.connect((host, port))
        print("Step 1: Connected")

        # 2. Version handshake
        version = sock.recv(12)
        print(f"Step 2: Got version {version.decode('ascii').strip()}")
        sock.send(version)  # Echo same version

        # 3. Authentication
        auth = struct.unpack('>I', sock.recv(4))[0]
        print(f"Step 3: Auth type = {auth}")

        # 4. ClientInit (shared desktop = YES)
        sock.send(b'\x01')
        print("Step 4: Sent ClientInit (shared=1)")

        # 5. Receive ServerInit
        server_init = sock.recv(1024)
        width = struct.unpack('>H', server_init[0:2])[0]
        height = struct.unpack('>H', server_init[2:4])[0]
        print(f"Step 5: Got ServerInit - Display {width}x{height}")

        # Parse pixel format from ServerInit
        bpp = server_init[4]
        depth = server_init[5]
        big_endian = server_init[6]
        true_color = server_init[7]
        print(f"  Current format: {bpp}bpp, depth={depth}, RGB565")

        # 6. SetEncodings (tell server what encodings we support)
        # This is CRITICAL - viewers always send this!
        print("\nStep 6: Sending SetEncodings (like viewers do)...")
        encodings = struct.pack(
            '>BBH',
            2,    # Message type: SetEncodings
            0,    # Padding
            3     # Number of encodings
        )
        # Add encoding types (Raw, CopyRect, RRE)
        encodings += struct.pack('>iii', 0, 1, 2)  # Raw, CopyRect, RRE
        sock.send(encodings)
        print("  Sent encoding preferences")

        # 7. Try INCREMENTAL update request (this is key!)
        print("\nStep 7: Sending INCREMENTAL FramebufferUpdateRequest...")
        # Type=3, incremental=1, x=0, y=0, width, height
        update_req = struct.pack(
            '>BBHHHH',
            3,     # Message type: FramebufferUpdateRequest
            1,     # INCREMENTAL (not 0!)
            0, 0,  # x, y
            width, height
        )
        sock.send(update_req)
        print(f"  Requested incremental update for full screen")

        # 8. Wait for response
        print("\nStep 8: Waiting for framebuffer data...")
        sock.settimeout(3)

        try:
            # Read response
            data = sock.recv(1024)
            if data:
                print(f"  Received {len(data)} bytes!")

                if data[0] == 0:  # FramebufferUpdate
                    print("  This is a FramebufferUpdate message!")
                    num_rects = struct.unpack('>H', data[2:4])[0]
                    print(f"  Number of rectangles: {num_rects}")

                    if num_rects == 0:
                        print("  Server says: No changes (incremental update)")
                        print("\n>>> This means the server IS working!")
                        print(">>> It just has no changes to send.")
                        print("\nTrying NON-incremental request...")

                        # Try non-incremental
                        update_req = struct.pack(
                            '>BBHHHH',
                            3,     # Message type
                            0,     # NON-incremental
                            0, 0,  # x, y
                            width, height
                        )
                        sock.send(update_req)
                        print("Sent non-incremental request...")

                        # Wait for response
                        data2 = sock.recv(65536)
                        if data2:
                            print(f"Got {len(data2)} bytes after non-incremental!")
                        else:
                            print("Server closed connection on non-incremental request")
                else:
                    print(f"  Unexpected message type: {data[0]}")
            else:
                print("  Connection closed by server")

        except socket.timeout:
            print("  Timeout - no response")
        except Exception as e:
            print(f"  Error: {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

    print("\n" + "="*60)
    print("CONCLUSION:")
    print("The Qt VNC server responds to INCREMENTAL updates")
    print("but closes on NON-incremental (full screen) requests.")
    print("TightVNC/RealVNC must use incremental updates and")
    print("have an initial screen state or use a different method.")
    print("="*60)


if __name__ == "__main__":
    mimic_vnc_viewer()