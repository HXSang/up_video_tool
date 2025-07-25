import os
import time
import subprocess
import xml.etree.ElementTree as ET
import re

from gui.automation.tap_create_short_button import tap_create_button, tap_short_button
from .tap_add_gallery_button import tap_add_gallery_button
from .tap_upload_short import tap_upload_short
from .tap_video_by_id import tap_video_by_id
from .tap_next_button import tap_next_button
from .tap_done_button import tap_done_button
from .tap_add_sound_button import tap_add_sound_button
from .pick_first_music_and_next import pick_first_music_and_next
from .search_music import search_music
from .video_utils import get_video_id_for_serial
from .tap_checkmark_button import tap_checkmark_button
from .tap_next_button_final import tap_next_button_final
from .adjust_volume_dynamic import adjust_volume_dynamic
from .get_pust_title import set_title_from_video_id

ADB_PATH = "C:\\Users\\dell\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe"

def open_youtube(serial):
    print(f"[{serial}] 🚀 Mở YouTube...")
    os.system(f'"{ADB_PATH}" -s {serial} shell monkey -p com.google.android.youtube -c android.intent.category.LAUNCHER 1')
    time.sleep(3)

def dump_ui(serial):
    subprocess.run([ADB_PATH, "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    subprocess.run([ADB_PATH, "-s", serial, "pull", "/sdcard/window_dump.xml", f"window_dump_{serial}.xml"], stdout=subprocess.DEVNULL)

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
                    print(f"[{serial}] ✅ Tìm thấy UI: '{keyword}'")
                    return True
        except Exception as e:
            print(f"[{serial}] ⚠️ Lỗi khi đọc XML: {e}")
        time.sleep(1)
    print(f"[{serial}] ❌ Hết thời gian chờ UI có '{keyword}'")
    return False

def wait_until_add_sound_visible(serial, max_wait=120):
    print(f"[{serial}] ⏳ Chờ đến khi thấy nút 'Add sound' (tối đa {max_wait}s)...")
    start = time.time()
    xml_file = f"window_dump_{serial}.xml"

    while time.time() - start < max_wait:
        subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
        subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml", xml_file], stdout=subprocess.DEVNULL)

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for node in root.iter():
                if (
                    node.attrib.get("resource-id") == "com.google.android.youtube:id/sound_button_title" and
                    node.attrib.get("text") == "Add sound" and
                    node.attrib.get("enabled") == "true"
                ):
                    print(f"[{serial}] ✅ Đã thấy nút 'Add sound'")
                    return True
        except Exception as e:
            print(f"[{serial}] ⚠️ Lỗi khi đọc XML: {e}")

        time.sleep(2)

    print(f"[{serial}] ❌ Hết thời gian chờ nút 'Add sound'")
    return False

def wait_until_volume_ui_visible(serial, max_wait=60):
    print(f"[{serial}] ⏳ Chờ giao diện chỉnh âm lượng (tối đa {max_wait}s)...")
    xml_file = f"window_dump_{serial}.xml"
    start = time.time()

    while time.time() - start < max_wait:
        subprocess.run(["adb", "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
        subprocess.run(["adb", "-s", serial, "pull", "/sdcard/window_dump.xml", xml_file], stdout=subprocess.DEVNULL)

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            if root is None:
                raise ValueError("Root node is null.")
        except Exception as e:
            print(f"[{serial}] ⚠️ XML dump lỗi hoặc rỗng: {e}")
            time.sleep(2)
            continue

        for node in root.iter():
            if (
                node.attrib.get("resource-id") == "com.google.android.youtube:id/shorts_edit_volume_button"
                and node.attrib.get("class") == "android.widget.Button"
                and node.attrib.get("content-desc", "").lower() == "volume"
                and node.attrib.get("enabled") == "true"
            ):
                print(f"[{serial}] ✅ Giao diện chỉnh âm lượng đã sẵn sàng.")
                return True

        time.sleep(2)

    print(f"[{serial}] ❌ Hết thời gian chờ giao diện âm lượng.")
    return False

def run(serial, song_name=None, api_key=None, voice_percent=100, music_percent=50):
    print(f"\n========== BẮT ĐẦU LUỒNG [{serial}] ==========")

    open_youtube(serial)

    if wait_until_ui_has(serial, "Create", timeout=10):
        tap_create_button(serial)

    if wait_until_ui_has(serial, "Short", timeout=10):
        tap_short_button(serial)

    if wait_until_ui_has(serial, "reel_camera_gallery_button_delegate", timeout=10):
        tap_add_gallery_button(serial)

        video_id = get_video_id_for_serial(serial)
        if video_id:
            tap_video_by_id(video_id, serial)
        else:
            print(f"[{serial}] ⚠️ Không tìm thấy video ID trong video_assigned.json")

        tap_next_button(serial)
        tap_done_button(serial)

        if not wait_until_add_sound_visible(serial, max_wait=120):
            print(f"[{serial}] ❌ Không thấy nút Add sound sau khi upload xong.")
            return

        tap_add_sound_button(serial)

        if song_name:
            search_music(song_name, serial)
            time.sleep(2)
            pick_first_music_and_next(serial)
        else:
            print(f"[{serial}] ⚠️ Không có tên bài nhạc được cung cấp.")

        if not wait_until_ui_has(serial, "shorts_camera_next_button_delegate", timeout=20):
            print(f"[{serial}] ❌ Không tìm thấy nút V (Checkmark) sau khi thêm nhạc.")
            return

        tap_checkmark_button(serial)

        # 🔊 Bổ sung quét giao diện chỉnh âm lượng bằng XML
        if wait_until_volume_ui_visible(serial, max_wait=60):
            adjust_volume_dynamic(serial, voice_percent, music_percent)
        else:
            print(f"[{serial}] ⚠️ Bỏ qua chỉnh volume vì không thấy giao diện.")

        if not wait_until_ui_has(serial, "shorts_upload_button", timeout=20):
            print(f"[{serial}] ❌ Không tìm thấy nút Next cuối.")
        else:
            tap_next_button_final(serial)

        if video_id and api_key:
            set_title_from_video_id(video_id, api_key, serial)
        else:
            print(f"[{serial}] ⚠️ Thiếu video_id hoặc api_key, không thể đặt tiêu đề.")

    print(f"========== ✅ KẾT THÚC LUỒNG [{serial}] ==========\n")
