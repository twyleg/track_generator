# Copyright (C) 2022 twyleg
import math
import drawsvg as draw

from pathlib import Path
from typing import Optional, Tuple
from track_generator.track import (
    Track,
    Start,
    Straight,
    Turn,
    Crosswalk,
    Intersection,
    Gap,
    ParkingArea,
    TrafficIsland,
    Clothoid,
    BackgroundColor,
    BackgroundImage,
)
from track_generator.coordinate_system import Point2d, Polygon

DEFAULT_LINE_WIDTH = 0.020
DEFAULT_TRACK_WIDTH = 0.800
DEFAULT_LANE_WIDTH = 0.380

DEFAULT_TRACK_COLOR = "#000000"
DEFAULT_LINE_COLOR = "#ffffff"


class SvgPoint:
    IMAGE_HEIGHT = 0.0

    def __init__(self, point: Point2d) -> None:
        self.point = point
        self.x = point.x_w
        self.y = self.IMAGE_HEIGHT - point.y_w

    @property
    def p(self) -> Tuple[float, float]:
        return self.x, self.y


class Painter:
    def __init__(self):
        self.d: Optional[draw.Drawing] = None
        self.dash_style = "stroke-miterlimit:4;stroke-dasharray:0.16,0.16;stroke-dashoffset:0"

        self.default_track_background_style = {
            "fill": "none",
            "stroke": DEFAULT_TRACK_COLOR,
            "stroke_width": DEFAULT_TRACK_WIDTH,
        }

        self.default_center_line_style = {
            "fill": "none",
            "stroke": DEFAULT_LINE_COLOR,
            "stroke_width": DEFAULT_LINE_WIDTH,
            "style": self.dash_style,
        }

        self.default_outer_line_style = {
            "fill": "none",
            "stroke": DEFAULT_LINE_COLOR,
            "stroke_width": DEFAULT_LINE_WIDTH,
        }

    @classmethod
    def direction_angle_to_svg_arc_angle(cls, direction_angle: float, cw: bool):
        rotation_angle = -90.0 if cw else 90.0
        return -direction_angle + rotation_angle

    def draw_polygon(self, polygon: Polygon, **kwargs) -> None:
        assert self.d
        points = []
        for point in polygon:
            points.extend([*SvgPoint(point).p])
        self.d.append(draw.Lines(*points, **kwargs))

    def draw_point(self, p: Point2d):
        assert self.d
        svg_p = SvgPoint(p)
        self.d.append(draw.Circle(*svg_p.p, 0.010, fill="red", stroke_width=0, stroke=DEFAULT_TRACK_COLOR))
        self.d.append(draw.Text(f"{p.x_w:.3f}\n{p.y_w:.3f}", 0.1, svg_p.x + 0.032, svg_p.y, fill="red"))

    def draw_arc_center_point(self, p: Point2d, radian_angle, radius):
        assert self.d
        svg_p = SvgPoint(p)
        self.d.append(draw.Circle(*svg_p.p, 0.010, fill="red", stroke_width=0, stroke=DEFAULT_TRACK_COLOR))
        self.d.append(
            draw.Text(
                f"{p.x_w:.3f}\n{p.y_w:.3f}\nr={radius:.3f}\na={radian_angle:.1f}°",
                0.1,
                svg_p.x + 0.032,
                svg_p.y,
                fill="red",
            )
        )

    def draw_start_verbose(self, segment: Start):
        self.draw_point(segment.start_point)

    def draw_straight(self, segment: Straight):
        self.draw_polygon(segment.center_line_polygon, **self.default_track_background_style)
        self.draw_polygon(segment.center_line_polygon, **self.default_center_line_style)
        self.draw_polygon(segment.left_line_polygon, **self.default_outer_line_style)
        self.draw_polygon(segment.right_line_polygon, **self.default_outer_line_style)

    def draw_straight_verbose(self, segment: Straight):
        self.draw_point(segment.center_line_polygon[0])
        self.draw_point(segment.left_line_polygon[0])
        self.draw_point(segment.right_line_polygon[0])

    def draw_turn(self, segment: Turn):
        assert segment.direction_angle is not None
        assert segment.start_direction_angle is not None
        assert segment.center_point
        assert self.d

        start_angle = self.direction_angle_to_svg_arc_angle(segment.start_direction_angle, segment.direction_clockwise)
        end_angle = self.direction_angle_to_svg_arc_angle(segment.direction_angle, segment.direction_clockwise)

        svg_center_point = SvgPoint(segment.center_point).p

        self.d.append(
            draw.Arc(
                *svg_center_point,
                math.fabs(segment.radius),
                start_angle,
                end_angle,
                cw=segment.direction_clockwise,
                **self.default_track_background_style,
            )
        )

        self.d.append(
            draw.Arc(
                *svg_center_point,
                math.fabs(segment.radius) - DEFAULT_LANE_WIDTH,
                start_angle,
                end_angle,
                cw=segment.direction_clockwise,
                **self.default_outer_line_style,
            )
        )

        self.d.append(
            draw.Arc(
                *svg_center_point,
                math.fabs(segment.radius) + DEFAULT_LANE_WIDTH,
                start_angle,
                end_angle,
                cw=segment.direction_clockwise,
                **self.default_outer_line_style,
            )
        )

        self.d.append(
            draw.Arc(
                *svg_center_point,
                math.fabs(segment.radius),
                start_angle,
                end_angle,
                cw=segment.direction_clockwise,
                **self.default_center_line_style,
            )
        )

    def draw_turn_verbose(self, segment: Turn):
        assert segment.direction_angle is not None
        assert segment.start_direction_angle is not None
        assert segment.center_point
        assert segment.start_point_center
        assert segment.start_point_left
        assert segment.start_point_right
        assert self.d

        start_angle = self.direction_angle_to_svg_arc_angle(segment.start_direction_angle, segment.direction_clockwise)
        end_angle = self.direction_angle_to_svg_arc_angle(segment.direction_angle, segment.direction_clockwise)

        svg_center_point = SvgPoint(segment.center_point).p

        p = draw.Path(fill="none", stroke="blue", stroke_width=DEFAULT_LINE_WIDTH)
        p.arc(
            *svg_center_point,
            math.fabs(segment.radius),
            start_angle,
            end_angle,
            cw=segment.direction_clockwise,
        )
        p.arc(
            *svg_center_point,
            0,
            start_angle,
            end_angle,
            cw=segment.direction_clockwise,
            include_l=True,
        )
        p.Z()
        self.d.append(p)

        self.draw_arc_center_point(segment.center_point, segment.radian_angle, segment.radius)
        self.draw_point(segment.start_point_center)
        self.draw_point(segment.start_point_left)
        self.draw_point(segment.start_point_right)

    def draw_crosswalk(self, segment: Crosswalk):
        self.draw_polygon(segment.center_line_polygon, **self.default_track_background_style)
        self.draw_polygon(segment.left_line_polygon, **self.default_outer_line_style)
        self.draw_polygon(segment.right_line_polygon, **self.default_outer_line_style)

        for polygon in segment.line_polygons:
            self.draw_polygon(polygon, stroke=DEFAULT_LINE_COLOR, stroke_width=0.03, fill="none")

    def draw_intersection(self, segment: Intersection):
        for polygon in segment.base_line_polygons:
            self.draw_polygon(polygon, **self.default_track_background_style)

        for polygon in segment.corner_line_polygons:
            self.draw_polygon(polygon, **self.default_outer_line_style)

        for polygon in segment.stop_line_polygons:
            self.draw_polygon(polygon, stroke=DEFAULT_LINE_COLOR, stroke_width=DEFAULT_LINE_WIDTH * 2, fill="none")

        for polygon in segment.center_line_polygons:
            self.draw_polygon(polygon, **self.default_center_line_style)

    def draw_traffic_island(self, segment: TrafficIsland):
        assert self.d
        self.draw_polygon(segment.background_polygon)

        for polygon in segment.line_polygons:
            self.draw_polygon(polygon, **self.default_outer_line_style)

        for polygon in segment.crosswalk_lines_polygons:
            self.draw_polygon(polygon, stroke=DEFAULT_LINE_COLOR, stroke_width=0.03, fill="none")

    def draw_parking_area(self, segment: ParkingArea):
        assert self.d
        self.draw_straight(segment)

        for polygon in segment.outline_polygon:
            self.draw_polygon(
                polygon, fill=DEFAULT_TRACK_COLOR, stroke=DEFAULT_LINE_COLOR, stroke_width=DEFAULT_LINE_WIDTH
            )

        for polygon in segment.spot_seperator_polygons:
            self.draw_polygon(polygon, **self.default_outer_line_style)

        for polygon in segment.blocker_polygons:
            self.draw_polygon(polygon, **self.default_outer_line_style)

    def draw_clothoid(self, segment: Clothoid):
        assert self.d
        self.draw_polygon(segment.lines[0], **self.default_track_background_style)
        self.draw_polygon(segment.lines[0], **self.default_center_line_style)
        self.draw_polygon(segment.lines[1], **self.default_outer_line_style)
        self.draw_polygon(segment.lines[2], **self.default_outer_line_style)

    def draw_template_based_segment(self, segment, template_file_path: str):
        assert self.d
        svg_start_point_center = SvgPoint(segment.start_point_center)
        self.d.append(
            draw.Image(
                svg_start_point_center.x - (segment.width / 2.0),
                svg_start_point_center.y,
                segment.width,
                segment.height,
                template_file_path,
                embed=True,
                transform=f"rotate({-segment.direction_angle + 90.0} , {svg_start_point_center.x}, {svg_start_point_center.y})",
            )
        )

    def draw_segment(self, segment):
        if isinstance(segment, Start):
            pass
        elif isinstance(segment, Gap):
            pass
        elif isinstance(segment, Crosswalk):
            self.draw_crosswalk(segment)
        elif isinstance(segment, ParkingArea):
            self.draw_parking_area(segment)
        elif isinstance(segment, Straight):
            self.draw_straight(segment)
        elif isinstance(segment, Turn):
            self.draw_turn(segment)
        elif isinstance(segment, Intersection):
            self.draw_intersection(segment)
        elif isinstance(segment, TrafficIsland):
            self.draw_traffic_island(segment)
        elif isinstance(segment, Clothoid):
            self.draw_clothoid(segment)
        else:
            raise RuntimeError()

    def draw_segment_verbose(self, segment):
        if isinstance(segment, Start):
            pass
        elif isinstance(segment, Straight):
            self.draw_straight_verbose(segment)
        elif isinstance(segment, Turn):
            self.draw_turn_verbose(segment)

    def draw_track(self, track: Track):
        SvgPoint.IMAGE_HEIGHT = track.height
        self.d = draw.Drawing(track.width, track.height, origin=track.origin, displayInline=False)
        self.d.set_pixel_scale(1000)

        if isinstance(track.background, BackgroundColor):
            self.d.append(
                draw.Rectangle(
                    0,
                    0,
                    track.width,
                    track.height,
                    fill=track.background.color,
                    fill_opacity=track.background.opacity,
                )
            )
        elif isinstance(track.background, BackgroundImage):
            img = track.background
            self.d.append(
                draw.Image(img.x, img.y, img.width, img.height, img.filepath, embed=True, preserveAspectRatio="none")
            )

        for segment in track.segments:
            self.draw_segment(segment)

    def draw_track_verbose(self, track: Track):
        for segment in track.segments:
            self.draw_segment_verbose(segment)

    def save_svg(self, track_name: str, output_directory: Path, file_name_postfix: str = ""):
        assert self.d
        output_file_path = output_directory / track_name
        self.d.save_svg(f"{output_file_path}{file_name_postfix}.svg")

    def save_png(self, track_name: str, output_directory: Path):
        assert self.d
        output_file_path = output_directory / track_name
        self.d.set_pixel_scale(1000)
        self.d.save_png(f"{output_file_path}.png")
