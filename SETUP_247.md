# PeakCut 24/7 — One-Time Setup

## Files created
- `peakcut_guardian.py` — runs server + tunnel, restarts if they die, saves URL to `peakcut_url.txt`
- `peakcut_startup.bat` — runs at Windows startup
- `peakcut_url.txt` — your current working URL

## Setup (do once)

### Option A: Task Scheduler (recommended, no admin needed for scheduling)

1. Open **Task Scheduler** (Windows search → "Task Scheduler")
2. **Create Basic Task** → name "PeakCut 24/7"
3. Trigger: **When the computer starts**
4. Action: **Start a program**
   - Program: `C:\Users\Iram\Downloads\CIIPING1\.venv\Scripts\python.exe`
   - Arguments: `peakcut_guardian.py`
   - Start in: `C:\Users\Iram\Downloads\CIIPING1`
5. Check **Run with highest privileges**
6. **Done**

### Option B: Startup folder (simplest)

1. Press `Win + R`, type `shell:startup`, press Enter
2. Create a shortcut to `peakcut_guardian.py` there
   - Or copy `peakcut_startup.bat` into the Startup folder

### Option C: Run now (immediate)

```
peakcut_guardian.py
```

## What happens
- PeakCut server starts on port 8765
- Cloudflare tunnel exposes it publicly
- URL saved to `peakcut_url.txt`
- If either dies, it restarts automatically
- Runs on every PC boot

## Keep running
- PC stays on, display can sleep
- Wi-Fi stays connected
- Don't close the guardian window

## Check URL
```
cat peakcut_url.txt
```