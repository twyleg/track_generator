import os
from typing import List

from track_generator.xml_reader import XmlReader
from track_generator.painter import Painter
from track_generator.gazebo_model_generator import GazeboModelGenerator

VERSION = '0.0.1'


def create_output_directory_if_required(self, output_directory):
    os.makedirs(output_directory, exist_ok=True)


def generate_track(track_files: List[str], generate_png=False, generate_gazebo_project=False):
    for track_file in track_files:
        xml_reader = XmlReader(track_file)
        track = xml_reader.read_track()
        track.calc()

        output_directory = os.path.join(args.output, track.name)
        create_output_directory_if_required(output_directory)

        painter = Painter()
        painter.draw_track(track)
        painter.save_svg(track.name, output_directory)
        if generate_png:
            painter.save_png(track.name, output_directory)

        if generate_gazebo_project:
            gazebo_model_generator = GazeboModelGenerator(output_directory)
            gazebo_model_generator.generate_gazebo_model(track)

            painter.save_png(track.name, gazebo_model_generator.track_materials_textures_directory)

        painter.draw_track_verbose(track)
        painter.save_svg(track.name, output_directory, file_name_postfix='_verbose')


def generate_trajectory():
    print('generate_trajectory not implemented yet')
