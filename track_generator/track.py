# Copyright (C) 2022 twyleg
from typing import Any, List, Tuple, Optional
from track_generator.coordinate_system import Polygon, Point2d, CartesianSystem2d

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

        self.center_line_polygon: List[Polygon] = []
        self.left_line_polygon: List[Polygon] = []
        self.right_line_polygon: List[Polygon] = []

    def __str__(self) -> str:
        return f'Straight: sp={self.center_line_polygon[0][0]}, ep={self.center_line_polygon[0][1]},' \
               f' length={self.length}, direction_angle={self.direction_angle}'

    def calc(self, prev_segment) -> None:
        start_coordinate_system = prev_segment.end_coordinate_system
        self.end_coordinate_system = CartesianSystem2d(self.length, 0.0, 0.0, start_coordinate_system)
        self.direction_angle = prev_segment.direction_angle

        self.center_line_polygon.append([
            Point2d(0.0, 0.0, start_coordinate_system),
            Point2d(self.length, 0.0, start_coordinate_system)
        ])

        self.left_line_polygon.append([
            Point2d(0.0, -LINE_OFFSET, start_coordinate_system),
            Point2d(self.length, -LINE_OFFSET, start_coordinate_system)
        ])

        self.right_line_polygon.append([
            Point2d(0.0, +LINE_OFFSET, start_coordinate_system),
            Point2d(self.length, +LINE_OFFSET, start_coordinate_system)
        ])


class Arc:
    def __init__(self, radius: float, radian_angle: float, direction_clockwise: bool):
        self.radius = radius
        self.radian_angle = radian_angle
        self.direction_clockwise = direction_clockwise
        self.start_direction_angle: Optional[float] = None
        self.direction_angle: Optional[float] = None
        self.end_coordinate_system: Optional[CartesianSystem2d] = None

        self.start_point_center: Optional[Point2d] = None
        self.start_point_left: Optional[Point2d] = None
        self.start_point_right: Optional[Point2d] = None
        self.end_point_center: Optional[Point2d] = None
        self.center_point: Optional[Point2d] = None

    def __str__(self) -> str:
        return f'Arc: sp={self.start_point_center}, ep={self.end_point_center}, cp={self.center_point},' \
               f' start_direction_angle={self.start_direction_angle}, direction_angle={self.direction_angle},' \
               f' cw={self.direction_clockwise}, angle={self.radian_angle}, radius={self.radius}'

    def calc(self, prev_segment) -> None:
        start_coordinate_system = prev_segment.end_coordinate_system

        signed_radian_angle = -self.radian_angle if self.direction_clockwise else self.radian_angle
        center_offset = self.radius if self.direction_clockwise else -self.radius

        center_coordinate_system = CartesianSystem2d(0.0, -center_offset, signed_radian_angle, start_coordinate_system)
        self.end_coordinate_system = CartesianSystem2d(0.0, center_offset, 0.0, center_coordinate_system)

        self.start_point_center = Point2d(0.0, 0.0, start_coordinate_system)
        self.start_point_left = Point2d(0.0, -LINE_OFFSET, start_coordinate_system)
        self.start_point_right = Point2d(0.0, +LINE_OFFSET, start_coordinate_system)

        self.end_point_center = Point2d(0.0, 0.0, self.end_coordinate_system)
        self.center_point = Point2d(0.0, 0.0, center_coordinate_system)

        self.start_direction_angle = prev_segment.direction_angle
        self.direction_angle = prev_segment.direction_angle + signed_radian_angle


class Crosswalk(Straight):
    def __init__(self, length: float):
        super().__init__(length)
        self.line_polygons: List[Polygon] = []

    def calc(self, prev_segment) -> None:
        super().calc(prev_segment)
        start_coordinate_system = prev_segment.end_coordinate_system

        line_width = 0.03
        freespace_width = 0.02
        pack_width = line_width + freespace_width

        num_lines = int(((TRACK_WIDTH - (2*LINE_WIDTH + line_width + 2*freespace_width)) / 2) / pack_width)
        line_freq = ((TRACK_WIDTH - (2*LINE_WIDTH + line_width + 2*freespace_width)) / 2) / num_lines

        self.line_polygons.append([
              Point2d(0, 0, start_coordinate_system),
              Point2d(self.length, 0, start_coordinate_system)
        ])
        for i in range(num_lines):
            y = line_freq * i + pack_width
            self.line_polygons.append([
                Point2d(0, y, start_coordinate_system),
                Point2d(self.length, y, start_coordinate_system)
            ])
            self.line_polygons.append([
                Point2d(0, -y, start_coordinate_system),
                Point2d(self.length, -y, start_coordinate_system)
            ])


