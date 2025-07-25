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

def find_bounds_for_next_button(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    for node in root.iter():
        if (
            node.attrib.get("resource-id") == "com.google.android.youtube:id/multi_select_next_button"
            and node.attrib.get("enabled") == "true"
        ):
            return node.attrib.get("bounds")
    return None

def tap_next_button(serial="emulator-5554"):
    print(f"📥 Dumping UI from device {serial}...")
    subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"])
    subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml"])

    print("🔍 Tìm nút Next trong giao diện...")
    bounds = find_bounds_for_next_button("window_dump.xml")
    if not bounds:
        print("❌ Không tìm thấy nút Next hoặc nó đang bị vô hiệu hóa (enabled=false).")
        return

    x, y = get_center_of_bounds(bounds)
    print(f"✅ Tap nút Next tại tọa độ ({x}, {y})")
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

if __name__ == "__main__":
    tap_next_button()  # GỌI HÀM TẠI ĐÂY