import schedule
import time
import subprocess


def run_script():
    print("Job started at:", time.strftime("%Y-%m-%d %H:%M:%S"))
    # Replace 'D:\yeeder\images_for_server\biography_update_and_json_generation.py' with the path to your script
    script_path = r'D:\yeeder\images_for_server\biography_update_and_json_generation.py'
    subprocess.call(['python', script_path])
    print("Job done at:", time.strftime("%Y-%m-%d %H:%M:%S"))


# Schedule the script to run every Monday at 00:00
schedule.every().monday.at("00:00").do(run_script)

# You can add more schedules for other days or times if needed

while True:
    print("Job holding at:", time.strftime("%Y-%m-%d %H:%M:%S"))
    schedule.run_pending()
    # Sleep for 10,000 seconds (approximately 2 hours and 46 minutes)
    time.sleep(1e4)
