import xml.etree.ElementTree as ET
import subprocess
import re
import os

def adb_tap(x, y, serial="emulator-5554"):
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

def dump_ui(serial="emulator-5554"):
    subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml", f"window_dump_{serial}.xml"], stdout=subprocess.DEVNULL)

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None
    x1, y1, x2, y2 = map(int, match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2

def tap_upload_short(serial="emulator-5554"):
    print(f"[{serial}] 📥 Dumping UI để tìm nút Upload Short...")
    dump_ui(serial)

    xml_path = f"window_dump_{serial}.xml"
    if not os.path.exists(xml_path):
        print(f"[{serial}] ❌ Không tìm thấy file {xml_path}")
        return

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi khi đọc XML: {e}")
        return

    for node in root.iter():
        if (
            node.attrib.get("resource-id") == "com.google.android.youtube:id/upload_bottom_button"
            and node.attrib.get("class") == "android.widget.Button"
            and node.attrib.get("text") == "Upload Short"
            and node.attrib.get("enabled") == "true"
        ):
            bounds = node.attrib.get("bounds", "")
            coords = get_center_of_bounds(bounds)
            if coords:
                x, y = coords
                print(f"[{serial}] ✅ Tap nút Upload Short tại ({x}, {y})")
                adb_tap(x, y, serial)
                return

    print(f"[{serial}] ❌ Không tìm thấy nút Upload Short.")

# Test thủ công
if __name__ == "__main__":
    tap_upload_short()
