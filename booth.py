import threading
import time
from signal import pause
from gpiozero import Button
# Import the functions from your original script
from adjust_brightness_print import capture_photo, process_and_print

# Configuration
BUTTON_PIN = 24  
DEBOUNCE_TIME = 0.1  # 100ms is standard for a momentary switch
IS_PROCESSING = False

def run_photobooth_sequence():
    global IS_PROCESSING
    
    # This check now safely runs inside our background thread
    if IS_PROCESSING:
        print("[!] Photo booth is busy, ignoring trigger.")
        return
        
    IS_PROCESSING = True
    print("\n[!] Photobooth triggered!")
    
    try:
        raw_file = capture_photo(wait_time=1.5)
        
        if raw_file:
            final_file = process_and_print(raw_file, brightness=2.5, contrast=0.6)
            if final_file:
                print(f"[+] Sequence complete! Printed and saved to {final_file}")
                
    except Exception as e:
        print(f"[-] Error running photobooth sequence: {e}")
        
    finally:
        print("[+] Ready for next trigger.")
        IS_PROCESSING = False

def button_pressed_callback():
    """
    Spawns the heavy photobooth sequence in a separate thread.
    This returns instantly, keeping the GPIO listener responsive.
    """
    threading.Thread(target=run_photobooth_sequence, daemon=True).start()

# Setup the button
button = Button(BUTTON_PIN, pull_up=True, bounce_time=DEBOUNCE_TIME)

# Bind the quick wrapper function, NOT the heavy blocking function
button.when_pressed = button_pressed_callback

print(f"[+] Switch listener active on GPIO {BUTTON_PIN}.")
print("[+] Standing by... Press Ctrl+C to exit.")

pause()