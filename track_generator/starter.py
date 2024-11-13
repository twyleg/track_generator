# Copyright (C) 2024 twyleg
import argparse
from pathlib import Path

from simple_python_app.subcommand_application import SubcommandApplication

from track_generator import __version__
from track_generator import generator


FILE_DIR = Path(__file__).parent


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

        # fmt: off
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
        # fmt: on

    def _handle_generate_track(self, args: argparse.Namespace) -> int:
        generator.generate_track(args.track_files, args.output, args.png, args.gazebo, args.ground_truth)
        return 0

    def _handle_generate_trajectory(self, args: argparse.Namespace) -> int:
        self.logm.warning("Subcommand not yet implemented!")
        return 0


def start() -> None:
    application = CliApplication()
    application.start()


if __name__ == "__main__":
    start()
