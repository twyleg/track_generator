# Copyright (C) 2022 twyleg
import numpy
from enum import Enum
from math import tan, factorial, sqrt, sin, cos, radians, pi
from typing import Any, List, Tuple, Optional
from track_generator.coordinate_system import Polygon, Point2d, CartesianSystem2d

LINE_WIDTH = 0.020
TRACK_WIDTH = 0.800
LINE_OFFSET = (TRACK_WIDTH / 2) - LINE_WIDTH

CROSSWALK_LINE_WIDTH = 0.03
CROSSWALK_LINE_GAP = 0.03


class Side(Enum):
    LEFT = 1
    RIGHT = 2


class IntersectionDirection(Enum):
    RIGHT = "right"
    LEFT = "left"
    STRAIGHT = "straight"


class ClothoidDirection(Enum):
    LEFT = -1
    RIGHT = 1


class ClothoidType(Enum):
    OPEND = "opend"
    CLOSING = "closing"


def calc_crosswalk_lines(length: float, width: float, coordinate_system: CartesianSystem2d) -> List[Polygon]:
    polygons: List[Polygon] = []
    pack_width = CROSSWALK_LINE_WIDTH + CROSSWALK_LINE_GAP

    num_lines = int(width / pack_width)
    line_freq = width / num_lines

    polygons.append([Point2d(0, 0, coordinate_system), Point2d(length, 0, coordinate_system)])
    for i in range(int(num_lines / 2)):
        y = line_freq * i + pack_width
        polygons.append([Point2d(0, +y, coordinate_system), Point2d(length, +y, coordinate_system)])
        polygons.append([Point2d(0, -y, coordinate_system), Point2d(length, -y, coordinate_system)])

    return polygons


class Background:
    class Color:
        def __init__(self, color: str, opacity: float):
            self.color = color
            self.opacity = opacity

    class Image:
        def __init__(self, file: str, x: float, y: float, width: float, height: float):
            self.file = file
            self.x = x
            self.y = y
            self.width = width
            self.height = height

    def __init__(self, color: Color = None, image: Image = None):
        self.color: Optional[Background.Color] = color
        self.image: Optional[Background.Image] = image


class Track:
    def __init__(
        self,
        version: str,
        width: float,
        height: float,
        origin: Tuple[float, float],
        background: Background,
        segments: List[Any],
    ):
        self.version = version
        self.width = width
        self.height = height
        self.origin = origin
        self.background = background
        self.segments = segments

    def calc(self) -> None:
        for i in range(len(self.segments)):
            if i == 0:
                self.segments[i].calc()
            else:
                prev_segment = self.segments[i - 1]
                self.segments[i].calc(prev_segment)


class Segment:
    def __init__(self):
        self.direction_angle: Optional[float] = None
        self.start_coordinate_system: Optional[CartesianSystem2d] = None
        self.end_coordinate_system: Optional[CartesianSystem2d] = None

    def calc(self, prev_segment):
        self.start_coordinate_system = prev_segment.end_coordinate_system
        self.direction_angle = prev_segment.direction_angle


class Start:
    def __init__(self, x: float, y: float, direction_angle: float):
        self.start_coordinate_system = CartesianSystem2d(x, y, direction_angle)
        self.direction_angle = direction_angle
        self.start_point = Point2d(0, 0, self.start_coordinate_system)
        self.end_coordinate_system = self.start_coordinate_system

    def __str__(self) -> str:
        return f"Start: end_point={self.end_point}, direction_angle={self.direction_angle}"

    def calc(self) -> None:
        pass


