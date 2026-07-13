import argparse
import time
import os
import cups
from PIL import Image, ImageEnhance
import picamera
from gpiozero import PWMLED  # Added for MOSFET control

# Configuration
SAVE_DIR = "print_history"
LED_PIN = 18  # GPIO 18 (Physical Pin 12)

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def capture_photo(wait_time, small=False, speed_factor=1.):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    raw_path = os.path.join(SAVE_DIR, f"raw_{timestamp}.jpg")
    
    # Initialize the PWM LED control
    led = PWMLED(LED_PIN)
    
    print("[+] Signaling countdown: Flashing LED 3 times at low intensity...")
    for _ in range(3):
        led.value = 0.2  # 20% brightness
        time.sleep(0.4/speed_factor)
        led.value = 0.0  # Off
        time.sleep(0.8/speed_factor)
        
    print("[+] Setting LED to high intensity for the photo...")
    led.value = 1.0  # 100% brightness
    
    print(f"[+] Initializing camera (Wait time: {wait_time}s)...")
    try:
        with picamera.PiCamera() as camera:
            # Using 1024x768 (binned mode) for better light sensitivity
            camera.resolution = (768, 576) if not small else (576, 432)    
            #camera.start_preview()
            
            # The camera uses this sleep time to auto-adjust exposure to the 100% brightness level
            time.sleep(wait_time/speed_factor) 
            
            camera.capture(raw_path)
            print(f"[+] Photo captured: {raw_path}")
    finally:
        # Turn off the LED and clean up the GPIO pin even if the camera fails
        led.value = 0.0
        led.close()
        
    return raw_path


def capture_three_strip(wait_time, header_path="./header2.png", spacer1_path="./spacer1.png", spacer2_path="./spacer2.png", footer_path="./footer3.png", **kwargs):
    """
    Captures 3 photos and stacks them vertically mixed with custom graphic assets:
    [Header] -> [Photo 1] -> [Spacer 1] -> [Photo 2] -> [Spacer 2] -> [Photo 3] -> [Footer]
    """
    print("\n[+] Starting asset-backed photo strip sequence...")
    captured_files = []
    
    # 1. Capture the 3 photos
    for i in range(3):
        print(f"\n--- Preparing Photo {i+1} of 3 ---")
        img_path = capture_photo(wait_time, small=True, **kwargs)
        captured_files.append(img_path)
        if i < 2:
            print("[+] Get ready for the next shot...")
            time.sleep(1.5)

    print("\n[+] Compiling graphical strip layers...")
    
    # 2. Open camera images
    photos = [Image.open(f) for f in captured_files]
    photo_w, photo_h = photos[0].size
    
    # Helper to safely open graphic assets if provided
    def open_asset(path, label):
        if path and os.path.exists(path):
            return Image.open(path)
        if path:
            print(f"[-] Warning: {label} path provided but file not found. Skipping.")
        return None

    header = open_asset(header_path, "Header")
    spacer1 = open_asset(spacer1_path, "Spacer 1")
    spacer2 = open_asset(spacer2_path, "Spacer 2")
    footer = open_asset(footer_path, "Footer")

    # 3. Dynamic height calculation based on available assets
    h_header = header.size[1] if header else 0
    h_spacer1 = spacer1.size[1] if spacer1 else 0
    h_spacer2 = spacer2.size[1] if spacer2 else 0
    h_footer = footer.size[1] if footer else 0
    
    print(f"{photo_w}")
    total_width = photo_w
    total_height = (photo_h * 3) + h_header + h_spacer1 + h_spacer2 + h_footer

    # Create canvas
    strip_img = Image.new("RGB", (total_width, total_height), "white")
    
    # 4. Sequential assembly line down the canvas (tracking Y coordinate)
    current_y = 0
    
    if header:
        strip_img.paste(header, (0, current_y))
        current_y += h_header
        
    strip_img.paste(photos[0], (0, current_y))
    current_y += photo_h
    
    if spacer1:
        strip_img.paste(spacer1, (0, current_y))
        current_y += h_spacer1
        
    strip_img.paste(photos[1], (0, current_y))
    current_y += photo_h
    
    if spacer2:
        strip_img.paste(spacer2, (0, current_y))
        current_y += h_spacer2
        
    strip_img.paste(photos[2], (0, current_y))
    current_y += photo_h
    
    if footer:
        strip_img.paste(footer, (0, current_y))

    # Save the composite strip
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    strip_path = os.path.join(SAVE_DIR, f"raw_strip_{timestamp}.jpg")
    strip_img.save(strip_path, quality=90)
    
    # Cleanup file handles
    for img in photos:
        img.close()
    for asset in [header, spacer1, spacer2, footer]:
        if asset:
            asset.close()
        
    print(f"[+] Photo strip successfully created: {strip_path}")
    return strip_path


