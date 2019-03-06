import random
import sys
import os
import argparse
import time
import bpy

sys.path.append(os.getcwd())

from src.texture_random import TextureRandomizer
from src.camera_position import CameraRandomizer
from src.table_setting import TableSettingRandomizer
from src.utils import blender_to_object_mode, ENV_OBJECT_NAMES, RANDOM_NAMES
from src.renderer import Renderer
from src.logger import Logger

argv = sys.argv
if "--" not in argv:
    argv = []
else:
   argv = argv[argv.index("--") + 1:]

parser = argparse.ArgumentParser()
parser.add_argument('--num-samples', type=int, default=10)
parser.add_argument('--two-cups', dest='two_cups', action='store_true')
parser.set_defaults(two_cups=False)

parser.add_argument('--folder', type=str, default='test')

parser.add_argument('--affordance', dest='affordance', action='store_true')
parser.add_argument('--no-affordance', dest='affordance', action='store_false')
parser.set_defaults(affordance=True)

parser.add_argument('--depth', dest='depth', action='store_true')
parser.add_argument('--no-depth', dest='depth', action='store_false')
parser.set_defaults(depth=True)

parser.add_argument('--debug', dest='debug', action='store_true')
parser.add_argument('--no-debug', dest='debug', action='store_false')
parser.set_defaults(debug=False)

args = parser.parse_args(argv)


def create_folder(directory, debug):
    if not os.path.isdir(directory):
       os.makedirs(directory)
    elif not debug:
        raise Exception('Folder exist already')

def empty_blender_memory():

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

    if args.debug:
        random.seed(10)

    folder_path = os.path.join('samples', args.folder)
    img_path = os.path.join(folder_path, 'images')
    affordance_path = os.path.join(folder_path, 'affordances')
    depth_path = os.path.join(folder_path, 'depths')

    create_folder(folder_path, args.debug)
    create_folder(img_path, args.debug)

    if (args.affordance):
        create_folder(affordance_path, args.debug)

    if (args.depth):
        create_folder(depth_path, args.debug)

    cup_names = ['cup_1']
    inner_names = ['inside_1']

    if (args.two_cups):
        cup_names.append('cup_2')
        inner_names.append('inside_2')


    # Change the Blender UI to the right mode
    blender_to_object_mode()

    table_randomizer = TableSettingRandomizer(cup_names, inner_names)

    textures = ENV_OBJECT_NAMES + cup_names + inner_names + RANDOM_NAMES
    texture_randomizer = TextureRandomizer(textures)

    camera_randomizer = CameraRandomizer(bpy.data.objects['Camera'], bpy.data.objects[cup_names[0]], args.two_cups)

    renderer = Renderer(img_path, depth_path, affordance_path, cup_names, inner_names, texture_randomizer, include_depth=args.depth)

    logger = Logger(table_randomizer, camera_randomizer, folder_path, cup_names[0])
    start = time.time()
    num_failures = 0

    print("Rendering {} samples".format(args.num_samples))

    for i in range(args.num_samples):

        success = False

        while not success:
            # Table Setting randomizer
            table_randomizer.randomize_all()
            # Camera randomizer
            success = camera_randomizer.change_camera_position()
            if not success:
                print('Table and camera failed')
                num_failures += 1

        # Saving the current table setting to the csv
        logger.log()

        # Random Textures
        renderer.switch_to_random_textures()

        # Render  RGB(-D)
        renderer.render_save()

        # Affordance labels
        if args.affordance:
            print('Affordance')
            renderer.switch_to_labels()
            renderer.render_save()

        # Remove lamps etc
        empty_blender_memory()

    end = time.time()
    print('num_failures', num_failures)
    print('time', end - start)


if __name__ == "__main__":

   sys.path.append(os.getcwd())
   if args.debug:
      import cProfile
      cProfile.run("main(args)", "blender.prof")
      import pstats
      p = pstats.Stats("blender.prof")
      p.sort_stats("cumulative").print_stats(20)
   else:
      main(args)

