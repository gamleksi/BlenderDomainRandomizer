import csv
import os
import bpy

HEADERS = ['cup_location', 'cup_scale', 'lamp_locations', 'lamp_scales', 'desk_location',
                  'desk_scale', 'random_objs_ids', 'random_objs_locations', 'random_objs_scales', 'design_coefs',
                  'camera_location', 'camera_rotation']


class Logger(object):
    def __init__(self, table_randomizer, camera_randomizer, folder_path, cup_name, file_name='logger'):
        self.table_randomizer = table_randomizer
        self.camera_randomizer = camera_randomizer
        self.cup_name = cup_name
        self.file_path = os.path.join(folder_path, '{}.csv'.format(file_name))

    def obj_rotation(self, obj):
        return obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2]

    def obj_pos(self, obj):
        return obj.location[0], obj.location[1], obj.location[2]

    def obj_scale(self, obj):
        return obj.scale[0], obj.scale[1], obj.scale[2]

    def objects_location_and_scale(self, objects):
        locations = []
        scales = []
        for lamp in objects:
            locations.append(self.obj_pos(lamp))
            scales.append(self.obj_scale(lamp))

        return locations, scales

    def log(self):

        bpy.context.scene.update()

        cup_location = self.obj_pos(self.table_randomizer.cups[0])
        cup_scale = self.obj_scale(self.table_randomizer.cups[0])

        lamp_locations, lamp_scales = self.objects_location_and_scale(self.table_randomizer.lamps)

        desk_location = self.obj_pos(self.table_randomizer.desk)
        desk_scale = self.obj_scale(self.table_randomizer.desk)

        random_objects, random_objs_ids = self.table_randomizer.noise_randomizer.get_info()
        random_objs_locations, random_objs_scales = self.objects_location_and_scale(random_objects)

        design_coefs = self.table_randomizer.cup_randomizer

        camera_location = self.obj_pos(self.camera_randomizer.camera)
        camera_rotation = self.obj_rotation(self.camera_randomizer.camera)

        fields = [cup_location, cup_scale, lamp_locations, lamp_scales, desk_location,
                  desk_scale, random_objs_ids, random_objs_locations, random_objs_scales, design_coefs,
                  camera_location, camera_rotation]

        file_exists = os.path.isfile(self.file_path)

        with open(self.file_path, 'a') as f:
            writer = csv.DictWriter(f, delimiter=',', fieldnames=HEADERS)
            if not(file_exists):
                writer.writeheader()
            row = {}
            for i, name in enumerate(HEADERS):
                row[name] = fields[i]

            writer.writerow(row)
