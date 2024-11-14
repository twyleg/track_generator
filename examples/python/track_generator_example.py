# Copyright (C) 2022 twyleg
import glob
from pathlib import Path
from typing import List

from track_generator.generator import generate_track


FILE_DIR = Path(__file__).parent


def get_track_file_examples() -> List[Path]:
    glob_files = glob.glob(str(FILE_DIR / "../track_files/*.xml"))
    return [Path(filepath) for filepath in glob_files]


if __name__ == "__main__":
    output_directory = FILE_DIR / "output"
    track_files = get_track_file_examples()
    track_output_directories = generate_track(track_files, output_directory, generate_png=True, generate_gazebo_project=True, generate_ground_truth=True)
    for track_output_directory in track_output_directories:
        print(track_output_directory)
