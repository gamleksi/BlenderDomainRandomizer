import bpy
from mathutils import Vector
 
def get_BoundBox(object_name):
    """
    http://www.cbcity.de/simple-3d-collision-detection-with-python-scripting-in-blender
    """
    bpy.context.scene.update()
    ob = bpy.context.scene.objects[object_name]
    bbox_corners = [ob.matrix_world * Vector(corner) for corner in ob.bound_box]
 
    return bbox_corners
 

def check_collision(obj1, obj2):

    box1 = get_BoundBox(obj1.name)
    box2 = get_BoundBox(obj2.name)


    x_max = max([e[0] for e in box1])
    x_min = min([e[0] for e in box1])
    y_max = max([e[1] for e in box1])
    y_min = min([e[1] for e in box1])
    z_max = max([e[2] for e in box1])
    z_min = min([e[2] for e in box1])
    print('Box1 min %.2f, %.2f, %.2f' % (x_min, y_min, z_min))
    print('Box1 max %.2f, %.2f, %.2f' % (x_max, y_max, z_max))

    x_max2 = max([e[0] for e in box2])
    x_min2 = min([e[0] for e in box2])
    y_max2 = max([e[1] for e in box2])
    y_min2 = min([e[1] for e in box2])
    z_max2 = max([e[2] for e in box2])
    z_min2 = min([e[2] for e in box2])
    print('Box2 min %.2f, %.2f, %.2f' % (x_min2, y_min2, z_min2))
    print('Box2 max %.2f, %.2f, %.2f' % (x_max2, y_max2, z_max2))
     
     
    isColliding = ((x_max >= x_min2 and x_max <= x_max2) \
                    or (x_min <= x_max2 and x_min >= x_min2)) \
                    and ((y_max >= y_min2 and y_max <= y_max2) \
                    or (y_min <= y_max2 and y_min >= y_min2)) \
                    and ((z_max >= z_min2 and z_max <= z_max2) \
                    or (z_min <= z_max2 and z_min >= z_min2))
 
    if isColliding:
        print('Kollision!')
         
    return isColliding
