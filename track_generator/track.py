import os
import math
import pathlib
import drawSvg as draw
import numpy as np
import pytransform3d.rotations as pyrot
import pytransform3d.transformations as pytr
from typing import Any, List, Tuple


class Track:
    def __init__(self, width: float, height: float, origin: Tuple[float, float], segments: List[Any]):
        self.segments = segments
        self.width = width
        self.height = height
        self.origin = origin


class Start:
    def __init__(self, x: float, y: float, direction_angle: float):
        self.ex = x
        self.ey = y
        self.direction_angle = direction_angle
        self.endpoint_to_world = None

    def __str__(self) -> str:
        return f'Start: ex={self.ex}, ey={self.ey}, direction_angle={self.direction_angle}'

    def calc(self):
        t = np.array([self.ex, self.ey, 0.0])
        r = np.array([0.0, 0.0, -1.0, np.deg2rad(self.direction_angle)])
        self.endpoint_to_world = pytr.transform_from(pyrot.matrix_from_axis_angle(r), t)

    def draw(self, d: draw.Drawing):
        pass


class Straight:
    def __init__(self, length: float):
        self.length = length
        self.direction_angle = None
        self.sx = None
        self.sy = None
        self.ex = None
        self.ey = None

        self.slx = None
        self.sly = None
        self.elx = None
        self.ely = None

        self.srx = None
        self.sry = None
        self.erx = None
        self.ery = None

        self.startpoint_to_world = None
        self.endpoint_to_world = None

    def __str__(self) -> str:
        return f'Straight: sx={self.sx}, sy={self.sy}, ex={self.ex}, ey={self.ey}, length={self.length}, direction_angle={self.direction_angle}'

    def calc(self, prev_elem):
        startpoint_to_world = prev_elem.endpoint_to_world

        p = np.array([self.length, 0.0, 0.0])
        a = np.array([0.0, 0.0, 1.0, 0.0])
        endpoint_to_startpoint = pytr.transform_from(pyrot.matrix_from_axis_angle(a), p)
        endpoint_to_world = pytr.concat(endpoint_to_startpoint, startpoint_to_world)

        element_startpoint = pytr.transform(startpoint_to_world, np.array([0.0, 0.0, 0.0, 1.0]))
        self.sx = element_startpoint[0]
        self.sy = element_startpoint[1]

        element_left_startpoint = pytr.transform(startpoint_to_world, np.array([0.0, -380.0, 0.0, 1.0]))
        self.slx = element_left_startpoint[0]
        self.sly = element_left_startpoint[1]

        element_right_startpoint = pytr.transform(startpoint_to_world, np.array([0.0, 380.0, 0.0, 1.0]))
        self.srx = element_right_startpoint[0]
        self.sry = element_right_startpoint[1]

        element_endpoint = pytr.transform(endpoint_to_world, np.array([0.0, 0.0, 0.0, 1.0]))
        self.ex = element_endpoint[0]
        self.ey = element_endpoint[1]

        element_left_endpoint = pytr.transform(endpoint_to_world, np.array([0.0, -380.0, 0.0, 1.0]))
        self.elx = element_left_endpoint[0]
        self.ely = element_left_endpoint[1]

        element_right_endpoint = pytr.transform(endpoint_to_world, np.array([0.0, 380.0, 0.0, 1.0]))
        self.erx = element_right_endpoint[0]
        self.ery = element_right_endpoint[1]

        self.startpoint_to_world = startpoint_to_world
        self.endpoint_to_world = endpoint_to_world
        self.direction_angle = prev_elem.direction_angle

    def draw(self, d: draw.Drawing):
        d.append(draw.Line(self.sx, -self.sy,
                            self.ex, -self.ey,
                            fill='#eeee00',
                            stroke='black',
                            stroke_width=800.0))

        d.append(draw.Line(self.sx, -self.sy, self.ex, -self.ey,
                          stroke='white', stroke_width=20.0, fill='none', style="stroke-miterlimit:4;stroke-dasharray:160,160;stroke-dashoffset:0"))

        d.append(draw.Line(self.slx, -self.sly, self.elx, -self.ely,
                          stroke='white', stroke_width=20.0, fill='none'))

        d.append(draw.Line(self.srx, -self.sry, self.erx, -self.ery,
                          stroke='white', stroke_width=20.0, fill='none'))


