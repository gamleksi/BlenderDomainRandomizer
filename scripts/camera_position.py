import random
import bpy
import numpy as np
import mathutils
from bpy_extras.object_utils import world_to_camera_view

CAMERA_Z_UPPER_LIMIT = 4
CAMERA_X_LIMIT = [1.5, 3]
ANGLE_LIMIT = [0.7, np.pi/2]


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

    def sample_z_position(self, north_limit):
        return random.uniform(north_limit[2] + 1, CAMERA_Z_UPPER_LIMIT)

    def sample_x_position(self, view_angle, south_limit, z):

        # lower limit
        z_delta = np.abs(z - south_limit[2])
        x_low = south_limit[0] + z_delta / np.tan(view_angle / 2)
        return random.uniform(1.2 * x_low, CAMERA_X_LIMIT[1])

    def sample_x_rotation(self, view_angle, north_limit, south_limit, z, x):

        # low angle
        delta_x = np.abs(x - north_limit[0])
        delta_z = np.abs(z - north_limit[2])
        low_angle = np.arctan(delta_x / delta_z) - view_angle / 2
        low_angle = low_angle * 1.1

        # high angle
        delta_x = np.abs(x - south_limit[0])
        delta_z = np.abs(z - south_limit[2])
        high_angle = np.arctan(delta_x / delta_z) + view_angle / 2
        high_angle = high_angle * 0.95
        high_angle = min(np.pi/2 - 0.2, high_angle)

        return random.uniform(low_angle, high_angle)

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

    def sample_y_position(self, west_limit, east_limit, sample_x):

        vertical_camera_angle = bpy.data.cameras['Camera'].angle_x

        # west limit
        x_delta = sample_x - west_limit[0]
        y_west = west_limit[1] + np.tan(vertical_camera_angle/2) * x_delta

        if y_west < 0:
            y_west = y_west * 1.1
        else:
            y_west = y_west * 0.9

        # west limit
        x_delta = sample_x - east_limit[0]
        y_east = east_limit[1] - np.tan(vertical_camera_angle/2) * x_delta

        if y_east < 0:
            y_east = y_east * 0.9
        else:
            y_east = y_east * 1.1

        return random.uniform(y_west, y_east)

    def random_z_rotation(self, view_angle, sample_y, sample_x, west_limit, east_limit):

        # highest angle
        delta_y = np.abs(sample_y - west_limit[1])
        delta_x = np.abs(sample_x - west_limit[0])
        theta = np.arctan(delta_y/ delta_x)

        if sample_y < west_limit[1]:
            west_angle = view_angle/2 + theta
        else:
            west_angle = view_angle/2 - theta

        # lowest angle
        delta_y = np.abs(sample_y - east_limit[1])
        delta_x = np.abs(sample_x - east_limit[0])
        theta = np.arctan(delta_y/ delta_x)

        if sample_y < east_limit[1]:
            east_angle = view_angle/2 - theta
        else:
            east_angle = view_angle/2 + theta

        return np.pi/2 + 0.95 * random.uniform(-west_angle, east_angle)

    def reset_camera_position(self):
        bpy.context.scene.update()
        self.camera = bpy.context.scene.objects['Camera']
        self.parent_cup = bpy.context.scene.objects['cup_1']
        self.camera.rotation_euler = mathutils.Vector([90, 0, 90]) * 2 * np.pi / 360
        self.camera.location = (4, 0, 6)

    def do_randomzation(self):

        self.reset_camera_position()
        cup = self.parent_cup
        mw = cup.matrix_world
        cup_coords = [np.array(mw * v.co) for v in cup.data.vertices] # Global coordinates of vertices

        # second cup
        cup2 = bpy.context.scene.objects['cup_2']
        mw = cup2.matrix_world
        cup_coords2 = [np.array(mw * v.co) for v in cup2.data.vertices] # Global coordinates of vertices

        cup_coords = cup_coords + cup_coords2

        camera_coord = self.camera.location

        north_limit = self.north_coord_limit(cup_coords, camera_coord)
        south_limit = self.south_coord_limit(cup_coords, camera_coord)
        west_limit, east_limit = self.west_and_east_limits(cup_coords, camera_coord[1])

        sample_z = self.sample_z_position(north_limit)
        # rotation
        sample_x = self.sample_x_position(bpy.data.cameras['Camera'].angle_y, south_limit, sample_z)
        sample_x_rotation = self.sample_x_rotation(bpy.data.cameras['Camera'].angle_y, north_limit, south_limit, sample_z, sample_x)

        sample_y = self.sample_y_position(west_limit, east_limit, sample_x)
        sample_z_rotation = self.random_z_rotation(bpy.data.cameras['Camera'].angle_x, sample_y, sample_x, west_limit, east_limit)

        return sample_x, sample_y, sample_z, sample_x_rotation, sample_z_rotation, [north_limit, south_limit, west_limit, east_limit]

    def change_camera_position(self):

        x, y, z, sample_x_rotation, sample_z_rotation, limits = self.do_randomzation()
        self.camera.location = (x, y, z)
        self.camera.rotation_euler[0] = sample_x_rotation
        self.camera.rotation_euler[2] = sample_z_rotation
        success = self.coords_within_image(limits)
        return success

    def coords_within_image(self, coords):

        scene = bpy.context.scene
        scene.update()
        cs, ce = self.camera.data.clip_start, self.camera.data.clip_end

        object_names = [obj.name for obj in list(bpy.data.objects)]
        random_objects = []
        image_coords = []

        for name in object_names:

            if 'random' == name[:6]:
                obj = bpy.data.objects[name]
                mat_world = obj.matrix_world
                verts = (mat_world * vert.co for vert in obj.data.vertices)
                coords_2d = [world_to_camera_view(scene, self.camera, coord) for coord in verts]
                image_coords.append(coords_2d)
                random_objects.append(obj)

        def random_object_is_blocking(obj_coords, limit_coord):

            for co in obj_coords:
                if np.abs(co.x - limit_coord.x) < 0.01 and np.abs(co.y - limit_coord.y) < 0.01 and co.z < limit_coord.z:
                    return True
            return False

        for idx, coord in enumerate(coords):
            coord = mathutils.Vector(coord)
            co_ndc = world_to_camera_view(scene, self.camera, coord)

            if not((0.0 < co_ndc.x < 1.0 and
                0.0 < co_ndc.y < 1.0 and cs < co_ndc.z < ce)):

                return False

            update_objects = []
            update_image_coords = []
            for i in range(len(image_coords)):

                if random_object_is_blocking(image_coords[i], co_ndc):
                    obstacle = random_objects[i]
                    print('POP', obstacle.name)
                    bpy.data.objects.remove(obstacle)
                else:
                    update_objects.append(random_objects[i])
                    update_image_coords.append(image_coords[i])
            random_objects = update_objects
            image_coords = update_image_coords

        return True


def blender_run():
    cr = CameraRandomizer(bpy.data.objects['Camera'], bpy.data.objects['cup_1'])
    cr.change_camera_position()

if __name__== '__main__':
    blender_run()

