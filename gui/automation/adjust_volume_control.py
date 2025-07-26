import xml.etree.ElementTree as ET
import subprocess
import re
import os

ADB_PATH = "C:\\Users\\Admin\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe"

def adb_tap(x, y, serial="emulator-5554"):
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

def dump_ui(serial):
    subprocess.run([ADB_PATH, "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    subprocess.run([ADB_PATH, "-s", serial, "pull", "/sdcard/window_dump.xml", f"window_dump_{serial}.xml"], stdout=subprocess.DEVNULL)

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None, None, None, None
    return map(int, match.groups())

def set_volume_from_slider_index(index, level_percent, serial="emulator-5554"):
    dump_ui(serial)
    xml_file = f"window_dump_{serial}.xml"
    if not os.path.exists(xml_file):
        print(f"❌ Không tìm thấy file {xml_file}")
        return

    tree = ET.parse(xml_file)
    root = tree.getroot()

    sliders = []
    for node in root.iter():
        if node.attrib.get("resource-id") == "com.google.android.youtube:id/slider":
            bounds = node.attrib.get("bounds", "")
            if bounds:
                sliders.append(bounds)

    if len(sliders) < index + 1:
        print(f"❌ Không tìm thấy thanh slider thứ {index+1}")
        return

    bounds = sliders[index]
    x1, y1, x2, y2 = get_center_of_bounds(bounds)
    if None in (x1, y1, x2, y2):
        print(f"❌ Giá trị bounds không hợp lệ: {bounds}")
        return

    y = (y1 + y2) // 2
    x = x1 + int((x2 - x1) * (level_percent / 100.0))

    label = "Voice" if index == 0 else "Music"
    print(f"✅ Set {label} volume: {level_percent}% tại ({x}, {y})")
    adb_tap(x, y, serial)

def tap_done_button(serial="emulator-5554"):
    print("📥 Dump UI để tìm nút Done...")
    dump_ui(serial)
    xml_file = f"window_dump_{serial}.xml"
    if not os.path.exists(xml_file):
        print(f"❌ Không tìm thấy file {xml_file}")
        return

    tree = ET.parse(xml_file)
    root = tree.getroot()

    for node in root.iter():
        rid = node.attrib.get("resource-id", "")
        desc = node.attrib.get("content-desc", "")
        enabled = node.attrib.get("enabled", "")
        clickable = node.attrib.get("clickable", "")
        if (
            rid in [
                "com.google.android.youtube:id/volume_done",
                "com.google.android.youtube:id/button_done"
            ]
            and desc.lower() == "done"
            and enabled == "true"
            and clickable == "true"
        ):
            bounds = node.attrib.get("bounds", "")
            match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
            if match:
                x1, y1, x2, y2 = map(int, match.groups())
                x = (x1 + x2) // 2
                y = (y1 + y2) // 2
                print(f"✅ Tap nút Done tại ({x}, {y}) [resource-id: {rid}]")
                adb_tap(x, y, serial)
                return

    print("❌ Không tìm thấy nút Done trong UI.")

def adjust_volume_dynamic(serial="emulator-5554", voice_percent=100, music_percent=50):
    voice = max(0, min(100, voice_percent))
    music = max(0, min(100, music_percent))

    print(f"[{serial}] 🔊 Bắt đầu chỉnh âm lượng: Voice={voice}%, Music={music}%")
    set_volume_from_slider_index(0, voice, serial)  # Voice là slider thứ 1
    set_volume_from_slider_index(1, music, serial)  # Music là slider thứ 2
    tap_done_button(serial)

# Cho phép chạy test thủ công
if __name__ == '__main__':
    try:
        voice = int(input("🎙 Voice (Your audio) %: "))
        music = int(input("🎵 Music (Faded) %: "))
        adjust_volume_dynamic(voice_percent=voice, music_percent=music)
    except ValueError:
        print("❌ Nhập không hợp lệ, vui lòng nhập số nguyên từ 0 đến 100.")