class Arc:
    def __init__(self, radius: float, angle: float):
        self.radius = radius
        self.angle = angle
        self.cw = None
        self.start_direction_angle = None
        self.direction_angle = None
        self.sx = None
        self.sy = None
        self.ex = None
        self.ey = None
        self.cx = None
        self.cy = None
        self.startpoint_to_world = None
        self.endpoint_to_world = None
        self.center_to_world = None

    def __str__(self) -> str:
        return f'Arc: sx={self.sx}, sy={self.sy}, ex={self.ex}, ey={self.ey}, cx={self.cx}, cy={self.cy}, start_direction_angle={self.start_direction_angle}, direction_angle={self.direction_angle}, cw={self.cw}, angle={self.angle}, radius={self.radius}'

    def calc(self, prev_elem):
        startpoint_to_world = prev_elem.endpoint_to_world

        p = np.array([0.0, self.radius, 0.0])
        a = np.array([0.0, 0.0, 1.0, 0.0])
        startpoint_to_center = pytr.transform_from(pyrot.matrix_from_axis_angle(a), p)

        p = np.array([0.0, -self.radius, 0.0])
        a = np.array([0.0, 0.0, -1.0, np.deg2rad(self.angle if self.radius > 0 else -self.angle)])
        center_to_endpoint = pytr.transform_from(pyrot.matrix_from_axis_angle(a), p)

        endpoint_to_startpoint = pytr.concat(startpoint_to_center, center_to_endpoint)
        endpoint_to_world = pytr.concat(endpoint_to_startpoint, startpoint_to_world)

        center_to_world = pytr.concat(center_to_endpoint, endpoint_to_world)

        element_startpoint = pytr.transform(startpoint_to_world, np.array([0.0, 0.0, 0.0, 1.0]))
        self.sx = element_startpoint[0]
        self.sy = element_startpoint[1]

        element_endpoint = pytr.transform(endpoint_to_world, np.array([0.0, 0.0, 0.0, 1.0]))
        self.ex = element_endpoint[0]
        self.ey = element_endpoint[1]

        element_center = pytr.transform(center_to_world, np.array([0.0, 0.0, 0.0, 1.0]))
        self.cx = element_center[0]
        self.cy = element_center[1]

        self.startpoint_to_world = startpoint_to_world
        self.endpoint_to_world = endpoint_to_world
        self.center_to_world = center_to_world
        self.start_direction_angle = prev_elem.direction_angle
        self.direction_angle = None
        self.cw = self.radius < 0
        if self.cw:
            self.direction_angle = (prev_elem.direction_angle - self.angle)
        else:
            self.direction_angle = (prev_elem.direction_angle + self.angle)

    def draw(self, d: draw.Drawing):
        end_angle = self.direction_angle
        start_angle = self.start_direction_angle

        if self.cw:
            final_end_angle = (end_angle + 90)
            final_start_angle = (start_angle + 90)
        else:
            final_end_angle = end_angle - 90
            final_start_angle = start_angle - 90

        d.append(draw.Arc(self.cx, -self.cy, math.fabs(self.radius), final_start_angle, final_end_angle, cw=self.cw,
                          stroke='black', stroke_width=800.0, fill='none'))

        d.append(draw.Arc(self.cx, -self.cy, math.fabs(self.radius) - 380.0, final_start_angle, final_end_angle, cw=self.cw,
                          stroke='white', stroke_width=20.0, fill='none'))

        d.append(draw.Arc(self.cx, -self.cy, math.fabs(self.radius) + 380.0, final_start_angle, final_end_angle, cw=self.cw,
                          stroke='white', stroke_width=20.0, fill='none'))

        d.append(draw.Arc(self.cx, -self.cy, math.fabs(self.radius), final_start_angle, final_end_angle, cw=self.cw,
                          stroke='white', stroke_width=20.0, fill='none', style="stroke-miterlimit:4;stroke-dasharray:160,160;stroke-dashoffset:0"))

class TemplateBasedElement:
    def __init__(self, length: float, width: float, height: float, template_file_path: str):
        self.length = length
        self.width = width
        self.height = height
        self.template_file_path = template_file_path
        self.direction_angle = None
        self.sx = None
        self.sy = None
        self.ex = None
        self.ey = None

        self.startpoint_to_world = None
        self.endpoint_to_world = None

    def __str__(self) -> str:
        return f'TemplateBasedElement: sx={self.sx}, sy={self.sy}, ex={self.ex}, ey={self.ey}, direction_angle={self.direction_angle}, length={self.length}'

    def calc(self, prev_elem):
        startpoint_to_world = prev_elem.endpoint_to_world

        p = np.array([self.length, 0.0, 0.0])
        a = np.array([0.0, 0.0, 1.0, 0.0])
        endpoint_to_startpoint = pytr.transform_from(pyrot.matrix_from_axis_angle(a), p)
        endpoint_to_world = pytr.concat(endpoint_to_startpoint, startpoint_to_world)

        element_startpoint = pytr.transform(startpoint_to_world, np.array([0.0, 0.0, 0.0, 1.0]))
        self.sx = element_startpoint[0]
        self.sy = element_startpoint[1]

        element_endpoint = pytr.transform(endpoint_to_world, np.array([0.0, 0.0, 0.0, 1.0]))
        self.ex = element_endpoint[0]
        self.ey = element_endpoint[1]

        self.startpoint_to_world = startpoint_to_world
        self.endpoint_to_world = endpoint_to_world
        self.direction_angle = prev_elem.direction_angle

    def draw(self, d: draw.Drawing):
        if self.template_file_path is not None:
            full_template_file_path = os.path.join(pathlib.Path(__file__).parent.absolute(), self.template_file_path)
            d.append(draw.Image(self.sx - (self.width/2.0), -self.sy, self.width, self.height,
                                full_template_file_path,
                                embed=True,
                                transform=f'rotate({-(self.direction_angle-90.0)} , {self.sx}, {self.sy})')
            )


class Crosswalk(TemplateBasedElement):
    def __init__(self):
        super().__init__(400, 800, 400, 'element_templates/crosswalk.svg')

class Intersection(TemplateBasedElement):
    def __init__(self):
        super().__init__(1600, 1600, 1600, 'element_templates/intersection.svg')

class Gap(TemplateBasedElement):
    def __init__(self, length: float):
        super().__init__(length, 0, 0, None)
