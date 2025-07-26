import xml.etree.ElementTree as ET
import subprocess
import re
import time
import os

def dump_ui(serial, adb_path="adb"):
    """Dump UI và lưu thành file theo serial"""
    xml_file = f"window_dump_{serial}.xml"
    print(f"[{serial}] 📲 Dump UI...")
    subprocess.run([adb_path, "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    subprocess.run([adb_path, "-s", serial, "pull", "/sdcard/window_dump.xml", xml_file], stdout=subprocess.DEVNULL)
    return xml_file

def adb_tap(x, y, serial, adb_path="adb"):
    """Chạm vào vị trí trên thiết bị"""
    print(f"[{serial}] 👆 Tapping tại ({x}, {y})")
    subprocess.run([adb_path, "-s", serial, "shell", "input", "tap", str(x), str(y)])

def get_bounds(bounds):
    """Parse [x1,y1][x2,y2]"""
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if not match:
        return None
    return map(int, match.groups())

def tap_add_gallery_button(serial, adb_path="adb"):
    """Tìm và nhấn nút Add Gallery"""
    xml_file = dump_ui(serial, adb_path)

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for node in root.iter():
            if (
                node.attrib.get("class") == "android.widget.Button"
                and node.attrib.get("resource-id") == "com.google.android.youtube:id/reel_camera_gallery_button_delegate"
            ):
                bounds = node.attrib.get("bounds")
                parsed = get_bounds(bounds)
                if parsed:
                    x1, y1, x2, y2 = parsed
                    x = (x1 + x2) // 2
                    y = (y1 + y2) // 2
                    print(f"[{serial}] ✅ Tìm thấy nút Add Gallery tại ({x}, {y})")
                    adb_tap(x, y, serial, adb_path)
                    return True

        print(f"[{serial}] ⚠️ Không tìm thấy nút Add Gallery.")
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi khi xử lý XML: {e}")

    return False
