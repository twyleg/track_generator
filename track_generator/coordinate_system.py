# Copyright (C) 2022 twyleg
import numpy as np
import pytransform3d.rotations as pyrot
import pytransform3d.transformations as pytr
from typing import Optional, List


class WorldCoordinateSystem:
    def __init__(self):
        self.local_to_world = pytr.transform_from(
            pyrot.matrix_from_axis_angle(np.array([0.0, 0.0, 1.0, 0.0])),
            np.array([0.0, 0.0, 0.0])
        )


class CartesianSystem2d:

    def __init__(self, x: float, y: float, yaw: float, parent: Optional['CartesianSystem'] = WorldCoordinateSystem()):

        p = np.array([x, y, 0.0])
        a = np.array([0.0, 0.0, 1.0, np.deg2rad(yaw)])
        local_to_parent = pytr.transform_from(pyrot.matrix_from_axis_angle(a), p)
        parent_to_world = parent.local_to_world
        self.local_to_world = pytr.concat(local_to_parent, parent_to_world)


class Point2d:
    def __init__(self, x_l: float, y_l: float, local_coordinate_system: CartesianSystem2d):
        self.local_coordinate_system = local_coordinate_system
        self.x_l = x_l
        self.y_l = y_l

        point_world = pytr.transform(self.local_coordinate_system.local_to_world, np.array([self.x_l, self.y_l, 0.0, 1.0]))
        self.x_w = point_world[0]
        self.y_w = point_world[1]

    def __str__(self):
        return f'Local: ({self.x_l},{self.y_l}), World: ({self.x_w},{self.y_w})'


Polygon = List[Point2d]

# class Polygon(List[Point2d]):
#     def __init__(self, *args):
#         super().__init__(self, *args)