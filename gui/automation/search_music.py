import xml.etree.ElementTree as ET
import subprocess
import re
import time

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None
    x1, y1, x2, y2 = map(int, match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2

def find_bounds_for_search_box(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    for node in root.iter():
        if (
            node.attrib.get("resource-id") == "com.google.android.youtube:id/music_picker_search_box"
            and node.attrib.get("enabled") == "true"
        ):
            return node.attrib.get("bounds")
    return None

def search_music(song_name, serial="emulator-5554", adb_path="adb"):
    xml_file = f"window_dump_{serial}.xml"

    print(f"[{serial}] Dumping UI...")
    subprocess.run([adb_path, "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    subprocess.run([adb_path, "-s", serial, "pull", "/sdcard/window_dump.xml", xml_file], stdout=subprocess.DEVNULL)

    print(f"[{serial}] Tìm ô tìm kiếm nhạc...")
    bounds = find_bounds_for_search_box(xml_file)
    if not bounds:
        print(f"[{serial}] ❌ Không tìm thấy ô search nhạc.")
        return

    x, y = get_center_of_bounds(bounds)
    print(f"[{serial}] Tap vào ô search tại ({x}, {y})")
    subprocess.run([adb_path, "-s", serial, "shell", "input", "tap", str(x), str(y)])

    time.sleep(1)

    query = song_name.strip().replace(" ", "+")
    print(f"[{serial}] Nhập bài nhạc: {song_name}")
    subprocess.run([adb_path, "-s", serial, "shell", "input", "text", query])
    time.sleep(1)

    subprocess.run([adb_path, "-s", serial, "shell", "input", "keyevent", "66"])
    time.sleep(1)
