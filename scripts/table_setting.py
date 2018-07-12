import bpy
import random
import sys
import os
import numpy as np

sys.path.append(os.path.join(os.getcwd(), 'scripts'))

# from scripts.utils import remove_object, set_parent, split_object, switch_origin, import_object
from utils import remove_object, set_parent, split_object, switch_origin, import_object

class TableSettingRandomizer(object):

    def __init__(self, cup_names, inside_names, cup_paths, max_num_lamps=8, desk_scale_limit=(2, 4), cup_scale_limit=(0.05, 0.2), lamp_pos_limit=(-8,8),
                lamp_height_limit=(3, 10), debug_cups=None):

        if debug_cups is None:

            self.cups = self.import_cups(cup_names, cup_paths)
            for i, cup_name in enumerate(cup_names):
                self.separate_cup_into_two_materials(cup_name, inside_names[i])
        else:
            self.cups = [bpy.data.objects[cup_names[0]]]

        self.desk = bpy.data.objects['desk']

        self.desk_scale_limit = desk_scale_limit
        self.cup_scale_limit = cup_scale_limit
        self.lamp_pos_limit = lamp_pos_limit
        self.lamp_height_limit = lamp_height_limit

        self.lamps = []
        self.max_num_lamps = max_num_lamps
        self.random_lamps()

        set_parent(self.cups[0], bpy.data.objects['Camera'])



    def import_cups(self, cup_names, cup_paths):

        cups = []

        for i in range(len(cup_names)):

            if hasattr(bpy.data.objects, cup_names[i]):
                print('hello')
                cups.append(bpy.data.objects[cup_names[i]])
            else:
                cups.append(self.setup_cup_on_table(cup_paths[i], cup_names[i]))

        return cups

    def setup_cup_on_table(self, path, name):

        switch_origin('desk', max_point=True, coords=(0, 0))
        obj = import_object(path, name)
        switch_origin(name, max_point=False)
        obj.scale = (0.15, 0.15, 0.15) # TODO: multiple cups
        desk = bpy.data.objects['desk']
        obj.location = (0, 0, desk.location[2]) # TODO: multiple cups
        set_parent(desk, obj, vertex_parenting=True)

        return obj

    def separate_cup_into_two_materials(self, cup_name, splitted_name):

        cup = bpy.data.objects[cup_name]
        split_object(cup, splitted_name)
        inner_part = bpy.data.objects[splitted_name]
        set_parent(cup, inner_part)

    def randomize_all(self):
        self.random_lamps()
        self.random_desk_scale()
        self.random_cup_scale()
        self.random_cup_position()

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

        for cup in self.cups: # TODO: multiple cups

            x_max = corner_coords[0][0] * 0.7
            y_max = corner_coords[0][1] * 0.7

            x = random.uniform(-x_max, x_max)
            y = random.uniform(-y_max, y_max)

            cup.location = (x, y, cup.location[2])
            cup.rotation_euler[2] = 0 # for initializing camera position

