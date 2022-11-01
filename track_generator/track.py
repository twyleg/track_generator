# Copyright (C) 2022 twyleg
from typing import Any, List, Tuple, Optional
from track_generator.coordinate_system import Point2d, CartesianSystem2d

LINE_WIDTH = 0.020
TRACK_WIDTH = 0.800
LINE_OFFSET = (TRACK_WIDTH / 2) - LINE_WIDTH


class Track:
    def __init__(self, version: str, width: float, height: float, origin: Tuple[float, float],
                 background_color: str, background_opacity: float, segments: List[Any]):
        self.version = version
        self.width = width
        self.height = height
        self.origin = origin
        self.background_color = background_color
        self.background_opacity = background_opacity
        self.segments = segments

    def calc(self) -> None:
        for i in range(len(self.segments)):
            if i == 0:
                self.segments[i].calc()
            else:
                prev_segment = self.segments[i - 1]
                self.segments[i].calc(prev_segment)


class Start:
    def __init__(self, x: float, y: float, direction_angle: float):
        self.start_coordinate_system = CartesianSystem2d(x, y, direction_angle)
        self.direction_angle = direction_angle
        self.start_point = Point2d(0, 0, self.start_coordinate_system)
        self.end_coordinate_system = self.start_coordinate_system

    def __str__(self) -> str:
        return f'Start: end_point={self.end_point}, direction_angle={self.direction_angle}'

    def calc(self) -> None:
        pass


class Straight:
    def __init__(self, length: float):
        self.length = length
        self.direction_angle: Optional[float] = None

        self.end_coordinate_system: Optional[CartesianSystem2d] = None

        self.sp: Optional[Point2d] = None
        self.slp: Optional[Point2d] = None
        self.srp: Optional[Point2d] = None

        self.ep: Optional[Point2d] = None
        self.elp: Optional[Point2d] = None
        self.erp: Optional[Point2d] = None

    def __str__(self) -> str:
        return f'Straight: sp={self.sp}, ep={self.ep}, length={self.length}, direction_angle={self.direction_angle}'

    def calc(self, prev_segment) -> None:
        start_coordinate_system = prev_segment.end_coordinate_system
        self.end_coordinate_system = CartesianSystem2d(self.length, 0.0, 0.0, start_coordinate_system)
        self.direction_angle = prev_segment.direction_angle

        self.sp = Point2d(0.0, 0.0, start_coordinate_system)
        self.slp = Point2d(0.0, -LINE_OFFSET, start_coordinate_system)
        self.srp = Point2d(0.0, +LINE_OFFSET, start_coordinate_system)

        self.ep = Point2d(self.length, 0.0, start_coordinate_system)
        self.elp = Point2d(self.length, -LINE_OFFSET, start_coordinate_system)
        self.erp = Point2d(self.length, +LINE_OFFSET, start_coordinate_system)


class Arc:
    def __init__(self, radius: float, radian_angle: float, cw: bool):
        self.radius = radius
        self.radian_angle = radian_angle
        self.cw = cw
        self.start_direction_angle: Optional[float] = None
        self.direction_angle: Optional[float] = None
        self.end_coordinate_system: Optional[CartesianSystem2d] = None

        self.sp: Optional[Point2d] = None
        self.slp: Optional[Point2d] = None
        self.srp: Optional[Point2d] = None
        self.ep: Optional[Point2d] = None
        self.cp: Optional[Point2d] = None

    def __str__(self) -> str:
        return f'Arc: sp={self.sp}, ep={self.ep}, cp={self.cp}, start_direction_angle={self.start_direction_angle},' \
               f' direction_angle={self.direction_angle}, cw={self.cw}, angle={self.radian_angle}, radius={self.radius}'

    def calc(self, prev_segment) -> None:
        start_coordinate_system = prev_segment.end_coordinate_system

        signed_radian_angle = -self.radian_angle if self.cw else self.radian_angle
        center_offset = self.radius if self.cw else -self.radius

        center_coordinate_system = CartesianSystem2d(0.0, -center_offset, signed_radian_angle, start_coordinate_system)
        self.end_coordinate_system = CartesianSystem2d(0.0, center_offset, 0.0, center_coordinate_system)

        self.sp = Point2d(0.0, 0.0, start_coordinate_system)
        self.slp = Point2d(0.0, -LINE_OFFSET, start_coordinate_system)
        self.srp = Point2d(0.0, +LINE_OFFSET, start_coordinate_system)

        self.ep = Point2d(0.0, 0.0, self.end_coordinate_system)
        self.cp = Point2d(0.0, 0.0, center_coordinate_system)

        self.start_direction_angle = prev_segment.direction_angle
        self.direction_angle = prev_segment.direction_angle + signed_radian_angle


class Crosswalk(Straight):
    def __init__(self, length: float):
        super().__init__(length)
        self.line_point_pairs: List[Tuple[Point2d, Point2d]] = []

    def calc(self, prev_segment) -> None:
        super().calc(prev_segment)
        start_coordinate_system = prev_segment.end_coordinate_system

        line_width = 0.03
        freespace_width = 0.02
        pack_width = line_width + freespace_width

        num_lines = int(((TRACK_WIDTH - (2*LINE_WIDTH + line_width + 2*freespace_width)) / 2) / pack_width)
        line_freq = ((TRACK_WIDTH - (2*LINE_WIDTH + line_width + 2*freespace_width)) / 2) / num_lines

        self.line_point_pairs.append((
              Point2d(0, 0, start_coordinate_system),
              Point2d(self.length, 0, start_coordinate_system)
        ))
        for i in range(num_lines):
            y = line_freq * i + pack_width
            self.line_point_pairs.append((
                Point2d(0, y, start_coordinate_system),
                Point2d(self.length, y, start_coordinate_system)
            ))
            self.line_point_pairs.append((
                Point2d(0, -y, start_coordinate_system),
                Point2d(self.length, -y, start_coordinate_system)
            ))


class TemplateBasedElement:
    def __init__(self, length: float, width: float, height: float):
        self.length = length
        self.width = width
        self.height = height
        self.direction_angle: Optional[float] = None
        self.end_coordinate_system: Optional[CartesianSystem2d] = None

        self.sp: Optional[Point2d] = None
        self.ep: Optional[Point2d] = None

    def __str__(self) -> str:
        return f'TemplateBasedElement: sp={self.sp}, ep={self.ep}, direction_angle={self.direction_angle},' \
               f' length={self.length}'

    def calc(self, prev_segment) -> None:
        start_coordinate_system = prev_segment.end_coordinate_system
        self.end_coordinate_system = CartesianSystem2d(self.length, 0.0, 0.0, start_coordinate_system)
        self.direction_angle = prev_segment.direction_angle

        self.sp = Point2d(0.0, 0.0, start_coordinate_system)
        self.ep = Point2d(self.length, 0.0, start_coordinate_system)





class Intersection(TemplateBasedElement):
    def __init__(self):
        super().__init__(1.600, 1.600, 1.600)


class Gap(TemplateBasedElement):
    def __init__(self, length: float):
        super().__init__(length, 0, 0)
