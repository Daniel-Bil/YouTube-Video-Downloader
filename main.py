import sys

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel, QMessageBox, QComboBox
)
import yt_dlp
from pathlib import Path

class DownloadThread(QThread):
    progress_updated = Signal(int)

    def __init__(self, url, output_path, ffmpeg_path, format_str):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.ffmpeg_path = ffmpeg_path
        self.format_str = format_str

        self.video_progress = 0
        self.audio_progress = 0
        self.video_size = 0
        self.audio_size = 0

    def run(self):
        print("run")
        try:
            # Download video using yt-dlp
            # Locate ffmpeg in the temp directory or working directory

            format_id = self.format_str.split(" | ")[0]  # Extract the format ID (first part of the string)
            ext = self.format_str.split(" | ")[1].lower()
            print(format_id, ext)
            if ext == "mp4":
                ydl_opts = {
                    'outtmpl': self.output_path,
                    'format': f"{format_id}+bestaudio/best",
                    'merge_output_format': ext,
                    'progress_hooks': [self.progress_hook],
                    'ffmpeg_location': self.ffmpeg_path,
                }
            elif ext == "webm":
                ydl_opts = {
                    'outtmpl': self.output_path,
                    'format': f"{format_id}+bestaudio/best",
                    'merge_output_format': ext,
                    'progress_hooks': [self.progress_hook],
                    'ffmpeg_location': self.ffmpeg_path,
                }
            else:
                raise Exception(f"wrong extension {ext}")


            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            # QMessageBox.information(self, "Download Complete", "Video downloaded successfully!")
            print("download complete")
        except Exception as e:
            print("Download Error")

            print(e)
            # QMessageBox.critical(self, "Download Error", f"An error occurred: {e}")

    def progress_hook(self, response):
        # Monitor the download progress
        if response['status'] == 'downloading':
            percent_str = response['_percent_str'].strip('%')
            try:
                percent = int(float(percent_str))
                self.progress_updated.emit(percent)  # Emit progress to the GUI
            except ValueError:
                pass


class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()

        # PyInstaller creates a temp folder and stores path in _MEIPASS when frozen
        # If not frozen, use the current directory (normal Python execution)
        try:
            self.base_path = Path(sys._MEIPASS)
        except AttributeError:
            self.base_path = Path()

        # Set up the window
        my_icon = QIcon()
        my_icon.addFile(str(self.base_path / Path("images/icon.png")))
        self.setWindowIcon(my_icon)

        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(400, 400, 400, 150)

        # Create layout
        layout = QVBoxLayout()

        # Create label and text input for URL
        self.url_label = QLabel("Enter YouTube URL:", self)
        layout.addWidget(self.url_label)

        self.url_input = QLineEdit(self)
        self.url_input.textChanged.connect(self.fetch_formats)
        layout.addWidget(self.url_input)

        # Button to choose download directory
        self.dir_button = QPushButton("Choose Download Directory", self)
        self.dir_button.clicked.connect(self.choose_directory)
        layout.addWidget(self.dir_button)

        # Label to show selected directory
        self.dir_label = QLabel("Selected Directory: None", self)
        layout.addWidget(self.dir_label)

        # Button to download video
        self.download_button = QPushButton("Download Video", self)
        self.download_button.clicked.connect(self.download_video)
        layout.addWidget(self.download_button)

        self.progress_label = QLabel("Download Progress: 0%")
        layout.addWidget(self.progress_label)

        self.combo = QComboBox()
        self.combo.addItem("None")

        layout.addWidget(self.combo)

        # Set layout
        self.setLayout(layout)

        # Default download directory
        self.download_directory = None

    def choose_directory(self):
        # Open file dialog to choose directory
        dir_path = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if dir_path:
            self.download_directory = Path(dir_path)
            self.dir_label.setText(f"Selected Directory: {self.download_directory}")
        else:
            self.dir_label.setText("Selected Directory: None")

    def download_video(self):
        ffmpeg_path = self.base_path / "ffmpeg" / "bin" / "ffmpeg.exe"

        # Get the YouTube URL from the text input
        video_url = self.url_input.text()

        selected_format = self.combo.currentText()
        print(self.combo.currentIndex())

        # Check if URL and directory are provided
        if not video_url:
            QMessageBox.warning(self, "Input Error", "Please enter a YouTube URL.")
            return

        if not self.download_directory:
            QMessageBox.warning(self, "Directory Error", "Please select a download directory.")
            return

        self.download_thread = DownloadThread(video_url, str(self.download_directory / '%(title)s.%(ext)s'),
                                              str(ffmpeg_path), format_str=selected_format)

        # Connect progress signal to update the progress label
        self.download_thread.progress_updated.connect(self.update_progress)

        # Start the download thread
        self.download_thread.start()

    def update_progress(self, progress):
        # Update the GUI with download progress
        self.progress_label.setText(f"Download Progress: {progress}%")

    def fetch_formats(self, url: str) -> None:

        if "youtube" not in url:
            return
        ydl_opts = {
            'listformats': True,
        }
        available_formats = []

        # Extract formats from yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])

                for fmt in formats:
                    format_id = fmt.get('format_id')
                    ext = fmt.get('ext')
                    resolution = fmt.get('resolution', 'audio only')
                    filesize = fmt.get('filesize', 'Unknown')
                    if filesize == "Unknown":
                        continue

                    if not isinstance(filesize, str):
                        filesize_mb = round(filesize / (1024 * 1024), 2)
                        filesize_str = f"{filesize_mb} MB"
                    else:
                        filesize_str = filesize
                    format_str = f"{format_id} | {ext.upper()} | {resolution} | {filesize_str if filesize_str else 'N/A'}"
                    available_formats.append(format_str)

            except yt_dlp.utils.DownloadError:
                self.download_button.setText("Invalid URL or unable to fetch formats.")
                self.download_button.setEnabled(False)
                return

        # Populate the combo box with available formats
        self.combo.clear()
        if available_formats:
            self.combo.addItems(available_formats[::-1])
            self.combo.setCurrentIndex(0)
        else:
            self.download_button.setText("No available formats found.")
            self.download_button.setEnabled(False)
            return

        self.download_button.setText("Download video")
        self.download_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec())
