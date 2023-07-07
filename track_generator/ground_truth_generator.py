from xml.etree import cElementTree as ET, ElementTree
from xml.etree import ElementTree
from xml.dom import minidom

from track_generator.track import (
    Segment,
    Track,
    Start,
    Straight,
    Arc,
    Crosswalk,
    Intersection,
    Gap,
    ParkingArea,
    TrafficIsland,
    Clothoid,
)


class GroundTruthGenerator:
    def __init__(self, track_name: str, output_directory: str):
        self.track_name = track_name
        self.output_directory = output_directory
        self.root = ET.Element("GroundTruth", {"version": "0.0.1"})
        self.points = ET.SubElement(self.root, "Points")

    def generate_ground_truth(self, track: Track):
        for segment in track.segments:
            self.generate_segment(segment)
        with open(self.output_directory + "ground_truth.xml", "w") as f:
            f.write(minidom.parseString(ET.tostring(self.root, "utf-8")).toprettyxml(indent="\t"))

    def generate_segment(self, segment: Segment):
        if isinstance(segment, Start):
            pass
        elif isinstance(segment, (Straight, ParkingArea, Gap, Crosswalk)):
            self.generate_straight(segment)
        elif isinstance(segment, Arc):
            self.generate_arc(segment)
        elif isinstance(segment, Intersection):
            self.generate_intersection(segment)
        elif isinstance(segment, TrafficIsland):
            self.generate_traffic_island(segment)
        elif isinstance(segment, Clothoid):
            self.generate_clothoid(segment)
        else:
            raise RuntimeError(f"Error in GroundTruthGenerator: {segment} not found")

    def generate_straight(self, segment: Straight):
        for i, _ in enumerate(segment.center_line_polygon):
            self.write_points(
                [segment.left_line_polygon[i].x_w, segment.left_line_polygon[i].y_w],
                [segment.right_line_polygon[i].x_w, segment.right_line_polygon[i].y_w],
            )

    def generate_arc(self, segment: Arc):
        self.write_points(
            [segment.start_point_left.x_w, segment.start_point_left.y_w],
            [segment.start_point_right.x_w, segment.start_point_right.y_w],
        )

    def generate_intersection(self, segment: Intersection):
        for i, _ in enumerate(segment.corner_line_polygons[0]):
            self.write_points(
                [segment.corner_line_polygons[0][i].x_w, segment.corner_line_polygons[0][i].y_w],
                [segment.corner_line_polygons[1][i].x_w, segment.corner_line_polygons[1][i].y_w],
            )
        for i, _ in enumerate(segment.corner_line_polygons[0]):
            self.write_points(
                [segment.corner_line_polygons[2][i].x_w, segment.corner_line_polygons[2][i].y_w],
                [segment.corner_line_polygons[3][i].x_w, segment.corner_line_polygons[3][i].y_w],
            )

    def generate_traffic_island(self, segment: TrafficIsland):
        for i, _ in enumerate(segment.line_polygons[2]):
            self.write_points(
                [segment.line_polygons[2][i].x_w, segment.line_polygons[2][i].y_w],
                [segment.line_polygons[3][i].x_w, segment.line_polygons[3][i].y_w],
            )

    def generate_clothoid(self, segment: Clothoid):
        for i, _ in enumerate(segment.lines[0]):
            self.write_points(
                [segment.lines[1][i].x_w, segment.lines[1][i].y_w], [segment.lines[2][i].x_w, segment.lines[2][i].y_w]
            )

    def write_points(self, point_1: list, point_2: list):
        ET.SubElement(
            self.points,
            "Point",
            {
                "x_1": str(point_1[0]),
                "y_1": str(point_1[1]),
                "x_2": str(point_2[0]),
                "y_2": str(point_2[1]),
            },
        )
