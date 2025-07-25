import xml.etree.ElementTree as ET
import subprocess
import re
import time

def dump_ui(serial="emulator-5554"):
    subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"])
    subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml"])

def adb_tap(x, y, serial):
    print(f"Tapping at ({x}, {y})")
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

def get_bounds(bounds):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if not match:
        return None
    return map(int, match.groups())  # x1, y1, x2, y2

def tap_create_button(serial="emulator-5554"):
    dump_ui(serial)
    tree = ET.parse("window_dump.xml")
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
                print(f"Tìm thấy nút Create tại ({x}, {y})")
                adb_tap(x, y, serial)
                return True
    print("Không tìm thấy nút Create.")
    return False

def tap_short_button(serial="emulator-5554"):
    dump_ui(serial)
    tree = ET.parse("window_dump.xml")
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
                print(f"Tìm thấy nút Short tại ({x}, {y})")
                adb_tap(x, y, serial)
                return True
    print("Không tìm thấy nút Short.")
    return False

if __name__ == "__main__":
    serial = "emulator-5554"
    if tap_create_button(serial):
        time.sleep(5)
        tap_short_button(serial)
