import sys, os

import bmesh
import bpy
from src.utils import split_object, set_parent
import random
import numpy as np


class CupRandomizer(object):

    def __init__(self, cup_names, inner_names, model_name='cup_model'):

        self.model_names = model_name
        self.cup_names = cup_names
        self.inner_names = inner_names
        self.cup_model = bpy.data.objects[model_name]
        self.coefs = []

    def random_function(self, z_values):

        r2 = random.uniform(-3, 3)
        r3 = random.uniform(-np.pi/4, np.pi/4)
        r4 = np.abs(np.min(z_values)) + random.uniform(1, 3)
        r5 = random.uniform(0, 1)

        fz = np.zeros(len(z_values))
        for i, z in enumerate(z_values):

            term1 = (1 + np.sin(r2 * z + r3)) / 2
            term2 = np.log(z + r4) / 3
            fz[i] = r5 * term1 + (1 - r5) * term2

        self.coefs = [r2, r3, r4, r5]

        return fz

    def transform_vertices(self, cup_model, cup_name, scale=1, b=0.3):

        cup = cup_model.copy()
        cup.data = cup_model.data.copy()
        bm = bmesh.new()
        bm.from_mesh(cup.data)
        bm.verts.ensure_lookup_table()

        vertices = list(bm.verts)

        fz = self.random_function([v.co.z for v in vertices])
        fz = fz * scale + b

        for i, vertex in enumerate(vertices):
            co = np.array([fz[i], fz[i], 1]) * vertex.co
            bm.verts[i].co = (co[0], co[1], co[2])

        bm.to_mesh(cup.data)
        bm.free()

        cup.name = cup_name
        return cup


    def separate_cup_into_two_materials(self, cup, splitted_name):

        split_object(cup, splitted_name)
        inner_part = bpy.data.objects[splitted_name]
        set_parent(cup, inner_part)

    def randomize_cup_design(self, cup_name, inner_name):

        if cup_name in [obj.name for obj in list(bpy.data.objects)]:
            bpy.data.objects.remove(bpy.data.objects[cup_name])
            bpy.data.objects.remove(bpy.data.objects[inner_name])

        cup = self.transform_vertices(self.cup_model, cup_name)
        cup.layers[0] = True
        bpy.context.scene.objects.link(cup)

        self.separate_cup_into_two_materials(cup, inner_name)

        return cup

    def generate_designs(self):

        cups = []
        for i, cup_name in enumerate(self.cup_names):
            cups.append(self.randomize_cup_design(cup_name, self.inner_names[i]))

        return cups


if __name__ == '__main__':
    sys.path.append(os.path.join(os.getcwd(), 'src'))
    cr = CupRandomizer(['cup_1'], ['inner_1'])
    cr.generate_designs()
