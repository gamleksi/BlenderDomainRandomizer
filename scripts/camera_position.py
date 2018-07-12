import random
import bpy
import numpy as np
import mathutils

CAMERA_Z_UPPER_LIMIT = 4
CAMERA_X_LIMIT = [1.5, 6]
ANGLE_LIMIT = [0.7, 1.56]


class CameraRandomizer(object):

    def __init__(self, camera, parent_cup):
        self.camera = camera
        self.parent_cup = parent_cup
        self.reset_camera_position()

    def north_coord_limit(self, cup_coords, camera_coord):

        max_idx = np.argmax([np.abs(coord[0] - camera_coord[0]) for coord in cup_coords])
        limit_coord = np.array(cup_coords[max_idx])
        limit_coord[2] = max([coord[2] for coord in cup_coords])
        return limit_coord

    def south_coord_limit(self, cup_coords, camera_coord):

        min_idx = np.argmin([np.abs(coord[0] - camera_coord[0]) for coord in cup_coords])
        limit_coord = np.array(cup_coords[min_idx])
        limit_coord[2] = min([coord[2] for coord in cup_coords])

        return limit_coord

    def sample_z_position(self, lower_limit):
        return random.uniform(lower_limit + 1, CAMERA_Z_UPPER_LIMIT)

    def sample_x_position(self, view_angle, north_limit, south_limit, z, theta):

        # lower limit
        z_delta = z - south_limit[2]
        beta = theta - view_angle/2
        x_low = south_limit[0] + np.tan(beta) * z_delta

        # lower limit
        z_delta = z - north_limit[2]
        beta = np.pi/2 - (theta + view_angle/2)

        if beta <= 0:
            x_up = CAMERA_X_LIMIT[1]
        else:
            x_up = north_limit[0] + z_delta / np.tan(beta)

        x_up = min(x_up, CAMERA_X_LIMIT[1])
        x_low = max(x_low, CAMERA_X_LIMIT[0])

        if x_low > x_up:
            return x_low, False
        else:
            print('x_low', x_low)
            print('x_up', x_up)
            return random.uniform(x_low, x_up), True

    def west_and_east_limits(self, cup_coords, camera_y):
        side1_idx = np.argmax([np.abs(coord[1] - camera_y) for coord in cup_coords])
        side1 = np.array(cup_coords[side1_idx])
        side2_idx = np.argmax([np.abs(coord[1] - side1[1]) for coord in cup_coords])
        side2 = np.array(cup_coords[side2_idx])

        if side2[1] < side1[1]:
            west_limit = side2
            east_limit = side1
        else:
            west_limit = side1
            east_limit = side2

        return west_limit, east_limit

    def sample_y_position(self, cup_coords, camera_coord, sample_x):

        vertical_camera_angle = bpy.data.cameras['Camera'].angle_x

        west_limit, east_limit = self.west_and_east_limits(cup_coords, camera_coord[1])

        # west limit
        x_delta = sample_x - west_limit[0]
        y_west = west_limit[1] + np.tan(vertical_camera_angle/2) * x_delta

        # west limit
        x_delta = sample_x - east_limit[0]
        y_east = east_limit[1] - np.tan(vertical_camera_angle/2) * x_delta

        print('y_west', y_west)
        print('y_east', y_east)

        return random.uniform(y_west, y_east)

    def random_z_rotation(self):
        self.parent_cup.rotation_euler[2] =random.uniform(-1, 1)

    def reset_camera_position(self):
        self.camera.rotation_euler = mathutils.Vector([60, 0, 90]) * 2 * np.pi / 360
        self.camera.location = (8, 0, 6)

    def do_randomzation(self):
        self.reset_camera_position()

        cup = self.parent_cup
        mw = cup.matrix_world
        cup_coords = [np.array(mw * v.co) for v in cup.data.vertices] # Global coordinates of vertices

        camera_coord = self.camera.location
        success = False
        while not success:

            north_limit = self.north_coord_limit(cup_coords, camera_coord)
            south_limit = self.south_coord_limit(cup_coords, camera_coord)
            sample_z = self.sample_z_position(north_limit[2])
            # rotation
            sample_theta = random.uniform(ANGLE_LIMIT[0], ANGLE_LIMIT[1])
            sample_x, success = self.sample_x_position(bpy.data.cameras['Camera'].angle_y, north_limit, south_limit, sample_z, sample_theta)

        y_sample = self.sample_y_position(cup_coords, camera_coord, sample_x)

        return sample_x, y_sample, sample_z, sample_theta

    def change_camera_position(self):
        x, y, z, theta = self.do_randomzation()
        self.camera.location = (x, y, z)
        self.camera.rotation_euler[0] = theta
        self.random_z_rotation()


def blender_run():
    cr = CameraRandomizer(bpy.data.objects['Camera'], bpy.data.objects['cup_1'])
    cr.change_camera_position()

if __name__== '__main__':
    blender_run()

