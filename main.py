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
import cv2  # <--- for timelapse creation
import numpy as np
import subprocess

# === SETTINGS ===
SAVE_DIR = r"D:\autoscreenshots"  # Change this path
HOTKEY = "ctrl+shift+alt+s"
INTERVAL = 10  # seconds
JPEG_QUALITY = 20  # lower = more compression (0–100)
DIFFERENCE_THRESHOLD = 10  # how different the new screenshot must be (1–100 scale)
FPS = 30  # frames per second for timelapse video

os.makedirs(SAVE_DIR, exist_ok=True)

last_screenshot_hash = None
stop_event = threading.Event()


# === Utility functions ===

def get_today_dir():
    """Return today's date folder path and ensure it exists."""
    today_folder = os.path.join(SAVE_DIR, datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(today_folder, exist_ok=True)
    return today_folder


def get_image_hash(image):
    """Create a hash of the image for quick comparison."""
    buf = BytesIO()
    image.save(buf, format="JPEG", quality=30)
    return hashlib.md5(buf.getvalue()).hexdigest()


def images_are_similar(img1, img2, threshold=DIFFERENCE_THRESHOLD):
    """Return True if two images are visually similar."""
    diff = ImageChops.difference(img1, img2)
    diff_hist = diff.convert("L").histogram()
    total_pixels = sum(diff_hist)
    avg_diff = sum(i * diff_hist[i] for i in range(256)) / total_pixels
    return avg_diff < threshold


# === Screenshot Handling ===

def take_screenshot():
    """Take and save screenshot if it’s different enough from the last one."""
    global last_screenshot_hash

    screenshot = pyautogui.screenshot().convert("RGB")

    # Compare to last screenshot
    current_hash = get_image_hash(screenshot)
    if current_hash == last_screenshot_hash:
        print("[=] Skipped identical screenshot.")
        return
    last_screenshot_hash = current_hash

    today_dir = get_today_dir()
    timestamp = datetime.now().strftime("%H%M%S")
    filename = os.path.join(today_dir, f"screenshot_{timestamp}.jpg")
    screenshot.save(filename, "JPEG", quality=JPEG_QUALITY)
    print(f"[+] Saved screenshot: {filename}")


def periodic_screenshots():
    """Take screenshots periodically until stopped."""
    while not stop_event.is_set():
        take_screenshot()
        time.sleep(INTERVAL)


def hotkey_listener():
    """Listen for manual screenshot hotkey."""
    print(f"Press {HOTKEY} to capture a screenshot manually.")
    while not stop_event.is_set():
        keyboard.wait(HOTKEY)
        take_screenshot()


# === Timelapse ===

def make_timelapse(folder_path):
    """Create a timelapse video from screenshots in a given folder."""
    images = sorted([f for f in os.listdir(folder_path) if f.endswith(".jpg")])

    if not images:
        print(f"[!] No screenshots found in {folder_path}")
        return

    first_img = cv2.imread(os.path.join(folder_path, images[0]))
    height, width, _ = first_img.shape

    output_path = os.path.join(
        folder_path,
        f"timelapse_{os.path.basename(folder_path)}.mp4"
    )

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, FPS, (width, height))

    print(f"[•] Creating timelapse for {folder_path} ({len(images)} frames)")
    for img_name in images:
        frame = cv2.imread(os.path.join(folder_path, img_name))
        if frame is not None:
            out.write(frame)

    out.release()
    print(f"[+] Timelapse saved: {output_path}")

def has_timelapse(folder_path):
    """Return True if the folder already has a timelapse video."""
    for f in os.listdir(folder_path):
        if f.lower().endswith(".mp4") and f.startswith("timelapse_"):
            return True
    return False


def auto_make_missing_timelapses():
    """Scan all date folders and create timelapses if missing."""
    for folder_name in os.listdir(SAVE_DIR):
        folder_path = os.path.join(SAVE_DIR, folder_name)

        if not os.path.isdir(folder_path):
            continue

        # skip if timelapse already exists
        if has_timelapse(folder_path):
            continue

        screenshots = [f for f in os.listdir(folder_path) if f.endswith(".jpg")]
        if screenshots:
            print(f"[AUTO] Missing timelapse in {folder_name}, creating...")
            make_timelapse(folder_path)

#====== open folder ========
def open_today_folder():
    """Open today's screenshot folder in File Explorer."""
    today_dir = get_today_dir()
    if os.path.exists(today_dir):
        subprocess.Popen(f'explorer "{today_dir}"')
    else:
        print("[!] No folder for today yet.")

# === Tray & Exit ===

def on_quit(icon, item):
    """Exit the tray app cleanly."""
    stop_event.set()
    icon.stop()
    print("[x] Exiting...")


def setup_tray():
    """Create a system tray icon with options."""
    icon_image = pyautogui.screenshot().resize((64, 64))
    menu = (
        item("Take Screenshot Now", lambda: take_screenshot()),
        item("Make Timelapse", lambda: make_timelapse()),
        item("Open File Location", lambda: open_today_folder()),
        item("Quit", on_quit),
    )
    icon = pystray.Icon("SmartScreenshot", icon_image, "Smart Screenshot Tool", menu)
    icon.run()


# === Main ===

def main():
    print("Smart Screenshot Tool running in background...")
    auto_make_missing_timelapses()
    threading.Thread(target=periodic_screenshots, daemon=True).start()
    threading.Thread(target=hotkey_listener, daemon=True).start()
    setup_tray()


if __name__ == "__main__":
    main()
