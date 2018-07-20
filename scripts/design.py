import sys, os

sys.path.append(os.path.join(os.getcwd(), 'scripts'))
import bpy
from utils import split_object, set_parent
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

    def transform_vertices(self, obj, scale=1, b=0.3):
        fz = self.random_function([v.co.z for v in obj.data.vertices])
        fz = fz * scale + b
        for i, vertex in enumerate(obj.data.vertices):
            vertex.co.x = fz[i] * vertex.co.x
            vertex.co.y = fz[i] * vertex.co.y

    def separate_cup_into_two_materials(self, cup, splitted_name):

        split_object(cup, splitted_name)
        inner_part = bpy.data.objects[splitted_name]
        set_parent(cup, inner_part)

    def randomize_cup_design(self, cup_name, inner_name):

        if cup_name in [obj.name for obj in list(bpy.data.objects)]:
            bpy.data.objects.remove(bpy.data.objects[cup_name])
            bpy.data.objects.remove(bpy.data.objects[inner_name])

        cup = self.cup_model.copy()
        cup.data = cup.data.copy()
        cup.name = cup_name

        cup.layers[1] = False
        cup.layers[0] = True

        bpy.context.scene.objects.link(cup)
        self.transform_vertices(cup)
        self.separate_cup_into_two_materials(cup, inner_name)

        return cup

    def generate_designs(self):

        cups = []
        for i, cup_name in enumerate(self.cup_names):
            cups.append(self.randomize_cup_design(cup_name, self.inner_names[i]))

        return cups

