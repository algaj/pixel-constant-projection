# Copyright (c) 2023 Aleš Gajdacz
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math
import bpy
from bpy.types import Panel, Operator


bl_info = {
    "name": "Pixel Constant Projection",
    "author": "Aleš Gajdacz",
    "version": (1, 0, 0),
    "blender": (3, 2, 1),
    "location": "3D Viewport -> Right Toolbar -> Pixel Constant Projection",
    "description": "Fit camera view to selected object.",
    "category": "3D View",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/algaj/PixelConstantAddon",
    "tracker_url": "https://github.com/algaj/PixelConstantAddon/issues",
}


def update_active_camera(camera, distance_from_center, pixels, angle, min_x, max_x, min_y, max_y, min_z, max_z):
    
    # Calculate center of the bounding box of the active object
    x_center = (min_x + max_x) / 2.0
    y_center = (min_y + max_y) / 2.0
    z_center = (min_z + max_z) / 2.0

    # Calculate how much to offset camera from the center of the active object
    z_offset = math.cos(math.radians(angle)) * distance_from_center
    y_offset = math.sin(math.radians(angle)) * distance_from_center

    camera.location = (x_center, y_center - y_offset, z_center + z_offset)
    camera.rotation_euler = (math.radians(angle), 0.0, 0.0)

    # Calculate render resolution and ortho size
    horizontal_size = max_x - min_x
    vertical_size = max_z - min_z
    depth_size = max_y - min_y

    render_settings = bpy.context.scene.render

    render_settings.resolution_x = int(pixels * horizontal_size)
    render_settings.resolution_y = int(
        pixels * (depth_size * math.cos(math.radians(angle)) + vertical_size * math.sin(math.radians(angle)))
    )

    camera.data.type = 'ORTHO'
    if render_settings.resolution_y < render_settings.resolution_x:
        camera.data.ortho_scale = horizontal_size
    else:
        camera.data.ortho_scale = depth_size * math.cos(math.radians(angle)) + vertical_size * math.sin(math.radians(angle))


class UpdateCameraOperator(Operator):
    """Update the camera view to fit the selected object. 
Disabled when:
    - there is no active object
    - thre is no camera in the scene"""

    bl_idname = "pixel_constant.update_camera"
    bl_label = "Update Camera"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.object is not None and context.object.type == 'MESH' and bpy.context.scene.camera is not None

    def execute(self, context):
        # Get the active object
        active_object = bpy.context.active_object
        mesh = active_object.data
        matrix = active_object.matrix_world
        vertices = [matrix @ v.co for v in mesh.vertices]

        min_x = min(vertices, key=lambda v: v.x).x
        max_x = max(vertices, key=lambda v: v.x).x
        min_y = min(vertices, key=lambda v: v.y).y
        max_y = max(vertices, key=lambda v: v.y).y
        min_z = min(vertices, key=lambda v: v.z).z
        max_z = max(vertices, key=lambda v: v.z).z

        # Get the active camera
        active_camera = bpy.context.scene.camera
        update_active_camera(
            active_camera,
            context.scene.camera_distance,
            context.scene.pixels_per_unit,
            context.scene.camera_angle,
            min_x,
            max_x,
            min_y,
            max_y,
            min_z,
            max_z
        )

        return {'FINISHED'}


class PixelConstantSidebar(Panel):
    """Pixel Constant Projection Addon"""
    bl_label = "Pixel Constant Projection"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Pixel Constant Projection"

    def draw(self, context):
        layout = self.layout
        layout.operator(UpdateCameraOperator.bl_idname)
        layout.prop(context.scene, "pixels_per_unit")
        layout.prop(context.scene, "camera_angle")
        layout.prop(context.scene, "camera_distance")


classes = [
    UpdateCameraOperator,
    PixelConstantSidebar,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.pixels_per_unit = bpy.props.IntProperty(
        name='Pixels Per Unit',
        default=100,
        min = 1
    )
    bpy.types.Scene.camera_angle = bpy.props.FloatProperty(
        name='Camera Angle',
        default=60.0,
        min=0.0,
        max=90.0
    )
    bpy.types.Scene.camera_distance = bpy.props.FloatProperty(
        name='Camera Distance',
        default=15.0,
        min=0.001
    )


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.pixels_per_unit
    del bpy.types.Scene.camera_angle
    del bpy.types.Scene.camera_distance


if __name__ == '__main__':
    register()