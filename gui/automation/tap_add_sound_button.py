import xml.etree.ElementTree as ET
import subprocess
import re
import os

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None
    x1, y1, x2, y2 = map(int, match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2

def find_bounds_for_add_sound_button(xml_file_path):
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        for node in root.iter():
            if (
                node.attrib.get("resource-id") == "com.google.android.youtube:id/sound_button_title"
                and node.attrib.get("text") == "Add sound"
                and node.attrib.get("enabled") == "true"
            ):
                return node.attrib.get("bounds")
    except Exception as e:
        print(f"[XML] ❌ Lỗi khi đọc file XML: {e}")
    return None

def tap_add_sound_button(serial, adb_path="adb"):
    xml_file = f"window_dump_{serial}.xml"
    print(f"[{serial}] 📥 Dump UI để tìm nút Add sound...")
    subprocess.run([adb_path, "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    subprocess.run([adb_path, "-s", serial, "pull", "/sdcard/window_dump.xml", xml_file], stdout=subprocess.DEVNULL)

    bounds = find_bounds_for_add_sound_button(xml_file)
    if not bounds:
        print(f"[{serial}] ❌ Không tìm thấy nút Add sound hoặc nó bị vô hiệu hóa.")
        return

    x, y = get_center_of_bounds(bounds)
    if x is None or y is None:
        print(f"[{serial}] ❌ Không lấy được tọa độ từ bounds: {bounds}")
        return

    print(f"[{serial}] 🎵 Tap nút Add sound tại tọa độ ({x}, {y})")
    subprocess.run([adb_path, "-s", serial, "shell", "input", "tap", str(x), str(y)])
