import bpy
import random
import numpy as np
from src.utils import remove_object, set_parent, split_object
from src.design import CupRandomizer
from src.random_objects import ClutterObjectsRandomizer
from src.collision import check_collision


class TableSettingRandomizer(object):

    def __init__(self, cup_names, inner_names, max_num_lamps=8, desk_scale_limit=(2, 4), cup_scale_limit=(0.2, 0.4), lamp_pos_limit=(-8,8),
                lamp_height_limit=(3, 10)):

        self.desk_scale_limit = desk_scale_limit
        self.desk = bpy.data.objects['desk']

        self.cup_scale_limit = cup_scale_limit
        self.cup_randomizer = CupRandomizer(cup_names, inner_names)
        self.cups = self.cup_randomizer.generate_designs()

        self.random_cup_position()
        self.random_cup_scale()

        self.clutter_randomizer = ClutterObjectsRandomizer()

        self.lamp_pos_limit = lamp_pos_limit
        self.lamp_height_limit = lamp_height_limit

        self.lamps = []
        self.max_num_lamps = max_num_lamps
        self.random_lamps()

    def separate_cup_into_two_materials(self, cup_name, splitted_name):

        cup = bpy.data.objects[cup_name]
        split_object(cup, splitted_name)
        inner_part = bpy.data.objects[splitted_name]
        set_parent(cup, inner_part)

    def randomize_all(self):
        self.random_lamps()
        self.random_desk_scale()
        self.cups = self.cup_randomizer.generate_designs()
        self.random_cup_scale()
        self.random_cup_position()
        self.random_clutter_objects()

    def random_desk_scale(self):

       self.desk.scale = (
           random.uniform(self.desk_scale_limit[0], self.desk_scale_limit[1]),
           random.uniform(self.desk_scale_limit[0], self.desk_scale_limit[1]),
           self.desk.scale[2]
       )

    def random_cup_scale(self):

        for cup in self.cups:
            scale = random.uniform(self.cup_scale_limit[0], self.cup_scale_limit[1])
            cup.scale = (scale, scale, scale)

    def random_position(self, x_limit, y_limit, z_limit):

        x = random.uniform(x_limit[0], x_limit[1])
        y = random.uniform(y_limit[0], y_limit[1])
        z = random.uniform(z_limit[0], z_limit[1])
        return x, y, z

    def random_lamps(self):

        for lamp in self.lamps:
            remove_object(lamp)
        self.lamps = []
        for i in range(random.randint(1, self.max_num_lamps)):
            bpy.ops.object.lamp_add(location=self.random_position(
                self.lamp_pos_limit,
                self.lamp_pos_limit,
                self.lamp_height_limit
            ))
            self.lamps.append(bpy.context.object)

    def random_cup_position(self):

        desk_mw = np.array([self.desk.matrix_world])
        corner_coords = desk_mw @ np.array([1, 1, 0, 1])

        x_max = corner_coords[0][0] * 0.7
        y_max = corner_coords[0][1] * 0.7

        # Cup origin on top of the table
        set_parent(self.desk, self.cups[0], vertex_parenting=True)

        # Draw x and y positions
        x = random.uniform(-x_max, x_max)
        y = random.uniform(-y_max, y_max)

        self.cups[0].location = (x, y, self.desk.location[2])
        self.cups[0].rotation_euler[2] = 0 # for initializing camera position

        # Uses collision checking (brute force) to draw a position for other cups
        for idx in range(1, len(self.cups)):

            set_parent(self.desk, self.cups[idx], vertex_parenting=True)

            collision = True
            while collision:

                x = random.uniform(-x_max, x_max)
                y = random.uniform(-y_max, y_max)

                self.cups[idx].location = (x, y, self.desk.location[2])
                self.cups[idx].rotation_euler[2] = 0

                collision = check_collision(self.cups[idx], self.cups[0])


    def random_clutter_objects(self):

        desk_mw = np.array([self.desk.matrix_world])
        corner_coords = desk_mw @ np.array([1, 1, 0, 1])
        x_max = corner_coords[0][0] * 0.7
        y_max = corner_coords[0][1] * 0.7

        # Sets the random number of clutter objects on the table
        noise_objects = self.clutter_randomizer.generate()

        for obj in noise_objects:

            collision = True
            while collision:

                x = random.uniform(-x_max, x_max)
                y = random.uniform(-y_max, y_max)

                obj.scale = (
                        random.uniform(4, 7),
                        random.uniform(4, 7), random.uniform(4, 7))

                obj.location = (x, y, self.desk.location[2])
                obj.rotation_euler[2] = random.uniform(0, np.pi * 2)

                # Checks the first cup collision
                collision = check_collision(obj, self.cups[0])

                # If collision not occudered, check a collision with rest of the cups
                if not(collision):
                    for idx in range(1, len(self.cups)):
                        collision = check_collision(obj, self.cups[idx])
                        if (collision):
                            break


if __name__ == "__main__":
    import sys, os
    sys.path.append(os.getcwd())
    cup_names = ['cup_1']
    inside_names = ['inside_1']
    setting_randomizer = TableSettingRandomizer(cup_names, inside_names)
