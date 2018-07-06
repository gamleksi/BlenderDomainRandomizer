import bpy
import random

from math import pi
import mathutils

import numpy as np
import bmesh

random.seed(3)

cup_path ='/home/aleksi/hacks/thesis/code/render/objects/cup.obj'
img_path = '/home/aleksi/hacks/thesis/code/render/test_images'

import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'scripts'))
from texture_random import intialize_textures, switch_to_random_textures



def deselected_all():
    bpy.ops.object.select_all(action='DESELECT')


def import_object(path, name, idx=0):

    bpy.ops.import_scene.obj(filepath=path)
    obj = bpy.context.selected_objects[idx]
    obj.name = name

    return obj

def remove_object(obj):

    deselected_all()
    obj.select = True
    bpy.ops.object.delete()


def render_save(img_path, index, depth=True, depth_name='depth', img_name='image'):

    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links

    for n in tree.nodes:
        tree.nodes.remove(n)

    rl = tree.nodes.new(type="CompositorNodeRLayers")

    if depth:

        mapValue = tree.nodes.new(type='CompositorNodeMapValue')
        mapValue.use_max = True; mapValue.use_min = True;
        mapValue.min = [0.]; mapValue.max = [255.]; mapValue.size = [0.05];

        links.new(rl.outputs['Depth'], mapValue.inputs['Value'])

        invert = tree.nodes.new(type='CompositorNodeInvert')
        links.new(mapValue.outputs['Value'], invert.inputs['Color'])

        # Visual Purpose
        # viewer = tree.nodes.new(type='CompositorNodeViewer')
        # viewer.use_alpha = False
        # links.new(invert.outputs['Color'], viewer.inputs['Image'])

        depth_saver = tree.nodes.new(type='CompositorNodeOutputFile')
        depth_saver.base_path = img_path
        depth_saver.file_slots[0].path = '{}_{}_'.format(index, depth_name)
        links.new(invert.outputs['Color'], depth_saver.inputs['Image'])

    image_saver = tree.nodes.new(type='CompositorNodeOutputFile')
    image_saver.base_path = img_path
    image_saver.file_slots[0].path = '{}_{}_'.format(index, img_name)
    links.new(rl.outputs['Image'], image_saver.inputs['Image'])

    bpy.ops.render.render(write_still=True)


def scale_object(obj_name, vals=(1,1,1)):
    x=vals[0]; y=vals[1]; z=vals[2]
    bpy.ops.object[obj_name].scale = (x, y, z)


def move_obj_to_location(obj_name, vals=(1,1,1)):
    x=vals[0]; y=vals[1]; z=vals[2]
    bpy.ops.object[obj_name].location = (x, y, z)


def origin_to_lowest_point(obj):
    deselected_all()
    obj.select = True

    mw = obj.matrix_world      # Active object's world matrix
    glob_vertex_coordinates = [ mw * v.co for v in obj.data.vertices ] # Global coordinates of vertices

    # Find the lowest Z value amongst the object's vertex

    minZ = min([co.z for co in glob_vertex_coordinates])

    for v in obj.data.vertices:

        if (mw * v.co).z == minZ:
            bpy.context.scene.cursor_location = mw * v.co
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    deselected_all()


def switch_origin(obj_name, max_point=True, coords=None):

    deselected_all()
    obj = bpy.data.objects[obj_name]
    obj.select = True

    mw = obj.matrix_world      # Active object's world matrix
    glob_vertex_coordinates = [ mw * v.co for v in obj.data.vertices ] # Global coordinates of vertices

    # Find the lowest Z value amongst the object's vertex

    if max_point:
        Z = max([co.z for co in glob_vertex_coordinates])
    else:
        Z = min([co.z for co in glob_vertex_coordinates])

    for v in obj.data.vertices:
        if (mw * v.co).z == Z:

            if coords is None:
                bpy.context.scene.cursor_location = mw * v.co
            else:

                bpy.context.scene.cursor_location = (coords[0], coords[1], (mw * v.co).z)

            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    deselected_all()


def set_parent(parent, child):

    deselected_all()

    parent.select = True
    child.select = True     #select the object for the 'parenting'

    bpy.context.scene.objects.active = parent    #the active object will be the parent of all selected object

    bpy.ops.object.parent_set()

    deselected_all()


def highest_edge(obj):

    max_idx = np.argmax([v.co.z for v in obj.data.vertices])
    obj.data.vertices[max_idx].select = True

    edges_with_max_vertex = []
    for edge in obj.data.edges:
        if edge.vertices[0] == max_idx or edge.vertices[1] == max_idx:
            edges_with_max_vertex.append(edge)

    edge_angles = []
    for edge  in edges_with_max_vertex:
        a_v = obj.data.vertices[edge.vertices[0]]
        b_v = obj.data.vertices[edge.vertices[1]]

        a_v = np.array([a_v.co.x, a_v.co.y])
        b_v = np.array([b_v.co.x, b_v.co.y])

        norm_a = np.linalg.norm(a_v)
        norm_b = np.linalg.norm(b_v)
        ab = a_v @ b_v
        angle = np.cos(ab / (norm_a * norm_b))

        edge_angles.append(angle)

    edge_idx = np.argmax(edge_angles)

    return edges_with_max_vertex[edge_idx].index


