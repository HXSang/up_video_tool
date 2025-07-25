import xml.etree.ElementTree as ET
import subprocess
import re

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None
    x1, y1, x2, y2 = map(int, match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2

def find_bounds_for_search_box(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    for node in root.iter():
        if (
            node.attrib.get("resource-id") == "com.google.android.youtube:id/music_picker_search_box"
            and node.attrib.get("enabled") == "true"
        ):
            return node.attrib.get("bounds")
    return None

def search_music(song_name, serial="emulator-5554"):
    print(f"📥 Dumping UI from device {serial}...")
    subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"])
    subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml"])

    print("🔍 Tìm ô tìm kiếm nhạc...")
    bounds = find_bounds_for_search_box("window_dump.xml")
    if not bounds:
        print("❌ Không tìm thấy ô search nhạc.")
        return

    x, y = get_center_of_bounds(bounds)
    print(f"✅ Tap vào ô search tại ({x}, {y})")
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

    # Chờ keyboard hiện ra
    import time
    time.sleep(1)

    # Gõ tên bài hát (thay khoảng trắng bằng +)
    query = song_name.strip().replace(" ", "+")
    print(f"Đang nhập: {song_name}")
    subprocess.run(["adb", "-s", serial, "shell", "input", "text", query])

    # Gửi phím Enter để tìm
    subprocess.run(["adb", "-s", serial, "shell", "input", "keyevent", "66"])  # KEYCODE_ENTER

if __name__ == "__main__":
    search_music("Alan Walker faded")
