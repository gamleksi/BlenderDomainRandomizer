import bpy
import random

MATERIAL = bpy.data.materials['random']
MATERIAL_NODE = bpy.data.materials['random_material']

TEXTURE_COLOR = bpy.data.textures['random_texture']
TEXTURE_DISPLACE = bpy.data.textures['random_displace']

SCALE = 5


def find_nodes(nodes, name):
    result = []
    for node in nodes:
        if name in node.name:
            result.append(node)
    return result


def find_objects(name):
    objs = []
    for obj in bpy.data.objects:
       if name in obj.name:
            objs.append(obj)
    return objs #[bpy.data.objects[name]]


class TextureRandomizer(object):
    def __init__(self, obj_name, displace=False):
        self.obj_name = obj_name
        self.displace = displace
        self.initialize_material()
        self.initialize_obj()
        self.random_all()

    def initialize_material(self):

        self.material = bpy.data.materials.new('{}_random'.format(self.obj_name))

        self.texture = TEXTURE_COLOR.copy()
        self.texture.name = '{}_texture'.format(self.obj_name)
        self.texture_node = self.texture.node_tree.nodes

        self.material.texture_slots.add()
        self.material.texture_slots[0].texture = self.texture
        self.material.texture_slots[0].texture_coords = 'ORCO'
        self.material.use_textures[0] = True

        if self.displace:

            self.displace_texture = TEXTURE_DISPLACE.copy()
            self.displace_node = self.displace_texture.node_tree.nodes
            self.material.texture_slots.add()
            self.material.texture_slots[1].texture = self.displace_texture
            self.material.texture_slots[1].texture_coords = 'ORCO'
            self.material.texture_slots[1].use_map_color_diffuse = False
            self.material.texture_slots[1].use_map_displacement = True
            self.material.use_textures[1] = True


    def initialize_obj(self):
        objects = find_objects(self.obj_name)

        for obj in objects:
            if obj.data.materials is None:
                obj.data.materials[0] = self.material
            else:
                obj.active_material = self.material


    def random_mix_factor(self, node):

        mix_nodes = find_nodes(node, 'Mix')
        for mix in mix_nodes:
            mix.inputs[0].default_value = random.random()

    def random_checker_color(self):

        color_nodes = find_nodes(self.texture_node, 'ColorRamp')
        for node in color_nodes:
            node.inputs[0].default_value = random.random()

    def random_checker_size(self, node):
        checker_nodes = find_nodes(node, 'Checker')
        for node in checker_nodes:
            node.inputs[2].default_value = random.random()

    def random_noise(self, node):
        nodes = find_nodes(node, 'Noise')
        for node in nodes:
            node.inputs[2].default_value = random.random()
            node.inputs[3].default_value = random.random()

    def random_scale(self, node):
        nodes = find_nodes(node, 'Scale')
        for node in nodes:
            node.inputs[1].default_value = (random.random() * SCALE, random.random() * SCALE, random.random() * SCALE)

    def random_rotate(self, node):
        nodes = find_nodes(node, 'Rotate')
        for node in nodes:
            node.inputs[1].default_value = random.random() # turns
            node.inputs[2].default_value = (random.random(), random.random(), random.random()) # x, y, z

    def random_translate(self, node):
        nodes = find_nodes(node, 'Translate')
        for node in nodes:

            node.inputs[1].default_value = (random.random() * SCALE, random.random() * SCALE, random.random() * SCALE) # turns

    def random_material_properties(self):
        self.material.emit = random.random()
        self.material.translucency = random.random()
        self.material.diffuse_intensity = random.random()

    def random_displace(self):
        self.material.texture_slots[1].displacement_factor = random.random() - 0.5


    def random_all(self):

        nodes = [self.texture_node]

        if self.displace:
            nodes.append(self.displace_node)
            self.random_displace()

        self.random_checker_color()
        self.random_material_properties()
        for node in nodes:

            self.random_checker_size(node)
            self.random_mix_factor(node)
            self.random_noise(node)
            self.random_rotate(node)
            self.random_scale(node)
            self.random_translate(node)


def intialize_textures(obj_names):

    textures = []

    for name in obj_names:

        displace = False
        if 'wall' in name:
            displace = True

        textures.append(TextureRandomizer(name, displace=displace))

    return textures


def switch_to_random_textures(textures):

    for texture in textures:
        texture.initialize_obj()
        texture.random_all()

    bpy.data.scenes['Scene'].render.use_antialiasing = True


if __name__ == "__main__":
    intialize_textures(['desk', 'wall1', 'wall2', 'wall3', 'leg1', 'leg2', 'leg3', 'leg4', 'floor'])

