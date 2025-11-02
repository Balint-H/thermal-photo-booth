#!/usr/bin/env python3
"""
Usage:
    python3 thermal_print.py myimage.png 1.2
        (brightness 1.2 = 20% brighter; 0.8 = darker)

Output file saved as: processed_thermal.png
"""

import sys
import os
import subprocess
from PIL import Image, ImageEnhance

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 thermal_print.py input.png brightness")
        sys.exit(1)

    input_file = sys.argv[1]
    brightness_value = float(sys.argv[2])
    output_file = "processed_thermal.png"

    print(f"[+] Loading {input_file}")
    img = Image.open(input_file).convert("RGB")

    # Adjust brightness
    print(f"[+] Applying brightness = {brightness_value}")
    img = ImageEnhance.Brightness(img).enhance(brightness_value)

    # Convert to grayscale then to 1-bit with dithering for thermal clarity
    print("[+] Converting to 1-bit thermal mode with dithering")
    img = img.convert("L")  # grayscale
    img = img.convert("1", dither=Image.FLOYDSTEINBERG)

    # Save processed image
    img.save(output_file)
    print(f"[+] Saved corrected file as {output_file}")

    # Print using default printer
    print("[+] Sending to printer...")
    subprocess.run(["lp", output_file], check=True)

    print("[✓] Printed successfully!")

if __name__ == "__main__":
    main()
