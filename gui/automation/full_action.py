import os
import time
import subprocess
import xml.etree.ElementTree as ET
import json
import re

from gui.automation import tap_volume_button
from gui.automation.set_title_dynamic import set_title_from_video_id
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
from .tap_volume_button import tap_volume_button
from .adjust_volume_control import adjust_volume_with_sync
from .tap_next_button_final import tap_next_button_final
from gui.automation.adjust_volume_control import ActionSync

UPLOADED_FILE = os.path.join(os.getcwd(), "uploaded_videos.json")

def load_uploaded_ids():
    if os.path.exists(UPLOADED_FILE):
        with open(UPLOADED_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_uploaded_ids(ids_set):
    with open(UPLOADED_FILE, "w") as f:
        json.dump(sorted(list(ids_set)), f, indent=2)

def open_youtube(serial, adb_path):
    print(f"[{serial}] Mở YouTube...")
    subprocess.run([adb_path, "-s", serial, "shell", "monkey", "-p", "com.google.android.youtube", "-c", "android.intent.category.LAUNCHER", "1"])
    time.sleep(3)

def dump_ui(serial, adb_path):
    subprocess.run([adb_path, "-s", serial, "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    subprocess.run([adb_path, "-s", serial, "pull", "/sdcard/window_dump.xml", f"window_dump_{serial}.xml"], stdout=subprocess.DEVNULL)

def wait_until_ui_has(serial, keyword, timeout=10, adb_path="adb"):
    print(f"[{serial}] Chờ UI chứa '{keyword}'...")
    start = time.time()
    while time.time() - start < timeout:
        dump_ui(serial, adb_path)
        try:
            tree = ET.parse(f"window_dump_{serial}.xml")
            root = tree.getroot()
            for node in root.iter():
                if (
                    keyword in node.attrib.get("content-desc", "") or
                    keyword in node.attrib.get("text", "") or
                    keyword in node.attrib.get("resource-id", "")
                ):
                    print(f"[{serial}] Tìm thấy UI: '{keyword}'")
                    return True
        except Exception as e:
            print(f"[{serial}] Lỗi khi đọc XML: {e}")
        time.sleep(1)
    print(f"[{serial}] Hết thời gian chờ UI có '{keyword}'")
    return False

def wait_until_add_sound_visible(serial, max_wait=120, adb_path="adb"):
    print(f"[{serial}] Chờ đến khi thấy nút 'Add sound' (tối đa {max_wait}s)...")
    start = time.time()
    xml_file = f"window_dump_{serial}.xml"

    while time.time() - start < max_wait:
        dump_ui(serial, adb_path)
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for node in root.iter():
                if (
                    node.attrib.get("resource-id") == "com.google.android.youtube:id/sound_button_title" and
                    node.attrib.get("text") == "Add sound" and
                    node.attrib.get("enabled") == "true"
                ):
                    print(f"[{serial}] Đã thấy nút 'Add sound'")
                    return True
        except Exception as e:
            print(f"[{serial}] Lỗi khi đọc XML: {e}")

        time.sleep(2)

    print(f"[{serial}] Hết thời gian chờ nút 'Add sound'")
    return False

def run_with_sync(serial, api_key, sync: ActionSync, song_name=None, voice_percent=99, music_percent=50, adb_path=None):
    if not adb_path or not os.path.exists(adb_path):
        print(f"[{serial}] ADB path không hợp lệ hoặc không được truyền từ GUI.")
        return

    print(f"\n========== BẮT ĐẦU LUỒNG [{serial}] ==========")

    open_youtube(serial, adb_path)
    sync.wait(f"[{serial}] ✅ Mở YouTube xong")

    if wait_until_ui_has(serial, "Create", timeout=10, adb_path=adb_path):
        tap_create_button(serial)
    sync.wait(f"[{serial}] ✅ Tap nút 'Create' xong")

    if wait_until_ui_has(serial, "Short", timeout=10, adb_path=adb_path):
        tap_short_button(serial)
    sync.wait(f"[{serial}] ✅ Tap nút 'Short' xong")

    if wait_until_ui_has(serial, "reel_camera_gallery_button_delegate", timeout=10, adb_path=adb_path):
        tap_add_gallery_button(serial)
        sync.wait(f"[{serial}] ✅ Tap 'Add gallery' xong")

        video_id = get_video_id_for_serial(serial)
        if video_id:
            tap_video_by_id(video_id, serial)
        else:
            print(f"[{serial}] Không tìm thấy video ID trong video_assigned.json")

        tap_next_button(serial)
        tap_done_button(serial)
        sync.wait(f"[{serial}] ✅ Chọn video và Next xong")

        if not wait_until_add_sound_visible(serial, max_wait=120, adb_path=adb_path):
            print(f"[{serial}] Không thấy nút Add sound sau khi upload xong.")
            return

        tap_add_sound_button(serial)
        sync.wait(f"[{serial}] ✅ Tap Add Sound xong")

        if song_name:
            search_music(song_name, serial)
            time.sleep(4)
            pick_first_music_and_next(serial)
        else:
            print(f"[{serial}] Không có tên bài nhạc được cung cấp.")
        sync.wait(f"[{serial}] ✅ Đã chọn nhạc xong")

        if not wait_until_ui_has(serial, "shorts_camera_next_button_delegate", timeout=20, adb_path=adb_path):
            print(f"[{serial}] Không tìm thấy nút V (Checkmark) sau khi thêm nhạc.")
            return

        tap_checkmark_button(serial)
        sync.wait(f"[{serial}] ✅ Tap nút V xong")

        tap_volume_button(serial)
        time.sleep(3)

        adjust_volume_with_sync(serial, sync, voice_percent, music_percent, adb_path=adb_path)
        time.sleep(3)

        tap_next_button_final(serial)
        sync.wait(f"[{serial}] ✅ Tap nút Next Final xong")

        set_title_from_video_id(video_id, api_key, serial)
        time.sleep(5)

        tap_upload_short(serial)
        sync.wait(f"[{serial}] ✅ Đã upload video")

        uploaded_ids = load_uploaded_ids()
        uploaded_ids.add(video_id)
        save_uploaded_ids(uploaded_ids)
        print(f"[{serial}] ✅ Đã lưu videoId vào uploaded_videos.json: {video_id}")

    print(f"========== KẾT THÚC LUỒNG [{serial}] ==========\n")
