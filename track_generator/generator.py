# Copyright (C) 2022 twyleg
import os
from pathlib import Path
from typing import List, Callable

from track_generator import xml_reader
from track_generator.painter import Painter
from track_generator.gazebo_model_generator import GazeboModelGenerator
from track_generator.gui.track_live_view import TrackLiveView
from track_generator.ground_truth_generator import GroundTruthGenerator

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def _create_output_directory_if_required(output_dirpath: Path):
    output_dirpath.mkdir(exist_ok=True)


def _get_track_name_from_file_path(track_filepath: Path) -> str:
    filename = os.path.basename(track_filepath)
    filename_without_extension, _ = os.path.splitext(filename)
    return filename_without_extension


def generate_track(
    track_filepaths: List[Path],
    root_output_dirpath: Path,
    generate_png=False,
    generate_gazebo_project=False,
    generate_ground_truth=False,
) -> List[str]:
    """
    Generate tracks (SVG, Gazebo project, etc) from given track files (XML)
    :param track_filepaths: List of track files
    :param root_output_dirpath: The output directory to write results to. Subdirectories for every track will be
    generated.
    :param generate_png: Flag whether a png image should be created for the track
    :param generate_gazebo_project:Flag whether gazebo project files should be created for the track
    :return: List of output directories for the tracks
    """
    track_output_directories: List[Path] = []
    for track_filepath in track_filepaths:
        track = xml_reader.read_track(track_filepath)
        track.calc()

        track_name = _get_track_name_from_file_path(track_filepath)
        track_output_directory = root_output_dirpath / track_name
        _create_output_directory_if_required(track_output_directory)
        track_output_directories.append(track_output_directory)

        painter = Painter()
        painter.draw_track(track)
        painter.save_svg(track_name, track_output_directory)
        if generate_png:
            painter.save_png(track_name, track_output_directory)

        if generate_gazebo_project:
            gazebo_model_generator = GazeboModelGenerator(track_name, track_output_directory)
            gazebo_model_generator.generate_gazebo_model(track)

            painter.save_png(track_name, gazebo_model_generator.track_materials_textures_directory)

        painter.draw_track_verbose(track)
        painter.save_svg(track_name, track_output_directory, file_name_postfix="_verbose")

        if generate_ground_truth:
            ground_truth_generator = GroundTruthGenerator(track_name, track_output_directory)
            ground_truth_generator.generate_ground_truth(track)
    return track_output_directories


class FileChangedHandler(FileSystemEventHandler):
    def __init__(self, input_filepath: Path, callback: Callable):
        self.input_filepath = input_filepath
        self.callback = callback

    # def on_any_event(self, event) -> None:
    #     pass

    def on_closed(self, event) -> None:
        event_filepath = Path(event.src_path)
        if event_filepath == self.input_filepath:
            self.callback()
        return None


def generate_track_live(track_file: Path, root_output_directory: Path) -> None:
    """
    Generate tracks (SVG, Gazebo project, etc) from given track files (XML)
    :param track_file: Track file
    :param root_output_directory: The output directory to write results to. Subdirectories for every track will be
    generated.
    :return: Output directory for the track
    """
    track_file_directory = track_file.parent
    track_name = _get_track_name_from_file_path(track_file)
    output_file_path = os.path.join(root_output_directory, track_name, f"{track_name}.svg")
    track_live_view = TrackLiveView(output_file_path)

    def update():
        print(f"Track file changed, regenerating track ({track_file})")
        generate_track([track_file], root_output_directory, generate_png=False, generate_gazebo_project=False)
        track_live_view.update()

    event_handler = FileChangedHandler(track_file, update)

    update()

    observer = Observer()
    observer.schedule(event_handler, track_file_directory, recursive=False)
    observer.start()

    track_live_view.run()

    observer.stop()
    observer.join()


def generate_trajectory():
    print("generate_trajectory not implemented yet")
