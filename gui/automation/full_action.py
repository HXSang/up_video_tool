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
from .action_sync import ActionSync

UPLOADED_FILE = os.path.join(os.getcwd(), "uploaded_videos.json")


def wait_until_done_enabled(serial, timeout=300, adb_path="adb"):
    print(f"[{serial}] ⏳ Đang chờ nút Done sẵn sàng...")
    start_time = time.time()
    xml_file = f"window_dump_{serial}.xml"
    tap_interval = 5  # Tap mỗi 5 giây
    last_tap = 0

    while time.time() - start_time < timeout:
        now = time.time()
        if now - last_tap >= tap_interval:
            # Tap giữa màn hình để hiện nút Done
            subprocess.run([adb_path, "-s", serial, "shell", "input", "tap", "500", "500"])
            print(f"[{serial}] 👆 Tap giữa màn hình để hiện nút Done")
            last_tap = now

        dump_ui(serial, adb_path)
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for node in root.iter():
                if (
                    node.attrib.get("resource-id") == "com.google.android.youtube:id/shorts_trim_finish_trim_button"
                    and node.attrib.get("enabled") == "true"
                ):
                    print(f"[{serial}] ✅ Nút Done đã sẵn sàng.")
                    return True
        except Exception as e:
            print(f"[{serial}] ⚠️ Lỗi khi kiểm tra nút Done: {e}")
        time.sleep(1)

    print(f"[{serial}] ❌ Hết thời gian chờ Done.")
    return False

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


def wait_until_add_sound_visible(serial, max_wait=300, adb_path="adb"):
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
                    node.attrib.get("resource-id") == "com.google.android.youtube:id/sound_button_title"
                    and node.attrib.get("text") == "Add sound"
                    and node.attrib.get("enabled") == "true"
                ):
                    print(f"[{serial}] Đã thấy nút 'Add sound'")
                    return True
        except Exception as e:
            print(f"[{serial}] Lỗi khi đọc XML: {e}")
        time.sleep(2)

    print(f"[{serial}] Hết thời gian chờ nút 'Add sound'")
    return False


def run_with_sync(serial, api_key, sync: ActionSync, song_name=None, voice_percent=98, music_percent=20, adb_path=None):
    if not adb_path or not os.path.exists(adb_path):
        print(f"[{serial}] ADB path không hợp lệ hoặc không được truyền từ GUI.")
        return

    print(f"\n========== BẮT ĐẦU LUỒNG [{serial}] ==========")

    try:
        open_youtube(serial, adb_path)
        sync.mark("youtube_opened", serial)
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi mở YouTube: {e}")
        sync.mark("youtube_opened", serial, status="failed")
        return

    sync.wait_threshold("youtube_opened", threshold=0.6)

    try:
        if wait_until_ui_has(serial, "Create", timeout=10, adb_path=adb_path):
            tap_create_button(serial)
            sync.mark("tap_create_done", serial)
        else:
            raise Exception("Không tìm thấy nút 'Create'")
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi bước 'Create': {e}")
        sync.mark("tap_create_done", serial, status="failed")
        return

    sync.wait_threshold("tap_create_done", threshold=0.6)

    try:
        if wait_until_ui_has(serial, "Short", timeout=10, adb_path=adb_path):
            tap_short_button(serial)
            sync.mark("tap_short_done", serial)
        else:
            raise Exception("Không tìm thấy nút 'Short'")
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi bước 'Short': {e}")
        sync.mark("tap_short_done", serial, status="failed")
        return

    # sync.wait_threshold("tap_short_done", threshold=0.6)

    try:
        if wait_until_ui_has(serial, "reel_camera_gallery_button_delegate", timeout=10, adb_path=adb_path):
            tap_add_gallery_button(serial)
            video_id = get_video_id_for_serial(serial)
            if not video_id:
                raise Exception("Không tìm thấy video ID")

            tap_video_by_id(video_id, serial)
            tap_next_button(serial)

            if wait_until_done_enabled(serial, timeout=300, adb_path=adb_path):
                tap_done_button(serial)
                sync.mark("select_video_done", serial)
            else:
                print(f"[{serial}] ❌ Hết thời gian chờ xử lý video")
                sync.mark("select_video_done", serial, status="failed")
                return
        else:
            raise Exception("Không tìm thấy nút Add gallery")
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi bước chọn video: {e}")
        sync.mark("select_video_done", serial, status="failed")
        return

    # sync.wait_threshold("select_video_done", threshold=0.6)

    try:
        if not wait_until_add_sound_visible(serial, max_wait=120, adb_path=adb_path):
            raise Exception("Không thấy nút Add sound")

        tap_add_sound_button(serial)

        if song_name:
            search_music(song_name, serial)
            time.sleep(4)
            pick_first_music_and_next(serial)
        else:
            print(f"[{serial}] Không có tên bài nhạc được cung cấp.")

        sync.mark("music_selected", serial)
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi khi chọn nhạc: {e}")
        sync.mark("music_selected", serial, status="failed")
        return

    # sync.wait_threshold("music_selected", threshold=0.6)

    try:
        if not wait_until_ui_has(serial, "shorts_camera_next_button_delegate", timeout=20, adb_path=adb_path):
            raise Exception("Không thấy nút checkmark")

        tap_checkmark_button(serial)
        sync.mark("checkmark_tapped", serial)
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi khi tap checkmark: {e}")
        sync.mark("checkmark_tapped", serial, status="failed")
        return

    # sync.wait_threshold("checkmark_tapped", threshold=0.6)

    try:
        tap_volume_button(serial)
        adjust_volume_with_sync(serial, voice_percent, music_percent, adb_path=adb_path)
        sync.mark("volume_adjusted", serial)
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi chỉnh âm lượng: {e}")
        sync.mark("volume_adjusted", serial, status="failed")
        return

    # sync.wait_threshold("volume_adjusted", threshold=0.6)

    try:
        tap_next_button_final(serial)
        sync.mark("final_next_tapped", serial)
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi khi tap nút Next Final: {e}")
        sync.mark("final_next_tapped", serial, status="failed")
        return

    # sync.wait_threshold("final_next_tapped", threshold=0.6)

    try:
        set_title_from_video_id(video_id, api_key, serial)
        time.sleep(5)
        tap_upload_short(serial)
        sync.mark("upload_done", serial)

        uploaded_ids = load_uploaded_ids()
        uploaded_ids.add(video_id)
        save_uploaded_ids(uploaded_ids)
        print(f"[{serial}] ✅ Đã lưu videoId vào uploaded_videos.json: {video_id}")
    except Exception as e:
        print(f"[{serial}] ❌ Lỗi khi upload video: {e}")
        sync.mark("upload_done", serial, status="failed")

    print(f"========== KẾT THÚC LUỒNG [{serial}] ==========\n")
