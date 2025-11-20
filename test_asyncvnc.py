"""Test VNC connection using asyncvnc library"""

import asyncio
import asyncvnc
from PIL import Image
import numpy as np
import time

async def test_vnc():
    host = "192.168.4.82"
    port = 5900

    print(f"Connecting to {host}:{port} using asyncvnc...")

    try:
        # Connect to VNC server
        async with asyncvnc.connect(
            host=host,
            port=port,
            password=None  # No password needed
        ) as client:
            print(f"Connected successfully!")
            print(f"Server name: {client.desktop_name}")
            print(f"Screen size: {client.width}x{client.height}")
            print(f"Pixel format: {client.pixel_format}")

            # Try to capture screenshot
            print("\nAttempting to capture screenshot...")

            try:
                # Get screen buffer
                pixels = client.screen
                if pixels is not None:
                    print(f"Screen buffer shape: {pixels.shape}")

                    # Convert to PIL Image
                    if len(pixels.shape) == 3:  # RGB array
                        img = Image.fromarray(pixels.astype('uint8'), 'RGB')
                    else:  # Grayscale or other format
                        img = Image.fromarray(pixels.astype('uint8'))

                    filename = f"asyncvnc_screenshot_{int(time.time())}.png"
                    img.save(filename)
                    print(f"[OK] Screenshot saved to {filename}")
                else:
                    print("[INFO] No screen buffer available")

            except Exception as e:
                print(f"Screenshot failed: {e}")

            # Try to get updates
            print("\nWaiting for screen updates...")
            await asyncio.sleep(2)

            # Check if we have new data
            pixels = client.screen
            if pixels is not None:
                print(f"Got screen data: {pixels.shape}")
            else:
                print("No screen data available")

    except AttributeError as e:
        print(f"Attribute Error: {e}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


async def test_with_events():
    """Test with keyboard/mouse events"""
    host = "192.168.4.82"
    port = 5900

    print(f"\n--- Testing with events ---")
    print(f"Connecting to {host}:{port}...")

    try:
        async with asyncvnc.connect(host=host, port=port) as client:
            print("Connected!")

            # Send a key press
            print("Sending key press (space)...")
            await client.keyboard.press(' ')
            await asyncio.sleep(0.5)

            # Move mouse
            print("Moving mouse...")
            await client.mouse.move(240, 136)  # Center of 480x272
            await asyncio.sleep(0.5)

            # Try to get screen after events
            pixels = client.screen
            if pixels is not None:
                print(f"Screen data available: {pixels.shape}")

                # Save it
                img = Image.fromarray(pixels.astype('uint8'))
                filename = f"asyncvnc_after_events_{int(time.time())}.png"
                img.save(filename)
                print(f"Saved to {filename}")
            else:
                print("No screen data after events")

    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Run all tests"""
    await test_vnc()
    await test_with_events()

    print("\n" + "="*60)
    print("SUMMARY:")
    print("asyncvnc library tested with Qt Embedded VNC server")
    print("This library uses async I/O and might handle the server better")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())