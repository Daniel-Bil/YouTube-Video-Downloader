import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel, QMessageBox
)
import yt_dlp
from pathlib import Path


class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the window
        my_icon = QIcon()
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS when frozen
            icon_base_path = Path(sys._MEIPASS)
        except AttributeError:
            # If not frozen, use the current directory (normal Python execution)
            icon_base_path = Path()
        my_icon.addFile(str(icon_base_path / Path("images/icon.png")))
        self.setWindowIcon(my_icon)

        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(400, 400, 400, 150)

        # Create layout
        layout = QVBoxLayout()

        # Create label and text input for URL
        self.url_label = QLabel("Enter YouTube URL:", self)
        layout.addWidget(self.url_label)

        self.url_input = QLineEdit(self)
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
        # Get the YouTube URL from the text input
        video_url = self.url_input.text()

        # Check if URL and directory are provided
        if not video_url:
            QMessageBox.warning(self, "Input Error", "Please enter a YouTube URL.")
            return

        if not self.download_directory:
            QMessageBox.warning(self, "Directory Error", "Please select a download directory.")
            return

        try:
            # Download video using yt-dlp

            try:
                # PyInstaller creates a temp folder and stores path in _MEIPASS when frozen
                base_path = Path(sys._MEIPASS)
            except AttributeError:
                # If not frozen, use the current directory (normal Python execution)
                base_path = Path()

            # Locate ffmpeg in the temp directory or working directory
            ffmpeg_path = base_path / "ffmpeg" / "bin" / "ffmpeg.exe"

            ydl_opts = {
                'outtmpl': str(self.download_directory / '%(title)s.%(ext)s'),
                'format': 'bestvideo+bestaudio/best',

                'ffmpeg_location': ffmpeg_path,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            QMessageBox.information(self, "Download Complete", "Video downloaded successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Download Error", f"An error occurred: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec())
