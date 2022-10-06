import os
import math
import pathlib
import drawSvg as draw

from typing import Optional
from track_generator.track import Point2d, Track, Start, Straight, Arc, Crosswalk, Intersection, Gap


class Painter:

    def __init__(self):
        self.d: Optional[draw.Drawing] = None

    def draw_point(self, p: Point2d):
        self.d.append(draw.Circle(p.x,
                                  p.y,
                                  10,
                                  fill='red', stroke_width=0, stroke='black'))

        self.d.append(draw.Text(f'({int(p.x)},{int(p.y)})', 64, p.x + 32, p.y, fill='red'))

    def draw_arc_center_point(self, p: Point2d, radian_angle, radius):
        self.d.append(draw.Circle(p.x,
                                  p.y,
                                  10,
                                  fill='red', stroke_width=0, stroke='black'))

        self.d.append(draw.Text(f'({int(p.x)},{int(p.y)})\nr={int(radius)}\na={int(radian_angle)}°', 64, p.x + 32, p.y, fill='red'))

    def draw_start_verbose(self, segment: Start):
        self.draw_point(segment.sp)
        self.draw_point(segment.slp)
        self.draw_point(segment.srp)

    def draw_straight(self, segment: Straight):
        self.d.append(draw.Line(segment.sp.x, segment.sp.y,
                            segment.ep.x, segment.ep.y,
                            fill='#eeee00',
                            stroke='black',
                            stroke_width=800.0))

        self.d.append(draw.Line(segment.sp.x, segment.sp.y, segment.ep.x, segment.ep.y,
                            stroke='white', stroke_width=20.0, fill='none',
                            style="stroke-miterlimit:4;stroke-dasharray:160,160;stroke-dashoffset:0"))

        self.d.append(draw.Line(segment.slp.x, segment.slp.y, segment.elp.x, segment.elp.y,
                            stroke='white', stroke_width=20.0, fill='none'))

        self.d.append(draw.Line(segment.srp.x, segment.srp.y, segment.erp.x, segment.erp.y,
                            stroke='white', stroke_width=20.0, fill='none'))

    def draw_straight_verbose(self, segment: Straight):
        self.draw_point(segment.sp)
        self.draw_point(segment.slp)
        self.draw_point(segment.srp)

    def draw_arc(self, segment: Arc):
        end_angle = segment.direction_angle
        start_angle = segment.start_direction_angle

        if segment.cw:
            final_end_angle = end_angle + 90
            final_start_angle = start_angle + 90
        else:
            final_end_angle = end_angle - 90
            final_start_angle = start_angle - 90

        self.d.append(draw.Arc(segment.cp.x, segment.cp.y, math.fabs(segment.radius), final_start_angle, final_end_angle,
                          cw=segment.cw, stroke='black', stroke_width=800.0, fill='none'))

        self.d.append(draw.Arc(segment.cp.x, segment.cp.y, math.fabs(segment.radius) - 380.0, final_start_angle,
                          final_end_angle, cw=segment.cw, stroke='white', stroke_width=20.0, fill='none'))

        self.d.append(draw.Arc(segment.cp.x, segment.cp.y, math.fabs(segment.radius) + 380.0, final_start_angle,
                          final_end_angle, cw=segment.cw, stroke='white', stroke_width=20.0, fill='none'))

        self.d.append(draw.Arc(segment.cp.x, segment.cp.y, math.fabs(segment.radius), final_start_angle, final_end_angle,
                          cw=segment.cw, stroke='white', stroke_width=20.0, fill='none',
                          style="stroke-miterlimit:4;stroke-dasharray:160,160;stroke-dashoffset:0"))

    def draw_arc_verbose(self, segment: Arc):
        end_angle = segment.direction_angle
        start_angle = segment.start_direction_angle

        if segment.cw:
            final_end_angle = end_angle + 90
            final_start_angle = start_angle + 90
        else:
            final_end_angle = end_angle - 90
            final_start_angle = start_angle - 90

        p = draw.Path(fill='none', stroke='blue', stroke_width=20.0)
        p.arc(segment.cp.x, segment.cp.y, math.fabs(segment.radius), final_end_angle, final_start_angle, cw=not segment.cw)
        p.arc(segment.cp.x, segment.cp.y, 0, final_start_angle, final_end_angle, cw=segment.cw, includeL=True)
        p.Z()
        self.d.append(p)

        self.draw_arc_center_point(segment.cp, segment.radian_angle, segment.radius)
        self.draw_point(segment.sp)
        self.draw_point(segment.slp)
        self.draw_point(segment.srp)

    def draw_crosswalk(self, segment: Crosswalk):
        full_template_file_path = os.path.join(pathlib.Path(__file__).parent.absolute(),
                                               'segment_templates/crosswalk.svg')
        self.draw_template_based_segment(segment, full_template_file_path)

    def draw_intersection(self, segment: Intersection):
        full_template_file_path = os.path.join(pathlib.Path(__file__).parent.absolute(),
                                               'segment_templates/intersection.svg')
        self.draw_template_based_segment(segment, full_template_file_path)
    
    def draw_template_based_segment(self, segment, template_file_path: str):
        self.d.append(draw.Image(segment.sp.x - (segment.width / 2.0), segment.sp.y, segment.width, segment.height,
                      template_file_path,
                      embed=True,
                      transform=f'rotate({-(segment.direction_angle - 90.0)} , {segment.sp.x}, {-segment.sp.y})')
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

    def draw_segment_verbose(self, segment):
        if isinstance(segment, Start):
            pass
        elif isinstance(segment, Straight):
            self.draw_straight_verbose(segment)
        elif isinstance(segment, Arc):
            self.draw_arc_verbose(segment)
        # elif isinstance(segment, Crosswalk):
        #     self.draw_crosswalk_verbose(segment)
        # elif isinstance(segment, Intersection):
        #     self.draw_intersection_verbose(segment)
        # elif isinstance(segment, Gap):
        #     pass
        # else:
        #     raise RuntimeError()

    def draw_track(self, track: Track):
        self.d = draw.Drawing(track.width, track.height, origin=track.origin, displayInline=False)
        self.d.append(draw.Rectangle(0, 0, track.width, track.height, fill=track.background_color,
                                     fill_opacity=track.background_opacity))
        for segment in track.segments:
            self.draw_segment(segment)

    def draw_track_verbose(self, track: Track):
        for segment in track.segments:
            self.draw_segment_verbose(segment)

    def save_svg(self, track_name: str, output_directory: str, file_name_postfix: str = ''):
        output_file_path = os.path.join(output_directory, track_name)
        self.d.saveSvg(f'{output_file_path}{file_name_postfix}.svg')

    def save_png(self, track_name: str, output_directory: str):
        output_file_path = os.path.join(output_directory, track_name)
        self.d.setPixelScale(1)
        self.d.savePng(f'{output_file_path}.png')
