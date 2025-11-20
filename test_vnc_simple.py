"""Simple VNC connection test"""
from vncdotool import api
import time

host = "192.168.4.82"
port = 0  # VNC display 0 = port 5900

print(f"Connecting to {host}:{port}...")

try:
    # Connect with a timeout
    client = api.connect(f"{host}:{port}", timeout=10)
    print("Connected successfully!")

    # Force a screen refresh to get initial framebuffer
    print("Requesting screen update...")
    client.refreshScreen()

    # Wait a bit for the framebuffer to arrive
    print("Waiting for framebuffer...")
    time.sleep(3)

    # Try to capture screenshot without accessing screen properties first
    filename = f"vnc_test_{int(time.time())}.png"
    print(f"Attempting to save screenshot to {filename}...")

    try:
        # Use captureScreen instead of screen.save
        client.captureScreen(filename)
        print(f"Screenshot saved to {filename}")
    except Exception as e:
        print(f"Screenshot failed: {e}")
        print("Trying alternative method...")

        # Alternative: try to save the screen buffer directly
        try:
            client.screen.save(filename)
            print(f"Screenshot saved using screen.save to {filename}")
        except Exception as e2:
            print(f"Alternative method also failed: {e2}")

    # Now try to get screen info (might work after refresh)
    try:
        print(f"Screen size: {client.screen.width}x{client.screen.height}")
    except:
        print("Could not get screen dimensions")

    client.disconnect()
    print("Disconnected")

except Exception as e:
    print(f"Connection failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()