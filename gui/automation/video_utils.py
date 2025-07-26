import os
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSIGNED_FILE = os.path.join(BASE_DIR, "video_assigned.json")

def get_video_id_for_serial(serial):
    try:
        with open(ASSIGNED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(serial)
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi khi đọc file video_assigned.json: {e}")
        return None
