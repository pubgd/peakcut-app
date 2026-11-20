"""Start PeakCut + Cloudflare Tunnel 24/7. Run once, leave it alone."""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CF = r"C:\Users\Iram\AppData\Local\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe"
URL_FILE = ROOT / "peakcut_url.txt"

def start_server():
    if os.name == "nt":
        subprocess.Popen(
            [sys.executable, "-m", "studio.server"],
            cwd=str(ROOT),
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    else:
        subprocess.Popen([sys.executable, "-m", "studio.server"], cwd=str(ROOT))
    print("PeakCut server starting on port 8765...")
    time.sleep(4)

def start_tunnel():
    print("Starting Cloudflare Tunnel...")
    proc = subprocess.Popen(
        [CF, "tunnel", "--url", "http://127.0.0.1:8765", "--no-autoupdate"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    url = None
    for line in proc.stdout:
        print(line, end="")
        if "trycloudflare.com" in line and "https://" in line:
            import re
            m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", line)
            if m:
                url = m.group(0)
                URL_FILE.write_text(url, encoding="utf-8")
                print(f"\n\n*** YOUR URL: {url} ***\n")
                break
    proc.wait()

if __name__ == "__main__":
    start_server()
    start_tunnel()