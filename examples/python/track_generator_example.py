# Copyright (C) 2022 twyleg
import os
from pathlib import Path
from track_generator.generator import generate_track


FILE_DIR = Path(__file__).parent


if __name__ == "__main__":
    simple_track_example_input_file = FILE_DIR / "../track_files/simple_track_example.xml"
    advanced_track_example_input_file = FILE_DIR / "../track_files/advanced_track_example.xml"
    output_directory = FILE_DIR / "output"

    track_files = [simple_track_example_input_file, advanced_track_example_input_file]
    track_output_directories = generate_track(track_files, output_directory, False, False)
    print(track_output_directories)
