import os
import math
import pathlib
import drawSvg as draw

from typing import Optional
from track_generator.track import Track, Start, Straight, Arc, Crosswalk, Intersection, Gap


class Painter:

    def __init__(self):
        self.d: Optional[draw.Drawing] = None

    def draw_straight(self, segment: Straight):
        self.d.append(draw.Line(segment.sx, segment.sy,
                            segment.ex, segment.ey,
                            fill='#eeee00',
                            stroke='black',
                            stroke_width=800.0))

        self.d.append(draw.Line(segment.sx, segment.sy, segment.ex, segment.ey,
                            stroke='white', stroke_width=20.0, fill='none',
                            style="stroke-miterlimit:4;stroke-dasharray:160,160;stroke-dashoffset:0"))

        self.d.append(draw.Line(segment.slx, segment.sly, segment.elx, segment.ely,
                            stroke='white', stroke_width=20.0, fill='none'))

        self.d.append(draw.Line(segment.srx, segment.sry, segment.erx, segment.ery,
                            stroke='white', stroke_width=20.0, fill='none'))

    def draw_arc(self, segment: Arc):
        end_angle = segment.direction_angle
        start_angle = segment.start_direction_angle

        if segment.cw:
            final_end_angle = end_angle + 90
            final_start_angle = start_angle + 90
        else:
            final_end_angle = end_angle - 90
            final_start_angle = start_angle - 90

        self.d.append(draw.Arc(segment.cx, segment.cy, math.fabs(segment.radius), final_start_angle, final_end_angle,
                          cw=segment.cw, stroke='black', stroke_width=800.0, fill='none'))

        self.d.append(draw.Arc(segment.cx, segment.cy, math.fabs(segment.radius) - 380.0, final_start_angle,
                          final_end_angle, cw=segment.cw, stroke='white', stroke_width=20.0, fill='none'))

        self.d.append(draw.Arc(segment.cx, segment.cy, math.fabs(segment.radius) + 380.0, final_start_angle,
                          final_end_angle, cw=segment.cw, stroke='white', stroke_width=20.0, fill='none'))

        self.d.append(draw.Arc(segment.cx, segment.cy, math.fabs(segment.radius), final_start_angle, final_end_angle,
                          cw=segment.cw, stroke='white', stroke_width=20.0, fill='none',
                          style="stroke-miterlimit:4;stroke-dasharray:160,160;stroke-dashoffset:0"))

    def draw_crosswalk(self, segment: Crosswalk):
        full_template_file_path = os.path.join(pathlib.Path(__file__).parent.absolute(),
                                               'segment_templates/crosswalk.svg')
        self.draw_template_based_segment(segment, full_template_file_path)

    def draw_intersection(self, segment: Intersection):
        full_template_file_path = os.path.join(pathlib.Path(__file__).parent.absolute(),
                                               'segment_templates/intersection.svg')
        self.draw_template_based_segment(segment, full_template_file_path)
    
    def draw_template_based_segment(self, segment, template_file_path: str):
        self.d.append(draw.Image(segment.sx - (segment.width / 2.0), segment.sy, segment.width, segment.height,
                      template_file_path,
                      embed=True,
                      transform=f'rotate({-(segment.direction_angle - 90.0)} , {segment.sx}, {-segment.sy})')
        )

    def draw_segment(self, segment):
        if isinstance(segment, Start):
            pass
        elif isinstance(segment, Straight):
            self.draw_straight(segment)
        elif isinstance(segment, Arc):
            self.draw_arc(segment)
        elif isinstance(segment, Crosswalk):
            self.draw_crosswalk(segment)
        elif isinstance(segment, Intersection):
            self.draw_intersection(segment)
        elif isinstance(segment, Gap):
            pass
        else:
            raise RuntimeError()

    def draw_track(self, track: Track):
        self.d = draw.Drawing(track.width, track.height, origin=track.origin, displayInline=False)
        self.d.append(draw.Rectangle(0, 0, track.width, track.height, fill=track.background_color,
                                     fill_opacity=track.background_opacity))
        for segment in track.segments:
            self.draw_segment(segment)

    def save_svg(self, track_name: str, output_directory: str):
        output_file_path = os.path.join(output_directory, track_name)
        self.d.saveSvg(f'{output_file_path}.svg')

    def save_png(self, track_name: str, output_directory: str):
        output_file_path = os.path.join(output_directory, track_name)
        self.d.setPixelScale(1)
        self.d.savePng(f'{output_file_path}.png')
