import os
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSIGNED_FILE = os.path.join(BASE_DIR, "video_assigned.json")
DOWNLOADED_FILE = os.path.join(BASE_DIR, "downloaded_videos.json")

def get_emulator_serials(adb_path):
    result = subprocess.getoutput(f'"{adb_path}" devices')
    lines = result.strip().splitlines()[1:]
    return [line.split()[0] for line in lines if "emulator" in line and "device" in line]

def load_assigned():
    if os.path.exists(ASSIGNED_FILE):
        with open(ASSIGNED_FILE, "r") as f:
            return json.load(f)
    return {}

def save_assigned(data):
    with open(ASSIGNED_FILE, "w") as f:
        json.dump(data, f, indent=2)

def assign_videos_to_emulators(adb_path):
    serials = get_emulator_serials(adb_path)
    assigned = load_assigned()
    assigned = {serial: assigned.get(serial) for serial in serials if assigned.get(serial)}

    save_assigned(assigned)
    return assigned
