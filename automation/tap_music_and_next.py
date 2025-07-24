import subprocess
import time

def adb_tap(x, y, serial="emulator-5554"):
    subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

def tap_first_music_item_and_arrow(serial="emulator-5554"):
    # Bước 1: Tap bài nhạc đầu tiên
    x1, y1 = 310, 434  # trung tâm của [0,348][620,520]
    print(f"✅ Tap bài nhạc đầu tiên tại ({x1}, {y1})")
    adb_tap(x1, y1, serial)

    # Bước 2: Đợi 1 giây cho giao diện phản hồi
    time.sleep(1)

    # Bước 3: Tap nút mũi tên bên phải cùng hàng
    x2, y2 = 678, 447  # trung tâm của [660,378][696,516]
    print(f"✅ Tap nút mũi tên cùng dòng tại ({x2}, {y2})")
    adb_tap(x2, y2, serial)

if __name__ == "__main__":
    tap_first_music_item_and_arrow()
