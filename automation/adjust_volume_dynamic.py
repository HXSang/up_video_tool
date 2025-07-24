import xml.etree.ElementTree as ET
import subprocess
import re

def adb_tap(x, y, serial="emulator-5554"):
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

def dump_ui(serial="emulator-5554"):
    subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"])
    subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml"])

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None, None, None, None
    return map(int, match.groups())

def set_volume_from_slider_index(index, level_percent, serial="emulator-5554"):
    dump_ui(serial)
    tree = ET.parse("window_dump.xml")
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
    y = (y1 + y2) // 2
    x = x1 + int((x2 - x1) * (level_percent / 100.0))

    label = "Voice" if index == 0 else "Music"
    print(f"✅ Set {label} volume: {level_percent}% tại ({x}, {y})")
    adb_tap(x, y, serial)

def tap_done_button(serial="emulator-5554"):
    import xml.etree.ElementTree as ET
    import re

    def dump_ui(s):
        subprocess.run(["adb", "-s", s, "shell", "uiautomator", "dump"])
        subprocess.run(["adb", "-s", s, "pull", "/sdcard/window_dump.xml"])

    def get_center_of_bounds(bounds_str):
        match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
        if not match:
            return None
        x1, y1, x2, y2 = map(int, match.groups())
        return (x1 + x2) // 2, (y1 + y2) // 2

    print("📥 Dump UI để tìm nút Done...")
    dump_ui(serial)

    tree = ET.parse("window_dump.xml")
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

def adjust_volume_dynamic(serial="emulator-5554"):
    try:
        voice = int(input("🎙 Voice (Your audio) %: "))
        music = int(input("🎵 Music (Faded) %: "))
    except ValueError:
        print("❌ Nhập không hợp lệ, vui lòng nhập số nguyên từ 0 đến 100.")
        return

    voice = max(0, min(100, voice))
    music = max(0, min(100, music))

    set_volume_from_slider_index(0, voice, serial)
    set_volume_from_slider_index(1, music, serial)
    tap_done_button(serial)

if __name__ == '__main__':
    adjust_volume_dynamic()
