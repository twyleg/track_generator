import sys
import os
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Property


class TrackLiveView:

    class Model(QObject):
        def __init__(self, filename: str) -> None:
            QObject.__init__(self)
            self._filename = filename

        def get_filename(self) -> str:
            return self._filename

        def set_filename(self, filename: str) -> None:
            self._filename = filename
            self.filename_changed.emit()

        @Signal
        def filename_changed(self) -> None:
            pass

        @Signal
        def reloadImage(self) -> None:
            pass

        filename = Property(str, get_filename, set_filename, notify=filename_changed)

    def __init__(self, output_file_path: str):
        self.app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine()
        self.model = TrackLiveView.Model(output_file_path)

        self.engine.rootContext().setContextProperty("model", self.model)
        self.engine.load(os.fspath(Path(__file__).resolve().parent / 'qml/track_live_view.qml'))

    def update(self):
        self.model.reloadImage.emit()

    def run(self):
        self.app.exec()
