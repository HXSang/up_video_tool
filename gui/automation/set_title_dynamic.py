import subprocess
import re
import time
import xml.etree.ElementTree as ET
from googleapiclient.discovery import build

def get_video_title(video_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.videos().list(part='snippet', id=video_id)
    response = request.execute()
    if response['items']:
        return response['items'][0]['snippet']['title']
    return None

def sanitize_for_adb(text):
    return re.sub(r"[^\w\s#@-]", "", text).replace(" ", "%s")

def dump_ui(serial, adb_path="adb"):
    xml_file = f"window_dump_{serial}.xml"
    subprocess.run([adb_path, "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    subprocess.run([adb_path, "-s", serial, "pull", "/sdcard/window_dump.xml", xml_file], stdout=subprocess.DEVNULL)
    return xml_file

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None
    x1, y1, x2, y2 = map(int, match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2

def adb_tap(x, y, serial, adb_path="adb"):
    subprocess.run([adb_path, "-s", serial, "shell", "input", "tap", str(x), str(y)])

def type_title_to_box(title, serial, adb_path="adb"):
    clean_title = sanitize_for_adb(title)
    subprocess.run([adb_path, "-s", serial, "shell", "input", "text", clean_title])

def set_title_from_video_id(video_id, api_key, serial, adb_path="adb"):
    print(f"[{serial}] 📥 Lấy tiêu đề video...")
    title = get_video_title(video_id, api_key)
    if not title:
        print(f"[{serial}] ❌ Không lấy được tiêu đề.")
        return
    print(f"[{serial}] 🎯 Tiêu đề lấy được: {title}")

    print(f"[{serial}] 🔍 Tìm ô nhập Caption...")
    xml_file = dump_ui(serial, adb_path)

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi khi đọc XML: {e}")
        return

    for node in root.iter():
        if (
            node.attrib.get("class") == "android.widget.EditText"
            and node.attrib.get("hint", "").lower() == "caption your short"
        ):
            bounds = node.attrib.get("bounds", "")
            coords = get_center_of_bounds(bounds)
            if coords:
                x, y = coords
                adb_tap(x, y, serial, adb_path)
                time.sleep(1)
                type_title_to_box(title, serial, adb_path)
                print(f"[{serial}] ✅ Đã nhập tiêu đề vào ô Caption.")
                return

    print(f"[{serial}] ⚠️ Không tìm thấy ô nhập tiêu đề.")
