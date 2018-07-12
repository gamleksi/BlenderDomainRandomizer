import bpy
import random

random.seed(9)


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

def main(steps, do_affordance=True):

    cup_names = ['cup_1']
    inside_names = ['inside_1']
    cup_path = ['/home/aleksi/hacks/thesis/code/render/objects/cup.obj']
    textures = ['desk', 'wall', 'leg', 'floor'] + cup_names + inside_names
    img_path = '/home/aleksi/hacks/thesis/code/render/test_images'
    affordnace_path = '/home/aleksi/hacks/thesis/code/render/test_images'

    assert(len(cup_names) == len(inside_names) and len(inside_names) == len(cup_path))

    initialize_environment()

    setting_randomizer = TableSettingRandomizer(cup_names, inside_names, cup_path)
    texture_randomizer = TextureRandomizer(textures)
    camera_randomizer = CameraRandomizer(bpy.data.objects['Camera'], bpy.data.objects[cup_names[0]]) # TODO: multiple cups?
    renderer = Renderer(img_path, affordnace_path, cup_names, inside_names, texture_randomizer)

    for i in range(steps):

        setting_randomizer.randomize_all()
        camera_randomizer.change_camera_position()

        # Random Textures
        renderer.switch_to_random_textures()
        renderer.render_save()

        # Affordance labels
        if do_affordance:
            renderer.switch_to_labels()
            renderer.render_save()

if __name__ == "__main__":
    main(1, do_affordance=False)
