import os
import drawSvg as draw

from track_generator.track import Track

class Painter:

    def __init__(self, track_name: str, output_directory: str):
        self.track_name = track_name
        self.output_directory = output_directory

    def draw_track(self, track: Track):
        for i in range(len(track.segments)):
            if i == 0:
                track.segments[i].calc()
            else:
                prev_elem = track.segments[i - 1]
                track.segments[i].calc(prev_elem)

        d = draw.Drawing(10000, 10000, origin=(0, 0), displayInline=False)
        for segment in track.segments:
            segment.draw(d)

        output_file_path = os.path.join(self.output_directory, self.track_name)

        d.saveSvg(f'{output_file_path}.svg')