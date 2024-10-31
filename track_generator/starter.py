# Copyright (C) 2024 twyleg
import argparse
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Property, QUrl
from simple_python_app.subcommand_application import SubcommandApplication

from simple_python_app_qt.qml_application import QmlApplication
from watchdog.observers import Observer

from track_generator import __version__
from track_generator import generator
from track_generator.generator import FileChangedHandler

FILE_DIR = Path(__file__).parent


# def subcommand_generate_track():
#     parser = argparse.ArgumentParser(description="Generates a track")
#     parser.add_argument(
#         "track_files", metavar="track_file", type=str, nargs="+", help="a track file (XML) to generate the track from"
#     )
#     parser.add_argument(
#         "-o",
#         "--output",
#         dest="output",
#         default=Path.cwd() / "output",
#         help='Output directory for generated tracks. Default="./"',
#     )
#     parser.add_argument("--png", action="store_true", help="Generate output PNG (SVG only by default).")
#     parser.add_argument("--gazebo", action="store_true", help="Generate Gazebo model for track.")
#     parser.add_argument("--ground_truth", action="store_true", help="Generate ground truth data for track.")
#     args = parser.parse_args(sys.argv[2:])
#
#     generator.generate_track(args.track_files, args.output, args.png, args.gazebo, args.ground_truth)
#
#
# def subcommand_generate_track_live():
#     parser = argparse.ArgumentParser(description="Generates a track")
#     parser.add_argument(
#         "track_file", metavar="track_file", type=str, help="a track file (XML) to generate the track from"
#     )
#     parser.add_argument(
#         "-o",
#         "--output",
#         dest="output",
#         default=Path.cwd() / "output",
#         help='Output directory for generated tracks. Default="./"',
#     )
#     args = parser.parse_args(sys.argv[2:])
#
#     track_filepath = Path(args.track_file)
#     generator.generate_track_live(track_filepath, args.output)
#
#
# def subcommand_generate_trajectory():
#     """TODO: Implement"""
#     pass
#
#
# def start():
#     parser = argparse.ArgumentParser(usage="track_generator <command> [<args>] <track_file>")
#     parser.add_argument("command", help="track_generator commands")
#     parser.add_argument("-v", "--version", help="show version and exit", action="version", version=__version__)
#     args = parser.parse_args(sys.argv[1:2])
#
#     if args.command == "generate_track":
#         subcommand_generate_track()
#     elif args.command == "generate_track_live":
#         subcommand_generate_track_live()
#     elif args.command == "generate_trajectory":
#         subcommand_generate_trajectory()

class GuiApplication(QmlApplication):

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

    def __init__(self):
        # fmt: off
        super().__init__(
            application_name="track_generator_gui",
            version=__version__,
            application_config_init_enabled=False,
            logging_logfile_output_dir= Path.cwd() / "logs/",
            frontend_qml_file_path=FILE_DIR / "gui/qml/track_live_view.qml"
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

    def _update(self):
        print(f"Track file changed, regenerating track ({self.track_filepath})")
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

        track_file_directory = self.track_filepath.parent
        event_handler = FileChangedHandler(self.track_filepath, self._update)
        observer = Observer()
        observer.schedule(event_handler, track_file_directory, recursive=False)
        observer.start()

        self.open()

        observer.stop()
        observer.join()



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
