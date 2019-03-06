import bpy

class Renderer(object):

    def __init__(self, random_texture_path, depth_path, affordance_path, cup_names, cup_insides, texture_randomizer,
                 include_depth=True, depth_name='depth', img_name='image', affordance_name='affordance'):

        self.affordance_path = affordance_path
        self.depth_path = depth_path
        self.random_texture_path = random_texture_path

        self.affordance_index = 0
        self.random_texture_index = 0

        self.depth_name = depth_name
        self.img_name = img_name
        self.affordance_name = affordance_name

        self.texture_randomizer = texture_randomizer
        self.cup_names = cup_names
        self.inside_names = cup_insides
        self.initialize_material_ids()

        self.affordance_material = False
        self.include_depth = include_depth

    def render_save(self):

        if self.affordance_material:
            img_path = self.affordance_path
            self.affordance_index += 1
            index = self.affordance_index
            img_name = self.affordance_name
        else:
            img_path = self.random_texture_path
            self.random_texture_index += 1
            index = self.random_texture_index
            img_name = self.img_name

        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links

        for n in tree.nodes:
            tree.nodes.remove(n)

        rl = tree.nodes.new(type="CompositorNodeRLayers")

        if not self.affordance_material and self.include_depth:

            mapValue = tree.nodes.new(type='CompositorNodeMapValue')
            mapValue.use_max = True; mapValue.use_min = True;
            mapValue.min = [0.]; mapValue.max = [255.]; mapValue.size = [0.05];

            links.new(rl.outputs['Depth'], mapValue.inputs['Value'])

            invert = tree.nodes.new(type='CompositorNodeInvert')
            links.new(mapValue.outputs['Value'], invert.inputs['Color'])

            depth_saver = tree.nodes.new(type='CompositorNodeOutputFile')
            depth_saver.base_path = self.depth_path
            depth_saver.file_slots[0].path = '{}_{}_'.format(index, self.depth_name)
            links.new(invert.outputs['Color'], depth_saver.inputs['Image'])

        image_saver = tree.nodes.new(type='CompositorNodeOutputFile')
        image_saver.base_path = img_path
        image_saver.file_slots[0].path = '{}_{}_'.format(index, img_name)
        links.new(rl.outputs['Image'], image_saver.inputs['Image'])

        bpy.ops.render.render(write_still=True)

    def initialize_material_ids(self):

        for obj in list(bpy.data.objects):

            if obj.name in self.cup_names:
                pass_index = 1
            elif obj.name in self.inside_names:
                pass_index = 2
            else:
                pass_index = 0

            obj.pass_index = pass_index

    def switch_to_labels(self):

        self.initialize_material_ids()

        self.affordance_material = True
        bpy.data.scenes['Scene'].render.use_antialiasing = False

        affordance_mat = bpy.data.materials.get('labels')

        for obj in bpy.data.objects:

            if hasattr(obj.data, 'materials'):

                if len(obj.data.materials) == 0:
                    obj.data.materials.append(affordance_mat)
                else:
                    obj.data.materials[0] = affordance_mat

    def switch_to_random_textures(self):

        self.affordance_material = False
        bpy.data.scenes['Scene'].render.use_antialiasing = True
        self.texture_randomizer.switch_and_randomize()
