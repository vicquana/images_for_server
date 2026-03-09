import schedule
import time
import subprocess
import os
import sys

def run_script():
    print("Job started at:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "biography_update_and_json_generation.py"
    )
    
    subprocess.call([sys.executable, script_path])
    print("Job done at:", time.strftime("%Y-%m-%d %H:%M:%S"))

# Schedule the script to run every Monday at 00:00
schedule.every().monday.at("00:00").do(run_script)

if __name__ == "__main__":
    print("Schedule update service started...")
    print("Job holding at:", time.strftime("%Y-%m-%d %H:%M:%S"))
    while True:
        schedule.run_pending()
        time.sleep(1) # We sleep 1s to allow run_pending to trigger more accurately
