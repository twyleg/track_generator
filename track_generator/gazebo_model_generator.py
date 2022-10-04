import os
from track_generator.track import Track
from string import Template
from typing import Optional


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def write(path, data):
    return open(path, 'w').write(data)


class GazeboModelGenerator:

    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        self.model_directory: Optional[str] = None
        self.materials_scripts_directory: Optional[str] = None
        self.materials_textures_directory: Optional[str] = None

    def create_directory_structure(self, track_name: str):
        self.model_directory = os.path.join(self.output_directory, track_name)
        self.materials_scripts_directory = os.path.join(self.model_directory, 'materials', 'scripts')
        self.materials_textures_directory = os.path.join(self.model_directory, 'materials', 'textures')

        os.makedirs(self.model_directory , exist_ok=True)
        os.makedirs(self.materials_scripts_directory, exist_ok=True)
        os.makedirs(self.materials_textures_directory, exist_ok=True)

    def generate_track_material(self, track: Track):
        template = Template(read('gazebo_model_templates/track.material.template'))
        output = template.substitute(
            material_name=f'{track.name}_material',
            texture_file_name=f'{track.name}.png'
        )
        write(os.path.join(self.materials_scripts_directory, 'track.material'), output)

    def generate_track_sdf(self, track: Track):
        template = Template(read('gazebo_model_templates/model.sdf.template'))
        output = template.substitute(
            name=track.name,
            width=track.width/1000.0,
            height=track.height/1000.0
        )
        write(os.path.join(self.model_directory, 'model.sdf'), output)

    def generate_track_config(self, track: Track):
        template = Template(read('gazebo_model_templates/model.config.template'))
        output = template.substitute(
            name=track.name,
            version=track.version,
            desc='foobar'
        )
        write(os.path.join(self.model_directory, 'model.config'), output)

    def generate_setup_script(self):
        output = read('gazebo_model_templates/setup.bash.template')
        write(os.path.join(self.output_directory, 'setup.bash'), output)

    def generate_gazebo_model(self, track: Track):
        self.create_directory_structure(track.name)
        self.generate_track_material(track)
        self.generate_track_sdf(track)
        self.generate_track_config(track)
        self.generate_setup_script()

