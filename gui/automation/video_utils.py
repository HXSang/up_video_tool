import os
import json

def get_video_id_for_serial(serial):
    json_path = os.path.join(os.path.dirname(__file__), "..", "video_assigned.json")
    json_path = os.path.abspath(json_path)

    try:
        with open(json_path, "r") as f:
            assignments = json.load(f)
        return assignments.get(serial)
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi khi đọc file video_assigned.json: {e}")
        return None
