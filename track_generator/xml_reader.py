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


class XmlReader:

    def __init__(self, xml_input_file_path: str):
        self.xml_input_file_path = xml_input_file_path

    def read_track(self) -> Track:
        tree = ET.parse(self.xml_input_file_path)
        root = tree.getroot()

        name, version = self._read_meta(root)
        width, height = self._read_size(root)
        x, y = self._read_origin(root)
        background_color, background_opacity = self._read_background(root)
        segments = self._read_segments(root)


        return Track(name, version, width, height, (x, y), background_color, background_opacity, segments)

    def _read_meta(self, root: ET.Element) -> Tuple[str, str]:
        meta_element = root.find('Meta')

        if meta_element is None:
            raise ElementMissingException('Meta', root)

        name = meta_element.get('name')
        version = meta_element.get('version')

        if name is None:
            raise AttributeMissingException('name', meta_element)
        elif version is None:
            raise AttributeMissingException('version', meta_element)

        return name, version

    def _read_size(self, root: ET.Element) -> Tuple[float, float]:

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

    def _read_origin(self, root: ET.Element) -> Tuple[float, float]:

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

    def _read_background(self, root: ET.Element) -> Tuple[str, float]:

        background_element = root.find('Background')

        if background_element is None:
            raise ElementMissingException('Background', root)

        color = background_element.get('color')
        opacity = background_element.get('opacity')

        if color is None:
            raise AttributeMissingException('color', background_element)

        if opacity is None:
            raise AttributeMissingException('opacity', background_element)

        return color, float(opacity)

    def _read_segments(self, root: ET.Element):

        segments_element = root.find("Segments")

        if segments_element is None:
            raise ElementMissingException('Segments', root)

        segments = []

        for segment_element in segments_element:
            if segment_element.tag == 'Start':
                segments.append(self._read_start_element(segment_element))
            elif segment_element.tag == 'Straight':
                segments.append(self._read_straight_element(segment_element))
            elif segment_element.tag == 'Turn':
                segments.append(self._read_turn_element(segment_element))
            elif segment_element.tag == 'Crosswalk':
                segments.append(self._read_crosswalk_element(segment_element))
            elif segment_element.tag == 'Intersection':
                segments.append(self._read_intersection_element(segment_element))
            elif segment_element.tag == 'Gap':
                segments.append(self._read_gap_element(segment_element))

        return segments

    def _read_start_element(self, start_element: ET.Element):
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

    def _read_straight_element(self, straight_element: ET.Element):
        length = straight_element.get('length')

        if length is None:
            raise AttributeMissingException('length', straight_element)

        return Straight(float(length))

    def _read_turn_element(self, turn_element: ET.Element):
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

    def _read_crosswalk_element(self, crosswalk_element: ET.Element):
        return Crosswalk()

    def _read_intersection_element(self, intersection_element: ET.Element):
        return Intersection()

    def _read_gap_element(self, straight_element: ET.Element):
        length = straight_element.get('length')

        if length is None:
            raise AttributeMissingException('length', straight_element)

        return Gap(float(length))
