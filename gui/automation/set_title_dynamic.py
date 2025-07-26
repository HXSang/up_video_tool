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

def dump_ui(serial="emulator-5554"):
    subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"])
    subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml", f"window_dump_{serial}.xml"], stdout=subprocess.DEVNULL)

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None
    x1, y1, x2, y2 = map(int, match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2

def adb_tap(x, y, serial="emulator-5554"):
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

def type_title_to_box(title, serial="emulator-5554"):
    clean_title = sanitize_for_adb(title)
    subprocess.run(["adb", "-s", serial, "shell", "input", "text", clean_title])

def set_title_from_video_id(video_id, api_key, serial="emulator-5554"):
    print("Lấy tiêu đề...")
    title = get_video_title(video_id, api_key)
    if not title:
        print("Không lấy được tiêu đề.")
        return
    print(f"Tiêu đề: {title}")

    print("Tìm ô nhập tiêu đề...")
    dump_ui(serial)
    xml_path = f"window_dump_{serial}.xml"
    tree = ET.parse(xml_path)
    root = tree.getroot()

    for node in root.iter():
        if (
            node.attrib.get("class") == "android.widget.EditText"
            and node.attrib.get("hint", "").lower() == "caption your short"
        ):
            bounds = node.attrib.get("bounds", "")
            coords = get_center_of_bounds(bounds)
            if coords:
                x, y = coords
                adb_tap(x, y, serial)
                time.sleep(1)
                type_title_to_box(title, serial)
                print("Đã nhập tiêu đề vào ô Caption.")
                return
    print("Không tìm thấy ô nhập tiêu đề.")

