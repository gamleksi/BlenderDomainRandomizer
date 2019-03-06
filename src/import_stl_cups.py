import os, sys
sys.path.append(os.path.join(os.getcwd(), 'scripts'))
import bpy
from design import CupRandomizer

# Script: Creating stl meshes for Mujoco

if __name__ == '__main__':

    fpath = "/home/aleksi/mujoco_ws/src/lumi_testbed/lumi_description/meshes"

    for i in range(10):
        cr = CupRandomizer(['cup_1'], ['inner_1'])
        cr.generate_designs()
        bpy.ops.object.select_all(action='DESELECT')
        fPath = os.path.join(fpath, '{}'.format(i + 1))
        bpy.data.objects['cup_1'].select = True
        bpy.ops.export_mesh.stl(filepath=fPath, ascii=False, batch_mode = 'OBJECT')
