# Copyright (C) 2022 twyleg
import jinja2
from pathlib import Path
from track_generator.track import Track


FILE_DIRPATH = Path(__file__).parent


def read(fname):
    return open(FILE_DIRPATH / fname).read()


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

        self.environment = jinja2.Environment(loader=jinja2.FileSystemLoader(FILE_DIRPATH / "gazebo_model_templates/"))

    def generate_track_material(self):
        assert self.track_materials_scripts_directory
        template = self.environment.get_template("track.material.jinja")

        material = {"name": f"{self.track_name}_material", "texture_file_name": f"{self.track_name}.png"}

        with open(self.track_materials_scripts_directory / "track.material", "w") as output_file:
            output_file.write(template.render(material=material))

    def generate_track_sdf(self, track: Track):
        assert self.track_directory
        template = self.environment.get_template("model.sdf.jinja")

        model = {"name": self.track_name, "width": track.width, "height": track.height}

        with open(self.track_directory / "model.sdf", "w") as output_file:
            output_file.write(template.render(model=model))

    def generate_track_config(self, track: Track):
        assert self.track_directory
        template = self.environment.get_template("model.config.jinja")

        model = {"name": self.track_name, "version": track.version, "desc": self.track_name}

        with open(self.track_directory / "model.config", "w") as output_file:
            output_file.write(template.render(model=model))

    def generate_example_world(self, track: Track):
        assert self.track_directory
        template = self.environment.get_template("example.world.jinja")

        example = {"name": self.track_name}
        output_filename = f"{self.track_name}.world"

        with open(self.gazebo_models_directory / output_filename, "w") as output_file:
            output_file.write(template.render(example=example))

    def generate_setup_script(self):
        assert self.gazebo_models_directory

        template = self.environment.get_template("setup.bash.jinja")

        with open(self.gazebo_models_directory / "setup.bash", "w") as output_file:
            output_file.write(template.render())

    def generate_gazebo_model(self, track: Track):
        self.generate_track_material()
        self.generate_track_sdf(track)
        self.generate_track_config(track)
        self.generate_example_world(track)
        self.generate_setup_script()
