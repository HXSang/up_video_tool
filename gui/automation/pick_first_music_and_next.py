import xml.etree.ElementTree as ET
import subprocess
import re
import time

def dump_ui(serial="emulator-5554"):
    subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"])
    subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml"], stdout=subprocess.DEVNULL)

def adb_tap(x, y, serial):
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

def get_bounds(bounds):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if not match:
        return None
    return map(int, match.groups())  # x1, y1, x2, y2

def get_bounds_center(bounds):
    coords = get_bounds(bounds)
    if coords is None:
        return None, None, None, None
    x1, y1, x2, y2 = coords
    x = (x1 + x2) // 2
    y = (y1 + y2) // 2
    return x1, y1, x, y

def find_next_button_near_y(serial, y_ref, delta=100):
    try:
        tree = ET.parse("window_dump.xml")
        root = tree.getroot()
        for node in root.iter():
            if (
                node.attrib.get("resource-id") == "com.google.android.youtube:id/shorts_camera_next_button_delegate"
                and node.attrib.get("enabled") == "true"
            ):
                bounds = node.attrib.get("bounds", "")
                x1, y1, x, y = get_bounds_center(bounds)
                if abs(y1 - y_ref) <= delta:
                    print(f"[{serial}] ⏭ Tap nút → gần y={y_ref} tại ({x}, {y})")
                    adb_tap(x, y, serial)
                    return True
    except Exception as e:
        print(f"[{serial}]Lỗi khi tìm next button: {e}")
    print(f"[{serial}]Không tìm thấy nút → gần bài nhạc.")
    return False

def pick_first_music_and_next(serial="emulator-5554"):
    print(f"[{serial}]Dumping UI để tìm bài nhạc...")
    dump_ui(serial)

    try:
        tree = ET.parse("window_dump.xml")
        root = tree.getroot()
    except Exception as e:
        print(f"[{serial}]Lỗi khi đọc XML: {e}")
        return

    candidates = []

    for node in root.iter():
        desc = node.attrib.get("content-desc", "")
        if (
            node.attrib.get("class") == "android.view.ViewGroup"
            and "Play a preview" in desc
        ):
            bounds = node.attrib.get("bounds", "")
            parsed = get_bounds(bounds)
            if parsed:
                x1, y1, x2, y2 = parsed
                candidates.append((y1, x1, x2, y2, bounds))

    if not candidates:
        print(f"[{serial}]Không tìm thấy bài nhạc nào.")
        return

    candidates.sort(key=lambda item: item[0])  # bài trên cùng
    y1, x1, x2, y2, bounds = candidates[0]

    x_center = (x1 + x2) // 2
    y_center = (y1 + y2) // 2
    print(f"[{serial}]Tap bài đầu tiên tại ({x_center}, {y_center}) bounds={bounds}")
    adb_tap(x_center, y_center, serial)

    # Chờ preview hiện ra
    time.sleep(3)
    print(f"[{serial}]Dump lại UI sau preview...")
    dump_ui(serial)

    success = find_next_button_near_y(serial, y1)
    if not success:
        print(f"[{serial}]Fallback tap bằng toạ độ tương đối...")
        width = x2 - x1
        height = y2 - y1
        x_relative = x1 + int(width * 0.85)
        y_relative = y1 + int(height * 0.40)
        print(f"[{serial}]Tap fallback tại ({x_relative}, {y_relative})")
        adb_tap(x_relative, y_relative, serial)
