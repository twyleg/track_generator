# Copyright (C) 2024 twyleg
import argparse
import logging
from pathlib import Path
from typing import List, Callable

from PySide6.QtCore import QObject, Signal, QUrl
from simple_python_app.subcommand_application import SubcommandApplication

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

        def __init__(self, filepath: str, parent: QObject | None = None) -> None:
            QObject.__init__(self, parent)
            self.filepath = filepath

        @Signal
        def reloadImage(self) -> None:
            pass

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
                dir_path =path if path.is_dir() else path.parent
                self.observer.schedule(self, dir_path, recursive=True)
                logging.info("FilesystemWatcher watching at %s", path)
            self.observer.start()

        def register_callback(self, callback: Callable[[], None]):
            self.callback = callback

        def on_any_event(self, event):
            if event.event_type in ["updated", "modified"] and Path(event.src_path) in self.paths:
                logging.debug("Detected updated event: %s", event.src_path)
                self.callback()


    def __init__(self):
        # fmt: off
        super().__init__(
            application_name="track_generator_gui",
            version=__version__,
            application_config_init_enabled=False,
            logging_logfile_output_dir= Path.cwd() / "logs/",
            frontend_qml_file_path=FILE_DIR / "frontend/qml/track_live_view.qml"
        )
        # fmt: on

        self.track_model: QObject | None = None


    def add_arguments(self, argparser: argparse.ArgumentParser):

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

    def _update(self) -> None:
        self.logm.info("Track file changed, regenerating track (%s)", self.track_filepath)
        generator.generate_track([self.track_filepath], self.output_directory, generate_png=False,
                                 generate_gazebo_project=False)
        self.track_model.reloadImage.emit()

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


class CliApplication(SubcommandApplication):

    def __init__(self):
        # fmt: off
        super().__init__(
            application_name="track_generator",
            version=__version__,
            application_config_schema_filepath=FILE_DIR / "resources/application_config_schema.json",
            logging_logfile_output_dir= Path.cwd() / "logs/",
        )
        # fmt: on

    def add_arguments(self, argparser: argparse.ArgumentParser):

        generate_track_command = self.add_subcommand(
            command="generate_track",
            help="Generate track.",
            description="Generate track.",
            handler=self._handle_generate_track
        )

        generate_track_command.parser.add_argument(
            "track_files",
            metavar="track_file",
            type=str,
            nargs="+",
            help="a track file (XML) to generate the track from"
        )
        generate_track_command.parser.add_argument(
            "-o",
            "--output",
            dest="output",
            default=Path.cwd() / "output",
            help='Output directory for generated tracks. Default="./"',
        )
        generate_track_command.parser.add_argument(
            "--png",
            action="store_true",
            help="Generate output PNG (SVG only by default)."
        )
        generate_track_command.parser.add_argument(
            "--gazebo",
            action="store_true",
            help="Generate Gazebo model for track."
        )
        generate_track_command.parser.add_argument(
            "--ground_truth",
            action="store_true",
            help="Generate ground truth data for track."
        )

        generate_trajectory_command = self.add_subcommand(
            command="generate_trajectory",
            help="Generate trajectory.",
            description="Generate trajectory.",
            handler=self._handle_generate_trajectory
        )

    def _handle_generate_track(self, args: argparse.Namespace) -> int:
        generator.generate_track(args.track_files, args.output, args.png, args.gazebo, args.ground_truth)
        return 0

    def _handle_generate_trajectory(self, args: argparse.Namespace) -> int:
        self.logm.warning("Subcommand not yet implemented!")
        return 0


def start_cli() -> None:
    application = CliApplication()
    application.start()


def start_gui() -> None:
    application = GuiApplication()
    application.start()


if __name__ == "__main__":
    start_gui()
