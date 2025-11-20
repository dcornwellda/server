"""Minimal VNC test - just connect and get info without screen updates"""
from vncdotool import api
import time

host = "192.168.4.82"
port = 0  # VNC display 0 = port 5900

print(f"Connecting to {host}:{port}...")

try:
    # Connect with a very short timeout for operations
    client = api.connect(f"{host}:{port}", timeout=5)
    print("Connected successfully!")

    # DON'T request screen updates or try to access screen properties
    # The Qt Embedded VNC server disconnects when we request updates

    # Try to capture without refresh (might have initial framebuffer)
    filename = f"vnc_initial_{int(time.time())}.png"
    print(f"Attempting to capture initial state to {filename}...")

    try:
        # This might work if there's an initial framebuffer
        client.captureScreen(filename)
        print(f"[OK] Screenshot saved to {filename}")
    except Exception as e:
        print(f"[INFO] No initial framebuffer available: {e}")
        print("This is expected with Qt Embedded VNC servers")

    # Clean disconnect
    try:
        client.disconnect()
        print("Disconnected cleanly")
    except:
        print("Server already disconnected")

except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

print("\n" + "="*60)
print("SUMMARY:")
print("The VNC server is a Qt for Embedded Linux VNC Server")
print("Display size: 480x272, Format: RGB565 (16bpp)")
print("Known limitation: Server disconnects on framebuffer update requests")
print("="*60)