import bpy
import random

random.seed(10)
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'scripts'))

#from scripts.texture_random import TextureRandomizer
#from scripts.camera_position import CameraRandomizer
#from scripts.table_setting import TableSettingRandomizer
#from scripts.utils import initialize_environment
#from scripts.renderer import Renderer

from texture_random import TextureRandomizer
from camera_position import CameraRandomizer
from table_setting import TableSettingRandomizer
from utils import initialize_environment
from renderer import Renderer
import time



def main(steps, do_affordance=True):

    cup_names = ['cup_1']
    inside_names = ['inside_1']
    random_names = ['random1', 'random2', 'random3', 'random4', 'random5', 'random6']

    textures = ['desk', 'wall', 'leg', 'floor'] + cup_names + inside_names + random_names
    img_path = 'test_images/'
    affordnace_path = 'test_images/'

    assert(len(cup_names) == len(inside_names) and len(inside_names))

    initialize_environment()

    setting_randomizer = TableSettingRandomizer(cup_names, inside_names, random_names)
    texture_randomizer = TextureRandomizer(textures)
    camera_randomizer = CameraRandomizer(bpy.data.objects['Camera'], bpy.data.objects[cup_names[0]]) # TODO: multiple cups?
    renderer = Renderer(img_path, affordnace_path, cup_names, inside_names, texture_randomizer)
    num_failures = 0

    start = time.time()

    for i in range(steps):

        success = False

        while not success:
            setting_randomizer.randomize_all()
            success = camera_randomizer.change_camera_position()
            if not success:
                num_failures += 1

        # Random Textures
        renderer.switch_to_random_textures()
        renderer.render_save()

        # Affordance labels
        if do_affordance:
            renderer.switch_to_labels()
            renderer.render_save()

    end = time.time()
    print('num_failures', num_failures)
    print('time', end - start)

if __name__ == "__main__":
    main(1, do_affordance=True)
