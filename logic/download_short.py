import os
import json
import subprocess
from googleapiclient.discovery import build
import yt_dlp
import isodate
import concurrent.futures

DOWNLOADED_FILE = "downloaded_videos.json"
ASSIGNED_FILE = "video_assigned.json"

def load_downloaded_list():
    if os.path.exists(DOWNLOADED_FILE):
        with open(DOWNLOADED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_downloaded_list(data):
    with open(DOWNLOADED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def save_assignment(data):
    with open(ASSIGNED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def run_download_process(api_key, adb_path, remote_folder, temp_folder,
                         search_video_query, number_of_videos=None):

    def get_emulator_serials():
        result = subprocess.getoutput(f'"{adb_path}" devices')
        lines = result.strip().splitlines()[1:]
        return [line.split()[0] for line in lines if "emulator" in line and "device" in line]

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

        downloaded_ids = {entry["video_id"] for entry in load_downloaded_list()}
        scored_videos = []

        for item in video_response["items"]:
            vid = item["id"]
            if vid in downloaded_ids:
                continue

            if item["snippet"].get("liveBroadcastContent") == "live":
                continue

            try:
                duration_sec = int(isodate.parse_duration(item["contentDetails"]["duration"]).total_seconds())
                if duration_sec > 60:
                    continue
            except:
                continue

            stats = item.get("statistics", {})
            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            score = likes * 10 + views
            scored_videos.append((vid, score, views, likes))

        scored_videos.sort(key=lambda x: x[1], reverse=True)
        return scored_videos[:number_of_videos]

    def download_and_push(serial, video_id):
        os.makedirs(temp_folder, exist_ok=True)
        file_path = os.path.join(temp_folder, f"{video_id}.mp4")
        url = f"https://www.youtube.com/watch?v={video_id}"

        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "merge_output_format": "mp4",
            "outtmpl": file_path,
            "quiet": False
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"[{serial}] Lỗi tải: {e}")
            return False

        subprocess.run([adb_path, "-s", serial, "push", file_path, remote_folder])
        subprocess.run([adb_path, "-s", serial, "shell", "am", "broadcast",
                        "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
                        "-d", f"file://{remote_folder}{video_id}.mp4"])
        os.remove(file_path)
        return True

    serials = get_emulator_serials()
    if not serials:
        print("❌ Không có máy ảo nào.")
        return

    if number_of_videos is None:
        number_of_videos = len(serials)

    print(f"🔍 Có {len(serials)} máy ảo:", serials)
    for serial in serials:
        subprocess.run([adb_path, "-s", serial, "shell", "rm", f"{remote_folder}*.mp4"])

    top_videos = get_top_shorts(search_video_query, number_of_videos)
    downloaded = load_downloaded_list()
    assignment = {}

    for serial, (vid, _, views, likes) in zip(serials, top_videos):
        print(f"\n[🎯 {serial}] Nhận video: {vid} - {views} views / {likes} likes")
        if download_and_push(serial, vid):
            downloaded.append({"video_id": vid, "serial": serial})
            assignment[serial] = vid
            print(f"[{serial}] ✅ Hoàn tất và gán video.")
        else:
            print(f"[{serial}] ❌ Thất bại khi tải/gán video.")

    save_downloaded_list(downloaded)
    save_assignment(assignment)
    print("\n✅ Đã đẩy và gán video xong.")
