import os
import bpy
import random
from src.utils import import_object, YCB_PATH, RANDOM_NAMES


def get_ycb_paths():

    clutter_file = open('clutter_objects.txt', 'r')

    names = []

    for line in clutter_file:
        names.append(line[:-1])

    clutter_file.close()
    names = list(filter(lambda x : 'cup' not in x and 'mug' not in x and 'bowl' not in x, names))
    paths = [os.path.join(YCB_PATH, name, 'google_16k/textured.obj') for name in names]

    return (names, paths)


class ClutterObjectsRandomizer(object):

    def __init__(self):

        self.noise_objs = []
        self.random_names = RANDOM_NAMES
        object_names = [obj.name for obj in list(bpy.data.objects)]

        ycb_names, ycb_paths = get_ycb_paths()

        for i, path in enumerate(ycb_paths):

            if not ycb_names[i] in object_names:

                if not(os.path.exists(path)):
                    raise Exception('You need to load object (.obj) to the right path')

                obj = import_object(path, ycb_names[i])
                obj.layers[2] = True
                obj.layers[0] = False
                obj.scale = (7, 7, 7)
                obj.name = ycb_names[i]
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
            obj_id = random.randint(1, len(self.noise_objs) - 1) # lazy fix to remove can from the list
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
    import sys
    sys.path.append(os.getcwd())
    nr = ClutterObjectsRandomizer()
