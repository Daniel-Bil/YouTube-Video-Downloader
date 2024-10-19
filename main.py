import argparse
from pathlib import Path
import yt_dlp

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that downloads yt videos")

    parser.add_argument("--url", type=str, help="url")
    args = parser.parse_args()

    current_directory = Path()
    videos_directory = current_directory / "videos"

    videos_directory.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': str(videos_directory / '%(title)s.%(ext)s'),  # Save in the videos folder with the title as the filename
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([args.url])


