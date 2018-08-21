import bpy
import random

import sys
import os
import argparse
sys.path.append(os.path.join(os.getcwd(), 'scripts'))

from texture_random import TextureRandomizer
from camera_position import CameraRandomizer
from table_setting import TableSettingRandomizer
from utils import initialize_environment
from renderer import Renderer
from logger import Logger
import time

argv = sys.argv
if "--" not in argv:
    argv = []
else:
   argv = argv[argv.index("--") + 1:]

parser = argparse.ArgumentParser()
parser.add_argument('--steps', type=int, default=10)
parser.add_argument('--folder', type=str, default='test')
parser.add_argument('--affordance', type=str, default='afforance_images/')
parser.add_argument('--image', type=str, default='images')
parser.add_argument('--depth', type=str, default='depth')

parser.add_argument('--affordance', dest='affordance', action='store_true')
parser.add_argument('--no-affordance', dest='affordance', action='store_false')
paser.set_defaults(affordance=True)

parser.add_argument('--depth', dest='depth', action='store_true')
parser.add_argument('--no-depth', dest='depth', action='store_false')
paser.set_defaults(depth=True)

parser.add_argument('--debug', dest='debug', action='store_true')
parser.add_argument('--no-debug', dest='debug', action='store_false')
paser.set_defaults(debug=False)

parser.add_argument('--sample_path', type=str, default='samples')
args = parser.parse_args(argv)

def create_folder(directory, debug):
    if not os.path.isdir(directory):
       os.makedirs(directory)
    elif not debug:
        raise Exception('Folder exist already')

def empty_memory():

    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)

    for block in bpy.data.lamps:
        if block.users == 0:
            bpy.data.lamps.remove(block)


def main(args):

    steps = args.steps
    do_affordance = args.affordance
    do_depth = args.depth
    debug = args.debug
    sample_path = args.sample_path

    folder_path = os.path.join(sample_path, args.folder)
    img_path = os.path.join(folder_path, args.image)
    affordance_path = os.path.join(folder_path, args.affordance)
    depth_path = os.path.join(folder_path, args.depth)

    create_folder(sample_path, True) # hacky
    create_folder(folder_path, debug)
    create_folder(img_path, debug)
    create_folder(affordance_path, debug)
    create_folder(depth_path, debug)

    cup_names = ['cup_1']
    inside_names = ['inside_1']
    random_names = ['random1', 'random2', 'random3', 'random4', 'random5', 'random6', 'random7', 'random8', 'random9', 'random10']
    textures = ['desk', 'wall', 'leg', 'floor'] + cup_names + inside_names + random_names

    assert(len(cup_names) == len(inside_names) and len(inside_names))

    if debug:
        random.seed(10)

    initialize_environment()

    setting_randomizer = TableSettingRandomizer(cup_names, inside_names, random_names)
    texture_randomizer = TextureRandomizer(textures)
    camera_randomizer = CameraRandomizer(bpy.data.objects['Camera'], bpy.data.objects[cup_names[0]]) # TODO: multiple cups?
    renderer = Renderer(img_path, depth_path, affordance_path, cup_names, inside_names, texture_randomizer,
                        randomizer_depth=do_depth)

    print(folder_path)
    logger = Logger(setting_randomizer, camera_randomizer, folder_path, cup_names[0])
    num_failures = 0
    start = time.time()

    for i in range(steps):

        success = False

        while not success:
            print('Table Setting randomizer')
            setting_randomizer.randomize_all()
            print('Camera randomizer')
            success = camera_randomizer.change_camera_position()
            if not success:
                print('Table and camera failed')
                num_failures += 1


        print('Logging')
        logger.log()

        # Random Textures
        print('Random textures')
        renderer.switch_to_random_textures()
        renderer.render_save()

        # Affordance labels
        if do_affordance:
            print('Affordance')
            renderer.switch_to_labels()
            renderer.render_save()

        empty_memory()

    end = time.time()
    print('num_failures', num_failures)
    print('time', end - start)

if __name__ == "__main__":
   if args.debug:
      import cProfile
      cProfile.run("main(args)", "blender.prof")
      import pstats
      p = pstats.Stats("blender.prof")
      p.sort_stats("cumulative").print_stats(20)
   else:
      main(args)

