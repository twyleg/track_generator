# Copyright (C) 2022 twyleg
from pathlib import Path
from track_generator.generator import generate_track_live


FILE_DIR = Path(__file__).parent


if __name__ == "__main__":
    simple_track_example_input_file = FILE_DIR / "../track_files/simple_track_example.xml"
    output_directory = FILE_DIR / "output"

    track_output_directories = generate_track_live(simple_track_example_input_file, output_directory)
    print(track_output_directories)
