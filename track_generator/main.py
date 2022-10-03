from track_generator.xml_reader import XmlReader
from track_generator.painter import Painter
from track_generator.track import Start, Straight, Arc, Crosswalk, Intersection, Gap

import drawSvg as draw

# def generate_track():
#     elements = [
#         Start(1000.0, -2000.0, direction_angle=90.0),
#         Straight(6140.0),
#         Crosswalk(),
#         Arc(-1000.0, 90.0),
#         Straight(6000.0),
#         Arc(-750.0, 180.0),
#         Straight(800.0),
#         Crosswalk(),
#         Straight(800.0),
#         Arc(750.0, 180.0),
#         Straight(2000.0),
#         Arc(-1000.0, 135.0),
#         Straight(1000.0),
#         Intersection(),
#         Straight(1000.0),
#         Arc(-1000.0, 45.0),
#         Straight(2000.0),
#         Arc(-1000.0, 90.0),
#         Straight(1000.0),
#         Arc(-1000.0, 90.0),
#         Crosswalk(),
#         Straight(1730.0),
#         Arc(-1000.0, 45.0),
#         Straight(820.0),
#         Gap(),
#         Straight(1000.0),
#         Arc(-1000.0, 135.0),
#         Straight(6000.0),
#         Arc(-1000.0, 90.0),
#         Straight(500.0)
#     ]
#
#     for i in range(len(elements)):
#         if i == 0:
#             elements[i].calc()
#         else:
#             prev_elem = elements[i-1]
#             elements[i].calc(prev_elem)
#
#     d = draw.Drawing(10000, 10000, origin=(0, 0), displayInline=False)
#     for elem in elements:
#         elem.draw(d)
#         print(elem)
#
#     d.saveSvg('example.svg')


if __name__ == '__main__':

    xml_reader = XmlReader('examples/advanced_track_example.xml')
    track = xml_reader.read_track()

    painter = Painter('example', './')
    painter.draw_track(track)
