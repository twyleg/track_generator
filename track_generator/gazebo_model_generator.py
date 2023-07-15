# Copyright (C) 2022 twyleg
import os
from pathlib import Path
from track_generator.track import Track
from string import Template


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def write(path, data):
    return open(path, "w").write(data)


class GazeboModelGenerator:
    def __init__(self, track_name: str, output_directory: Path):
        self.track_name = track_name
        self.output_directory = output_directory
        self.gazebo_models_directory = self.output_directory / "gazebo_models"
        self.track_directory = self.gazebo_models_directory / track_name
        self.track_materials_scripts_directory = self.track_directory / "materials/scripts"
        self.track_materials_textures_directory = self.track_directory / "materials/textures"

        self.gazebo_models_directory.mkdir(parents=True, exist_ok=True)
        self.track_directory.mkdir(parents=True, exist_ok=True)
        self.track_materials_scripts_directory.mkdir(parents=True, exist_ok=True)
        self.track_materials_textures_directory.mkdir(parents=True, exist_ok=True)

    def generate_track_material(self):
        assert self.track_materials_scripts_directory
        template = Template(read("gazebo_model_templates/track.material.template"))
        output = template.substitute(
            material_name=f"{self.track_name}_material", texture_file_name=f"{self.track_name}.png"
        )
        write(self.track_materials_scripts_directory / "track.material", output)

    def generate_track_sdf(self, track: Track):
        assert self.track_directory
        template = Template(read("gazebo_model_templates/model.sdf.template"))
        output = template.substitute(name=self.track_name, width=track.width, height=track.height)
        write(self.track_directory / "model.sdf", output)

    def generate_track_config(self, track: Track):
        assert self.track_directory
        template = Template(read("gazebo_model_templates/model.config.template"))
        output = template.substitute(
            name=self.track_name,
            version=track.version,
            desc=self.track_name,
        )
        write(self.track_directory / "model.config", output)

    def generate_setup_script(self):
        assert self.gazebo_models_directory
        output = read("gazebo_model_templates/setup.bash.template")
        write(self.gazebo_models_directory / "setup.bash", output)

    def generate_gazebo_model(self, track: Track):
        self.generate_track_material()
        self.generate_track_sdf(track)
        self.generate_track_config(track)
        self.generate_setup_script()
