import xml.etree.ElementTree as ET
import subprocess
import re
import time

def dump_ui(serial="emulator-5554"):
    """Dump UI của thiết bị và lưu về file window_dump.xml"""
    print(f"[{serial}]Dump UI...")
    subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml"], stdout=subprocess.DEVNULL)

def adb_tap(x, y, serial):
    """Nhấn tại vị trí x, y trên thiết bị"""
    print(f"[{serial}]Tapping tại ({x}, {y})")
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

def get_bounds(bounds):
    """Chuyển chuỗi bounds dạng [x1,y1][x2,y2] thành số"""
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if not match:
        return None
    return map(int, match.groups())

def tap_add_gallery_button(serial="emulator-5554"):
    """Tìm và nhấn nút Add Gallery trong giao diện Shorts"""
    dump_ui(serial)
    try:
        tree = ET.parse("window_dump.xml")
        root = tree.getroot()

        for node in root.iter():
            if (
                node.attrib.get("class") == "android.widget.Button"
                and node.attrib.get("resource-id") == "com.google.android.youtube:id/reel_camera_gallery_button_delegate"
            ):
                bounds = node.attrib.get("bounds")
                parsed = get_bounds(bounds)
                if parsed:
                    x1, y1, x2, y2 = parsed
                    x = (x1 + x2) // 2
                    y = (y1 + y2) // 2
                    print(f"[{serial}]Tìm thấy nút Add Gallery tại ({x}, {y})")
                    adb_tap(x, y, serial)
                    return True
        print(f"[{serial}]Không tìm thấy nút Add Gallery.")
    except Exception as e:
        print(f"[{serial}]Lỗi khi xử lý XML: {e}")
    return False
