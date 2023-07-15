# Copyright (C) 2022 twyleg
import sys
import os
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Property


class TrackLiveView:
    class Model(QObject):
        reloadImage = Signal()
        filename_changed = Signal()

        def __init__(self, filename: str) -> None:
            QObject.__init__(self)
            self._filename = filename

        def get_filename(self) -> str:
            return self._filename

        def set_filename(self, filename: str) -> None:
            self._filename = filename
            self.filename_changed.emit()

        filename = Property(str, get_filename, set_filename, notify=filename_changed)  # type: ignore [arg-type]

    def __init__(self, output_file_path: str):
        self.app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine()
        self.model = TrackLiveView.Model(output_file_path)

        self.engine.rootContext().setContextProperty("model", self.model)
        self.engine.load(os.fspath(Path(__file__).resolve().parent / "qml/track_live_view.qml"))

    def update(self):
        self.model.reloadImage.emit()

    def run(self):
        self.app.exec()
