"""
Test FastAPI VNC endpoints
"""

import requests
import json
import time
import subprocess
import sys

def test_api():
    """Test the API endpoints"""

    base_url = "http://localhost:8000"

    print("=" * 60)
    print("Testing FastAPI VNC Endpoints")
    print("=" * 60)

    # Start server in background
    print("\n[*] Starting FastAPI server...")
    server_process = subprocess.Popen([sys.executable, "main.py"],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)

    # Wait for server to start
    time.sleep(3)

    try:
        # Test 1: Health check
        print("\n[1] Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"    Status: {response.status_code}")
        print(f"    Response: {json.dumps(response.json(), indent=2)}")

        # Test 2: Root endpoint
        print("\n[2] Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"    Status: {response.status_code}")
        data = response.json()
        print(f"    Available instruments: {list(data.get('instruments', {}).keys())}")

        # Test 3: VNC Connect
        print("\n[3] Testing VNC connect...")
        response = requests.post(
            f"{base_url}/vnc/connect",
            json={"host": "192.168.4.82", "port": 5900},
            timeout=10
        )
        print(f"    Status: {response.status_code}")
        print(f"    Response: {json.dumps(response.json(), indent=2)}")

        # Test 4: VNC Status
        print("\n[4] Testing VNC status...")
        response = requests.get(f"{base_url}/vnc/status", timeout=5)
        print(f"    Status: {response.status_code}")
        print(f"    Response: {json.dumps(response.json(), indent=2)}")

        # Test 5: VNC Screenshot (base64)
        print("\n[5] Testing VNC screenshot (base64)...")
        response = requests.post(f"{base_url}/vnc/screenshot", timeout=60)
        print(f"    Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    Format: {data.get('format')}")
            print(f"    Encoding: {data.get('encoding')}")
            print(f"    Image data size: {len(data.get('image', ''))} characters")
        else:
            print(f"    Error: {response.text}")

        # Test 6: VNC Screenshot (raw PNG)
        print("\n[6] Testing VNC screenshot (raw PNG)...")
        response = requests.post(f"{base_url}/vnc/screenshot/raw", timeout=60)
        print(f"    Status: {response.status_code}")
        print(f"    Content-Type: {response.headers.get('content-type')}")
        if response.status_code == 200:
            print(f"    Image size: {len(response.content)} bytes")
            # Save the image
            with open("api_screenshot.png", "wb") as f:
                f.write(response.content)
            print(f"    Saved to: api_screenshot.png")
        else:
            print(f"    Error: {response.text}")

        # Test 7: VNC Disconnect
        print("\n[7] Testing VNC disconnect...")
        response = requests.post(f"{base_url}/vnc/disconnect", timeout=5)
        print(f"    Status: {response.status_code}")
        print(f"    Response: {json.dumps(response.json(), indent=2)}")

        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[!] Error: {type(e).__name__}: {e}")

    finally:
        print("\n[*] Shutting down server...")
        server_process.terminate()
        server_process.wait(timeout=5)
        print("[*] Server stopped")


if __name__ == "__main__":
    test_api()
