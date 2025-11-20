"""Analyze the partial data we're receiving"""

import numpy as np
from PIL import Image

# Load the partial data
with open("vnc_partial_data.bin", "rb") as f:
    data = f.read()

print(f"Total data: {len(data)} bytes")

# Skip header (16 bytes)
pixel_data = data[16:]
print(f"Pixel data: {len(pixel_data)} bytes")

width = 480
height = 272
expected_16bit = width * height * 2  # 261,120
expected_8bit = width * height  # 130,560

print(f"\nExpected for full screen:")
print(f"  16-bit: {expected_16bit} bytes")
print(f"  8-bit: {expected_8bit} bytes")
print(f"  We have: {len(pixel_data)} bytes")

# Try different interpretations
images = {}

# 1. Half screen at 16bpp (top half)
if len(pixel_data) >= (width * (height // 2) * 2):
    half_height = height // 2
    pixels = np.frombuffer(pixel_data[:width * half_height * 2], dtype='<u2').reshape((half_height, width))
    r = ((pixels >> 11) & 0x1F) * 255 // 31
    g = ((pixels >> 5) & 0x3F) * 255 // 63
    b = (pixels & 0x1F) * 255 // 31
    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
    img = Image.fromarray(rgb)
    img.save("vnc_half_screen_16bit_le.png")
    print("Saved: vnc_half_screen_16bit_le.png (top half, little-endian)")

    # Try big-endian too
    pixels = np.frombuffer(pixel_data[:width * half_height * 2], dtype='>u2').reshape((half_height, width))
    r = ((pixels >> 11) & 0x1F) * 255 // 31
    g = ((pixels >> 5) & 0x3F) * 255 // 63
    b = (pixels & 0x1F) * 255 // 31
    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
    img = Image.fromarray(rgb)
    img.save("vnc_half_screen_16bit_be.png")
    print("Saved: vnc_half_screen_16bit_be.png (top half, big-endian)")

# 2. Full screen at 8bpp grayscale
if len(pixel_data) >= expected_8bit:
    pixels = np.frombuffer(pixel_data[:expected_8bit], dtype=np.uint8).reshape((height, width))
    img = Image.fromarray(pixels, mode='L')
    img.save("vnc_full_screen_8bit_gray.png")
    print("Saved: vnc_full_screen_8bit_gray.png (full screen, grayscale)")

# 3. Full screen at 8bpp with palette (RGB332)
if len(pixel_data) >= expected_8bit:
    pixels = np.frombuffer(pixel_data[:expected_8bit], dtype=np.uint8).reshape((height, width))
    # RGB332: RRRGGGBB
    r = ((pixels >> 5) & 0x07) * 255 // 7
    g = ((pixels >> 2) & 0x07) * 255 // 7
    b = (pixels & 0x03) * 255 // 3
    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
    img = Image.fromarray(rgb)
    img.save("vnc_full_screen_8bit_rgb332.png")
    print("Saved: vnc_full_screen_8bit_rgb332.png (full screen, RGB332)")

# 4. Full screen at 8bpp with palette (RGB222) - as RealVNC mentioned
if len(pixel_data) >= expected_8bit:
    pixels = np.frombuffer(pixel_data[:expected_8bit], dtype=np.uint8).reshape((height, width))
    # RGB222: 00RRGGBB
    r = ((pixels >> 4) & 0x03) * 85  # 0-3 -> 0-255
    g = ((pixels >> 2) & 0x03) * 85
    b = (pixels & 0x03) * 85
    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
    img = Image.fromarray(rgb)
    img.save("vnc_full_screen_8bit_rgb222.png")
    print("Saved: vnc_full_screen_8bit_rgb222.png (full screen, RGB222 - RealVNC format)")

print("\nCheck all saved images to see which looks correct!")