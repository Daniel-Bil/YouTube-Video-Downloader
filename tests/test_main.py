import pytest
from PySide6.QtWidgets import QApplication

from main import YouTubeDownloader

@pytest.fixture
def app(qtbot):
    app = QApplication.instance() or QApplication([])
    return app

@pytest.fixture
def yt_downloader(app):
    yt_downloader = YouTubeDownloader()
    return yt_downloader

def test_default_combo_equals_none(yt_downloader):
    assert yt_downloader.combo.currentText() == "None"


def test_addition_to_combo(yt_downloader):
    yt_downloader.combo.addItem("new_item")
    yt_downloader.combo.addItem("new_item2")
    assert yt_downloader.combo.count() == 3