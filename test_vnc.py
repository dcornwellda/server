"""
Test VNC screenshot capture using 32-bit RGBA format with INCREMENTAL update requests

This script successfully captures screenshots from Qt Embedded Linux VNC servers
by using INCREMENTAL update requests, which is what TightVNC/RealVNC viewers do.

Key discoveries:
1. Qt Embedded VNC servers disconnect on non-incremental (full) update requests
2. They work fine with incremental update requests
3. The server sends the full screen on the first incremental request
4. Request 32-bit RGBA format from server for better color quality
"""

from vnc import VNCClient
import time

def test_vnc_screenshot():
    """Test VNC screenshot capture using RGB565 format"""

    host = "192.168.4.82"
    port = 5900

    max_retries = 3

    for attempt in range(max_retries):
        try:
            print(f"\nAttempt {attempt + 1}/{max_retries}")
            print(f"Connecting to {host}:{port}...")

            # Create VNC client
            client = VNCClient(host=host, port=port)

            # Connect
            if not client.connect():
                print("Failed to connect")
                continue

            print(f"Connected!")
            print(f"Screen size: {client.width}x{client.height}")

            # Capture screenshot
            print("Capturing screenshot...")
            filename = f"screenshot_{int(time.time())}.png"

            image_bytes = client.screenshot()

            # Save to file
            with open(filename, "wb") as f:
                f.write(image_bytes)

            print(f"Screenshot saved: {filename}")
            print(f"File size: {len(image_bytes):,} bytes")

            # Disconnect
            client.disconnect()
            print("Disconnected")
            print("\nSuccess!")
            break

        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
                time.sleep(2)
            else:
                print("All retries failed")
                break


if __name__ == "__main__":
    print("=" * 60)
    print("VNC Screenshot Test")
    print("=" * 60)
    print("Format: 32-bit RGBA (little-endian)")
    print("Resolution: 480 x 272")
    print("Method: INCREMENTAL update requests")
    print("=" * 60)

    test_vnc_screenshot()
