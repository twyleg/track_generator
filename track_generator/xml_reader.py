# Copyright (C) 2022 twyleg
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union

from xmlschema import XMLSchema
from track_generator.track import *

# mypy: disable-error-code="union-attr"


FILE_DIR = Path(__file__).parent


def read_track(xml_input_filepath: Path) -> Track:
    print(f"Reading track: {xml_input_filepath}")
    schema = XMLSchema(FILE_DIR / "xsd/track.xsd")
    schema.validate(xml_input_filepath)

    tree = ET.parse(xml_input_filepath)
    root = tree.getroot()

    version = _read_root(root)
    width, height = _read_size(root)
    x, y = _read_origin(root)
    background = _read_background(root, xml_input_filepath)
    segments = _read_segments(root)

    return Track(version, width, height, (x, y), background, segments)


def _read_root(root: ET.Element) -> str:
    version = root.attrib["version"]
    return version


def _read_size(root: ET.Element) -> Tuple[float, float]:
    size_element = root.find("Size")
    width = size_element.attrib["width"]
    height = size_element.attrib["height"]
    return float(width), float(height)


def _read_origin(root: ET.Element) -> Tuple[float, float]:
    origin_element = root.find("Origin")
    x = origin_element.attrib["x"]
    y = origin_element.attrib["y"]
    return float(x), float(y)


def _read_background(root: ET.Element, xml_filepath: Path) -> Union[BackgroundColor, BackgroundImage]:
    background_element = root.find("Background")
    background_image_element = root.find("BackgroundImage")
    if background_element is not None:
        color = background_element.attrib["color"]
        opacity = background_element.attrib["opacity"]
        return BackgroundColor(color, float(opacity))
    elif background_image_element is not None:
        file = Path(background_image_element.attrib["file"])
        x = float(background_image_element.attrib["x"])
        y = float(background_image_element.attrib["y"])
        width = float(background_image_element.attrib["width"])
        height = float(background_image_element.attrib["height"])

        if not file.is_absolute():
            xml_file_basedir = Path(xml_filepath).parent
            file = xml_file_basedir / file

        return BackgroundImage(file, x, y, width, height)

    raise RuntimeError("Here be dragons - XSD prevents us from getting here!")


def _read_segments(root: ET.Element):
    segments_element = root.find("Segments")

    segments = []

    for segment_element in segments_element:
        if segment_element.tag == "Start":
            segments.append(_read_start_element(segment_element))
        elif segment_element.tag in ["Straight", "BlockedArea"]:
            segments.append(_read_straight_element(segment_element))
        elif segment_element.tag == "Turn":
            segments.append(_read_turn_element(segment_element))
        elif segment_element.tag == "Crosswalk":
            segments.append(_read_crosswalk_element(segment_element))
        elif segment_element.tag == "Intersection":
            segments.append(_read_intersection_element(segment_element))
        elif segment_element.tag == "Gap":
            segments.append(_read_gap_element(segment_element))
        elif segment_element.tag == "ParkingArea":
            segments.append(_read_parking_area_element(segment_element))
        elif segment_element.tag == "TrafficIsland":
            segments.append(_read_traffic_island_element(segment_element))
        elif segment_element.tag == "Clothoid":
            segments.append(_read_clothoid_element(segment_element))

    return segments


def _read_start_element(start_element: ET.Element):
    x = start_element.attrib["x"]
    y = start_element.attrib["y"]
    direction_angle = start_element.attrib["direction_angle"]
    return Start(float(x), float(y), float(direction_angle))


def _read_straight_element(straight_element: ET.Element):
    length = straight_element.attrib["length"]
    return Straight(float(length))


def _read_turn_element(turn_element: ET.Element):
    direction = turn_element.attrib["direction"]
    radius = turn_element.attrib["radius"]
    radian = turn_element.attrib["radian"]
    cw = True if direction == "right" else False
    return Arc(float(radius), float(radian), cw)


def _read_crosswalk_element(crosswalk_element: ET.Element):
    length = crosswalk_element.attrib["length"]
    return Crosswalk(float(length))


def _read_intersection_element(intersection_element: ET.Element):
    length = intersection_element.attrib["length"]
    direction = IntersectionDirection(intersection_element.attrib["direction"])
    return Intersection(float(length), direction)


def _read_gap_element(straight_element: ET.Element):
    length = straight_element.attrib["length"]
    direction = IntersectionDirection(straight_element.attrib["direction"])
    return Gap(float(length), direction)


def _read_spot_element(spot_element: ET.Element) -> ParkingArea.ParkingLot.Spot:
    type = spot_element.attrib["type"]
    length = spot_element.attrib["length"]
    return ParkingArea.ParkingLot.Spot(type, float(length))


def _read_parking_lot_element(parking_lot_element: ET.Element) -> ParkingArea.ParkingLot:
    start = parking_lot_element.attrib["start"]
    depth = parking_lot_element.attrib["depth"]
    opening_ending_angle = parking_lot_element.attrib["opening_ending_angle"]
    spots: List[ParkingArea.ParkingLot.Spot] = []

    for spot_element in parking_lot_element:
        spot = _read_spot_element(spot_element)
        spots.append(spot)

    return ParkingArea.ParkingLot(float(start), float(depth), float(opening_ending_angle), spots)


def _read_parking_area_element(parking_area_element: ET.Element):
    length = parking_area_element.attrib["length"]

    right_lots: List[ParkingArea.ParkingLot] = []
    left_lots: List[ParkingArea.ParkingLot] = []

    right_lots_element = parking_area_element.find("RightLots")
    for parking_lot_element in right_lots_element:
        parking_lot = _read_parking_lot_element(parking_lot_element)
        right_lots.append(parking_lot)

    left_lots_element = parking_area_element.find("LeftLots")
    for parking_lot_element in left_lots_element:
        parking_lot = _read_parking_lot_element(parking_lot_element)
        left_lots.append(parking_lot)

    return ParkingArea(float(length), right_lots, left_lots)


def _read_traffic_island_element(traffic_island_element: ET.Element):
    island_width = traffic_island_element.attrib["island_width"]
    crosswalk_length = traffic_island_element.attrib["crosswalk_length"]
    curve_segment_length = traffic_island_element.attrib["curve_segment_length"]
    curvature = traffic_island_element.attrib["curvature"]

    return TrafficIsland(float(island_width), float(crosswalk_length), float(curve_segment_length), float(curvature))


def _read_clothoid_element(clothoid_element: ET.Element) -> Clothoid:
    a = clothoid_element.attrib["a"]
    angle = clothoid_element.attrib["angle"]
    angle_offset = clothoid_element.attrib["angle_offset"]
    direction = ClothoidDirection(clothoid_element.attrib["direction"])
    type = ClothoidType(str(clothoid_element.attrib["type"]))

    return Clothoid(float(a), float(angle), float(angle_offset), direction, ClothoidType(type))
