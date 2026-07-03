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

def capture_photo(wait_time):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    raw_path = os.path.join(SAVE_DIR, f"raw_{timestamp}.jpg")
    
    # Initialize the PWM LED control
    led = PWMLED(LED_PIN)
    
    print("[+] Signaling countdown: Flashing LED 3 times at low intensity...")
    for _ in range(3):
        led.value = 0.2  # 20% brightness
        time.sleep(0.3)
        led.value = 0.0  # Off
        time.sleep(0.3)
        
    print("[+] Setting LED to high intensity for the photo...")
    led.value = 1.0  # 100% brightness
    
    print(f"[+] Initializing camera (Wait time: {wait_time}s)...")
    try:
        with picamera.PiCamera() as camera:
            # Using 1024x768 (binned mode) for better light sensitivity
            camera.resolution = (1024, 768)        
            camera.start_preview()
            
            # The camera uses this sleep time to auto-adjust exposure to the 100% brightness level
            time.sleep(wait_time) 
            
            camera.capture(raw_path)
            print(f"[+] Photo captured: {raw_path}")
    finally:
        # Turn off the LED and clean up the GPIO pin even if the camera fails
        led.value = 0.0
        led.close()
        
    return raw_path

def process_and_print(input_file, brightness):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    processed_path = os.path.join(SAVE_DIR, f"print_{timestamp}.jpg")

    print(f"[+] Applying brightness ({brightness})")
    img = Image.open(input_file)
    
    # Simple brightness adjustment
    enhancer = ImageEnhance.Brightness(img)
    img_enhanced = enhancer.enhance(brightness)
    
    img_enhanced.save(processed_path, quality=90)

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

if __name__ == "__main__":
    main()