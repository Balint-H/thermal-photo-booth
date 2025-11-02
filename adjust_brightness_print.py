"""
Usage:
    python3 thermal_print.py image.png 1.2
    python3 thermal_print.py photo 1.2   # take photo via raspistill

Brightness example:
    1.2 = 20% brighter
    0.8 = darker
"""

import sys
import subprocess
from PIL import Image, ImageEnhance

OUTPUT_FILE = "processed_thermal.png"
CAM_CAPTURE_FILE = "camera_capture.jpg"
TEMP_FILE = "temp.png"

def capture_photo():
    print("[+] Capturing photo with raspistill...")

    cmd = [
        "raspistill",
        "-o", CAM_CAPTURE_FILE,
        "-w", "1280",
        "-h", "720",
        "-t", "1000"  # 1s capture time
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[+] Saved camera image to {CAM_CAPTURE_FILE}")
    return CAM_CAPTURE_FILE


def process_and_print(input_file, brightness):
    print(f"Loading {input_file}")
    img = Image.open(input_file).convert("RGB")
    print(f"Applying brightness = {brightness}")
    img = ImageEnhance.Brightness(img).enhance(brightness)
    
    print(f"Saving temporary PIL-processed file as {TEMP_FILE}...")
    # Save the processed image from PIL to a temporary file
    img_enhanced.save(TEMP_FILE, "PNG")
    
    print(f"Stripping metadata with ImageMagick...")
    cmd = [
        "convert",
        TEMP_FILE,
        "-strip",  
        OUTPUT_FILE
    ]
    
    img.save(OUTPUT_FILE)
    print(f"Saved processed image as {OUTPUT_FILE}")
    subprocess.run(["lp", OUTPUT_FILE], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Printed submitted")


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 thermal_print.py image.png brightness")
        print("  python3 thermal_print.py photo brightness")
        sys.exit(1)

    source = sys.argv[1]
    brightness = float(sys.argv[2])

    if source.lower() == "photo":
        input_file = capture_photo()
    else:
        input_file = source

    process_and_print(input_file, brightness)


if __name__ == "__main__":
    main()
