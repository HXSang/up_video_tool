import xml.etree.ElementTree as ET
import subprocess
import re

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None
    x1, y1, x2, y2 = map(int, match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2

def find_bounds_for_next_button(xml_file_path):
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        for node in root.iter():
            if (
                node.attrib.get("resource-id") == "com.google.android.youtube:id/multi_select_next_button"
                and node.attrib.get("enabled") == "true"
            ):
                return node.attrib.get("bounds")
    except Exception as e:
        print(f"[XML] ❌ Lỗi khi đọc file XML: {e}")
    return None

def tap_next_button(serial, adb_path="adb"):
    print(f"[{serial}] 📥 Dumping UI để tìm nút 'Next' sau chọn video...")
    xml_file = f"window_dump_{serial}.xml"
    subprocess.run([adb_path, "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    subprocess.run([adb_path, "-s", serial, "pull", "/sdcard/window_dump.xml", xml_file], stdout=subprocess.DEVNULL)

    bounds = find_bounds_for_next_button(xml_file)
    if not bounds:
        print(f"[{serial}] ❌ Không tìm thấy nút Next hoặc nó đang bị vô hiệu hóa.")
        return

    coords = get_center_of_bounds(bounds)
    if coords:
        x, y = coords
        print(f"[{serial}] ✅ Tap nút Next tại tọa độ ({x}, {y})")
        subprocess.run([adb_path, "-s", serial, "shell", "input", "tap", str(x), str(y)])
    else:
        print(f"[{serial}] ⚠️ Không xác định được tọa độ từ bounds: {bounds}")
