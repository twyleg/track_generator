import numpy as np
import pytransform3d.rotations as pyrot
import pytransform3d.transformations as pytr
from typing import Any, List, Tuple, Optional


class Point2d:
    def __init__(self, x: Optional[float] = None, y: Optional[float] = None):
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x},{self.y})'


class Track:
    def __init__(self, name: str, version: str, width: float, height: float, origin: Tuple[float, float],
                 background_color: str, background_opacity: float, segments: List[Any]):
        self.name = name
        self.version = version
        self.width = width
        self.height = height
        self.origin = origin
        self.background_color = background_color
        self.background_opacity = background_opacity
        self.segments = segments

    def calc(self):
        for i in range(len(self.segments)):
            if i == 0:
                self.segments[i].calc()
            else:
                prev_segment = self.segments[i - 1]
                self.segments[i].calc(prev_segment)


class Start:
    def __init__(self, x: float, y: float, direction_angle: float):
        self.ep = Point2d(x, y)
        self.direction_angle = direction_angle
        self.endpoint_to_world = None

    def __str__(self) -> str:
        return f'Start: ep={self.ep}, direction_angle={self.direction_angle}'

    def calc(self):
        t = np.array([self.ep.x, self.ep.y, 0.0])
        r = np.array([0.0, 0.0, 1.0, np.deg2rad(self.direction_angle)])
        self.endpoint_to_world = pytr.transform_from(pyrot.matrix_from_axis_angle(r), t)


class Straight:
    def __init__(self, length: float):
        self.length = length
        self.direction_angle: Optional[float] = None

        self.sp: Optional[Point2d] = None
        self.slp: Optional[Point2d] = None
        self.srp: Optional[Point2d] = None

        self.ep: Optional[Point2d] = None
        self.elp: Optional[Point2d] = None
        self.erp: Optional[Point2d] = None

        self.startpoint_to_world = None
        self.endpoint_to_world = None

    def __str__(self) -> str:
        return f'Straight: sp={self.sp}, ep={self.ep}, length={self.length}, direction_angle={self.direction_angle}'

    def calc(self, prev_segment):
        startpoint_to_world = prev_segment.endpoint_to_world

        p = np.array([self.length, 0.0, 0.0])
        a = np.array([0.0, 0.0, 1.0, 0.0])
        endpoint_to_startpoint = pytr.transform_from(pyrot.matrix_from_axis_angle(a), p)
        endpoint_to_world = pytr.concat(endpoint_to_startpoint, startpoint_to_world)

        segment_startpoint = pytr.transform(startpoint_to_world, np.array([0.0, 0.0, 0.0, 1.0]))
        self.sp = Point2d(segment_startpoint[0], segment_startpoint[1])

        segment_left_startpoint = pytr.transform(startpoint_to_world, np.array([0.0, -380.0, 0.0, 1.0]))
        self.slp = Point2d(segment_left_startpoint[0], segment_left_startpoint[1])

        segment_right_startpoint = pytr.transform(startpoint_to_world, np.array([0.0, 380.0, 0.0, 1.0]))
        self.srp = Point2d(segment_right_startpoint[0], segment_right_startpoint[1])

        segment_endpoint = pytr.transform(endpoint_to_world, np.array([0.0, 0.0, 0.0, 1.0]))
        self.ep = Point2d(segment_endpoint[0], segment_endpoint[1])

        segment_left_endpoint = pytr.transform(endpoint_to_world, np.array([0.0, -380.0, 0.0, 1.0]))
        self.elp = Point2d(segment_left_endpoint[0], segment_left_endpoint[1])

        segment_right_endpoint = pytr.transform(endpoint_to_world, np.array([0.0, 380.0, 0.0, 1.0]))
        self.erp = Point2d(segment_right_endpoint[0], segment_right_endpoint[1])

        self.startpoint_to_world = startpoint_to_world
        self.endpoint_to_world = endpoint_to_world
        self.direction_angle = prev_segment.direction_angle


