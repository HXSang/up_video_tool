import xml.etree.ElementTree as ET
import subprocess
import re
from googleapiclient.discovery import build

def adb_tap(x, y, serial):
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

def paste_text(text, serial):
    subprocess.run(["adb", "-s", serial, "shell", "input", "clipboard", text])
    subprocess.run(["adb", "-s", serial, "shell", "input", "keyevent", "279"])  # KEYCODE_PASTE

def dump_ui(serial):
    subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"])
    subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml"], stdout=subprocess.DEVNULL)

def get_center_of_bounds(bounds_str):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        return None
    x1, y1, x2, y2 = map(int, match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2

def find_title_input_box(serial):
    dump_ui(serial)
    tree = ET.parse("window_dump.xml")
    root = tree.getroot()

    for node in root.iter():
        if (
            node.attrib.get("class") == "android.widget.EditText"
            and node.attrib.get("text", "").lower().startswith("caption")
        ):
            bounds = node.attrib.get("bounds", "")
            return get_center_of_bounds(bounds)
    return None

def get_video_title(video_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.videos().list(part='snippet', id=video_id)
    response = request.execute()

    if response['items']:
        return response['items'][0]['snippet']['title']
    return None

def supports_clipboard(serial):
    try:
        result = subprocess.run(
            ["adb", "-s", serial, "shell", "input", "clipboard", "test"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=3
        )
        return result.returncode == 0 and "Unknown option" not in result.stderr.decode()
    except Exception:
        return False

def set_title_from_video_id(video_id, api_key, serial):
    print(f"[{serial}] 📡 Đang lấy tiêu đề từ videoId: {video_id}...")
    title = get_video_title(video_id, api_key)
    if not title:
        print(f"[{serial}] ❌ Không tìm thấy tiêu đề.")
        return

    print(f"[{serial}] ✅ Tiêu đề lấy được: {title}")

    print(f"[{serial}] 🔎 Đang tìm ô nhập tiêu đề...")
    coords = find_title_input_box(serial)
    if not coords:
        print(f"[{serial}] ❌ Không tìm thấy ô nhập tiêu đề.")
        return

    x, y = coords
    print(f"[{serial}] 🖱️ Tap vào ({x}, {y})")
    adb_tap(x, y, serial)

    if supports_clipboard(serial):
        print(f"[{serial}] 📋 Dán tiêu đề bằng clipboard...")
        paste_text(title, serial)
        print(f"[{serial}] ✅ Tiêu đề đã được dán.")
    else:
        print(f"[{serial}] ⚠️ Không hỗ trợ clipboard. Bạn cần gõ bằng tay.")
