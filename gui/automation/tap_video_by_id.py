import xml.etree.ElementTree as ET
import subprocess
import re
import subprocess
from .video_utils import get_video_id_for_serial

def adb_tap(x, y, serial):
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

def dump_ui(serial):
    subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    local_xml = f"window_dump_{serial}.xml"
    subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml", local_xml], stdout=subprocess.DEVNULL)
    return local_xml

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

def tap_video_by_id(video_id, serial):
    print(f"[{serial}Dumping UI...")
    xml_file = dump_ui(serial)

    print(f"[{serial}]Tìm video có ID: {video_id}")
    bounds = find_bounds_for_video(xml_file, video_id)
    if not bounds:
        print(f"[{serial}]Không tìm thấy video: {video_id} trong UI")
        return

    center = get_center_of_bounds(bounds)
    if center:
        x, y = center
        print(f"[{serial}]Tap video tại tọa độ ({x}, {y})")
        adb_tap(x, y, serial)
    else:
        print(f"[{serial}Không xác định được tọa độ trung tâm")

def run_all_from_assignment():
    import subprocess
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')[1:]
    serials = [line.split('\t')[0] for line in lines if "device" in line]

    for serial in serials:
        video_id = get_video_id_for_serial(serial)
        if video_id:
            tap_video_by_id(video_id, serial)
        else:
            print(f"[{serial}]Không tìm thấy video ID trong video_assigned.json")

