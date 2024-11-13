# Copyright (C) 2024 twyleg
import argparse
import logging
from pathlib import Path
from typing import List, Callable

from PySide6.QtCore import QObject, Signal, QUrl

from simple_python_app_qt.qml_application import QmlApplication
from simple_python_app_qt.property import Property, PropertyMeta
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from track_generator import __version__
from track_generator import generator


FILE_DIR = Path(__file__).parent


class GuiApplication(QmlApplication):

    class Model(QObject, metaclass=PropertyMeta):
        filepath = Property(str)
        reload_image = Signal(name="reloadImage")

        def __init__(self, filepath: str, parent: QObject | None = None) -> None:
            QObject.__init__(self, parent)
            self.filepath = filepath  # type: ignore

    class FilesystemWatcher(FileSystemEventHandler):
        def __init__(self, paths: List[Path]):
            self.observer = Observer()
            self.paths = paths
            self.callback: Callable[[], None] | None = None
            logging.info("Filesystem Watcher created!")

        def stop(self):
            self.observer.stop()
            try:
                self.observer.join()
                for directory_path in self.paths:
                    logging.info("Filesystem Watcher stopped to watch at %s", directory_path)
            except RuntimeError:
                logging.info("Filesystem Watcher wasn't running!")
            logging.info("Filesystem Watcher stopped!")

        def start(self) -> None:
            for path in self.paths:
                dir_path = path if path.is_dir() else path.parent
                self.observer.schedule(self, dir_path, recursive=True)
                logging.info("FilesystemWatcher watching at %s", path)
            self.observer.start()

        def register_callback(self, callback: Callable[[], None]):
            self.callback = callback

        def on_any_event(self, event):
            if event.event_type in ["updated", "modified"] and Path(event.src_path) in self.paths:
                logging.debug("Detected updated event: %s", event.src_path)
                self.callback()

    def __init__(self) -> None:
        # fmt: off
        super().__init__(
            application_name="track_generator_gui",
            version=__version__,
            application_config_init_enabled=False,
            logging_logfile_output_dir= Path.cwd() / "logs/",
            frontend_qml_file_path=FILE_DIR / "frontend/qml/track_live_view.qml"
        )
        # fmt: on

        self.track_model: GuiApplication.Model | None = None

    def add_arguments(self, argparser: argparse.ArgumentParser):

        # fmt: off
        argparser.add_argument(
            "track_file",
            metavar="track_file",
            type=str,
            help="a track file (XML) to generate the track from"
        )
        argparser.add_argument(
            "-o",
            "--output",
            dest="output",
            default=Path.cwd() / "output",
            help='Output directory for generated tracks. Default="./"',
        )
        # fmt: on

    def _update(self) -> None:
        self.logm.info("Track file changed, regenerating track (%s)", self.track_filepath)
        generator.generate_track([self.track_filepath], self.output_directory, generate_png=False, generate_gazebo_project=False)
        assert self.track_model
        self.track_model.reload_image.emit()

    def run(self, args: argparse.Namespace):
        self.track_filepath = Path(args.track_file)
        self.output_directory = Path(args.output)
        self.output_directory.mkdir(exist_ok=True)

        track_name = generator.get_track_name_from_file_path(self.track_filepath)
        self.output_filepath = self.output_directory / track_name / f"{track_name}.svg"

        self.track_model = GuiApplication.Model(QUrl.fromLocalFile(self.output_filepath.absolute()).toString())
        self.add_model(self.track_model, "model")

        self._update()

        filesystem_watcher = GuiApplication.FilesystemWatcher([self.track_filepath])
        filesystem_watcher.register_callback(self._update)
        filesystem_watcher.start()

        self.open()

        filesystem_watcher.stop()


def start() -> None:
    application = GuiApplication()
    application.start()


if __name__ == "__main__":
    start()
