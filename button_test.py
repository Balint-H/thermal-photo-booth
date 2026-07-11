
# button_test.py
import time
from signal import pause
from gpiozero import Button

BUTTON_PIN = 24
DEBOUNCE_TIME = 0.1  # Start at 100ms

press_count = 0

def on_press():
    global press_count
    press_count += 1
    print(f"[➔] PRESSED!  Total count: {press_count}")

def on_release():
    print("[  ] RELEASED")

button = Button(BUTTON_PIN, pull_up=True, bounce_time=DEBOUNCE_TIME)
button.when_pressed = on_press
button.when_released = on_release

print(f"Testing button on GPIO {BUTTON_PIN}. Press Ctrl+C to exit.")
pause()