class Straight(Segment):
    def __init__(self, length: float):
        super().__init__()
        self.length = length

        self.center_line_polygon: Polygon = []
        self.left_line_polygon: Polygon = []
        self.right_line_polygon: Polygon = []

    def __str__(self) -> str:
        return (
            f"Straight: sp={self.center_line_polygon[0][0]}, ep={self.center_line_polygon[0][1]},"
            f" length={self.length}, direction_angle={self.direction_angle}"
        )

    def calc(self, prev_segment) -> None:
        super().calc(prev_segment)
        self.end_coordinate_system = CartesianSystem2d(self.length, 0.0, 0.0, self.start_coordinate_system)

        self.center_line_polygon = [
            Point2d(0.0, 0.0, self.start_coordinate_system),
            Point2d(self.length, 0.0, self.start_coordinate_system),
        ]

        self.left_line_polygon = [
            Point2d(0.0, -LINE_OFFSET, self.start_coordinate_system),
            Point2d(self.length, -LINE_OFFSET, self.start_coordinate_system),
        ]

        self.right_line_polygon = [
            Point2d(0.0, +LINE_OFFSET, self.start_coordinate_system),
            Point2d(self.length, +LINE_OFFSET, self.start_coordinate_system),
        ]


class Arc(Segment):
    def __init__(self, radius: float, radian_angle: float, direction_clockwise: bool):
        super().__init__()
        self.radius = radius
        self.radian_angle = radian_angle
        self.direction_clockwise = direction_clockwise
        self.start_direction_angle: Optional[float] = None

        self.start_point_center: Optional[Point2d] = None
        self.start_point_left: Optional[Point2d] = None
        self.start_point_right: Optional[Point2d] = None
        self.end_point_center: Optional[Point2d] = None
        self.center_point: Optional[Point2d] = None

    def __str__(self) -> str:
        return (
            f"Arc: sp={self.start_point_center}, ep={self.end_point_center}, cp={self.center_point},"
            f" start_direction_angle={self.start_direction_angle}, direction_angle={self.direction_angle},"
            f" cw={self.direction_clockwise}, angle={self.radian_angle}, radius={self.radius}"
        )

    def calc(self, prev_segment) -> None:
        super().calc(prev_segment)

        signed_radian_angle = -self.radian_angle if self.direction_clockwise else self.radian_angle
        center_offset = self.radius if self.direction_clockwise else -self.radius

        center_coordinate_system = CartesianSystem2d(
            0.0, -center_offset, signed_radian_angle, self.start_coordinate_system
        )
        self.end_coordinate_system = CartesianSystem2d(0.0, center_offset, 0.0, center_coordinate_system)

        self.start_point_center = Point2d(0.0, 0.0, self.start_coordinate_system)
        self.start_point_left = Point2d(0.0, -LINE_OFFSET, self.start_coordinate_system)
        self.start_point_right = Point2d(0.0, +LINE_OFFSET, self.start_coordinate_system)

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
        self.line_polygons = calc_crosswalk_lines(self.length, TRACK_WIDTH, self.start_coordinate_system)


