# PeakCut Project Handover & Complete Technical Blueprint for Claude AI

> **Purpose:** This document is prepared specifically for **Claude AI** (or any incoming AI assistant / engineer) to gain 100% instant, granular context on the current state of the PeakCut project, what has been built, what bugs were resolved, and the exact next steps.

---

## 1. Project Overview & User Goals

* **Project:** [PeakCut](https://github.com/haziqahmedqasmi/peakcut) — an autonomous stream and video clipping platform (similar to OpusClip / Klap). It ingests long videos or livestreams (YouTube, Twitch, Kick, or local video uploads), analyzes transcripts and loudness to find viral moments using Google Gemini AI, and renders vertical 9:16 vertical shorts with animated subtitles/captions (bounce, hype, clean) and custom layouts (blurred background, center crop, split screen).
* **Git Repository (Active):** [`https://github.com/pubgd/peakcut-app.git`](https://github.com/pubgd/peakcut-app.git) (Branch: `main`)
* **Local Workspace Path:** `C:\Users\Iram\Downloads\CIIPING1`
* **Python Environment:** Python 3.12 (`C:\Users\Iram\Downloads\CIIPING1\.venv\Scripts\python.exe`)
* **User's Goal:** The user wants to run and use PeakCut **24/7 on their mobile device (Android)** with all features (paste links, upload, 9:16 render, bounce captions, preview, 1-click download) **without any errors**, ideally without needing their laptop on all the time.
* **Core Non-Technical Rule:** The user is non-technical and requested complete automation. Never ask the user to edit code or run complex CLI scripts. Keep all explanations simple and in friendly Hinglish.

---

## 2. Architecture & File Structure

```
├── Dockerfile                  # Container definition (Debian 12, Python 3.11, ffmpeg, deno, nodejs)
├── render.yaml                 # Infrastructure-as-code for Render.com deployment
├── requirements.txt            # Python dependencies (FastAPI, yt-dlp, sherpa-onnx, SQLAlchemy, etc.)
├── cookies.txt                 # Local netscape-format YouTube cookies
├── peakcut_url.txt             # Latest active public Cloudflare tunnel URL
│
├── studio/                     # Core Backend Engine
│   ├── server.py               # FastAPI routes, Gate middleware (auth, size limits, headers)
│   ├── config.py               # Environment variable parser
│   ├── media.py                # yt-dlp extraction, format selection, audio slicing, ffmpeg probe
│   ├── jobs.py                 # Background worker queue, clip selection, transcription pipeline
│   ├── brain.py                # AI prompts (hook, title, viral score, speech punctuation)
│   ├── ai.py                   # LLM integrations (Gemini, OpenAI, Groq, Ollama)
│   ├── render.py               # Video composition, ffmpeg filters, PIL animated captions
│   ├── live.py                 # Live stream recording & real-time buffering
│   └── transcribe.py           # Sherpa-ONNX local speech recognition model (~480MB)
│
├── web/                        # Single-Page Frontend (No build step, pure Vanilla JS)
│   ├── index.html              # Full application UI (Dashboard, player, clip editor, settings)
│   ├── manifest.webmanifest    # PWA configuration (Standalone mobile app, share target, icons)
│   ├── sw.js                   # Service Worker for offline asset caching
│   └── brand/                  # App logos, favicon, PWA icons
│
└── android/                    # Native Android Studio Project
    ├── app/src/main/           # AndroidManifest.xml, MainActivity.java (WebChromeClient + file picker + DownloadManager)
    └── build.gradle            # Gradle build configuration
```

---

## 3. Current Live Services & Status

| Service | Environment / URL | Status | Details |
|---|---|---|---|
| **Render Cloud (24/7)** | `https://peakcut-app.onrender.com` | **LIVE (HTTP 200)** | Runs on Docker free tier. Gemini AI connected (`ready: true`). YouTube cookies auto-restored on boot. |
| **Cloudflare Tunnel (Local)** | `https://compensation-mortality-diagram-participation.trycloudflare.com` | **LIVE (HTTP 200)** | Tunnels local port `8765` directly from user's laptop residential Wi-Fi. (Saved in `peakcut_url.txt`). |
| **Local Server Daemon** | `http://127.0.0.1:8765` | **RUNNING** | Running in background (`python -m studio.server`). |
| **Active GitHub Commit** | `b342c3c` on `pubgd/peakcut-app:main` | **PUSHED** | Format fallback fix + player client update. |

---

## 4. Key Fixes & Milestones Completed

### A. Mobile PWA & Native Android Support
1. **PWA Manifest & Service Worker:** Added `web/manifest.webmanifest` and `web/sw.js`. Supports `display: standalone` and `share_target` (users can share YouTube links directly from the YouTube Android app to PeakCut).
2. **In-App Install Prompt:** Added an explicit `+ Install App` button in the header of `web/index.html` with a listener for `beforeinstallprompt`.
3. **Android Studio Native App Project:** Created complete native wrapper in `android/` with `MainActivity.java` implementing `WebChromeClient` (file upload picker), `DownloadListener` (`DownloadManager`), and intent handling for shared video URLs.

### B. Mobile Touch & Paste Interaction Fix
* **The Bug:** On Android mobile browsers (Chrome), tapping the on-screen "Paste" button (`data-act="pasteurl"`) silently failed because `navigator.clipboard.readText()` throws permission exceptions on mobile without an explicit OS prompt, falling back to an unhandled catch block.
* **The Fix (`web/index.html`):**
  - Added an interactive fallback: if `navigator.clipboard.readText()` fails or is blocked, it opens `window.prompt("YouTube / Twitch / Kick link yahan paste karein:")` allowing the user to paste directly using Android's native context menu.
  - Form validation auto-focuses and accepts the link immediately into the processing queue.

### C. Cloud Cookie Upload & 413 "Request Too Large" Fix
* **The Bug:** When the user tried uploading `cookies.txt` via `Settings -> Connected apps -> YouTube cookies`, the server returned **HTTP 413: "That request is too large"**.
* **The Fix (`studio/server.py`):**
  - Line 107 of `studio/server.py` had a rigid `256 KB` hard cap on all non-upload JSON requests.
  - Updated the middleware to allow up to `2 MB` specifically for the `/api/youtube-cookies` route.
  - Added startup persistence: `PEAKCUT_YT_COOKIES_TEXT` environment variable auto-writes `/data/youtube-cookies.txt` on startup so cookies survive ephemeral container restarts.

### D. YouTube OAuth2 vs Cookie Stripping Conflict
* **The Bug:** In `studio/media.py`, when `PEAKCUT_YT_OAUTH2=1` was enabled on Render, the code executed `base.pop("cookiefile", None)`, which stripped any saved cookies and forced the unauthenticated OAuth2 device flow (which fails in headless cloud environments).
* **The Fix (`studio/media.py`):**
  - Modified `_ydl()` so that uploaded cookies take first priority. When cookies exist, `cookiefile` is preserved and passed to yt-dlp, using the Android player client to bypass datacenter bot checks without requiring device authorization.

### E. Long Video / Livestream Format Selection Fix
* **The Bug:** The user attempted to clip a 4-hour GTA 5 stream (`XPfst4ws5Oc`) and received:
  `ERROR: [youtube+oauth2] XPfst4ws5Oc: Requested format is not available. Use --list-formats for a list of available formats`.
* **Root Cause:**
  - YouTube's SABR experiment stripped direct HTTPS `m4a` audio streams for Android clients on long streams, leaving only `m3u8` streams (`233`, `234`) or combined video/audio streams.
  - PeakCut's hardcoded audio format string `"format": "ba[ext=m4a]/ba/worst"` crashed when standalone `m4a` was withheld.
* **The Fix (`studio/media.py` - Commit `b342c3c`):**
  - Updated audio format to `"format": "ba[ext=m4a]/ba/b/best"`. If dedicated audio streams are blocked, it seamlessly falls back to combined streams (`b`) or `best`, which ffmpeg easily converts to wav for ASR.
  - Updated video formats in `_video_format()` and `_section_format()` to append `/b/best`.
  - Added `web` alongside `android` and `visionos` in `player_client` extractor args.

---

## 5. Configuration & Credentials Guide

All credentials and configuration live in `.env` and `data/`:

* **Gemini AI Key:** Saved locally in `data/ai.json` and in Render's configuration:
  - Provider: `gemini`
  - Model: `gemini-3.1-flash-lite`
  - Key: Managed in `data/ai.json` (`ready: true` on Render)
* **Port Settings:** Default local port is `8765`.
* **Data Storage:** Local data lives in `C:\Users\Iram\Downloads\CIIPING1\data`.
* **Cookies File:** `C:\Users\Iram\Downloads\CIIPING1\cookies.txt` (also uploaded to Render's `/data/youtube-cookies.txt`).

---

## 6. Verification & Test Commands

To verify the system at any time:

```powershell
# 1. Run complete automated unit and regression tests (19 suites, 460+ checks):
cd C:\Users\Iram\Downloads\CIIPING1
.venv\Scripts\python.exe tests/run.py

# 2. Check local server health:
curl.exe -s http://127.0.0.1:8765/api/status

# 3. Check Render cloud service health:
curl.exe -s https://peakcut-app.onrender.com/api/status

# 4. Test YouTube link preview on Render:
curl.exe -s "https://peakcut-app.onrender.com/api/preview?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DdQw4w9WgXcQ"
```

---

## 7. Immediate Next Steps for Claude AI

1. **Verify Render Cloud Deployment:**
   - Ensure Render completes building commit `157a248` (Fix: YouTube OAuth2 username typo and headless checks; prioritize android/visionos player clients).
   - Removed typo `username="oauth"` (plugin requires `username="oauth2"`).
   - Ensured headless background daemon does not attempt unapproved OAuth2 device flows.
   - Set `PEAKCUT_YT_OAUTH2=0` in Dockerfile and `render.yaml`.
   - Client prioritization: `["android", "visionos", "web"]` prevents datacenter IP bot challenges.
2. **APK Generation for User (If Requested):**
   - If the user prefers a standalone `.apk` install file over the PWA (Chrome "Add to Home Screen"), compile the Gradle project in `android/` using `gradlew assembleRelease` or guide the user to generate an APK via PWABuilder / WebIntoApp with the URL `https://peakcut-app.onrender.com`.
3. **Keep User Informed in Simple Hinglish:**
   - Always explain actions clearly without overwhelming technical jargon. Provide direct links for testing.
