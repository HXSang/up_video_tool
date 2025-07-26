import os
import sys
import subprocess
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFileDialog, QHeaderView, QMessageBox

# ✅ Đưa thư mục cha vào sys.path TRƯỚC KHI import các module tự viết
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logic.download_short import run_download_process
from assign_video import assign_videos_to_emulators, get_emulator_serials
from gui.automation.adjust_volume_control import ActionSync
from gui.automation.full_action import run_with_sync
from concurrent.futures import ThreadPoolExecutor



class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        ui_path = os.path.join(os.path.dirname(__file__), "untitled.ui")
        uic.loadUi(ui_path, self)

        self.button_adb_path.clicked.connect(self.choose_adb_path)
        self.button_remote_folder.clicked.connect(self.choose_remote_folder)
        self.button_temp_folder.clicked.connect(self.choose_temp_folder)
        self.button_run.clicked.connect(self.run_task)

        QTimer.singleShot(0, self.adjust_table_columns)

    def adjust_table_columns(self):
        try:
            table = self.table_status
            header = table.horizontalHeader()
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.Stretch)
            table.setColumnWidth(0, 50)
        except:
            pass

    def choose_adb_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục ADB")
        if folder:
            self.line_adb_path.setText(folder)

    def choose_remote_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục Remote")
        if folder:
            self.line_remote_folder.setText(folder)

    def choose_temp_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục Temp")
        if folder:
            self.line_temp_folder.setText(folder)

    def run_task(self):
        api_key = self.line_youtube.text().strip()
        adb_path = self.line_adb_path.text().strip()
        remote_folder = self.line_remote_folder.text().strip() or "/sdcard/Movies/"
        temp_folder = self.line_temp_folder.text().strip() or "./temp_videos"
        search_query = self.line_search_video.text().strip()
        song_name = self.line_search_music.text().strip()
        number_str = self.line_number_video.text().strip()

        voice_str = self.line_volume_video.text().strip()
        music_str = self.line_volume_music.text().strip()
        try:
            voice_percent = int(voice_str)
        except:
            voice_percent = 100
        try:
            music_percent = int(music_str)
        except:
            music_percent = 50

        if number_str:
            try:
                number_of_videos = int(number_str)
                if number_of_videos <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Lỗi", "NUMBER_VIDEOS phải là số nguyên dương.")
                return
        else:
            number_of_videos = None

        if not api_key or not adb_path or not search_query:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Vui lòng nhập API Key, ADB path và từ khóa video.")
            return

        try:
            # 1. Tải video
            run_download_process(
                api_key=api_key,
                adb_path=adb_path,
                remote_folder=remote_folder,
                temp_folder=temp_folder,
                search_video_query=search_query,
                number_of_videos=number_of_videos
            )

            # 2. Gán video cho từng máy
            assign_videos_to_emulators(adb_path)

            # 3. Lấy danh sách serials
            serials = get_emulator_serials(adb_path)
            if not serials:
                QMessageBox.warning(self, "Không có thiết bị", "Không tìm thấy máy ảo nào đang chạy.")
                return

            # 4. Tạo đối tượng đồng bộ
            sync = ActionSync(len(serials))

            # 5. Hàm chạy từng máy
            def task(serial):
                print(f"▶️ Chạy upload + nhạc trên {serial}")
                run_with_sync(
                    serial=serial,
                    api_key=api_key,
                    sync=sync,
                    song_name=song_name,
                    voice_percent=voice_percent,
                    music_percent=music_percent,
                    adb_path=adb_path
                )

            # 6. Chạy tất cả máy ảo đồng thời và đồng bộ
            with ThreadPoolExecutor(max_workers=len(serials)) as executor:
                executor.map(task, serials)

            QMessageBox.information(self, "Thành công", "Đã hoàn tất toàn bộ luồng.")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xử lý: {str(e)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
