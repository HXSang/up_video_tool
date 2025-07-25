import xml.etree.ElementTree as ET
import subprocess
import re

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None
    x1, y1, x2, y2 = map(int, match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2

def find_bounds_for_add_sound_button(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    for node in root.iter():
        if (
            node.attrib.get("resource-id") == "com.google.android.youtube:id/sound_button_title"
            and node.attrib.get("text") == "Add sound"
            and node.attrib.get("enabled") == "true"
        ):
            return node.attrib.get("bounds")
    return None

def tap_add_sound_button(serial="emulator-5554"):
    print(f"📥 Dumping UI from device {serial}...")
    subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"])
    subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml"])

    print("🔍 Tìm nút Add sound trong giao diện...")
    bounds = find_bounds_for_add_sound_button("window_dump.xml")
    if not bounds:
        print("❌ Không tìm thấy nút Add sound hoặc nó đang bị vô hiệu hóa.")
        return

    x, y = get_center_of_bounds(bounds)
    print(f"✅ Tap nút Add sound tại tọa độ ({x}, {y})")
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

if __name__ == "__main__":
    tap_add_sound_button()
