import xml.etree.ElementTree as ET
import subprocess
import re
import os
import threading

class ActionSync:
    def __init__(self, num_participants):
        self.barrier = threading.Barrier(num_participants)

    def wait(self, message=None):
        if message:
            print(message)
        self.barrier.wait()

def adb_tap(x, y, serial, adb_path="adb"):
    subprocess.run([adb_path, "-s", serial, "shell", "input", "tap", str(x), str(y)])

def dump_ui(serial, adb_path="adb"):
    xml_file = f"window_dump_{serial}.xml"
    subprocess.run([adb_path, "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    subprocess.run([adb_path, "-s", serial, "pull", "/sdcard/window_dump.xml", xml_file], stdout=subprocess.DEVNULL)
    return xml_file

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None, None, None, None
    return map(int, match.groups())

def set_volume_from_slider_index(index, level_percent, serial, adb_path="adb"):
    xml_file = dump_ui(serial, adb_path)
    if not os.path.exists(xml_file):
        print(f"[{serial}] ❌ Không tìm thấy file {xml_file}")
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
        print(f"[{serial}] ❌ Không tìm thấy thanh slider thứ {index+1}")
        return

    bounds = sliders[index]
    x1, y1, x2, y2 = get_center_of_bounds(bounds)
    if None in (x1, y1, x2, y2):
        print(f"[{serial}] ❌ Giá trị bounds không hợp lệ: {bounds}")
        return

    y = (y1 + y2) // 2
    x = x1 + int((x2 - x1) * (level_percent / 100.0))

    label = "Voice" if index == 0 else "Music"
    print(f"[{serial}] 🎚 Set {label} volume: {level_percent}% tại ({x}, {y})")
    adb_tap(x, y, serial, adb_path)

def tap_done_button(serial, adb_path="adb"):
    print(f"[{serial}] 🔍 Dump UI để tìm nút Done...")
    xml_file = dump_ui(serial, adb_path)
    if not os.path.exists(xml_file):
        print(f"[{serial}] ❌ Không tìm thấy file {xml_file}")
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
                print(f"[{serial}] ✅ Tap nút Done tại ({x}, {y})")
                adb_tap(x, y, serial, adb_path)
                return

    print(f"[{serial}] ⚠️ Không tìm thấy nút Done trong UI.")

def adjust_volume_with_sync(serial, sync: ActionSync, voice_percent=100, music_percent=50, adb_path="adb"):
    voice = max(0, min(100, voice_percent))
    music = max(0, min(100, music_percent))

    print(f"[{serial}] 🔊 Bắt đầu chỉnh âm lượng: Voice={voice}%, Music={music}%")
    dump_ui(serial, adb_path)
    sync.wait(f"[{serial}] ⏸️ Chờ tất cả máy ảo dump xong...")

    set_volume_from_slider_index(0, voice, serial, adb_path)
    set_volume_from_slider_index(1, music, serial, adb_path)

    sync.wait(f"[{serial}] ⏸️ Chờ trước khi nhấn Done...")
    tap_done_button(serial, adb_path)
    
def get_emulator_serials(adb_path):
    result = subprocess.getoutput(f'"{adb_path}" devices')
    lines = result.strip().splitlines()[1:]
    serials = [line.split()[0] for line in lines if "emulator" in line and "device" in line]
    return serials