# Copyright (C) 2022 twyleg
import argparse
import sys
from pathlib import Path

from track_generator import __version__
from track_generator import generator


def subcommand_generate_track():
    parser = argparse.ArgumentParser(description="Generates a track")
    parser.add_argument(
        "track_files", metavar="track_file", type=str, nargs="+", help="a track file (XML) to generate the track from"
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        default=Path.cwd() / "output",
        help='Output directory for generated tracks. Default="./"',
    )
    parser.add_argument("--png", action="store_true", help="Generate output PNG (SVG only by default).")
    parser.add_argument("--gazebo", action="store_true", help="Generate Gazebo model for track.")
    parser.add_argument("--ground_truth", action="store_true", help="Generate ground truth data for track.")
    args = parser.parse_args(sys.argv[2:])

    track_file_filepaths = [Path(filepath) for filepath in args.track_files]
    output_dirpath = Path(args.output)

    generator.generate_track(track_file_filepaths, output_dirpath, args.png, args.gazebo, args.ground_truth)


def subcommand_generate_track_live():
    parser = argparse.ArgumentParser(description="Generates a track")
    parser.add_argument(
        "track_file", metavar="track_file", type=str, help="a track file (XML) to generate the track from"
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        default=Path.cwd() / "output",
        help='Output directory for generated tracks. Default="./"',
    )
    args = parser.parse_args(sys.argv[2:])

    track_filepath = Path(args.track_file)
    output_dirpath = Path(args.output)
    generator.generate_track_live(track_filepath, output_dirpath)


def subcommand_generate_trajectory():
    """TODO: Implement"""
    pass


def start():
    parser = argparse.ArgumentParser(usage="track_generator <command> [<args>] <track_file>")
    parser.add_argument("command", help="track_generator commands")
    parser.add_argument("-v", "--version", help="show version and exit", action="version", version=__version__)
    args = parser.parse_args(sys.argv[1:2])

    if args.command == "generate_track":
        subcommand_generate_track()
    elif args.command == "generate_track_live":
        subcommand_generate_track_live()
    elif args.command == "generate_trajectory":
        subcommand_generate_trajectory()


if __name__ == "__main__":
    start()