class Arc:
    def __init__(self, radius: float, radian_angle: float, cw: bool):
        self.radius = radius
        self.radian_angle = radian_angle
        self.cw = cw
        self.start_direction_angle: Optional[float] = None
        self.direction_angle: Optional[float] = None
        self.sp: Optional[Point2d] = None
        self.slp: Optional[Point2d] = None
        self.srp: Optional[Point2d] = None
        self.ep: Optional[Point2d] = None
        self.cp: Optional[Point2d] = None

        self.startpoint_to_world = None
        self.endpoint_to_world = None
        self.center_to_world = None

    def __str__(self) -> str:
        return f'Arc: sp={self.sp}, ep={self.ep}, cp={self.cp}, start_direction_angle={self.start_direction_angle}, direction_angle={self.direction_angle}, cw={self.cw}, angle={self.radian_angle}, radius={self.radius}'

    def calc(self, prev_segment):
        startpoint_to_world = prev_segment.endpoint_to_world

        signed_radian_angle = -self.radian_angle if self.cw else self.radian_angle
        center_offset = -self.radius if self.cw else self.radius

        p = np.array([0.0, -center_offset, 0.0])
        a = np.array([0.0, 0.0, 1.0, 0.0])
        startpoint_to_center = pytr.transform_from(pyrot.matrix_from_axis_angle(a), p)

        p = np.array([0.0, center_offset, 0.0])
        a = np.array([0.0, 0.0, 1.0, np.deg2rad(signed_radian_angle)])
        center_to_endpoint = pytr.transform_from(pyrot.matrix_from_axis_angle(a), p)

        endpoint_to_startpoint = pytr.concat(startpoint_to_center, center_to_endpoint)
        endpoint_to_world = pytr.concat(endpoint_to_startpoint, startpoint_to_world)

        center_to_world = pytr.concat(center_to_endpoint, endpoint_to_world)

        segment_startpoint = pytr.transform(startpoint_to_world, np.array([0.0, 0.0, 0.0, 1.0]))
        self.sp = Point2d(segment_startpoint[0], segment_startpoint[1])

        segment_left_startpoint = pytr.transform(startpoint_to_world, np.array([0.0, -380.0, 0.0, 1.0]))
        self.slp = Point2d(segment_left_startpoint[0], segment_left_startpoint[1])

        segment_right_startpoint = pytr.transform(startpoint_to_world, np.array([0.0, 380.0, 0.0, 1.0]))
        self.srp = Point2d(segment_right_startpoint[0], segment_right_startpoint[1])

        segment_endpoint = pytr.transform(endpoint_to_world, np.array([0.0, 0.0, 0.0, 1.0]))
        self.ep = Point2d(segment_endpoint[0], segment_endpoint[1])

        segment_center = pytr.transform(center_to_world, np.array([0.0, 0.0, 0.0, 1.0]))
        self.cp = Point2d(segment_center[0], segment_center[1])

        self.startpoint_to_world = startpoint_to_world
        self.endpoint_to_world = endpoint_to_world
        self.center_to_world = center_to_world
        self.start_direction_angle = prev_segment.direction_angle
        self.direction_angle = prev_segment.direction_angle + signed_radian_angle


class TemplateBasedElement:
    def __init__(self, length: float, width: float, height: float):
        self.length = length
        self.width = width
        self.height = height
        self.direction_angle: Optional[float] = None
        self.sp: Optional[Point2d] = None
        self.ep: Optional[Point2d] = None

        self.startpoint_to_world = None
        self.endpoint_to_world = None

    def __str__(self) -> str:
        return f'TemplateBasedElement: sp={self.sp}, ep={self.ep}, direction_angle={self.direction_angle}, length={self.length}'

    def calc(self, prev_segment):
        startpoint_to_world = prev_segment.endpoint_to_world

        p = np.array([self.length, 0.0, 0.0])
        a = np.array([0.0, 0.0, 1.0, 0.0])
        endpoint_to_startpoint = pytr.transform_from(pyrot.matrix_from_axis_angle(a), p)
        endpoint_to_world = pytr.concat(endpoint_to_startpoint, startpoint_to_world)

        segment_startpoint = pytr.transform(startpoint_to_world, np.array([0.0, 0.0, 0.0, 1.0]))
        self.sp = Point2d(segment_startpoint[0], segment_startpoint[1])

        segment_endpoint = pytr.transform(endpoint_to_world, np.array([0.0, 0.0, 0.0, 1.0]))
        self.ep = Point2d(segment_endpoint[0], segment_endpoint[1])

        self.startpoint_to_world = startpoint_to_world
        self.endpoint_to_world = endpoint_to_world
        self.direction_angle = prev_segment.direction_angle


class Crosswalk(TemplateBasedElement):
    def __init__(self):
        super().__init__(400, 800, 400)


class Intersection(TemplateBasedElement):
    def __init__(self):
        super().__init__(1600, 1600, 1600)


class Gap(TemplateBasedElement):
    def __init__(self, length: float):
        super().__init__(length, 0, 0)
