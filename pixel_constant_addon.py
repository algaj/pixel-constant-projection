import math 
import bpy
from bpy.types import Panel
from bpy.types import Operator
from bpy.props import IntProperty


bl_info = {
    "name": "Pixel Constant Projection",
    "author": "Aleš Gajdacz",
    "version": "1.0.0",
    "location": "3D Viewport -> right toolbar -> Pixel Constant Projection",
    "blender": (3, 2, 1),
    "description": "Fit camera view to selected object.",
    "category": "3D View",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/algaj/PixelConstantAddon",
    "tracker_url": "https://github.com/algaj/PixelConstantAddon/issues",
}

# camera - active camera
# pixels - pixels per meter in the horizontal direction
# angle - camera angle (0 deg - facing down, 90 deg - facing forward)
# min_x, max_x... - bounds of the active object
def update_active_camera(camera, pixels, angle, min_x, max_x, min_y, max_y, min_z, max_z):
    x_center = (min_x + max_x) / 2.0
    y_center = (min_y + max_y) / 2.0
    z_center = (min_z + max_z) / 2.0

    distance_from_center = 15.0

    z_offset = math.cos(math.radians(angle)) * distance_from_center
    y_offset = math.sin(math.radians(angle)) * distance_from_center

    camera.location = (x_center, y_center - y_offset, z_center + z_offset)
    camera.rotation_euler = (math.radians(angle), 0.0, 0.0)


    horizontal_size = max_x - min_x
    vertical_size = max_z - min_z
    depth_size = max_y - min_y

    # Access the render settings of the current scene
    render_settings = bpy.context.scene.render

    # Set the desired resolution
    render_settings.resolution_x = int(pixels * horizontal_size)
    render_settings.resolution_y = int(pixels * (depth_size * math.cos(math.radians(angle)) + vertical_size * math.sin(math.radians(angle))))


    camera.data.type = 'ORTHO'
    if render_settings.resolution_y < render_settings.resolution_x:
        camera.data.ortho_scale = horizontal_size
    else:
        camera.data.ortho_scale = depth_size * math.cos(math.radians(angle)) + vertical_size * math.sin(math.radians(angle))
    pass

class TLA_OT_operator(Operator):
    """ tooltip goes here """
    bl_idname = "demo.operator"
    bl_label = "I'm a Skeleton Operator"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):

        # Get the active object
        active_object = bpy.context.active_object

        if active_object and active_object.type == 'MESH':
            # Get the mesh data
            mesh = active_object.data

            # Get the object's world matrix
            matrix = active_object.matrix_world

            # Get the object's vertices
            vertices = [matrix @ v.co for v in mesh.vertices]

            # Calculate the bounding box coordinates
            min_x = min(vertices, key=lambda v: v.x).x
            max_x = max(vertices, key=lambda v: v.x).x
            min_y = min(vertices, key=lambda v: v.y).y
            max_y = max(vertices, key=lambda v: v.y).y
            min_z = min(vertices, key=lambda v: v.z).z
            max_z = max(vertices, key=lambda v: v.z).z

        else:
            self.report({'ERROR'}, "No active object, ignoring request.")
            return {'FINISHED'}
        
        # Get the active camera
        active_camera = bpy.context.scene.camera
        if active_camera:
            update_active_camera(active_camera, context.scene.pixels_per_horizontal_meter, context.scene.camera_angle, min_x, max_x, min_y, max_y, min_z, max_z)
        else:
            self.report({'ERROR'}, "No active camera, ignoring request.")
            return {'FINISHED'}

        return {'FINISHED'}


class TLA_PT_sidebar(Panel):
    """Display test button"""
    bl_label = "Prerender Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Prerender Tools"

    def draw(self, context):
        col = self.layout.column(align=True)
        prop = col.operator(TLA_OT_operator.bl_idname, text="Update Camera")
        col.prop(context.scene, "pixels_per_horizontal_meter")
        col.prop(context.scene, "camera_angle")

def update_property(self, context):
    self.execute(context)
 
classes = [
    TLA_OT_operator,
    TLA_PT_sidebar,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    bpy.types.Scene.pixels_per_horizontal_meter = bpy.props.IntProperty(
        name='Pixels per Horizontal Meter',
        default=0
    )

    bpy.types.Scene.camera_angle = bpy.props.FloatProperty(
        name='Camera Angle',
        default=0.0
    )


def unregister():
    del bpy.types.Scene.pixels_per_horizontal_meter
    del bpy.types.Scene.camera_angle
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == '__main__':
    register()