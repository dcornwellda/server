"""Fix color artifacts in VNC screenshots - test different RGB565 conversions"""

import socket
import struct
import time
from PIL import Image
import numpy as np

def capture_with_different_conversions(host="192.168.4.82", port=5900):
    """Capture and try different RGB565 conversion methods"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    try:
        print("Capturing screen data...")

        # Quick connection and capture
        sock.connect((host, port))
        version = sock.recv(12)
        sock.send(version)
        sock.recv(4)  # auth
        sock.send(b'\x01')  # ClientInit

        server_init = sock.recv(1024)
        width = struct.unpack('>H', server_init[0:2])[0]
        height = struct.unpack('>H', server_init[2:4])[0]

        # Send encodings and request
        sock.send(struct.pack('>BBHi', 2, 0, 1, 0))
        sock.send(struct.pack('>BBHHHH', 3, 1, 0, 0, width, height))

        # Read full framebuffer
        total_data = b''
        expected_size = 4 + 12 + (width * height * 2)

        while len(total_data) < expected_size:
            chunk = sock.recv(8192)
            if not chunk:
                break
            total_data += chunk

        sock.close()

        # Extract pixel data
        pixel_data = total_data[16:16 + (width * height * 2)]
        print(f"Got {len(pixel_data)} bytes of pixel data")

        # Try different conversion methods
        conversions = {}

        # Method 1: Big-endian RGB565 (current method)
        pixels = np.frombuffer(pixel_data, dtype='>u2').reshape((height, width))
        r = ((pixels >> 11) & 0x1F) * 255 // 31
        g = ((pixels >> 5) & 0x3F) * 255 // 63
        b = (pixels & 0x1F) * 255 // 31
        rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
        conversions['big_endian_rgb565'] = Image.fromarray(rgb)

        # Method 2: Little-endian RGB565
        pixels = np.frombuffer(pixel_data, dtype='<u2').reshape((height, width))
        r = ((pixels >> 11) & 0x1F) * 255 // 31
        g = ((pixels >> 5) & 0x3F) * 255 // 63
        b = (pixels & 0x1F) * 255 // 31
        rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
        conversions['little_endian_rgb565'] = Image.fromarray(rgb)

        # Method 3: BGR565 (swapped R and B)
        pixels = np.frombuffer(pixel_data, dtype='>u2').reshape((height, width))
        b = ((pixels >> 11) & 0x1F) * 255 // 31  # Blue in high bits
        g = ((pixels >> 5) & 0x3F) * 255 // 63
        r = (pixels & 0x1F) * 255 // 31  # Red in low bits
        rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
        conversions['big_endian_bgr565'] = Image.fromarray(rgb)

        # Method 4: Little-endian BGR565
        pixels = np.frombuffer(pixel_data, dtype='<u2').reshape((height, width))
        b = ((pixels >> 11) & 0x1F) * 255 // 31
        g = ((pixels >> 5) & 0x3F) * 255 // 63
        r = (pixels & 0x1F) * 255 // 31
        rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
        conversions['little_endian_bgr565'] = Image.fromarray(rgb)

        # Method 5: Byte-swapped before conversion
        swapped_data = np.frombuffer(pixel_data, dtype=np.uint8).reshape(-1, 2)
        swapped_data = swapped_data[:, [1, 0]].flatten()  # Swap bytes
        pixels = np.frombuffer(swapped_data, dtype='>u2').reshape((height, width))
        r = ((pixels >> 11) & 0x1F) * 255 // 31
        g = ((pixels >> 5) & 0x3F) * 255 // 63
        b = (pixels & 0x1F) * 255 // 31
        rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
        conversions['byte_swapped'] = Image.fromarray(rgb)

        # Method 6: Different bit shifts for RGB565
        pixels = np.frombuffer(pixel_data, dtype='>u2').reshape((height, width))
        # Try with proper scaling for 5 and 6 bit values
        r = ((pixels >> 11) & 0x1F) << 3  # 5 bits to 8 bits
        g = ((pixels >> 5) & 0x3F) << 2   # 6 bits to 8 bits
        b = (pixels & 0x1F) << 3          # 5 bits to 8 bits
        rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
        conversions['shift_method'] = Image.fromarray(rgb)

        return conversions, width, height

    except Exception as e:
        print(f"Error: {e}")
        return None, 0, 0


def analyze_image_quality(img, name):
    """Analyze an image for quality issues"""
    arr = np.array(img)

    # Check for pure black pixels
    black_pixels = np.all(arr == [0, 0, 0], axis=2).sum()

    # Check for near-black pixels (should be black)
    near_black = np.all(arr < [30, 30, 30], axis=2).sum()

    # Check for color artifacts in dark areas
    dark_mask = np.mean(arr, axis=2) < 50
    dark_pixels = arr[dark_mask]

    if len(dark_pixels) > 0:
        # Standard deviation of colors in dark areas (should be low)
        color_variance = np.std(dark_pixels, axis=0)
    else:
        color_variance = [0, 0, 0]

    # Count unique colors
    unique_colors = len(np.unique(arr.reshape(-1, 3), axis=0))

    print(f"\n{name}:")
    print(f"  Black pixels: {black_pixels:,}")
    print(f"  Near-black pixels: {near_black:,}")
    print(f"  Color variance in dark areas (R,G,B): {color_variance}")
    print(f"  Unique colors: {unique_colors}")

    # Sample some pixels that should be black (text areas)
    # Check top-left corner area (usually has text)
    corner = arr[:50, :100]
    dark_in_corner = corner[np.mean(corner, axis=2) < 100]
    if len(dark_in_corner) > 0:
        avg_dark = np.mean(dark_in_corner, axis=0)
        print(f"  Average 'black' text color (R,G,B): {avg_dark.astype(int)}")

    return color_variance


def main():
    print("Testing different RGB565 conversion methods...")
    print("="*60)

    conversions, width, height = capture_with_different_conversions()

    if conversions is None:
        print("Failed to capture screen")
        return

    print(f"\nScreen size: {width}x{height}")
    print("\nAnalyzing each conversion method:")
    print("-"*60)

    best_method = None
    best_variance = float('inf')

    for name, img in conversions.items():
        # Save each version
        filename = f"vnc_test_{name}.png"
        img.save(filename)
        print(f"\nSaved: {filename}")

        # Analyze quality
        variance = analyze_image_quality(img, name)
        total_variance = sum(variance)

        if total_variance < best_variance:
            best_variance = total_variance
            best_method = name

    print("\n" + "="*60)
    print(f"BEST METHOD: {best_method}")
    print("This has the least color variance in dark areas")
    print("\nCheck the saved images to see which one has:")
    print("1. Pure black text (no color speckles)")
    print("2. Correct colors overall")
    print("3. Clean edges on text")

    # Save the best one
    if best_method:
        best_img = conversions[best_method]
        best_img.save("vnc_screenshot_fixed.png")
        print(f"\nBest version saved as: vnc_screenshot_fixed.png")


if __name__ == "__main__":
    main()