class Intersection(Segment):
    def __init__(self, length: float, direction: IntersectionDirection):
        super().__init__()
        self.length = length
        self.direction = direction
        self.base_line_polygons: List[Polygon] = []
        self.corner_line_polygons: List[Polygon] = []
        self.stop_line_polygons: List[Polygon] = []
        self.center_line_polygons: List[Polygon] = []

    def calc_base_lines(self) -> None:
        self.base_line_polygons.append(
            [
                Point2d(0.0, 0.0, self.start_coordinate_system),
                Point2d(self.length, 0.0, self.start_coordinate_system),
            ]
        )
        self.base_line_polygons.append(
            [
                Point2d(self.length / 2, -self.length / 2, self.start_coordinate_system),
                Point2d(self.length / 2, +self.length / 2, self.start_coordinate_system),
            ]
        )

    def calc_corner_lines(self) -> None:
        center_x = self.length / 2.0

        self.corner_line_polygons.append(
            [
                Point2d(0, -LINE_OFFSET, self.start_coordinate_system),
                Point2d(center_x - LINE_OFFSET, -LINE_OFFSET, self.start_coordinate_system),
                Point2d(center_x - LINE_OFFSET, -self.length / 2, self.start_coordinate_system),
            ]
        )

        self.corner_line_polygons.append(
            [
                Point2d(0, +LINE_OFFSET, self.start_coordinate_system),
                Point2d(center_x - LINE_OFFSET, +LINE_OFFSET, self.start_coordinate_system),
                Point2d(center_x - LINE_OFFSET, +self.length / 2, self.start_coordinate_system),
            ]
        )

        self.corner_line_polygons.append(
            [
                Point2d(self.length, -LINE_OFFSET, self.start_coordinate_system),
                Point2d(center_x + LINE_OFFSET, -LINE_OFFSET, self.start_coordinate_system),
                Point2d(center_x + LINE_OFFSET, -self.length / 2, self.start_coordinate_system),
            ]
        )

        self.corner_line_polygons.append(
            [
                Point2d(self.length, +LINE_OFFSET, self.start_coordinate_system),
                Point2d(center_x + LINE_OFFSET, +LINE_OFFSET, self.start_coordinate_system),
                Point2d(center_x + LINE_OFFSET, +self.length / 2, self.start_coordinate_system),
            ]
        )

    def calc_stop_lines(self) -> None:
        center_x = self.length / 2.0

        self.stop_line_polygons.append(
            [
                Point2d(center_x - LINE_OFFSET, 0, self.start_coordinate_system),
                Point2d(center_x - LINE_OFFSET, -LINE_OFFSET, self.start_coordinate_system),
            ]
        )

        self.stop_line_polygons.append(
            [
                Point2d(center_x + LINE_OFFSET, 0, self.start_coordinate_system),
                Point2d(center_x + LINE_OFFSET, +LINE_OFFSET, self.start_coordinate_system),
            ]
        )

    def calc_center_lines(self) -> None:
        center_x = self.length / 2.0

        self.center_line_polygons.append(
            [
                Point2d(0, 0, self.start_coordinate_system),
                Point2d(center_x - LINE_OFFSET, 0, self.start_coordinate_system),
            ]
        )

        self.center_line_polygons.append(
            [
                Point2d(self.length, 0, self.start_coordinate_system),
                Point2d(center_x + LINE_OFFSET, 0, self.start_coordinate_system),
            ]
        )

        self.center_line_polygons.append(
            [
                Point2d(center_x, self.length / 2, self.start_coordinate_system),
                Point2d(center_x, +LINE_OFFSET, self.start_coordinate_system),
            ]
        )

        self.center_line_polygons.append(
            [
                Point2d(center_x, -self.length / 2, self.start_coordinate_system),
                Point2d(center_x, -LINE_OFFSET, self.start_coordinate_system),
            ]
        )

    def calc(self, prev_segment) -> None:
        super().calc(prev_segment)
        if self.direction == IntersectionDirection.RIGHT:
            new_end = [self.length / 2, -self.length / 2, -90]
        elif self.direction == IntersectionDirection.STRAIGHT:
            new_end = [self.length, 0, 0]
        else:
            new_end = [self.length / 2, self.length / 2, 90]
        self.end_coordinate_system = CartesianSystem2d(new_end[0], new_end[1], new_end[2], self.start_coordinate_system)
        self.direction_angle += new_end[2]

        self.calc_base_lines()
        self.calc_corner_lines()
        self.calc_stop_lines()
        self.calc_center_lines()


class Gap(Straight):
    def __init__(self, length: float, direction: IntersectionDirection):
        super().__init__(length)
        self.direction = direction

    def calc(self, prev_segment) -> None:
        super().calc(prev_segment)
        if self.direction == IntersectionDirection.RIGHT:
            new_end = [self.length / 2, -self.length / 2, -90]
        elif self.direction == IntersectionDirection.STRAIGHT:
            new_end = [self.length, 0, 0]
        else:
            new_end = [self.length / 2, self.length / 2, 90]
        self.end_coordinate_system = CartesianSystem2d(new_end[0], new_end[1], new_end[2], self.start_coordinate_system)
        self.direction_angle += new_end[2]


