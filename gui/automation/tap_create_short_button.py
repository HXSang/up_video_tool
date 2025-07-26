import xml.etree.ElementTree as ET
import subprocess
import re
import time

def dump_ui(serial, adb_path="adb"):
    xml_file = f"window_dump_{serial}.xml"
    subprocess.run([adb_path, "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    subprocess.run([adb_path, "-s", serial, "pull", "/sdcard/window_dump.xml", xml_file], stdout=subprocess.DEVNULL)
    return xml_file

def adb_tap(x, y, serial, adb_path="adb"):
    print(f"[{serial}] 👆 Tap tại ({x}, {y})")
    subprocess.run([adb_path, "-s", serial, "shell", "input", "tap", str(x), str(y)])

def get_bounds(bounds):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if not match:
        return None
    return map(int, match.groups())  # x1, y1, x2, y2

def tap_create_button(serial, adb_path="adb"):
    xml_file = dump_ui(serial, adb_path)
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for node in root.iter():
            if (
                node.attrib.get("class") == "android.widget.Button"
                and node.attrib.get("content-desc") == "Create"
            ):
                bounds = node.attrib.get("bounds")
                parsed = get_bounds(bounds)
                if parsed:
                    x1, y1, x2, y2 = parsed
                    x = (x1 + x2) // 2
                    y = (y1 + y2) // 2
                    print(f"[{serial}] ✅ Tìm thấy nút Create tại ({x}, {y})")
                    adb_tap(x, y, serial, adb_path)
                    return True
        print(f"[{serial}] ❌ Không tìm thấy nút Create.")
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi khi đọc XML: {e}")
    return False

def tap_short_button(serial, adb_path="adb"):
    xml_file = dump_ui(serial, adb_path)
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for node in root.iter():
            if (
                node.attrib.get("class") == "android.widget.Button"
                and node.attrib.get("text") == "Short"
                and node.attrib.get("resource-id") == "com.google.android.youtube:id/creation_mode_button"
            ):
                bounds = node.attrib.get("bounds")
                parsed = get_bounds(bounds)
                if parsed:
                    x1, y1, x2, y2 = parsed
                    x = (x1 + x2) // 2
                    y = (y1 + y2) // 2
                    print(f"[{serial}] ✅ Tìm thấy nút Short tại ({x}, {y})")
                    adb_tap(x, y, serial, adb_path)
                    return True
        print(f"[{serial}] ❌ Không tìm thấy nút Short.")
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi khi đọc XML: {e}")
    return False
