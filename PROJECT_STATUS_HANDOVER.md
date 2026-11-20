# PeakCut Project Handover & Comprehensive Context for Claude AI

> **Purpose:** This document is prepared for **Claude AI** to get 100% instant context on the current state of the PeakCut project, what has been completed, what works, and the exact remaining technical blocker on cloud hosting.

---

## 1. Executive Summary & User Goal

* **Project:** [PeakCut](https://github.com/haziqahmedqasmi/peakcut) — an AI-powered stream & video clipping tool (similar to OpusClip) that extracts viral moments from long videos, transcribes speech, generates hooks/titles using AI, and renders 9:16 vertical shorts with animated captions (bounce style) and layouts (blur/split).
* **Fork / Active Repository:** [`https://github.com/pubgd/peakcut-app.git`](https://github.com/pubgd/peakcut-app.git) (Branch: `main`)
* **Local Workspace Path:** `C:\Users\Iram\Downloads\CIIPING1`
* **User's Goal:** The user wants to access and use PeakCut **24/7 from their mobile phone** without needing to keep their home PC switched on. They want to paste any YouTube link on their mobile and have it download, clip, and process smoothly.
* **Core Constraint:** The user does **not** know how to code and explicitly requested: *"pura work automation me hona chahiye, kuch bhi manually nahi hona chahiye"* (Everything must be fully automated, zero manual steps).

---

## 2. Technology Stack & Key Files

| Component | Technology / Library |
|---|---|
| **Backend** | Python 3.11, FastAPI, Uvicorn, SQLite (SQLAlchemy Core) |
| **Media Processing** | `ffmpeg`, `yt-dlp==2024.10.21`, `soundfile`, `numpy` |
| **Speech-to-Text (ASR)** | YouTube Transcripts (word-by-word via JSON3 captions) + Sherpa-ONNX (`sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8`, ~480MB model) |
| **AI LLM** | Google Gemini (`gemini-3.1-flash-lite`) via `studio/ai.py` |
| **Frontend** | Vanilla JS, HTML5, CSS (Single file: `web/index.html`, no build step, no framework) |
| **Containerization** | `Dockerfile` (Debian 12-slim, Python 3.11, FFmpeg, Deno, Node.js) |
| **Cloud Deployment** | Render.com Web Service (`peakcut-app`, Docker runtime, Free Tier) |
| **Tunneling** | Cloudflare Tunnel (`cloudflared` with HTTP/2 protocol) |

### Key Project Architecture Files:
* `studio/server.py` — FastAPI routes, request gatekeeper (`_own_address()`), security checks, upload/stream endpoints.
* `studio/config.py` — Settings loaded from `.env` and environment variables.
* `studio/media.py` — Video download via `yt-dlp`, media probing, audio extraction, loudness analysis, YouTube transcript fetching.
* `studio/ai.py` — AI provider integration (Gemini, OpenAI, Groq, Anthropic).
* `studio/jobs.py` — Background job execution queue, clip planning, rendering pipeline.
* `studio/render.py` — FFmpeg clip slicing, vertical 9:16 layout formatting, animated captions.
* `web/index.html` — Complete frontend UI.

---

## 3. What Has Been Accomplished & What Works 100%

### A. Local PC Execution (Flawless)
1. **Full Pipeline Verified:** The server was run locally (`.venv\Scripts\python.exe -m studio.server`). It processed a **2-hour long YouTube video** (`https://youtu.be/7mjhCbFi9Wk`), analyzed loudness, fetched YouTube transcripts (15,533 words), selected highlights, and generated **4 vertical 9:16 MP4 clips** with animated bounce captions and blurred background layout in just **3.5 minutes**.
2. **Automated Test Suite:** All 19 test suites and 460+ checks pass cleanly:
   ```bash
   .venv\Scripts\python.exe tests/run.py
   # Output: "All tests passed."
   ```
3. **Bug Fixes Already Committed & Pushed:**
   * `render.py`: Fixed `[WinError 5] Access is denied` on Windows during temporary folder moves by unlinking destination before `shutil.move()`.
   * `config.py`: Added support for dynamic cloud `PORT` environment variables (Render/Railway).
   * `server.py`: Updated `_own_address()` gatekeeper to whitelist `.onrender.com`, `.trycloudflare.com`, `.railway.app`, and `RENDER` env var.
   * `server.py`: Added endpoints for cookie management (`/api/cookies`) and diagnostics (`/api/debug/cookies`, `/api/debug/yt`).
   * `media.py`: Optimized `download_section()` with segmented m3u8 stream slicing (7 seconds vs 15+ minutes).
   * `media.py`: Added `process=False` to `info()` and `youtube_words()` so metadata extraction succeeds in 1 second without throwing format matching errors (`Requested format is not available`).
   * `media.py`: Fixed error classification so unavailable/private YouTube videos cleanly return HTTP 422 with *"This video is unavailable or private on YouTube. Check the link."* instead of triggering confusing bot blocks.
   * `Dockerfile`: Added native `nodejs` package alongside Deno so `yt-dlp` has a full JavaScript runtime for YouTube challenge solving.

### B. Cloudflare Tunnel (Active Local Remote Access)
* Running daemon with HTTP/2 protocol:
  `cloudflared tunnel --protocol http2 --url http://127.0.0.1:8765`
* Connects the local residential IP to a public domain. Any YouTube link pasted here works 100% without any bot check because it runs from a residential Wi-Fi connection.

### C. Render Deployment Status
* **Live Service URL:** `https://peakcut-app.onrender.com` (Returns HTTP 200 OK).
* **AI Configuration:** Gemini API is connected and active (`gemini-3.1-flash-lite`, `ready: true`).
* **Direct File Uploads:** Uploading MP4 video files directly from mobile/PC works 100% 24/7 on Render.
* **Twitch & Kick Streams:** Supported and functional.

---

## 4. The Exact Technical Blocker on Cloud (Render)

### The Problem:
When the user opens `https://peakcut-app.onrender.com` on mobile and pastes a YouTube link, the server returns HTTP 503:
> *"YouTube isn't letting PeakCut download videos right now. Upload the video file instead, or use a Twitch or Kick link. YouTube links will be tried again in a few minutes."*

### Deep Root Cause Analysis:
1. **Datacenter ASN IP Blacklist:**
   Render hosts its services in cloud datacenters (AWS us-west / GCP Oregon). YouTube's anti-bot system (SABR / GVS / Cloudflare Turnstile bot detection) flags **all automated traffic from known cloud hosting IP ranges** (AWS, GCP, DigitalOcean, Hetzner, Render).
   When `yt-dlp` connects anonymously from a Render IP, YouTube returns:
   `Sign in to confirm you’re not a bot. This helps protect our community.`

2. **Why `cookies.txt` Failed on Render:**
   * The user exported their YouTube `cookies.txt` from Chrome on their home PC in India and provided it.
   * We injected and baked `cookies.txt` into the Render deployment.
   * When Render's server in **Oregon, USA** attempted to use session cookies originating from an Indian residential IP, YouTube's security system flagged the geographic anomaly and immediately rotated/invalidated the session:
     ```
     WARNING: [youtube] The provided YouTube account cookies are no longer valid.
     They have likely been rotated in the browser as a security measure.
     ```
   * As a result, the session became unauthenticated, falling back to anonymous datacenter traffic, which YouTube instantly blocked again.

3. **Ephemeral Container Resets on Free Plan:**
   On Render's Free tier, the root and `/data` filesystem is ephemeral. While we baked `cookies.txt` into the Docker image, static browser cookies expire rapidly anyway.

---

## 5. Potential Engineering Solutions for Claude AI to Implement

To fulfill the user's requirement of **"running 24/7 in the cloud without requiring a home PC and without YouTube blocking"**, here are the viable architectural paths:

### Path A: Use YouTube OAuth2 Device Flow (Recommended for Server Auth)
`yt-dlp` now has built-in YouTube OAuth2 authentication:
```bash
yt-dlp --username oauth --password "" <URL>
```
* Generates a device code (`https://www.google.com/device`).
* OAuth2 issues long-lived **refresh tokens** rather than browser session cookies. Refresh tokens do not expire when IP addresses change, making them substantially more resilient to datacenter IP checks than desktop Chrome cookies.

### Path B: Route YouTube Traffic Through a Residential Proxy
If headless cloud hosting must download from YouTube without cookies, `yt-dlp` must route requests through a residential or mobile proxy:
```python
base["proxy"] = os.environ.get("PEAKCUT_YOUTUBE_PROXY") # e.g. residential proxy
```
* Adding proxy support in `studio/config.py` and `studio/media.py` allows passing a residential proxy URL via an environment variable in Render.

### Path C: Integrate an External Cloud Video Download API / Scraper Microservice
Instead of having Render's blocked IP download YouTube media streams directly:
* Offload YouTube stream URL extraction to an external API service (e.g. Cobalt API, Apify YouTube Downloader Actor, or a dedicated Piped/Invidious extractor instance that handles IP rotation).

### Path D: Turn User's Local Machine into a Background 24/7 Home Server
If the user chooses not to use external paid proxies:
* Configure the local Windows machine with a persistent **Cloudflare Named Tunnel** (`cloudflared tunnel run <name>`) and run PeakCut as a Windows background service (`NSSM` or Windows Task Scheduler).
* The PC stays on with display sleep disabled, using residential Wi-Fi (where YouTube never blocks), providing a permanent, free 24/7 URL for their mobile device.

---

## 6. How to Run and Test Right Now

```powershell
# Navigate to project
cd C:\Users\Iram\Downloads\CIIPING1

# Run automated tests
.venv\Scripts\python.exe tests/run.py

# Run local web server
.venv\Scripts\python.exe -m studio.server

# Start Cloudflare HTTP/2 tunnel
cloudflared tunnel --protocol http2 --url http://127.0.0.1:8765
```

---
*Document generated on 2026-11-20 for instant handover to Claude AI.*