class Intersection:
    def __init__(self, length: float):
        self.length = length
        self.base_line_polygons: List[Polygon] = []
        self.corner_line_polygons: List[Polygon] = []
        self.stop_line_polygons: List[Polygon] = []
        self.center_line_polygons: List[Polygon] = []
        self.end_coordinate_system: Optional[CartesianSystem2d] = None
        self.direction_angle: Optional[float] = None

    def calc_base_lines(self, start_coordinate_system: CartesianSystem2d) -> None:
        self.base_line_polygons.append([
            Point2d(0.0, 0.0, start_coordinate_system),
            Point2d(self.length, 0.0, start_coordinate_system),
        ])
        self.base_line_polygons.append([
            Point2d(self.length/2, -self.length/2, start_coordinate_system),
            Point2d(self.length/2, +self.length/2, start_coordinate_system),
        ])

    def calc_corner_lines(self, start_coordinate_system: CartesianSystem2d) -> None:
        center_x = self.length / 2.0

        self.corner_line_polygons.append([
            Point2d(0, -LINE_OFFSET, start_coordinate_system),
            Point2d(center_x - LINE_OFFSET, -LINE_OFFSET, start_coordinate_system),
            Point2d(center_x - LINE_OFFSET, -self.length/2, start_coordinate_system),
        ])

        self.corner_line_polygons.append([
            Point2d(0, +LINE_OFFSET, start_coordinate_system),
            Point2d(center_x - LINE_OFFSET, +LINE_OFFSET, start_coordinate_system),
            Point2d(center_x - LINE_OFFSET, +self.length/2, start_coordinate_system),
        ])

        self.corner_line_polygons.append([
            Point2d(self.length, -LINE_OFFSET, start_coordinate_system),
            Point2d(center_x + LINE_OFFSET, -LINE_OFFSET, start_coordinate_system),
            Point2d(center_x + LINE_OFFSET, -self.length/2, start_coordinate_system),
        ])

        self.corner_line_polygons.append([
            Point2d(self.length, +LINE_OFFSET, start_coordinate_system),
            Point2d(center_x + LINE_OFFSET, +LINE_OFFSET, start_coordinate_system),
            Point2d(center_x + LINE_OFFSET, +self.length/2, start_coordinate_system),
        ])

    def calc_stop_lines(self, start_coordinate_system: CartesianSystem2d) -> None:
        center_x = self.length / 2.0

        self.stop_line_polygons.append([
            Point2d(center_x - LINE_OFFSET, 0, start_coordinate_system),
            Point2d(center_x - LINE_OFFSET, -LINE_OFFSET, start_coordinate_system),
        ])

        self.stop_line_polygons.append([
            Point2d(center_x + LINE_OFFSET, 0, start_coordinate_system),
            Point2d(center_x + LINE_OFFSET, +LINE_OFFSET, start_coordinate_system),
        ])

    def calc_center_lines(self, start_coordinate_system: CartesianSystem2d) -> None:
        center_x = self.length / 2.0

        self.center_line_polygons.append([
            Point2d(0, 0, start_coordinate_system),
            Point2d(center_x - LINE_OFFSET, 0, start_coordinate_system),
        ])

        self.center_line_polygons.append([
            Point2d(self.length, 0, start_coordinate_system),
            Point2d(center_x + LINE_OFFSET, 0, start_coordinate_system),
        ])

        self.center_line_polygons.append([
            Point2d(center_x, self.length/2, start_coordinate_system),
            Point2d(center_x, +LINE_OFFSET, start_coordinate_system),
        ])

        self.center_line_polygons.append([
            Point2d(center_x, -self.length/2, start_coordinate_system),
            Point2d(center_x, -LINE_OFFSET, start_coordinate_system),
        ])

    def calc(self, prev_segment) -> None:
        start_coordinate_system = prev_segment.end_coordinate_system

        self.calc_base_lines(start_coordinate_system)
        self.calc_corner_lines(start_coordinate_system)
        self.calc_stop_lines(start_coordinate_system)
        self.calc_center_lines(start_coordinate_system)

        self.end_coordinate_system = CartesianSystem2d(self.length, 0.0, 0.0, start_coordinate_system)
        self.direction_angle = prev_segment.direction_angle


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


class Gap(TemplateBasedElement):
    def __init__(self, length: float):
        super().__init__(length, 0, 0)
