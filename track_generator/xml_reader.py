# Copyright (C) 2022 twyleg
import os
import xml.etree.ElementTree as ET

from track_generator.track import *


class ElementMissingException(Exception):
    def __init__(self, element_name: str, parent_element: ET.Element):
        self.element_name = element_name
        self.parent_element = parent_element

    def __str__(self):
        return f'ElementMissingException: missing element="{self.element_name}" in parent element "{self.parent_element.tag}"'


class AttributeMissingException(Exception):
    def __init__(self, attribute_name: str, element: ET.Element):
        self.attribute_name = attribute_name
        self.element = element

    def __str__(self):
        return f'AttributeMissingException: missing attribute="{self.attribute_name}" in element "{self.element.tag}""'


def read_track(xml_input_file_path: str) -> Track:
    tree = ET.parse(xml_input_file_path)
    root = tree.getroot()

    version = _read_root(root)
    width, height = _read_size(root)
    x, y = _read_origin(root)
    background = _read_background(root, xml_input_file_path)
    segments = _read_segments(root)

    return Track(version, width, height, (x, y), background, segments)


def _read_root(root: ET.Element) -> str:
    version = root.get('version')

    if version is None:
        raise AttributeMissingException('version', root)

    return version


def _read_size(root: ET.Element) -> Tuple[float, float]:

    size_element = root.find('Size')

    if size_element is None:
        raise ElementMissingException('Size', root)

    width = size_element.get('width')
    height = size_element.get('height')

    if width is None:
        raise AttributeMissingException('width', size_element)

    if height is None:
        raise AttributeMissingException('height', size_element)

    return float(width), float(height)


def _read_origin(root: ET.Element) -> Tuple[float, float]:

    origin_element = root.find('Origin')

    if origin_element is None:
        raise ElementMissingException('Origin', root)

    x = origin_element.get('x')
    y = origin_element.get('y')

    if x is None:
        raise AttributeMissingException('x', origin_element)

    if y is None:
        raise AttributeMissingException('y', origin_element)

    return float(x), float(y)


def _read_background(root: ET.Element, xml_file_path: str) -> Background:

    background_element = root.find('Background')

    if background_element is None:
        raise ElementMissingException('Background', root)

    color = background_element.get('color')
    opacity = background_element.get('opacity')

    if color is None:
        raise AttributeMissingException('color', background_element)

    if opacity is None:
        raise AttributeMissingException('opacity', background_element)

    background_color = Background.Color(color, opacity)

    background_image_element = root.find('BackgroundImage')
    background_image = None

    if background_image_element is not None:
        file = background_image_element.get('file')
        x = float(background_image_element.get('x'))
        y = float(background_image_element.get('y'))
        width = float(background_image_element.get('width'))
        height = float(background_image_element.get('height'))

        if not os.path.isabs(file):
            xml_file_basedir = os.path.dirname(xml_file_path)
            file = os.path.join(xml_file_basedir, file)

        background_image = Background.Image(file, x, y, width, height)

    return Background(background_color, background_image)


def _read_segments(root: ET.Element):

    segments_element = root.find("Segments")

    if segments_element is None:
        raise ElementMissingException('Segments', root)

    segments = []

    for segment_element in segments_element:
        if segment_element.tag == 'Start':
            segments.append(_read_start_element(segment_element))
        elif segment_element.tag in ['Straight', 'BlockedArea']:
            segments.append(_read_straight_element(segment_element))
        elif segment_element.tag == 'Turn':
            segments.append(_read_turn_element(segment_element))
        elif segment_element.tag == 'Crosswalk':
            segments.append(_read_crosswalk_element(segment_element))
        elif segment_element.tag == 'Intersection':
            segments.append(_read_intersection_element(segment_element))
        elif segment_element.tag == 'Gap':
            segments.append(_read_gap_element(segment_element))
        elif segment_element.tag == 'ParkingArea':
            segments.append(_read_parking_area_element(segment_element))
        elif segment_element.tag == 'TrafficIsland':
            segments.append(_read_traffic_island_element(segment_element))
        elif segment_element.tag == 'Clothoid':
            segments.append(_read_clothoid_element(segment_element))

    return segments


