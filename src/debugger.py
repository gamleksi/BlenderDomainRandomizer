import bpy
import random

random.seed(9)


import sys
import os
sys.path.append(os.path.join(os.getcwd()))

#from scripts.texture_random import TextureRandomizer
#from scripts.camera_position import CameraRandomizer
#from scripts.table_setting import TableSettingRandomizer
#from scripts.utils import initialize_environment
#from scripts.renderer import Renderer

from src.camera_position import CameraRandomizer
from src.table_setting import TableSettingRandomizer

def main():

    cup_names = ['cup_1']
    inside_names = ['inside_1']
    cup_path = ['/home/aleksi/hacks/thesis/code/render/objects/cup.obj']

    assert(len(cup_names) == len(inside_names) and len(inside_names) == len(cup_path))

    setting_randomizer = TableSettingRandomizer(cup_names, inside_names, cup_path, debug_cups=[bpy.data.objects[cup_names[0]]])
    camera_randomizer = CameraRandomizer(bpy.data.objects['Camera'], bpy.data.objects[cup_names[0]])
    setting_randomizer.randomize_all()
    camera_randomizer.change_camera_position()



if __name__ == "__main__":
    main()