"""Analyze and enhance VNC screenshots"""

from PIL import Image
import numpy as np
import glob
import os

def analyze_screenshot(filename):
    """Analyze a VNC screenshot"""
    print(f"\nAnalyzing: {filename}")
    print("-" * 50)

    img = Image.open(filename)

    # Basic info
    print(f"Format: {img.format}")
    print(f"Mode: {img.mode}")
    print(f"Size: {img.width} x {img.height} pixels")
    print(f"File size: {os.path.getsize(filename):,} bytes")

    # Check if it's low quality
    if img.mode == 'P':
        print("Image is in palette mode (indexed color)")
        colors = len(img.getpalette()) // 3 if img.getpalette() else 0
        print(f"Number of colors: {colors}")

    # Convert to numpy for analysis
    arr = np.array(img)
    print(f"Array shape: {arr.shape}")
    print(f"Data type: {arr.dtype}")
    print(f"Unique colors: {len(np.unique(arr.reshape(-1, arr.shape[-1]), axis=0))}")

    return img


def enhance_screenshot(img, filename_base):
    """Enhance and save in multiple formats"""

    # 1. Save as high-quality PNG
    high_quality_png = f"{filename_base}_highquality.png"
    img.save(high_quality_png, 'PNG', optimize=False, compress_level=0)
    print(f"\nHigh-quality PNG saved: {high_quality_png}")
    print(f"  Size: {os.path.getsize(high_quality_png):,} bytes")

    # 2. Scale up 2x with different algorithms
    img_2x_nearest = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
    img_2x_linear = img.resize((img.width * 2, img.height * 2), Image.BILINEAR)
    img_2x_cubic = img.resize((img.width * 2, img.height * 2), Image.BICUBIC)

    img_2x_nearest.save(f"{filename_base}_2x_nearest.png")
    print(f"2x nearest neighbor saved: {filename_base}_2x_nearest.png")

    img_2x_linear.save(f"{filename_base}_2x_bilinear.png")
    print(f"2x bilinear saved: {filename_base}_2x_bilinear.png")

    img_2x_cubic.save(f"{filename_base}_2x_bicubic.png")
    print(f"2x bicubic saved: {filename_base}_2x_bicubic.png")

    # 3. Save as BMP (uncompressed)
    bmp_file = f"{filename_base}.bmp"
    img.save(bmp_file, 'BMP')
    print(f"BMP saved: {bmp_file}")
    print(f"  Size: {os.path.getsize(bmp_file):,} bytes")

    # 4. Save as high-quality JPEG
    jpg_file = f"{filename_base}_q95.jpg"
    img.save(jpg_file, 'JPEG', quality=95, subsampling=0)
    print(f"High-quality JPEG saved: {jpg_file}")
    print(f"  Size: {os.path.getsize(jpg_file):,} bytes")


def check_rgb565_conversion():
    """Check if RGB565 conversion is correct"""
    print("\n" + "="*60)
    print("RGB565 Conversion Check:")
    print("="*60)

    # Test values
    test_values = [
        (0x0000, (0, 0, 0)),      # Black
        (0xFFFF, (255, 255, 255)), # White
        (0xF800, (255, 0, 0)),     # Red
        (0x07E0, (0, 255, 0)),     # Green
        (0x001F, (0, 0, 255)),     # Blue
    ]

    for rgb565, expected in test_values:
        r = ((rgb565 >> 11) & 0x1F) * 255 // 31
        g = ((rgb565 >> 5) & 0x3F) * 255 // 63
        b = (rgb565 & 0x1F) * 255 // 31
        print(f"RGB565: 0x{rgb565:04X} -> RGB: ({r}, {g}, {b}) - Expected: {expected}")


def main():
    # Find most recent screenshot
    screenshots = glob.glob("vnc_screenshot_*.png")
    if not screenshots:
        print("No VNC screenshots found!")
        return

    # Sort by modification time and get the latest
    latest = max(screenshots, key=os.path.getmtime)

    # Analyze
    img = analyze_screenshot(latest)

    # Enhance
    filename_base = latest.replace('.png', '')
    enhance_screenshot(img, filename_base)

    # Check conversion
    check_rgb565_conversion()

    print("\n" + "="*60)
    print("RESOLUTION NOTES:")
    print("="*60)
    print("The VNC server reports 480x272 pixels as its native resolution.")
    print("This is typical for embedded displays (like industrial HMIs).")
    print("The low resolution is from the device, not a capture issue.")
    print("\nTo get better quality:")
    print("1. Use the 2x scaled versions for viewing")
    print("2. The BMP file is uncompressed (largest but highest fidelity)")
    print("3. The device itself would need to support higher resolution")


if __name__ == "__main__":
    main()