def process_and_print(input_file, brightness, contrast=0.8):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    processed_path = os.path.join(SAVE_DIR, f"print_{timestamp}.jpg")

    print(f"[+] Applying brightness ({brightness})")
    img = Image.open(input_file)
    
    # Simple brightness adjustment
    enhancer1 = ImageEnhance.Contrast(img)
    img_enhanced = enhancer1.enhance(contrast)
    enhancer = ImageEnhance.Brightness(img_enhanced)
    img_enhanced = enhancer.enhance(brightness)
    
    img_enhanced.save(processed_path, quality=80)
    # reset_printer_via_cups()
    # Print via pycups
    conn = cups.Connection()
    printers = conn.getPrinters()
    
    if not printers:
        print("[-] Error: No printers found.")
        return None

    # Use the ZJ-80 or first available printer
    printer_name = "ZJ-80" if "ZJ-80" in printers else list(printers.keys())[0]
    
    print(f"[+] Sending to printer: {printer_name}")
    conn.printFile(printer_name, processed_path, f"Job_{timestamp}", {})
    
    return processed_path

def main():
    parser = argparse.ArgumentParser(description="Thermal Printer Photo Booth")
    
    # Positional argument: 'photo' or a file path
    parser.add_argument('source', type=str, 
                        help="Set to 'photo' to capture, or provide a path to an existing .jpg")
    
    # Optional arguments
    parser.add_argument('--brightness', type=float, default=1.0, 
                        help="Brightness multiplier (e.g., 1.5 to brighten). Default is 1.0")
    
    parser.add_argument('--wait', type=float, default=2.0, 
                        help="Seconds to wait for camera sensor to adjust (warm-up). Default is 2.0")

    args = parser.parse_args()

    try:
        if args.source.lower() == "photo":
            input_file = capture_photo(args.wait)
        else:
            input_file = args.source

        if not os.path.exists(input_file):
            print(f"[-] Error: File {input_file} not found.")
            return

        final_file = process_and_print(input_file, args.brightness)
        if final_file:
            print(f"[+] Success! File stored at {final_file}")
        
    except Exception as e:
        print(f"[-] An error occurred: {e}")


def reset_printer_via_cups():
    """
    Clears the printer buffer using native CUPS raw pipelines.
    Bypasses the driver filter completely. Does NOT require sudo.
    """
    print("[*] Sending native CUPS raw hardware flush...")
    try:
        conn = cups.Connection()
        printers = conn.getPrinters()
        printer_name = "ZJ-80" if "ZJ-80" in printers else list(printers.keys())[0]
        
        # 1. Generate the exact same Null-Flood + Kill Switch bytes
        raw_payload = b"\x00" * 3000 + b"\x1b\x40"
        
        # 2. Write it to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(raw_payload)
            temp_path = temp_file.name
            
        # 3. Force CUPS to send it raw (bypassing rastertozj filter)
        conn.printFile(
            printer_name, 
            temp_path, 
            "Buffer_Purge_Job", 
            {"document-format": "application/vnd.cups-raw"}
        )
        
        # 4. Clean up the temp file
        os.unlink(temp_path)
        time.sleep(0.5)  # Give the printer firmware a split second to reboot
        print("[+] Hardware reset complete via CUPS.")
        
    except Exception as e:
        print(f"[-] CUPS raw flush failed: {e}")

if __name__ == "__main__":
    main()
