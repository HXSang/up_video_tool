import xml.etree.ElementTree as ET
import subprocess
import re

def find_bounds_for_video(xml_file_path, video_id):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    for node in root.iter():
        if node.attrib.get("class") == "android.widget.ImageView":
            desc = node.attrib.get("content-desc", "")
            if desc.strip() == f"{video_id}.mp4":
                return node.attrib.get("bounds")
    return None

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None
    x1, y1, x2, y2 = map(int, match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2

def tap_video_by_id(video_id, serial="emulator-5554"):
    print(f"📥 Dumping UI from device {serial}...")
    subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"])
    subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml"])

    print(f"🔍 Tìm video có ID: {video_id}")
    bounds = find_bounds_for_video("window_dump.xml", video_id)
    if not bounds:
        print(f"❌ Không tìm thấy video: {video_id}")
        return

    x, y = get_center_of_bounds(bounds)
    print(f"✅ Tap video {video_id} tại tọa độ ({x}, {y})")
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

# Ví dụ sử dụng:
if __name__ == "__main__":
    # Nhập ID video tại đây (không cần đuôi .mp4)
    tap_video_by_id("q2HPS4pBSAE")
