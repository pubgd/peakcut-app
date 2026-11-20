"""PeakCut 24/7 Guardian. Runs both server and tunnel, restarts them if they die."""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CF = r"C:\Users\Iram\AppData\Local\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe"
URL_FILE = ROOT / "peakcut_url.txt"

def start_server():
    return subprocess.Popen(
        [sys.executable, "-m", "studio.server"],
        cwd=str(ROOT),
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

def start_tunnel():
    return subprocess.Popen(
        [CF, "tunnel", "--url", "http://127.0.0.1:8765", "--no-autoupdate"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )

def main():
    server = start_server()
    tunnel = start_tunnel()
    print("Both started. Guardian watching...")
    while True:
        time.sleep(5)
        if server.poll() is not None:
            print("Server died, restarting...")
            server = start_server()
        if tunnel.poll() is not None:
            print("Tunnel died, restarting...")
            tunnel = start_tunnel()
            # Capture URL from tunnel output
            for line in iter(tunnel.stdout.readline, ""):
                if "trycloudflare.com" in line:
                    import re
                    m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", line)
                    if m:
                        URL_FILE.write_text(m.group(0), encoding="utf-8")
                        print(f"\n*** URL: {m.group(0)} ***\n")
                    break

if __name__ == "__main__":
    main()