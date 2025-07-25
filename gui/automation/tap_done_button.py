import xml.etree.ElementTree as ET
import subprocess
import re
import time
import subprocess

ADB_PATH = 'C:\\Users\\ADMIN\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe'

def run_adb(cmd, serial):
    subprocess.run([ADB_PATH, "-s", serial, "shell"] + cmd.split(), shell=False)

def tap(x, y, serial, delay=4):
    run_adb(f"input tap {x} {y}", serial)
    time.sleep(delay)

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None
    x1, y1, x2, y2 = map(int, match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2

def find_bounds_for_done_button(xml_file_path):
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        for node in root.iter():
            if (
                node.attrib.get("resource-id") == "com.google.android.youtube:id/shorts_trim_finish_trim_button"
                and node.attrib.get("enabled") == "true"
            ):
                return node.attrib.get("bounds")
    except Exception as e:
        print(f"Lỗi đọc XML: {e}")
    return None

def tap_done_button(serial="emulator-5554"):
    print(f"[{serial}]Tap giữa màn hình để dừng preview...")
    time.sleep(2)
    tap(500, 500, serial)
    time.sleep(2)

    print(f"[{serial}]Dumping UI...")
    subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"])
    subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml"], stdout=subprocess.DEVNULL)

    print(f"[{serial}]Tìm nút Done trong giao diện...")
    bounds = find_bounds_for_done_button("window_dump.xml")
    if not bounds:
        print(f"[{serial}]Không tìm thấy nút Done hoặc nó đang bị vô hiệu hóa (enabled=false).")
        return

    x, y = get_center_of_bounds(bounds)
    if x and y:
        print(f"[{serial}]Tap nút Done tại tọa độ ({x}, {y})")
        subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])
    else:
        print(f"[{serial}]Không xác định được tọa độ trung tâm của bounds: {bounds}")

if __name__ == "__main__":
    tap_done_button()
