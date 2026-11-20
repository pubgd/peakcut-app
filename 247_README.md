# PeakCut 24/7 Setup — One-Time, Fully Automated

## What this does
Runs PeakCut on your Windows PC + Cloudflare Tunnel so you can reach it from your phone 24/7.
Your residential IP is never blocked by YouTube.

## Files created
- `setup_247.bat` — **Run this ONCE as Administrator**. Installs both as Windows services.
- `run_247.py` — Alternative: starts both in one command (no admin needed).
- `start_peakcut.bat` — Just starts the server (no tunnel).

## After running setup_247.bat
- Two services install: `PeakCutServer` and `CloudflareTunnel`
- Both auto-start when your PC boots
- Your public URL is saved to `peakcut_url.txt`

## Open on your phone
```
https://peakcut-tunnel.trycloudflare.com
```
(Or read `peakcut_url.txt` for the actual URL.)

## Keep it running
- PC stays on, don't close it
- Display can sleep (Settings → Power & Sleep → Screen → Never on battery/plugged)
- Wi-Fi stays connected
- Both services restart automatically on PC reboot