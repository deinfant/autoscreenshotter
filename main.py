import os
import time
import threading
import pyautogui
import keyboard
import hashlib
from datetime import datetime
from PIL import Image, ImageChops
import pystray
from pystray import MenuItem as item
from io import BytesIO
import cv2
import subprocess

# === SETTINGS ===
BASE_DIR = r"D:\autoscreenshots"
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshots")
TIMELAPSE_DIR = os.path.join(BASE_DIR, "timelapses")

HOTKEY = "ctrl+shift+alt+s"
INTERVAL = 10
JPEG_QUALITY = 20
DIFFERENCE_THRESHOLD = 10
FPS = 30

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(TIMELAPSE_DIR, exist_ok=True)

last_screenshot_hash = None
stop_event = threading.Event()

# === Utility functions ===

def get_today_screenshot_dir():
    today = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(SCREENSHOT_DIR, today)
    os.makedirs(path, exist_ok=True)
    return path

def get_today_timelapse_dir():
    today = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(TIMELAPSE_DIR, today)
    os.makedirs(path, exist_ok=True)
    return path

def get_image_hash(image):
    buf = BytesIO()
    image.save(buf, format="JPEG", quality=30)
    return hashlib.md5(buf.getvalue()).hexdigest()

# === Screenshot Handling ===

def take_screenshot():
    global last_screenshot_hash

    screenshot = pyautogui.screenshot().convert("RGB")
    current_hash = get_image_hash(screenshot)

    if current_hash == last_screenshot_hash:
        return

    last_screenshot_hash = current_hash

    folder = get_today_screenshot_dir()
    timestamp = datetime.now().strftime("%H%M%S")
    filename = os.path.join(folder, f"screenshot_{timestamp}.jpg")

    screenshot.save(filename, "JPEG", quality=JPEG_QUALITY)
    print(f"[+] Saved screenshot: {filename}")

def periodic_screenshots():
    while not stop_event.is_set():
        take_screenshot()
        time.sleep(INTERVAL)

def hotkey_listener():
    print(f"Press {HOTKEY} to capture manually.")
    while not stop_event.is_set():
        keyboard.wait(HOTKEY)
        take_screenshot()

# === Timelapse ===

def make_timelapse(date_folder):
    screenshot_folder = os.path.join(SCREENSHOT_DIR, date_folder)
    images = sorted(f for f in os.listdir(screenshot_folder) if f.endswith(".jpg"))
    if not images:
        print(f"[!] No screenshots found for {date_folder}")
        return
    first = cv2.imread(os.path.join(screenshot_folder, images[0]))
    height, width, _ = first.shape
    output_path = os.path.join(
        TIMELAPSE_DIR,
        f"timelapse_{date_folder}.mp4"
    )
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, FPS, (width, height))

    print(f"[•] Creating timelapse for {date_folder} ({len(images)} frames)")
    for img in images:
        frame = cv2.imread(os.path.join(screenshot_folder, img))
        if frame is not None:
            out.write(frame)

    out.release()
    print(f"[+] Timelapse saved: {output_path}")

def auto_make_missing_timelapses():
    today = datetime.now().strftime("%Y-%m-%d")

    for date_folder in os.listdir(SCREENSHOT_DIR):
        if date_folder == today:
            continue  # skip today's screenshots

        screenshot_path = os.path.join(SCREENSHOT_DIR, date_folder)
        if not os.path.isdir(screenshot_path):
            continue

        expected_video = os.path.join(
            TIMELAPSE_DIR, f"timelapse_{date_folder}.mp4"
        )

        if os.path.exists(expected_video):
            continue

        screenshots = [
            f for f in os.listdir(screenshot_path) if f.endswith(".jpg")
        ]
        if screenshots:
            print(f"[AUTO] Missing timelapse for {date_folder}, creating...")
            make_timelapse(date_folder)
            
# === Tray ===

def open_today_folder():
    subprocess.Popen(f'explorer "{get_today_screenshot_dir()}"')

def on_quit(icon, item):
    stop_event.set()
    icon.stop()

def setup_tray():
    icon_image = pyautogui.screenshot().resize((64, 64))
    menu = (
        item("Take Screenshot Now", lambda: take_screenshot()),
        item("Make Today's Timelapse",
             lambda: make_timelapse(datetime.now().strftime("%Y-%m-%d"))),
        item("Open Screenshot Folder", open_today_folder),
        item("Quit", on_quit),
    )
    pystray.Icon("SmartScreenshot", icon_image, "Smart Screenshot Tool", menu).run()

# === Main ===

def main():
    print("Smart Screenshot Tool running...")
    auto_make_missing_timelapses()
    threading.Thread(target=periodic_screenshots, daemon=True).start()
    threading.Thread(target=hotkey_listener, daemon=True).start()
    setup_tray()

if __name__ == "__main__":
    main()
