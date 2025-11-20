"""
Test FastAPI VNC mouse control endpoints
"""

import requests
import json
import time
import subprocess
import sys

def test_mouse_api():
    """Test the VNC mouse control API endpoints"""

    base_url = "http://localhost:8000"

    print("=" * 60)
    print("Testing FastAPI VNC Mouse Control")
    print("=" * 60)

    # Start server in background
    print("\n[*] Starting FastAPI server...")
    server_process = subprocess.Popen([sys.executable, "main.py"],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)

    # Wait for server to start
    time.sleep(3)

    try:
        # Test 1: Connect to VNC
        print("\n[1] Connecting to VNC...")
        response = requests.post(
            f"{base_url}/vnc/connect",
            json={"host": "192.168.4.82", "port": 5900},
            timeout=10
        )
        print(f"    Status: {response.status_code}")
        if response.status_code == 200:
            print(f"    Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"    Error: {response.text}")
            return

        # Test 2: Take initial screenshot
        print("\n[2] Taking initial screenshot...")
        response = requests.post(f"{base_url}/vnc/screenshot", timeout=60)
        print(f"    Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    Format: {data.get('format')}")
            print(f"    Image size: {len(data.get('image', ''))} characters")
        else:
            print(f"    Error: {response.text}")

        # Test 3: Mouse move
        print("\n[3] Moving mouse to (100, 50)...")
        response = requests.post(
            f"{base_url}/vnc/mouse/move",
            json={"x": 100, "y": 50},
            timeout=10
        )
        print(f"    Status: {response.status_code}")
        if response.status_code == 200:
            print(f"    Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"    Error: {response.text}")

        # Test 4: Mouse click at specific position
        print("\n[4] Clicking at (240, 136)...")
        response = requests.post(
            f"{base_url}/vnc/mouse/click",
            json={"x": 240, "y": 136, "button": 1},
            timeout=10
        )
        print(f"    Status: {response.status_code}")
        if response.status_code == 200:
            print(f"    Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"    Error: {response.text}")

        # Test 5: Take screenshot after click
        print("\n[5] Taking screenshot after click...")
        response = requests.post(f"{base_url}/vnc/screenshot", timeout=60)
        print(f"    Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    Format: {data.get('format')}")
            print(f"    Image size: {len(data.get('image', ''))} characters")

            # Save the screenshot
            import base64
            image_bytes = base64.b64decode(data['image'])
            with open("mouse_test_screenshot.png", "wb") as f:
                f.write(image_bytes)
            print(f"    Saved to: mouse_test_screenshot.png")
        else:
            print(f"    Error: {response.text}")

        # Test 6: Click Back button (if there's one)
        print("\n[6] Clicking Back button area (50, 20)...")
        response = requests.post(
            f"{base_url}/vnc/mouse/click",
            json={"x": 50, "y": 20, "button": 1},
            timeout=10
        )
        print(f"    Status: {response.status_code}")
        if response.status_code == 200:
            print(f"    Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"    Error: {response.text}")

        # Test 7: Final screenshot
        print("\n[7] Taking final screenshot...")
        response = requests.post(f"{base_url}/vnc/screenshot/raw", timeout=60)
        print(f"    Status: {response.status_code}")
        print(f"    Content-Type: {response.headers.get('content-type')}")
        if response.status_code == 200:
            print(f"    Image size: {len(response.content)} bytes")
            with open("mouse_test_final.png", "wb") as f:
                f.write(response.content)
            print(f"    Saved to: mouse_test_final.png")
        else:
            print(f"    Error: {response.text}")

        # Test 8: Disconnect
        print("\n[8] Disconnecting...")
        response = requests.post(f"{base_url}/vnc/disconnect", timeout=5)
        print(f"    Status: {response.status_code}")
        print(f"    Response: {json.dumps(response.json(), indent=2)}")

        print("\n" + "=" * 60)
        print("Mouse control tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[!] Error: {type(e).__name__}: {e}")

    finally:
        print("\n[*] Shutting down server...")
        server_process.terminate()
        server_process.wait(timeout=5)
        print("[*] Server stopped")


if __name__ == "__main__":
    test_mouse_api()
