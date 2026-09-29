import time
import os
import subprocess
from main import run_agent
from agent.notifier import send_digest

# Run interval in seconds (4 hours = 14400s)
POLL_INTERVAL = 14400

def continuous_loop():
    print("Starting NorthStar autonomous continuous application daemon...")
    while True:
        try:
            print("\n--- Running pipeline cycle ---")
            # 1. Ingest, match skills, and apply
            run_agent()

            # 2. Dispatch real-time digest update to maildiyadeepu@gmail.com
            send_digest()

            # 3. Automatically push updated tracker.json to GitHub Pages
            subprocess.run(["git", "add", "docs/tracker.json"], check=False)
            subprocess.run(["git", "commit", "-m", "Auto-update tracker pipeline"], check=False)
            subprocess.run(["git", "push", "origin", "main"], check=False)

            print(f"Cycle finished. Sleeping for {POLL_INTERVAL // 3600} hours...")
        except Exception as err:
            print(f"Loop encounter error: {err}")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    continuous_loop()