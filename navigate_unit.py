"""
Interactive VNC navigation for Keithley unit (192.168.4.82:5900)
Demonstrates screen capture, menu navigation, and interaction
"""

from vnc import VNCClient
import time
import base64
from PIL import Image
import io
import sys


class UnitNavigator:
    """Navigate and interact with unit via VNC"""

    def __init__(self, host: str = "192.168.4.82", port: int = 5900):
        self.client = VNCClient(host, port)
        self.host = host
        self.port = port

    def connect(self) -> bool:
        """Connect to the unit"""
        try:
            if not self.client.connect():
                print("Failed to connect")
                return False
            print(f"[OK] Connected to {self.host}:{self.port}")
            print(f"[OK] Screen size: {self.client.width}x{self.client.height}")
            return True
        except Exception as e:
            print(f"[FAIL] Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from unit"""
        self.client.disconnect()
        print("[OK] Disconnected")

    def _fresh_connection(self):
        """Create a fresh connection (Qt server needs new connection per framebuffer request)"""
        # Always disconnect and reconnect for Qt Embedded Linux VNC servers
        if self.client:
            try:
                self.client.disconnect()
            except:
                pass
        self.client = VNCClient(self.host, self.port)
        self.client.connect()

    def capture_screenshot(self, filename: str = None) -> bytes:
        """Capture and optionally save screenshot"""
        try:
            # Qt server requires fresh connection for each framebuffer request
            self._fresh_connection()
            image_bytes = self.client.screenshot()
            if filename:
                with open(filename, "wb") as f:
                    f.write(image_bytes)
                print(f"[OK] Screenshot saved: {filename}")
            return image_bytes
        except Exception as e:
            print(f"[FAIL] Screenshot error: {e}")
            return None

    def display_screenshot(self) -> Image.Image:
        """Capture and display screenshot info"""
        try:
            # Qt server requires fresh connection for each framebuffer request
            self._fresh_connection()
            image_bytes = self.client.screenshot()
            img = Image.open(io.BytesIO(image_bytes))
            print(f"[OK] Screenshot: {img.width}x{img.height}, format={img.format}")
            return img
        except Exception as e:
            print(f"[FAIL] Display error: {e}")
            return None

    def click(self, x: int, y: int, button: int = 1) -> bool:
        """Click at coordinates"""
        try:
            # Fresh connection for mouse operations
            self._fresh_connection()
            self.client.mouse_click(x, y, button)
            btn_name = {1: "left", 2: "middle", 3: "right"}.get(button, "unknown")
            print(f"[OK] Clicked {btn_name} button at ({x}, {y})")
            time.sleep(0.3)  # Small delay for UI response
            return True
        except Exception as e:
            print(f"[FAIL] Click error: {e}")
            return False

    def move_mouse(self, x: int, y: int) -> bool:
        """Move mouse to coordinates"""
        try:
            # Fresh connection for mouse operations
            self._fresh_connection()
            self.client.mouse_move(x, y)
            print(f"[OK] Mouse moved to ({x}, {y})")
            return True
        except Exception as e:
            print(f"[FAIL] Move error: {e}")
            return False

    def navigate_menu(self, *clicks: tuple):
        """Navigate through menu sequence

        Args:
            clicks: Sequence of (x, y) tuples for menu navigation
        """
        print(f"\n[*] Starting menu navigation ({len(clicks)} steps)...")
        for i, (x, y) in enumerate(clicks, 1):
            print(f"[*] Step {i}/{len(clicks)}: Click ({x}, {y})")
            self.capture_screenshot(f"step_{i:02d}.png")
            self.click(x, y)
            time.sleep(0.5)
        print("[OK] Menu navigation complete\n")


def demo_basic_navigation():
    """Demonstrate basic VNC navigation"""
    print("=" * 60)
    print("Keithley Unit VNC Navigation Demo")
    print("=" * 60)

    nav = UnitNavigator()

    if not nav.connect():
        return

    try:
        # Take initial screenshot
        print("\n[*] Capturing initial screen...")
        image_bytes = nav.capture_screenshot("unit_screen_1_initial.png")
        if image_bytes:
            img = Image.open(io.BytesIO(image_bytes))
            print(f"[OK] Image size: {img.width}x{img.height}")

        # Example: Click on MENU button (varies by unit layout)
        print("\n[*] To navigate this unit:")
        print("[?] Screen size: 480x272 pixels")
        print("[?] Typical click targets:")
        print("    - Back button: (~50, 20)")
        print("    - Menu items: center area")
        print("    - Scroll: right side")

        # Click somewhere and take another screenshot
        print("\n[*] Clicking center of screen...")
        nav.click(240, 136)

        print("\n[*] Taking screenshot after click...")
        nav.capture_screenshot("unit_screen_2_after_click.png")

        print("\n[*] Navigation demo complete!")
        print("[?] Check the saved screenshots:")
        print("    - unit_screen_1_initial.png")
        print("    - unit_screen_2_after_click.png")

    finally:
        nav.disconnect()


def demo_menu_navigation():
    """Demonstrate specific menu navigation sequence"""
    print("=" * 60)
    print("Keithley Unit - Menu Navigation Sequence")
    print("=" * 60)

    nav = UnitNavigator()

    if not nav.connect():
        return

    try:
        # Take initial screenshot to see current state
        print("\n[*] Taking initial screenshot...")
        nav.capture_screenshot("menu_start.png")
        nav.display_screenshot()

        # Example navigation sequence (you'll need to adjust coordinates)
        # This assumes a typical menu layout
        menu_sequence = [
            # Step 1: Click on MENU button
            (240, 30),  # Assuming top center
            # Step 2: Wait and capture
            (None, None),
            # Step 3: Navigate to INTERFACE menu
            (120, 100),
            # Step 4: Wait and capture
            (None, None),
        ]

        print("\n[*] Navigation sequence example")
        print("[?] Adjust these coordinates based on your screenshot:")
        print("    - (240, 30) = Top menu button")
        print("    - (120, 100) = Menu option")

        # Actually demonstrate just a simple click and wait
        print("\n[*] Demonstrating single click (you can extend this)...")
        nav.click(240, 136)  # Click center of screen
        nav.capture_screenshot("menu_after_click.png")

    finally:
        nav.disconnect()


def demo_measurement_workflow():
    """Demonstrate measurement configuration workflow"""
    print("=" * 60)
    print("Keithley Unit - Measurement Workflow")
    print("=" * 60)

    nav = UnitNavigator()

    if not nav.connect():
        return

    try:
        # Take screenshot
        print("\n[1] Capturing current unit state...")
        nav.capture_screenshot("measurement_1_initial.png")
        nav.display_screenshot()

        print("\n[2] Unit information:")
        print(f"    Resolution: {nav.client.width}x{nav.client.height}")
        print(f"    Format: PNG (32-bit RGBA)")

        print("\n[3] Next steps for automated measurement:")
        print("    - Analyze screenshot to find measurement buttons")
        print("    - Click MENU to access measurement types")
        print("    - Select measurement function (Voltage, Current, etc.)")
        print("    - Click READ or MEASURE to get reading")
        print("    - Capture screenshot to see result")

        print("\n[4] Example coordinates (estimate):")
        print("    - Menu button: ~(240, 30) or top corners")
        print("    - Measurement options: Middle area")
        print("    - Read button: Bottom area")

    finally:
        nav.disconnect()


def interactive_mode():
    """Interactive command-line navigation"""
    print("=" * 60)
    print("Keithley Unit - Interactive VNC Control")
    print("=" * 60)

    nav = UnitNavigator()

    if not nav.connect():
        return

    try:
        cmd_count = 0
        while True:
            print("\nCommands:")
            print("  s = Screenshot")
            print("  c = Click (prompts for coordinates)")
            print("  m = Move mouse (prompts for coordinates)")
            print("  d = Demo menu navigation")
            print("  q = Quit")

            cmd = input("\nCommand: ").strip().lower()

            if cmd == 's':
                cmd_count += 1
                nav.capture_screenshot(f"interactive_screenshot_{cmd_count}.png")
                nav.display_screenshot()

            elif cmd == 'c':
                try:
                    x = int(input("X coordinate: "))
                    y = int(input("Y coordinate: "))
                    nav.click(x, y)
                except ValueError:
                    print("[FAIL] Invalid coordinates")

            elif cmd == 'm':
                try:
                    x = int(input("X coordinate: "))
                    y = int(input("Y coordinate: "))
                    nav.move_mouse(x, y)
                except ValueError:
                    print("[FAIL] Invalid coordinates")

            elif cmd == 'd':
                print("\n[*] Running demo menu navigation...")
                nav.navigate_menu(
                    (240, 30),   # Top center (menu button)
                    (120, 100),  # Left option
                    (120, 150),  # Next option
                )

            elif cmd == 'q':
                print("[*] Exiting interactive mode")
                break

            else:
                print("[?] Unknown command")

    finally:
        nav.disconnect()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Navigate Keithley unit via VNC"
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="basic",
        choices=["basic", "menu", "measurement", "interactive"],
        help="Navigation mode (default: basic)"
    )

    args = parser.parse_args()

    if args.mode == "basic":
        demo_basic_navigation()
    elif args.mode == "menu":
        demo_menu_navigation()
    elif args.mode == "measurement":
        demo_measurement_workflow()
    elif args.mode == "interactive":
        interactive_mode()