def select_edge_loop(edge):

    for loop in edge.link_loops:
       if len(loop.vert.link_edges) == 4:
            edge.select = True

    while len(loop.vert.link_edges) == 4:

        loop = loop.link_loop_prev.link_loop_radial_prev.link_loop_prev
        edge_next = loop.edge

        if edge_next.select:
            break;
        else:
            edge_next.select = True


def activate_object(obj):
    obj.select = True
    bpy.context.scene.objects.active = obj


def split_object(obj, splitted_name, choose_edge=highest_edge):

    activate_object(obj)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    edge_id = choose_edge(obj)

    bm = bmesh.new()   # create an empty BMesh
    bm.from_mesh(obj.data)   # fill it in from a Mesh

    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

    select_edge_loop(bm.edges[edge_id])

    bm.to_mesh(obj.data)
    bm.free()

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.loop_to_region()
    bpy.ops.mesh.separate(type='SELECTED')

    bpy.ops.object.editmode_toggle()
    inner = bpy.context.selected_objects[0]
    inner.name = splitted_name

    bpy.ops.object.select_all(action='DESELECT')


def separate_obj_material_ids(obj, splitted_name, material_id):

    split_object(obj, splitted_name)
    inner = bpy.data.objects[splitted_name]
    inner.pass_index = material_id
    set_parent(obj, inner)



CUP_Y_LIM = (-3.8, 3.8)
CUP_X_LIM = (-1.5, 1.5)
LAMP_Y_LIM = [-10, 10]
LAMP_X_LIM = [-10, 10]
LAMP_Z_LIM = [3, 10]
NUM_LIGHTS = 10


def random_cup_position():

    x = random.uniform(CUP_X_LIM[0], CUP_X_LIM[1])
    y = random.uniform(CUP_Y_LIM[0], CUP_Y_LIM[1])

    return (x, y)


def random_lamp_position():

    x = random.uniform(LAMP_X_LIM[0], LAMP_X_LIM[1])
    y = random.uniform(LAMP_Y_LIM[0], LAMP_Y_LIM[1])
    z = random.uniform(LAMP_Z_LIM[0], LAMP_Z_LIM[1])

    return (x, y, z)


def initialize_lamp(name):

    bpy.ops.object.lamp_add(location=random_lamp_position())
    lamp = bpy.context.object
    lamp.name = name

    desk = bpy.data.objects['desk']
    set_parent(desk, lamp)

    return lamp


def initialize_material_ids():

    for obj in bpy.data.objects:

        if obj.name == 'cup':
            pass_index = 1

            # separate inside of a cup from  the outer part
            separate_obj_material_ids(obj, 'cup_inner', 2)
        else:
            pass_index = 0

        obj.pass_index = pass_index


def switch_to_labels():

    affordance_mat = bpy.data.materials.get('labels')

    for obj in bpy.data.objects:

        if hasattr(obj.data, 'materials'):
            obj.data.materials[0] = affordance_mat


def reset_camera_position():

    camera = bpy.data.objects['Camera']
    camera.rotation_euler = mathutils.Vector([60, 0, 90]) * 2 * pi / 360
    # camera.location = (8, 0, 6)


def import_and_set_on_table(path, name):

    obj = import_object(path, name)
    switch_origin(name, max_point=False)
    obj.scale = (0.15, 0.15, 0.15)
    desk = bpy.data.objects['desk']
    obj.location = (0, 0, desk.location[2])
    set_parent(desk, obj)

    return obj



bpy.ops.object.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode="OBJECT")

switch_origin('desk', coords=(0, 0))

reset_camera_position()

lamps = []
cups = []

cups.append(import_and_set_on_table(cup_path, 'cup'))

random_textures = intialize_textures(['cup', 'desk', 'wall', 'floor', 'leg'])
initialize_material_ids()

for i in range(2):

    # Random cup position
    x, y = random_cup_position()
    cups[0].location = (x, y, cups[0].location[2])

    # Remove lamps
    for l in lamps:
        remove_object(l)

    # Generate new lamps and their positions
    lamps = []
    for j in range(random.randint(1, NUM_LIGHTS)):
        lamps.append(initialize_lamp('lamp_{}'.format(j)))

    switch_to_random_textures(random_textures)
    render_save(img_path, i, depth=True, img_name='random')
    switch_to_labels()
    #render_save(img_path, i, depth=False, img_name='affordance')
