import time
import subprocess
import xml.etree.ElementTree as ET
import re
import os

def tap(x, y, serial, adb_path="adb"):
    print(f"[{serial}] 👆 Tap tại ({x}, {y})")
    subprocess.run([adb_path, "-s", serial, "shell", "input", "tap", str(x), str(y)])
    time.sleep(1)

def dump_ui(serial, adb_path="adb"):
    subprocess.run([adb_path, "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    local_xml = f"window_dump_{serial}.xml"
    subprocess.run([adb_path, "-s", serial, "pull", "/sdcard/window_dump.xml", local_xml], stdout=subprocess.DEVNULL)
    return local_xml

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None, None
    x1, y1, x2, y2 = map(int, match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2

def find_bounds_for_done_button(xml_file_path):
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        for node in root.iter():
            rid = node.attrib.get("resource-id", "")
            enabled = node.attrib.get("enabled", "")
            if (
                rid == "com.google.android.youtube:id/shorts_trim_finish_trim_button"
                and enabled == "true"
            ):
                return node.attrib.get("bounds")
    except Exception as e:
        print(f"❌ Lỗi đọc XML: {e}")
    return None

def tap_done_button(serial="emulator-5554", adb_path="adb", timeout=180):
    print(f"[{serial}] ⏯ Đang chờ nút Done sẵn sàng...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        # Tap nhẹ để kích hoạt UI nếu đang preview
        tap(500, 500, serial, adb_path)

        # Dump UI
        xml_file = dump_ui(serial, adb_path)

        # Tìm nút Done đã bật
        bounds = find_bounds_for_done_button(xml_file)
        if bounds:
            x, y = get_center_of_bounds(bounds)
            if x and y:
                print(f"[{serial}] ✅ Tap nút Done tại ({x}, {y})")
                subprocess.run([adb_path, "-s", serial, "shell", "input", "tap", str(x), str(y)])
                return True

        print(f"[{serial}] ⏳ Chưa thấy nút Done, thử lại...")
        time.sleep(1)

    print(f"[{serial}] ❌ Hết thời gian chờ nút Done.")
    return False