class ParkingArea(Straight):
    class ParkingLot:
        class Spot:
            def __init__(self, type: str, length: float):
                self.type = type
                self.length = length

        def __init__(self, start: float, depth: float, opening_ending_angle: float, spots: List[Spot]):
            self.start = start
            self.depth = depth
            self.opening_ending_angle = opening_ending_angle
            self.spots = spots
            self.length = self.calc_parking_lot_length()

        def calc_parking_lot_length(self):
            length = 0.0
            for spot in self.spots:
                length = length + spot.length
            return length

    def __init__(self, length: float, right_lots: List[ParkingLot], left_lots: List[ParkingLot]):
        super().__init__(length)
        self.right_lots = right_lots
        self.left_lots = left_lots
        self.outline_polygon: List[Polygon] = []
        self.spot_seperator_polygons: List[Polygon] = []
        self.blocker_polygons: List[Polygon] = []

    def calc_lots(self, lots: List[ParkingLot], side: Side, start_coordinate_system: CartesianSystem2d):
        side_factor = 1 if side == Side.LEFT else -1

        for lot in lots:
            opening_ending_length = lot.depth / tan(numpy.deg2rad(lot.opening_ending_angle))

            self.outline_polygon.append(
                [
                    Point2d(lot.start, side_factor * LINE_OFFSET, start_coordinate_system),
                    Point2d(
                        lot.start + opening_ending_length,
                        side_factor * (LINE_OFFSET + lot.depth),
                        start_coordinate_system,
                    ),
                    Point2d(
                        lot.start + lot.length + opening_ending_length,
                        side_factor * (LINE_OFFSET + lot.depth),
                        start_coordinate_system,
                    ),
                    Point2d(
                        lot.start + lot.length + 2 * opening_ending_length,
                        side_factor * LINE_OFFSET,
                        start_coordinate_system,
                    ),
                ]
            )

            offset = opening_ending_length
            for spot in lot.spots:
                self.spot_seperator_polygons.append(
                    [
                        Point2d(lot.start + offset, side_factor * LINE_OFFSET, start_coordinate_system),
                        Point2d(lot.start + offset, side_factor * (LINE_OFFSET + lot.depth), start_coordinate_system),
                    ]
                )

                if spot.type == "blocked":
                    self.blocker_polygons.append(
                        [
                            Point2d(lot.start + offset, side_factor * LINE_OFFSET, start_coordinate_system),
                            Point2d(
                                lot.start + offset + spot.length,
                                side_factor * (LINE_OFFSET + lot.depth),
                                start_coordinate_system,
                            ),
                        ]
                    )
                    self.blocker_polygons.append(
                        [
                            Point2d(
                                lot.start + offset + spot.length, side_factor * LINE_OFFSET, start_coordinate_system
                            ),
                            Point2d(
                                lot.start + offset, side_factor * (LINE_OFFSET + lot.depth), start_coordinate_system
                            ),
                        ]
                    )

                offset = offset + spot.length

            self.spot_seperator_polygons.append(
                [
                    Point2d(lot.start + offset, side_factor * LINE_OFFSET, start_coordinate_system),
                    Point2d(lot.start + offset, side_factor * (LINE_OFFSET + lot.depth), start_coordinate_system),
                ]
            )

    def calc(self, prev_segment) -> None:
        super().calc(prev_segment)
        start_coordinate_system = prev_segment.end_coordinate_system

        self.calc_lots(self.left_lots, Side.LEFT, start_coordinate_system)
        self.calc_lots(self.right_lots, Side.RIGHT, start_coordinate_system)


