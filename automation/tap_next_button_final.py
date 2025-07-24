import xml.etree.ElementTree as ET
import subprocess
import re

def adb_tap(x, y, serial="emulator-5554"):
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

def dump_ui(serial):
    subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"])
    subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml"])

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None
    x1, y1, x2, y2 = map(int, match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2

def tap_next_button_final(serial="emulator-5554"):
    print("📥 Dumping UI để tìm nút 'Next' cuối...")
    dump_ui(serial)

    tree = ET.parse("window_dump.xml")
    root = tree.getroot()

    for node in root.iter():
        if (
            node.attrib.get("resource-id") == "com.google.android.youtube:id/shorts_post_bottom_button"
            and node.attrib.get("class") == "android.widget.Button"
            and node.attrib.get("text") == "Next"
            and node.attrib.get("enabled") == "true"
        ):
            bounds = node.attrib.get("bounds", "")
            x, y = get_center_of_bounds(bounds)
            print(f"✅ Tap nút Next cuối tại ({x}, {y})")
            adb_tap(x, y, serial)
            return

    print("❌ Không tìm thấy nút Next cuối.")

# Chạy thử
if __name__ == "__main__":
    tap_next_button_final()
