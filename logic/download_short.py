import os
import json
import subprocess
from googleapiclient.discovery import build
import yt_dlp
import isodate
import concurrent.futures

DOWNLOADED_FILE = "downloaded_videos.json"

def load_downloaded_ids():
    if os.path.exists(DOWNLOADED_FILE):
        with open(DOWNLOADED_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_downloaded_ids(ids_set):
    with open(DOWNLOADED_FILE, "w") as f:
        json.dump(sorted(list(ids_set)), f, indent=2)

def run_download_process(api_key, adb_path, remote_folder, temp_folder,
                         search_video_query, number_of_videos=None):

    def get_emulator_serials():
        result = subprocess.getoutput(f'"{adb_path}" devices')
        lines = result.strip().splitlines()[1:]
        serials = [line.split()[0] for line in lines if "emulator" in line and "device" in line]
        return serials

    def get_video_title(video_id):
        youtube = build("youtube", "v3", developerKey=api_key)
        response = youtube.videos().list(part="snippet", id=video_id).execute()
        items = response.get("items", [])
        return items[0]["snippet"]["title"] if items else None

    def get_top_shorts(query, number_of_videos, search_pool=30):
        youtube = build("youtube", "v3", developerKey=api_key)
        search_response = youtube.search().list(
            q=query,
            part="id",
            type="video",
            maxResults=search_pool,
            order="viewCount"
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search_response["items"]]
        video_response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(video_ids)
        ).execute()

        scored_videos = []
        for item in video_response["items"]:
            vid = item["id"]
            if vid in downloaded_ids:
                continue

            # Bỏ livestream
            if item["snippet"].get("liveBroadcastContent") == "live":
                print(f"⛔ Bỏ livestream: {vid}")
                continue

            duration_str = item["contentDetails"]["duration"]
            try:
                duration_sec = int(isodate.parse_duration(duration_str).total_seconds())
                if duration_sec > 60:
                    print(f"⏭️ Bỏ video dài: {vid} ({duration_sec}s)")
                    continue
            except:
                continue

            stats = item["statistics"]
            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0)) if "likeCount" in stats else 0
            score = likes * 10 + views
            scored_videos.append((vid, score, views, likes))

        scored_videos.sort(key=lambda x: x[1], reverse=True)
        return scored_videos[:number_of_videos]

    def refresh_media_on_emulator(serial, filepath):
        subprocess.run([
            adb_path, "-s", serial, "shell", "am", "broadcast",
            "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
            "-d", f"file://{filepath}"
        ], check=False)

    def clear_remote_videos(serial):
        print(f"[{serial}] Xóa toàn bộ video trên máy ảo...")
        subprocess.run([adb_path, "-s", serial, "shell", "rm", f"{remote_folder}*.mp4"], check=False)

    def download_and_push_to_emulator(video_id, serial):
        os.makedirs(temp_folder, exist_ok=True)
        local_path = os.path.join(temp_folder, f"{video_id}.mp4")
        url = f"https://www.youtube.com/watch?v={video_id}"

        print(f"[{serial}] Tải video ID: {video_id}")
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "merge_output_format": "mp4",
            "outtmpl": local_path,
            "quiet": False,
            "noplaylist": True,
            "match_filter": lambda info: "LIVE" if info.get("is_live") else None,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"[{serial}] ⚠️ Lỗi khi tải video: {e}")
            if os.path.exists(local_path + ".part"):
                os.remove(local_path + ".part")
            return

        if not os.path.exists(local_path):
            print(f"[{serial}] ⚠️ Không tìm thấy file sau khi tải: {local_path}")
            return

        print(f"[{serial}] Đẩy vào máy ảo...")
        subprocess.run([adb_path, "-s", serial, "push", local_path, remote_folder], check=True)
        refresh_media_on_emulator(serial, remote_folder + os.path.basename(local_path))

        os.remove(local_path)

        downloaded_ids.add(video_id)
        save_downloaded_ids(downloaded_ids)

        print(f"[{serial}] Hoàn tất")

    def handle_emulator_task(idx, serial, vid, views, likes):
        try:
            title = get_video_title(vid)
            print(f"\nMáy ảo {idx} ({serial}) nhận video TOP {idx}")
            print(f"{title} — {views} views / {likes} likes")
            download_and_push_to_emulator(vid, serial)
        except Exception as e:
            print(f"[{serial}] Lỗi: {e}")

    serials = get_emulator_serials()
    if not serials:
        print("Không tìm thấy máy ảo nào.")
        return

    if number_of_videos is None:
        number_of_videos = len(serials)

    print(f"Tìm thấy {len(serials)} máy ảo:", serials)

    for serial in serials:
        clear_remote_videos(serial)

    global downloaded_ids
    downloaded_ids = load_downloaded_ids()

    top_videos = get_top_shorts(query=search_video_query, number_of_videos=number_of_videos, search_pool=50)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(serials)) as executor:
        futures = []
        for idx, (serial, (vid, score, views, likes)) in enumerate(zip(serials, top_videos), start=1):
            futures.append(
                executor.submit(handle_emulator_task, idx, serial, vid, views, likes)
            )
        concurrent.futures.wait(futures)

    print("\nĐã đẩy xong video lên tất cả máy ảo.")