class TrafficIsland(Segment):
    def __init__(self, island_width: float, crosswalk_length: float, curve_segment_length: float, curvature: float):
        super().__init__()
        self.direction_angle: Optional[float] = None
        self.island_width = island_width
        self.overall_width = island_width + TRACK_WIDTH
        self.crosswalk_length = crosswalk_length
        self.curve_segment_length = curve_segment_length
        self.curvature = curvature
        self.background_polygon: Polygon = []
        self.line_polygons: List[Polygon] = []
        self.crosswalk_lines_polygons: List[Polygon] = []

    def calc_lane(self, side: Side):
        side_factor = 1 if side == Side.LEFT else -1

        self.line_polygons.append(
            [
                Point2d(0.0, 0.0, self.start_coordinate_system),
                Point2d(self.curve_segment_length, side_factor * self.island_width / 2, self.start_coordinate_system),
                Point2d(
                    self.curve_segment_length + self.crosswalk_length,
                    side_factor * self.island_width / 2,
                    self.start_coordinate_system,
                ),
                Point2d(2 * self.curve_segment_length + self.crosswalk_length, 0.0, self.start_coordinate_system),
            ]
        )

        self.line_polygons.append(
            [
                Point2d(0.0, side_factor * LINE_OFFSET, self.start_coordinate_system),
                Point2d(
                    self.curve_segment_length,
                    side_factor * (self.island_width / 2 + LINE_OFFSET),
                    self.start_coordinate_system,
                ),
                Point2d(
                    self.curve_segment_length + self.crosswalk_length,
                    side_factor * (self.island_width / 2 + LINE_OFFSET),
                    self.start_coordinate_system,
                ),
                Point2d(
                    2 * self.curve_segment_length + self.crosswalk_length,
                    side_factor * LINE_OFFSET,
                    self.start_coordinate_system,
                ),
            ]
        )

    def calc_background(self):
        self.background_polygon = [
            Point2d(0.0, TRACK_WIDTH / 2, self.start_coordinate_system),
            Point2d(self.curve_segment_length, TRACK_WIDTH / 2 + self.island_width / 2, self.start_coordinate_system),
            Point2d(
                self.curve_segment_length + self.crosswalk_length,
                TRACK_WIDTH / 2 + self.island_width / 2,
                self.start_coordinate_system,
            ),
            Point2d(
                2 * self.curve_segment_length + self.crosswalk_length, TRACK_WIDTH / 2, self.start_coordinate_system
            ),
            Point2d(
                2 * self.curve_segment_length + self.crosswalk_length, -TRACK_WIDTH / 2, self.start_coordinate_system
            ),
            Point2d(
                self.curve_segment_length + self.crosswalk_length,
                -(TRACK_WIDTH / 2 + self.island_width / 2),
                self.start_coordinate_system,
            ),
            Point2d(
                self.curve_segment_length, -(TRACK_WIDTH / 2 + self.island_width / 2), self.start_coordinate_system
            ),
            Point2d(0.0, -TRACK_WIDTH / 2, self.start_coordinate_system),
        ]

    def calc_crosswalk_lines(self):
        width = TRACK_WIDTH / 2 - LINE_WIDTH
        self.crosswalk_lines_polygons = calc_crosswalk_lines(
            self.crosswalk_length,
            width,
            CartesianSystem2d(
                self.curve_segment_length, +(self.island_width / 2 + LINE_OFFSET / 2), 0.0, self.start_coordinate_system
            ),
        )

        self.crosswalk_lines_polygons = self.crosswalk_lines_polygons + calc_crosswalk_lines(
            self.crosswalk_length,
            width,
            CartesianSystem2d(
                self.curve_segment_length, -(self.island_width / 2 + LINE_OFFSET / 2), 0.0, self.start_coordinate_system
            ),
        )

    def calc(self, prev_segment):
        super().calc(prev_segment)
        overall_length = 2 * self.curve_segment_length + self.crosswalk_length
        self.end_coordinate_system = CartesianSystem2d(overall_length, 0.0, 0.0, self.start_coordinate_system)

        self.calc_background()
        self.calc_lane(Side.LEFT)
        self.calc_lane(Side.RIGHT)
        self.calc_crosswalk_lines()


