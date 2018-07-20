import sys, os, bpy

sys.path.append(os.path.join(os.getcwd(), 'scripts'))
from utils import import_object


YCB_PATH = 'objects/ycb'
NAMES = os.listdir(YCB_PATH)

NAMES = list(filter(lambda x : 'cup' not in x and 'mug' not in x and 'bowl' not in x, NAMES))

PATHS = [os.path.join(YCB_PATH, name, 'google_16k/textured.obj') for name in NAMES]


import random
import numpy as np

class NoiseObjectsRandomizer(object):

    def __init__(self, random_names, object_paths=PATHS, names=NAMES):

        self.noise_objs = []
        self.random_names = random_names
        object_names = [obj.name for obj in list(bpy.data.objects)]

        for i, path in enumerate(object_paths):

            if not names[i] in object_names:
                obj = import_object(path, names[i])
                obj.layers[2] = True
                obj.layers[0] = False
                obj.scale = (7, 7, 7)
                obj.name = names[i]
                obj.rotation_euler[0] = 0
            else:
                self.noise_objs.append(bpy.data.objects[object_names[i]])

        self.random_ids = []
        self.random_objects = []

    def get_info(self):

        objects = []
        ids = []

        for i, name in enumerate(self.random_names):
            if bpy.data.objects.get(name) is not None:
                objects.append(bpy.data.objects[name])
                ids.append(self.random_ids[i])

        return objects, ids

    def generate(self):

        for name in self.random_names:
            if bpy.data.objects.get(name) is not None:
                bpy.data.objects.remove(bpy.data.objects[name])

        num_objects = random.randint(0, len(self.random_names))
        random_objects = []
        self.random_ids = []

        for i in range(num_objects):
            obj_id = random.randint(0, len(self.noise_objs) - 1)
            noise_obj = self.noise_objs[obj_id]
            self.random_ids.append(noise_obj.name)
            obj = noise_obj.copy()
            obj.data = noise_obj.data.copy()
            obj.name = self.random_names[i]
            obj.layers[0] = True
            obj.layers[2] = False
            bpy.context.scene.objects.link(obj)
            random_objects.append(obj)

        return random_objects



if __name__ == "__main__":
    random_names = ['random1', 'random2', 'random3', 'random4', 'random5', 'random6']
    nr = NoiseObjectsRandomizer(random_names)
