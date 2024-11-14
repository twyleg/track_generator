# Copyright (C) 2022 twyleg
import os
import logging

from pathlib import Path
from typing import List, Callable

from track_generator import xml_reader
from track_generator.painter import Painter
from track_generator.gazebo_model_generator import GazeboModelGenerator
from track_generator.ground_truth_generator import GroundTruthGenerator


logm = logging.getLogger(__name__)


def _create_output_directory_if_required(output_dirpath: Path):
    output_dirpath.mkdir(parents=True, exist_ok=True)


def get_track_name_from_file_path(track_filepath: Path) -> str:
    filename = os.path.basename(track_filepath)
    filename_without_extension, _ = os.path.splitext(filename)
    return filename_without_extension


def generate_track(
    track_filepaths: List[Path],
    root_output_dirpath: Path,
    generate_png=False,
    generate_gazebo_project=False,
    generate_ground_truth=False,
) -> List[Path]:
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

        track_name = get_track_name_from_file_path(track_filepath)
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


def generate_trajectory():
    logm.warning("generate_trajectory not implemented yet")
