import os
import json

def get_video_id_for_serial(serial):
    # Lấy đường dẫn tuyệt đối tới thư mục gui/
    gui_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Trỏ tới file video_assigned.json nằm trong gui/
    json_path = os.path.join(gui_dir, "video_assigned.json")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            assignments = json.load(f)
        return assignments.get(serial)
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi khi đọc file video_assigned.json: {e}")
        return None