def _read_start_element(start_element: ET.Element):
    x = start_element.get('x')
    y = start_element.get('y')
    direction_angle = start_element.get('direction_angle')

    if x is None:
        raise AttributeMissingException('x', start_element)
    elif y is None:
        raise AttributeMissingException('y', start_element)
    elif direction_angle is None:
        raise AttributeMissingException('direction_angle', start_element)

    return Start(float(x), float(y), float(direction_angle))


def _read_straight_element(straight_element: ET.Element):
    length = straight_element.get('length')

    if length is None:
        raise AttributeMissingException('length', straight_element)

    return Straight(float(length))


def _read_turn_element(turn_element: ET.Element):
    direction = turn_element.get('direction')
    radius = turn_element.get('radius')
    radian = turn_element.get('radian')

    if direction is None:
        raise AttributeMissingException('direction', turn_element)
    elif radius is None:
        raise AttributeMissingException('radius', turn_element)
    elif radian is None:
        raise AttributeMissingException('radian', turn_element)

    cw = True if direction == 'right' else False

    return Arc(float(radius), float(radian), cw)


def _read_crosswalk_element(crosswalk_element: ET.Element):
    length = crosswalk_element.get('length')

    if length is None:
        raise AttributeMissingException('length', crosswalk_element)

    return Crosswalk(float(length))


def _read_intersection_element(intersection_element: ET.Element):
    length = intersection_element.get('length')
    direction = IntersectionDirection(str(intersection_element.get('direction')))
    if length is None:
        raise AttributeMissingException('length', intersection_element)
    return Intersection(float(length), direction)


def _read_gap_element(straight_element: ET.Element):
    length = straight_element.get('length')
    direction = IntersectionDirection(str(straight_element.get('direction')))
    if length is None:
        raise AttributeMissingException('length', straight_element)

    return Gap(float(length), direction)


def _read_spot_element(spot_element: ET.Element) -> ParkingArea.ParkingLot.Spot:
    type = spot_element.get('type')
    length = spot_element.get('length')
    return ParkingArea.ParkingLot.Spot(type, float(length))


def _read_parking_lot_element(parking_lot_element: ET.Element) -> ParkingArea.ParkingLot:
    start = parking_lot_element.get('start')
    depth = parking_lot_element.get('depth')
    opening_ending_angle = parking_lot_element.get('opening_ending_angle')
    spots: List[ParkingArea.ParkingLot.Spot] = []

    for spot_element in parking_lot_element:
        spot = _read_spot_element(spot_element)
        spots.append(spot)

    return ParkingArea.ParkingLot(float(start), float(depth), float(opening_ending_angle), spots)


def _read_parking_area_element(parking_area_element: ET.Element):
    length = parking_area_element.get('length')

    if length is None:
        raise AttributeMissingException('length', parking_area_element)

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
    island_width = traffic_island_element.get('island_width')
    crosswalk_length = traffic_island_element.get('crosswalk_length')
    curve_segment_length = traffic_island_element.get('curve_segment_length')
    curvature = traffic_island_element.get('curvature')

    return TrafficIsland(float(island_width), float(crosswalk_length), float(curve_segment_length), float(curvature))

def _read_clothoid_element(clothoid_element: ET.Element) -> Clothoid:
    a = clothoid_element.get('a')
    angle = clothoid_element.get('angle')
    angle_offset = clothoid_element.get('angle_offset')
    direction = ClothoidDirection.RIGHT if clothoid_element.get('direction') == 'right' else ClothoidDirection.LEFT
    type = ClothoidType(str(clothoid_element.get('type')))

    return Clothoid(float(a), float(angle), float(angle_offset), direction, str(type))
