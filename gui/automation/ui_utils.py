import time
import subprocess
import xml.etree.ElementTree as ET
import re

def dump_ui(adb_path, serial):
    subprocess.run([adb_path, "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    subprocess.run([adb_path, "-s", serial, "pull", "/sdcard/window_dump.xml", f"window_dump_{serial}.xml"], stdout=subprocess.DEVNULL)

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None
    x1, y1, x2, y2 = map(int, match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2

def wait_and_tap_by_text(adb_path, serial, target_text, timeout=30, interval=1):
    """
    Chờ nút có text cụ thể rồi tự động tap vào giữa nút
    """
    print(f"[{serial}] ⏳ Chờ nút có text '{target_text}' xuất hiện...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        dump_ui(adb_path, serial)
        xml_path = f"window_dump_{serial}.xml"

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            for node in root.iter("node"):
                if node.attrib.get("text") == target_text:
                    bounds = node.attrib.get("bounds")
                    if bounds:
                        x, y = get_center_of_bounds(bounds)
                        if x and y:
                            print(f"[{serial}] ✅ Tìm thấy và tap vào '{target_text}' tại ({x}, {y})")
                            subprocess.run([adb_path, "-s", serial, "shell", "input", "tap", str(x), str(y)])
                            return True
        except Exception as e:
            print(f"[{serial}] ⚠️ Lỗi khi đọc XML: {e}")

        time.sleep(interval)

    print(f"[{serial}] ❌ Hết thời gian chờ '{target_text}'")
    return False
