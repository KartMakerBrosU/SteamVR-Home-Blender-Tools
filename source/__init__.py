import bpy
import os
import bpy.utils.previews

## -------------------------------------------------------
## Blender Addon General Info
## -------------------------------------------------------
bl_info = {
    "name": "Image Dropdown Preivew",
    "description": "Image Dropdown Preview",
    "author": "KartMakerBrosU",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "3D View > Tools",
    "category": "UI"
}

preview_collections = {}
IMAGE_ENUM = []

def get_image_enum_items(self,context):
    return IMAGE_ENUM

def load_previews(directory):
    print("Previews Called")
    pcoll = preview_collections.get("hammer")

    #If there are any previews currently in the variable, delete them.
    if(pcoll):
        bpy.utils.previews.remove(pcoll)
    
    pcoll = bpy.utils.previews.new()
    preview_collections["hammer"]=pcoll

    IMAGE_ENUM.clear()

    valid_exts = {'.png','.jpg','.jpeg','.bmp'}
    for idx,file in enumerate(os.listdir(directory)):
        if not file.lower().endswith(tuple(valid_exts)):
            continue

        filepath = os.path.join(directory,file)
        thumb = pcoll.load(file,filepath,'IMAGE')


        ##Replace the file.replace with the referenced name in the txt
        IMAGE_ENUM.append((file,file.replace(".png",""),"",thumb.icon_id,idx))
        


class MyProperties(bpy.types.PropertyGroup):
    my_enum: bpy.props.EnumProperty(
        name="Image Picker",
        description="Select an image",
        items=get_image_enum_items
    ) # type: ignore
        
#Image Dropdown
class IMAGE_PT_DropdownPanel(bpy.types.Panel):
    bl_label = "Image Dropdown"
    bl_idname = "IMAGE_PT_dropdown"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ImageDropdown'

    def draw(self, context):
        layout = self.layout
        props = context.scene.my_props

        layout.prop(props, "my_enum", text="Choose Image")
    

def register():
    print("Previews Called")
    # Load previews from a folder
    directory = os.path.join(os.path.dirname(__file__), "thumbnails")
    if os.path.exists(directory):
        load_previews(directory)
    
    ##Register the classes
    from bpy.utils import register_class
    for cls in [MyProperties, IMAGE_PT_DropdownPanel]:
        register_class(cls)

    bpy.types.Scene.my_props = bpy.props.PointerProperty(type=MyProperties)


def unregister():
    from bpy.utils import unregister_class
    for cls in [MyProperties, IMAGE_PT_DropdownPanel]:
        unregister_class(cls)

    del bpy.types.Scene.my_props

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()