import os
import time
import subprocess
import xml.etree.ElementTree as ET
import re

ADB_PATH = "C:\\Users\\ADMIN\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe"

# === Mở ứng dụng YouTube ===
def open_youtube(serial):
    print(f"[{serial}] 🚀 Mở YouTube")
    os.system(f'"{ADB_PATH}" -s {serial} shell monkey -p com.google.android.youtube -c android.intent.category.LAUNCHER 1')

# === Dump UI về file riêng cho từng máy ảo ===
def dump_ui(serial):
    subprocess.run([ADB_PATH, "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    subprocess.run([ADB_PATH, "-s", serial, "pull", "/sdcard/window_dump.xml", f"window_dump_{serial}.xml"], stdout=subprocess.DEVNULL)

# === Hàm chờ cho đến khi UI có phần tử mong muốn ===
def wait_until_ui_has(serial, keyword, timeout=10):
    print(f"[{serial}] ⏳ Chờ UI chứa '{keyword}'...")
    start = time.time()
    while time.time() - start < timeout:
        dump_ui(serial)
        try:
            tree = ET.parse(f"window_dump_{serial}.xml")
            root = tree.getroot()
            for node in root.iter():
                if (
                    keyword in node.attrib.get("content-desc", "") or
                    keyword in node.attrib.get("text", "") or
                    keyword in node.attrib.get("resource-id", "")
                ):
                    print(f"[{serial}] ✅ Đã tìm thấy phần tử chứa: {keyword}")
                    return True
        except Exception as e:
            print(f"[{serial}] ⚠️ Lỗi khi đọc XML: {e}")
        time.sleep(1)
    print(f"[{serial}] ❌ Hết thời gian chờ UI có '{keyword}'")
    return False

# === Tap vào vị trí bằng ADB ===
def adb_tap(x, y, serial):
    print(f"[{serial}] 👉 Tap tại ({x}, {y})")
    subprocess.run([ADB_PATH, "-s", serial, "shell", "input", "tap", str(x), str(y)])

# === Parse bounds dạng [x1,y1][x2,y2] về int ===
def get_bounds(bounds):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if not match:
        return None
    return map(int, match.groups())

# === Tìm và nhấn nút "Create" ===
def tap_create_button(serial):
    dump_ui(serial)
    try:
        tree = ET.parse(f"window_dump_{serial}.xml")
        root = tree.getroot()

        for node in root.iter():
            if (
                node.attrib.get("class") == "android.widget.Button"
                and node.attrib.get("content-desc") == "Create"
            ):
                bounds = node.attrib.get("bounds")
                parsed = get_bounds(bounds)
                if parsed:
                    x1, y1, x2, y2 = parsed
                    x = (x1 + x2) // 2
                    y = (y1 + y2) // 2
                    print(f"[{serial}] ✅ Tìm thấy nút Create tại ({x}, {y})")
                    adb_tap(x, y, serial)
                    return True
        print(f"[{serial}] ❌ Không tìm thấy nút Create.")
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi khi đọc UI: {e}")
    return False

# === Tìm và nhấn nút "Short" ===
def tap_short_button(serial):
    dump_ui(serial)
    try:
        tree = ET.parse(f"window_dump_{serial}.xml")
        root = tree.getroot()

        for node in root.iter():
            if (
                node.attrib.get("class") == "android.widget.Button"
                and node.attrib.get("text") == "Short"
                and node.attrib.get("resource-id") == "com.google.android.youtube:id/creation_mode_button"
            ):
                bounds = node.attrib.get("bounds")
                parsed = get_bounds(bounds)
                if parsed:
                    x1, y1, x2, y2 = parsed
                    x = (x1 + x2) // 2
                    y = (y1 + y2) // 2
                    print(f"[{serial}] ✅ Tìm thấy nút Short tại ({x}, {y})")
                    adb_tap(x, y, serial)
                    return True
        print(f"[{serial}] ❌ Không tìm thấy nút Short.")
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi khi đọc UI: {e}")
    return False

# === Chạy toàn bộ các bước ===
def run(serial):
    print(f"[{serial}] ▶️ Bắt đầu workflow...")

    open_youtube(serial)

    if wait_until_ui_has(serial, "Create", timeout=10):
        tap_create_button(serial)

    if wait_until_ui_has(serial, "Short", timeout=10):
        tap_short_button(serial)

if __name__ == "__main__":
    serial = "emulator-5554"
    run(serial)
