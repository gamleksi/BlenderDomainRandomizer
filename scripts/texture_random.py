import bpy
import random

MATERIAL = bpy.data.materials['random']
MATERIAL_NODE = bpy.data.materials['random_material']
TEXTURE = bpy.data.textures['random_texture']
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
    return objs


class TextureRandomizer(object):
    def __init__(self, obj_name):
        self.obj_name = obj_name
        self.initialize_material()
        self.initialize_obj()
        self.random_all()

    def initialize_material(self):

        self.material = MATERIAL.copy()
        self.material.name = 'material_node_{}'.format(self.obj_name)

        self.texture = TEXTURE.copy()
        self.texture.name = 'texture_{}'.format(self.obj_name)
        self.texture_node = self.texture.node_tree.nodes

        self.material_node = MATERIAL_NODE.copy()
        self.material_node.name = 'material_node_{}'.format(self.obj_name)

        self.material.node_tree.nodes['Texture'].texture = self.texture
        self.material.node_tree.nodes['Material'].material = self.material_node
        #self.material.active_node_material = self.material_node
        #self.material.active_texture = self.texture

    def initialize_obj(self):
        objects = find_objects(self.obj_name)

        for obj in objects:
            if obj.data.materials is None:
                obj.data.materials[0] = self.material
            else:
                obj.active_material = self.material


    def random_mix_factor(self):
        mix_nodes = find_nodes(self.texture_node, 'Mix')
        for mix in mix_nodes:
            mix.inputs[0].default_value = random.random()


    def random_checker_color(self):
        color_nodes = find_nodes(self.texture_node, 'ColorRamp')
        for node in color_nodes:
            node.inputs[0].default_value = random.random()


    def random_checker_size(self):
        checker_nodes = find_nodes(self.texture_node, 'Checker')
        for node in checker_nodes:
            node.inputs[2].default_value = random.random()


    def random_noise(self):
        nodes = find_nodes(self.texture_node, 'Noise')
        for node in nodes:
            node.inputs[2].default_value = random.random()
            node.inputs[3].default_value = random.random()

    def random_scale(self):
        nodes = find_nodes(self.texture_node, 'Scale')
        for node in nodes:
            node.inputs[1].default_value = (random.random() * SCALE, random.random() * SCALE, random.random() * SCALE)

    def random_rotate(self):
        nodes = find_nodes(self.texture_node, 'Rotate')
        for node in nodes:
            node.inputs[1].default_value = random.random() # turns
            node.inputs[2].default_value = (random.random(), random.random(), random.random()) # x, y, z


    def random_translate(self):
        nodes = find_nodes(self.texture_node, 'Translate')
        for node in nodes:
            node.inputs[1].default_value = (random.random() * SCALE, random.random() * SCALE, random.random() * SCALE) # turns

    def random_material_properties(self):
        self.material_node.emit = random.random()
        self.material_node.translucency = random.random()


    def random_all(self):

        self.random_checker_color()
        self.random_checker_size()
        self.random_mix_factor()
        self.random_noise()
        self.random_rotate()
        self.random_scale()
        self.random_translate()
        self.random_material_properties()


def intialize_textures(obj_names):

    textures = []

    for name in obj_names:
        textures.append(TextureRandomizer(name))

    return textures


def switch_to_random_textures(textures):

    for texture in textures:
        texture.initialize_obj()
        texture.random_all()


if __name__ == "__main__":
    intialize_textures(['desk', 'wall', 'leg', 'floor'])

