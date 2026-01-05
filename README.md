# 📸 Smart Screenshot Tool

A lightweight Python background tool that **automatically takes screenshots**, **skips duplicates**, and **creates daily timelapse videos** — all while running quietly in the system tray.

Perfect for:

* Productivity tracking
* Study/work session reviews
* Visual logs of long tasks
* Passive screen recording without huge video files

---

## ✨ Features

* 🕒 **Automatic screenshots** at a fixed interval
* ⌨️ **Manual screenshot hotkey**
* 🧠 **Duplicate detection** (skips identical screenshots)
* 🗂️ **Daily folders** (organized by date)
* 🎞️ **Timelapse video generation** (MP4)
* 🔄 **Auto-create missing timelapses**
* 🖥️ **System tray icon** with quick actions
* 📂 **Open today’s screenshot folder instantly**
* 🗜️ **Compressed JPEG storage** to save space

---

## 🛠 Requirements

* Python **3.9+** (recommended)
* Windows (tested on Windows due to tray + explorer usage)

All Python dependencies are listed in `requirements.txt`.

---

## 📦 Installation

1. **Clone the repository**

```bash
git clone https://github.com/deinfant/autoscreenshotter.git
cd autoscreenshotter
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Edit these values at the top of `main.py`:

```python
SAVE_DIR = r"D:\autoscreenshots"  # Where screenshots are stored
HOTKEY = "ctrl+shift+alt+s"       # Manual screenshot hotkey
INTERVAL = 10                    # Screenshot interval (seconds)
JPEG_QUALITY = 20                # Lower = smaller files (0–100)
DIFFERENCE_THRESHOLD = 10        # Sensitivity for image changes
FPS = 30                         # Timelapse video FPS
```

---

## ▶️ Usage

Run the script:

```bash
python main.py
```

Once running:

* The app works **in the background**
* A **system tray icon** appears
* Screenshots are taken automatically
* Press **Ctrl + Shift + Alt + S** to take a screenshot manually

---

## 🧰 System Tray Menu

Right-click the tray icon to:

* 📸 **Take Screenshot Now**
* 🎞️ **Create Timelapse**
* 📂 **Open Today’s Folder**
* ❌ **Quit**

---

## 📁 Folder Structure

```
autoscreenshots/
└── 2026-01-06/
    ├── screenshot_120000.jpg
    ├── screenshot_120010.jpg
    ├── ...
    └── timelapse_2026-01-06.mp4
```

Each day gets its own folder and timelapse.

---

## 🎞️ Timelapse Behavior

* Timelapses are created using **OpenCV**
* One video per day
* Automatically generated if missing when the app starts
* Skipped if already present

---

## 🚨 Notes & Limitations

* This tool **does not record video**, only screenshots
* Designed for **personal use**
* Tray icon uses a screenshot thumbnail (quick & simple)
* Best used on a single-monitor setup (can be extended)

---

## 🧠 Future Ideas (Optional)

* Multi-monitor support
* Config file instead of hardcoded settings
* Pause/resume from tray
* Screenshot activity heatmaps
* Cross-platform tray support

---

## 📜 License

MIT License — feel free to use, modify, and learn from it.

### (vibecoded btw if u care)