# Copyright (C) 2022 twyleg
import sys
import os
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Property

BASE_DIR = Path(__file__).parent
class TrackLiveView:
    class Model(QObject):
        reloadImage = Signal()
        filepath_changed = Signal()

        def __init__(self, filepath: Path) -> None:
            QObject.__init__(self)
            self._filepath = str(filepath)

        def get_filepath(self) -> str:
            return self._filepath

        def set_filepath(self, filepath: Path) -> None:
            self._filepath = str(filepath)
            self.filepath_changed.emit()

        filepath = Property(str, get_filepath, set_filepath, notify=filepath_changed)  # type: ignore [arg-type]

    def __init__(self, output_filepath: Path):
        self.app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine()
        self.model = TrackLiveView.Model(output_filepath)

        self.engine.rootContext().setContextProperty("model", self.model)
        self.engine.load(BASE_DIR / "qml/track_live_view.qml")

    def update(self):
        self.model.reloadImage.emit()

    def run(self):
        self.app.exec()
