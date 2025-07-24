import subprocess
import time

def get_video_title(video_id, api_key):
    from googleapiclient.discovery import build
    youtube = build("youtube", "v3", developerKey=api_key)
    response = youtube.videos().list(part="snippet", id=video_id).execute()
    items = response.get("items", [])
    if not items:
        return None
    return items[0]["snippet"]["title"]

def adb_tap(x, y, serial="emulator-5554"):
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

def adb_input_text(text, serial="emulator-5554"):
    safe_text = text.replace(" ", "%s").replace("&", "\\&").replace('"', '\\"')
    subprocess.run(["adb", "-s", serial, "shell", "input", "text", safe_text])

def input_caption_from_title(video_id, api_key, serial="emulator-5554"):
    title = get_video_title(video_id, api_key)
    if not title:
        print("❌ Không tìm thấy tiêu đề video.")
        return

    print(f"📋 Tiêu đề lấy được: {title}")

    # Tap vào ô caption
    x, y = 457, 224  # tọa độ ô "Caption your Short"
    print(f"✅ Tap vào ô caption tại ({x}, {y})")
    adb_tap(x, y, serial)
    time.sleep(1)

    # Nhập tiêu đề vào ô
    print("⌨️  Đang nhập tiêu đề...")
    adb_input_text(title, serial)

if __name__ == "__main__":
    VIDEO_ID = "q2HPS4pBSAE"        # Thay ID video bạn đang xử lý
    API_KEY = "AIzaSyB_erdAHuHDQOUIKRZemFfzKrR-HQ0Ma6A"  # Thay bằng API Key thật của bạn
    input_caption_from_title(VIDEO_ID, API_KEY)
