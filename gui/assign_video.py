import os
import json
import subprocess

DOWNLOADED_FILE = "downloaded_videos.json"
ASSIGNED_FILE = "video_assigned.json"

def get_emulator_serials(adb_path):
    result = subprocess.getoutput(f'"{adb_path}" devices')
    lines = result.strip().splitlines()[1:]
    serials = [line.split()[0] for line in lines if "emulator" in line and "device" in line]
    return serials

def load_downloaded_ids():
    if os.path.exists(DOWNLOADED_FILE):
        with open(DOWNLOADED_FILE, "r") as f:
            return json.load(f)
    return []

def load_assigned():
    if os.path.exists(ASSIGNED_FILE):
        with open(ASSIGNED_FILE, "r") as f:
            return json.load(f)
    return {}

def save_assigned(data):
    with open(ASSIGNED_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_downloaded_ids(data):
    with open(DOWNLOADED_FILE, "w") as f:
        json.dump(data, f, indent=2)

def assign_videos_to_emulators(adb_path):
    serials = get_emulator_serials(adb_path)
    downloaded_ids = load_downloaded_ids()
    assigned = {}

    changed = False
    available_ids = downloaded_ids.copy()

    for serial in serials:
        if available_ids:
            assigned[serial] = available_ids.pop(0)
            changed = True
        else:
            print(f"[{serial}] ⚠️ Không còn video nào để gán")

    if changed:
        save_assigned(assigned)
        remaining = [vid for vid in downloaded_ids if vid not in assigned.values()]
        save_downloaded_ids(remaining)

    return assigned
