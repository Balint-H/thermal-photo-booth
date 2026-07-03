import time
from signal import pause
from gpiozero import Button
# Import the functions from your original script (assumed to be photobooth.py)
from adjust_brightness_print import capture_photo, process_and_print

# Configuration
BUTTON_PIN = 24  # Choose any available GPIO pin (e.g., GPIO 24, physical pin 18)
DEBOUNCE_TIME = 0.3  # 300ms to ignore mechanical contact bounce
IS_PROCESSING = False

def run_photobooth_sequence():
    global IS_PROCESSING
    
    # Debounce/State lock: Ignore triggers if a photo is already being processed
    if IS_PROCESSING:
        print("[!] Photo booth is busy, ignoring trigger.")
        return
        
    IS_PROCESSING = True
    print("\n[!] Photobooth triggered via switch state change!")
    
    try:
        # Call functions from your original script
        # You can customize your default wait time and brightness multipliers here
        raw_file = capture_photo(wait_time=2.0)
        
        if raw_file:
            final_file = process_and_print(raw_file, brightness=1.0)
            if final_file:
                print(f"[+] Sequence complete! Printed and saved to {final_file}")
                
    except Exception as e:
        print(f"[-] Error running photobooth sequence: {e}")
        
    finally:
        # Re-enable the button triggers once everything is finished
        print("[+] Ready for next trigger.")
        IS_PROCESSING = False

# Setup the button
# pull_up=True uses the Pi's internal 50k Ohm resistor to limit current draw to ~66uA when closed.
# Wire one side of your latching switch to BUTTON_PIN, and the other side to a GND pin.
button = Button(BUTTON_PIN, pull_up=True, bounce_time=DEBOUNCE_TIME)

# Assign the exact same function to BOTH actions (rising and falling edges)
button.when_pressed = run_photobooth_sequence
button.when_released = run_photobooth_sequence

print(f"[+] Switch listener active on GPIO {BUTTON_PIN}.")
print("[+] Standing by... Press Ctrl+C to exit.")

# Keep the script running efficiently in the background without burning CPU cycles
pause()