class Clothoid(Segment):
    def __init__(self, a: float, angle: float, angle_offset: float, direction: ClothoidDirection, type: ClothoidType):
        super().__init__()
        self.a = a
        self.angle = angle
        self.angle_offset = angle_offset
        self.direction = direction
        self.type = type
        self.lines: List[Polygon] = []
        self.background_polygon: List[Polygon] = []

    def get_int(self, number: float) -> int:
        return int(number + 0.5 if number >= 0 else number - 0.5)

    def move_point(self, point: List[float], postponmet: List[float]) -> List[float]:
        return [point[0] + postponmet[0], point[1] + postponmet[1], point[2]]

    def rotate_point(self, point: List[float], radian: float) -> List[float]:
        return [
            point[0] * cos(radian) + point[1] * sin(radian),
            -point[0] * sin(radian) + point[1] * cos(radian),
            point[2],
        ]

    def get_clothoid_point(self, length: float, direction: float) -> List[List[float]]:
        toggle = 1
        x = 0
        y = 0
        for loops in range(20):
            x_ = (
                toggle
                * length ** (1 + 4 * loops)
                / (self.a ** (4 * loops) * factorial(2 * loops) * (1 + 4 * loops) * 2 ** (2 * loops))
            )
            y_ = (
                toggle
                * length ** (3 + 4 * loops)
                / (self.a ** (2 + 4 * loops) * factorial(1 + 2 * loops) * (3 + 4 * loops) * 2 ** (1 + 2 * loops))
            )
            x += x_
            y += y_
            toggle *= -1
        return [x, y * direction, length]

    def get_inverted_points(self, points: List[List[float]]) -> List[List[float]]:
        angle = radians(self.angle) * self.direction.value
        new_points = []
        start = points[0]
        end = self.move_point(points[-1], [-start[0], -start[1]])
        for point in points:
            point = self.move_point(point, [-start[0], -start[1]])
            point = [(-point[0] + end[0]), (point[1] - end[1]), point[2]]
            point = self.rotate_point(point, angle)
            new_points.append(self.move_point(point, [start[0], start[1]]))
        return new_points[::-1]

    def get_clothoid(self) -> List[List[float]]:
        direction = self.direction.value * -1
        arc_length_start = self.a * sqrt(2 * radians(self.angle_offset))
        arc_length_end = self.a * sqrt(2 * radians(self.angle_offset + self.angle))
        points = []
        distance = 0.04
        l = [
            i * distance
            for i in range(self.get_int(arc_length_start / distance), self.get_int(arc_length_end / distance) + 1)
        ]
        l.append(arc_length_end)
        for i in l:
            points.append(self.get_clothoid_point(i, direction))
        first_point = [points[0][0] * -1, points[0][1] * -1]
        for i, point in enumerate(points):
            points[i] = self.rotate_point(self.move_point(point, first_point), radians(self.angle_offset) * direction)
        return points

    def get_moved_clothoid(self, points: List[List[float]], offset: float) -> List[List[float]]:
        new_points = []
        for point in points:
            angle = (point[2] ** 2 / (2 * self.a**2) - radians(self.angle_offset)) * self.direction.value
            new_points.append([point[0] + offset * sin(angle), point[1] + offset * cos(angle), point[2]])
        return new_points

    def calc(self, prev_segment: Segment) -> None:
        super().calc(prev_segment)
        direction = self.direction.value * -1
        self.direction_angle += self.angle * direction

        middle_points = self.get_clothoid()
        left_lane_points = self.get_moved_clothoid(middle_points, +LINE_OFFSET)
        right_line_points = self.get_moved_clothoid(middle_points, -LINE_OFFSET)

        if self.type == ClothoidType.OPEND:
            middle_points = self.get_inverted_points(middle_points)
            left_lane_points = self.get_inverted_points(left_lane_points)
            right_line_points = self.get_inverted_points(right_line_points)

        self.end_coordinate_system = CartesianSystem2d(
            middle_points[-1][0], middle_points[-1][1], self.angle * direction, self.start_coordinate_system
        )

        self.lines.append([Point2d(p[0], p[1], self.start_coordinate_system) for p in middle_points])
        self.lines.append([Point2d(p[0], p[1], self.start_coordinate_system) for p in left_lane_points])
        self.lines.append([Point2d(p[0], p[1], self.start_coordinate_system) for p in right_line_points])

        background_polygon = right_line_points + left_lane_points[::-1]
        self.background_polygon = [Point2d(p[0], p[1], self.start_coordinate_system) for p in background_polygon]
