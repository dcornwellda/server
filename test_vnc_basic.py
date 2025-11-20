"""Ultra-basic VNC connectivity test"""
import socket
import time

host = "192.168.4.82"
port = 5900  # VNC display 0

print(f"Testing raw socket connection to {host}:{port}...")

try:
    # First test raw TCP connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    result = sock.connect_ex((host, port))

    if result == 0:
        print("[OK] TCP connection successful!")

        # Try to read VNC version string (should start with "RFB")
        try:
            data = sock.recv(12)
            if data.startswith(b'RFB'):
                version = data.decode('ascii').strip()
                print(f"[OK] VNC server responded with: {version}")
            else:
                print(f"[?] Received unexpected data: {data}")
        except Exception as e:
            print(f"[FAIL] Could not read VNC handshake: {e}")

        sock.close()
    else:
        print(f"[FAIL] TCP connection failed with error code: {result}")

except Exception as e:
    print(f"[FAIL] Connection test failed: {e}")

print("\n" + "="*50)
print("Now testing with vncdotool...")
print("="*50 + "\n")

try:
    from vncdotool import api

    # Try connecting with password if needed
    passwords = [None, "", "password", "admin"]

    for pwd in passwords:
        try:
            pwd_str = f" with password '{pwd}'" if pwd else " without password"
            print(f"Trying to connect{pwd_str}...")

            if pwd:
                client = api.connect(f"{host}:0", password=pwd, timeout=5)
            else:
                client = api.connect(f"{host}:0", timeout=5)

            print(f"[OK] Connected successfully{pwd_str}!")

            # Just disconnect, don't try to access screen yet
            client.disconnect()
            print("[OK] Disconnected cleanly")
            break

        except Exception as e:
            error_msg = str(e)
            if "password" in error_msg.lower() or "auth" in error_msg.lower():
                print(f"[FAIL] Authentication failed{pwd_str}")
            elif "timeout" in error_msg.lower():
                print(f"[FAIL] Connection timed out{pwd_str}")
            else:
                print(f"[FAIL] Connection failed{pwd_str}: {error_msg}")

except ImportError:
    print("[FAIL] vncdotool not installed")
except Exception as e:
    print(f"[FAIL] Unexpected error: {e}")
    import traceback
    traceback.print_exc()