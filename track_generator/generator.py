import argparse
import sys
import os

from track_generator.xml_reader import XmlReader
from track_generator.painter import Painter
from track_generator.gazebo_model_generator import GazeboModelGenerator

VERSION = '0.0.1'


class Generator:
    def __init__(self):
        parser = argparse.ArgumentParser(usage='track_generator <command> [<args>] <track_file>')
        parser.add_argument('command', help='track_generator commands')
        parser.add_argument('-v', '--version', help='show version and exit', action='version', version=VERSION)
        args = parser.parse_args(sys.argv[1:2])
        getattr(self, args.command)()

    def generate_track(self):
        parser = argparse.ArgumentParser(description='Generates a track')
        parser.add_argument('track_files', metavar='track_file', type=str, nargs='+',
                            help='a track file (XML) to generate the track from')
        parser.add_argument('-o', '--output', dest='output', default=os.path.join(os.getcwd(), 'output'),
                            help='Output directory for generated tracks. Default="./"')
        parser.add_argument('--png', action='store_true',
                            help='Generate output PNG (SVG only by default).')
        parser.add_argument('--gazebo', action='store_true',
                            help='Generate Gazebo model for track.')
        args = parser.parse_args(sys.argv[2:])

        for track_file in args.track_files:
            xml_reader = XmlReader(track_file)
            track = xml_reader.read_track()
            track.calc()

            output_directory = os.path.join(args.output, track.name)
            self.create_output_directory_if_required(output_directory)

            painter = Painter()
            painter.draw_track(track)
            painter.save_svg(track.name, output_directory)
            if args.png:
                painter.save_png(track.name, output_directory)

            if args.gazebo:
                gazebo_model_generator = GazeboModelGenerator(output_directory)
                gazebo_model_generator.generate_gazebo_model(track)

                painter.save_png(track.name, gazebo_model_generator.track_materials_textures_directory)

            painter.draw_track_verbose(track)
            painter.save_svg(track.name, output_directory, file_name_postfix='verbose')

    def generate_trajectory(self):
        print('generate_trajectory not implemented yet')

    def create_output_directory_if_required(self, output_directory):
        os.makedirs(output_directory, exist_ok=True)


def run():
    Generator()


if __name__ == '__main__':
    run()
