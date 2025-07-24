import os
import time
import threading
import subprocess
import pyperclip
from download_short import get_video_title

ADB_PATH = 'C:\\Users\\ADMIN\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe'

def run_adb(cmd, serial):
    subprocess.run([ADB_PATH, "-s", serial, "shell"] + cmd.split(), shell=False)

def tap(x, y, serial, delay=4):
    run_adb(f"input tap {x} {y}", serial)
    time.sleep(delay)

def open_youtube(serial):
    print(f"[{serial}] 🚀 Mở YouTube")
    os.system(f'"{ADB_PATH}" -s {serial} shell monkey -p com.google.android.youtube -c android.intent.category.LAUNCHER 1')
    time.sleep(5)

def input_text_and_search(text, serial):
    print(f"[{serial}] 🔍 Nhập và tìm kiếm: {text}")
    tap(210, 180, serial, 3)  # Nhấn vào ô tìm kiếm
    pyperclip.copy('')
    formatted_text = text.replace(" ", "%s")
    run_adb(f'input text {formatted_text}', serial)
    time.sleep(1)
    run_adb("input keyevent 66", serial)   # Enter
    time.sleep(4)

def input_title(text, serial):
    print(f"[{serial}] 📝 Nhập tiêu đề video: {text}")
    pyperclip.copy(text)
    tap(251, 362, serial, 2)
    run_adb("input keyevent 279", serial)
    pyperclip.copy('')

def run_workflow(serial):
    print(f"[{serial}] ▶️ Bắt đầu quy trình đăng Shorts")
    open_youtube(serial)
    tap(360, 1200, serial)  # Nút +
    tap(80, 1040, serial)   # Chọn video
    tap(80, 440, serial)
    tap(611, 1157, serial)  # Tiếp theo
    tap(611, 1157, serial)  # Done
    time.sleep(90)
    tap(611,1040, serial)
    tap(350, 120, serial)   # Thêm âm thanh
    tap(340, 180, serial)   # Tìm kiếm
    input_text_and_search("Duc hugolina", serial)
    tap(260, 410, serial,2)   # Chọn gợi ý đầu
    tap(629, 416, serial)  # Chọn nhạc
    tap(521, 1175, serial)  # Tiếp
    tap(342, 208, serial)
    time.sleep(5)
    input_title("Thả diều 5 mét cậu bé kéo diều nhảy lên cao lướt trên sân quá hay", serial)
    time.sleep(5)
    tap(521, 596, serial)  # Đăng
    print(f"[{serial}] ✅ Hoàn tất")

# ✅ Hàm tự động lấy danh sách các máy ảo emulator đang chạy
def get_emulator_serials():
    result = subprocess.getoutput("adb devices")
    lines = result.strip().splitlines()[1:]  # Bỏ dòng đầu
    serials = [line.split()[0] for line in lines if "emulator" in line]
    return serials

def main():
    serials = get_emulator_serials()
    if not serials:
        print("❌ Không có máy ảo nào đang chạy.")
        return

    threads = []
    for serial in serials:
        t = threading.Thread(target=run_workflow, args=(serial,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("🎉 Tất cả máy đã hoàn tất quy trình.")

if __name__ == "__main__":
    main()
