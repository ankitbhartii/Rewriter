import os
import sys

# Force UTF-8 stdout and stderr encoding for Windows console compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import time
import webbrowser
import threading
import uvicorn

def open_browser():
    time.sleep(1.2)
    print("\n[Grammarly Web] Opening browser at http://localhost:8000 ...")
    try:
        webbrowser.open("http://localhost:8000")
    except Exception as e:
        print(f"[Grammarly Web] Browser auto-launch notice: {e}")

if __name__ == "__main__":
    print("=" * 65)
    print("      Starting Grammarly Web Browser Application")
    print("=" * 65)
    print(" * Real-time Grammarly Web Editor:  http://localhost:8000")
    print(" * Web Component & Plugin Demo:     http://localhost:8000/extension")
    print(" * API Documentation (Swagger):    http://localhost:8000/docs")
    print("=" * 65)

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False, log_level="info")
