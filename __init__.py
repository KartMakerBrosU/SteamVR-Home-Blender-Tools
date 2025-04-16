import math
import winreg

svr_modspath = ""

## Basic Classes
class Vector:
    def __init__(self,x:float,y:float,z:float):
        self.x = x
        self.y = y
        self.z = z
class Influence:
    def __init__(self, name:str,location:Vector,rotation:Vector,weight:float,root:bool):
        self.m_influenceName = name
        self.locationX = round(-location.y * 3.28084 * 12,6)
        self.locationY = round(location.x * 3.28084 * 12,6)
        self.locationZ = round(location.z * 3.28084 * 12,6)
        self.rotationX = round(math.degrees(rotation.x),6)
        self.rotationY = round(math.degrees(rotation.y),6)
        self.rotationZ = round(math.degrees(rotation.z),6)
        self.weight = 1.0
        self.root = root
    def returnLocation(self):
        return f"[ {self.locationX},{self.locationY},{self.locationZ} ]"
    def returnRotation(self):
        return f"[ {self.rotationX},{self.rotationY},{self.rotationZ} ]"
class Attatchment:
    def __init__(self, name: str,influence):
        self.m_name = name
        self.influences = influence


def getMods() -> str:
    """Gets a list of SteamVR Home mods."""
    mod_names = []
    global svr_modspath
    ## Get location of steam downloads
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,"SOFTWARE\WOW6432Node\Valve\Steam")
    value,_ = winreg.QueryValueEx(key,"InstallPath")
    winreg.CloseKey(key)
    library = open(value + "\steamapps\libraryfolders.vdf")

    ## Clean up values
    for str in library.readlines():
        if '"path"' in str:
            str = str.replace('"path"',"")
            ##literal \\ is \ when displayed. and \\\\ is \\ when displayed.
            str = str.strip().replace("\\\\","\\").replace('"','')
            
            svr_path = os.path.join(str,"steamapps","common","SteamVR","tools","steamvr_environments","content","steamtours_addons")
            if os.path.exists(svr_path):
                for f in os.scandir(svr_path):
                    if f.is_dir():
                        mod_names.append(f.name)
                svr_modspath = svr_path
    options = []

    ##Add modnames to options then return.
    for i in range(len(mod_names)):
        options.append((f"{mod_names[i]}", f"{mod_names[i]}",f"AddonNo{i}"))
    return options

preview_collections = {}
IMAGE_ENUM = []

def get_image_enum_items(self,context):
    """Returns image enum"""
    return IMAGE_ENUM

## -------------------------------------------------------
## Blender Addon General Info
## -------------------------------------------------------
bl_info = {
    "name": "SteamVR Blender Tools",
    "description": "Tools for SteamVR Workshop Development..",
    "author": "KartMakerBrosU",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "3D View > Tools",
    "warning":"", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "SVR"
}

import bpy
import os
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       )
from bpy_extras.io_utils import ExportHelper,ImportHelper
from bpy.props import StringProperty,BoolProperty,CollectionProperty

import bpy.utils.previews as bpy_previews

if bpy.app.version < (4, 0, 0):
    raise Exception("This add-on is incompatible with Blender versions older than 4.0.0")

# ------------------------------------------------------------------------
#    Additional Functions
# ------------------------------------------------------------------------

def writeAttatchments(selected:bool,file_path:str):
    """Gets the empties from scene and exports their locations and rotations to .attatch file."""
    print("Writing Attatchment file...")
    obj = []
    f = open(file_path, 'w', encoding='utf-8')

    ## Add empy names to array (selected as context)
    if(selected):
        for object in bpy.context.selected_objects:
            if(object.type == 'EMPTY'):
                obj.append(object)
    else:
        for object in bpy.data.objects:
            if(object.type == 'EMPTY'):
                obj.append(object)

    influ = []
    for empty in obj:
        position = Vector(empty.location.x, empty.location.y,empty.location.z)
        rotation = Vector(empty.rotation_euler.x,empty.rotation_euler.y,empty.rotation_euler.z)
        influ.append(Influence(empty.name_full,position,rotation,1.0,True))
    
    attch = Attatchment("",influ)
    
    ##Write attatchment file.
    f.write("<!-- kv3 encoding:text:version{e21c7f3c-8a33-41c5-9977-a76d3a32aa0d} format:generic:version{7412167c-06e9-4698-aff2-e63eb59037e7} -->\n")
    f.write("{\n")
    tabs = "    "
    i = 1
    f.write(tabs + "m_name = \"\"\n")
    f.write(tabs + "m_attachments = \n")
    f.write((tabs*i) + "[\n")
    i+=1
    for inf in attch.influences:
        f.write((tabs*i) + "{\n")
        i+=1
        f.write((tabs*i) + "m_name = \""+ inf.m_influenceName + "\"\n")
        f.write((tabs*i) + "m_influences = \n")
        f.write((tabs*i) + "[\n")
        i+=1
        f.write((tabs*i) + "{\n")
        i+=1
        f.write((tabs*i) + "m_influenceName = \"root\"" + "\n")
        f.write((tabs*i) + "m_vTranslationOffset = " + inf.returnLocation() + "\n")
        f.write((tabs*i) + "m_vRotationOffset = " + inf.returnRotation() + "\n")
        f.write((tabs*i) + "m_flWeight = " + str(inf.weight) + "\n")
        f.write((tabs*i) + "m_bRoot = true\n")
        i-=1
        f.write((tabs*i) + "},\n")
        i-=1
        f.write((tabs*i) + "]\n")
        i-=1
        f.write((tabs*i) + "},\n")
    i-=1
    f.write((tabs*i) + "]\n")
    f.write("}\n")
    f.close()

def findDictItem(listDict:list[dict], name):
    for item in listDict:
        if item["file"] == name:
            return item
    return dict(file = "nofile.png", displayname = "No Binding Found")

def load_previews(directory):
    """Loads the dropdown previews from the given directory."""
    pcoll = preview_collections.get("hammer")

    #If there are any previews currently in the variable,delete them.
    if(pcoll):
        bpy_previews.remove(pcoll)

    pcoll = bpy_previews.new()
    preview_collections["hammer"] = pcoll

    IMAGE_ENUM.clear()

    valid_exts = {'.png'}

    bindingfile = open(os.path.join(directory,"bindings.txt"),"r")
    lines = bindingfile.readlines()
    filedict = []
    for line in lines:
        names = line.split(";")
        linedict = dict(file =  names[0], displayname = names[1].strip())
        filedict.append(linedict)

    for idx,file in enumerate(os.listdir(directory)):
        if not file.lower().endswith(tuple(valid_exts)):
            continue

        filepath = os.path.join(directory,file)
        thumb = pcoll.load(file,filepath,'IMAGE')

        ##TODO: Replace the file.replace with the referenced name in the txt
        IMAGE_ENUM.append((file,findDictItem(filedict, file.replace(".png",""))["displayname"],"",thumb.icon_id,idx))

def unload_previews(directory):
    """Unloads the dropdown previews."""
    for pcoll in preview_collections.values():
        bpy_previews.remove(pcoll)
    preview_collections.clear()

def update_materials(tex_name):
    print(f"Material updated to: {tex_name}")


# ------------------------------------------------------------------
#    Operator Scripts
# ------------------------------------------------------------------------


class svr_exportAttatchments(Operator,ExportHelper):
    """Exports Empties as an Attatchment File"""
    bl_idname = "svr.exportatt"
    bl_label = "Export Attatchments"

    filename_ext = ".attach"

    filter_glob: StringProperty(
        default="*.attach",
        options={'HIDDEN'},
        maxlen=1024,  # Max internal buffer length, longer would be clamped.
    ) # type: ignore

    selected_only: BoolProperty(
        name="Selected Only",
        description="Export only the selected empties.",
        default=False,
    ) # type: ignore

    def execute(self, context):
        writeAttatchments(self.selected_only,self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        ##Set the default direcory
        self.filepath = os.path.join(svr_modspath + "\\",context.scene.svr_modname.preset_enum,"models","general")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

##NOTE: Will only show when material has FBX_vmatPath property.
class svr_openVMAT(Operator,ImportHelper):
    """Opens a directory to select VMAT Files"""
    bl_idname = "svr.openvmat"
    bl_label = "Select VMAT"
    
    filename_ext = ".vmat"

    filter_glob: StringProperty(
        default="*.vmat",
        options={'HIDDEN'},
        maxlen=1024,  # Max internal buffer length, longer would be clamped.
    ) # type: ignore
    
    #add VMAT path relative to mod directory.
    def execute(self, context):
        global svr_modspath

        svr_modpath = os.path.join(svr_modspath + "\\",context.scene.svr_modname.preset_enum)
        filepath = str(self.filepath).replace(svr_modpath + "\\","")
        if ":" not in filepath:
            bpy.context.active_object.active_material["FBX_vmatPath"] = filepath

        return {'FINISHED'}
    
    ## Set the ImportHelper default open directory.
    def invoke(self, context, event):
        if(bpy.context.active_object.active_material):
            ##Set default directory.
            self.filepath = os.path.join(svr_modspath + "\\",context.scene.svr_modname.preset_enum,"materials","models")
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'ERROR'},"Empty material list.")
            return {'CANCELLED'}

class svd_addVMATPath(Operator):
    """Contains button to add VMAT path to material."""
    bl_idname = "svr.addvmat"
    bl_label = "Add VMAT Property"


    def execute(self,context):
        mat = bpy.context.active_object.active_material
        if(mat):
            mat["FBX_vmatPath"] = "materials/dev/reflectivity_50.vmat"
            bpy.context.scene.svr_devtex.dev_enum = "reflectivity_50.png"
            return {'FINISHED'}
        else:
            self.report({'ERROR'},"Empty material list.")
            return {'CANCELLED'}

class svr_selectMod(PropertyGroup):
    """Contains dropdown for svr mod selection"""
    bl_idname = "svr.selectmod"
    bl_label = "Select Mod"

    preset_enum : bpy.props.EnumProperty(
        items = getMods(),
        name = "",
        description="Select SteamVR Home Mod",

    ) # type: ignore

    def draw(self,context):
        layout = self.layout
        layout.prop(self,"preset_enum")

class svr_VMATDevTex(PropertyGroup):
    """Contains enum to select dev texture."""

    ## On New VMAT
    def dev_tex_changed(self,context):
        mat = bpy.context.active_object.active_material
        if mat and mat.get("FBX_vmatPath"):
            newname = str(self.dev_enum).removesuffix(".png")
            mat["FBX_vmatPath"] = f"materials/dev/{newname}.vmat"

    dev_enum: bpy.props.EnumProperty(
        name = "Dev Tex Picker",
        description="Select a Dev Texture",
        items = get_image_enum_items,
        update = dev_tex_changed,
    ) #type: ignore

# ------------------------------------------------------------------------
#    Panel Classes
# ------------------------------------------------------------------------

class SVR_PT_CustomPanel(Panel):
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "SVR"
    bl_context = "objectmode"

class SVR_PT_MainPanel(SVR_PT_CustomPanel):
    """SVR Workshop Tools main panel."""
    bl_label = "SteamVR Workshop Tools"
    bl_idname = "SVR_PT_mainPanel"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text = "Select Mod:")
        
        scene = context.scene
        svrwork = scene.svr_modname

        layout.prop(svrwork,"preset_enum")
        layout.operator("svr.exportatt",icon="EMPTY_ARROWS")

class SVR_PT_MatPanel(SVR_PT_CustomPanel):
    """SVR Material subpanel"""
    bl_label = "Material Tools"
    bl_idname = "SVR_PT_matPanel"
    bl_parent_id = "SVR_PT_mainPanel"

    def draw(self,context):
        layout = self.layout
        props = context.scene.svr_devtex
        sel_obj = bpy.context.selected_objects

        ## If the selectd object is a mesh.
        if sel_obj and sel_obj[0].type == 'MESH':
            mat = bpy.context.active_object.active_material
            ## If selected material has custom property, show dev tex menu.
            if mat and mat.get("FBX_vmatPath"):
                layout.operator("svr.openvmat",icon='MATERIAL')
                layout.label(text="Dev Texture:")
                layout.prop(props,"dev_enum",text="")
            ## else, show add vmat button.
            else:
                layout.operator("svr.addvmat",icon = "PROPERTIES")
        ## If not, tell user. 
        else:
            layout.label(text="Select an Object")
               

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------
##Classes to be registered
classes = (
    svr_selectMod,
    SVR_PT_MainPanel,
    SVR_PT_MatPanel,
    svr_exportAttatchments,
    svr_openVMAT,
    svd_addVMATPath,
    svr_VMATDevTex,

)
def register():
    ##Load the dev texture previews.
    image_directory = os.path.join(os.path.dirname(__file__),"dev_tex")
    if os.path.exists(image_directory):
        load_previews(image_directory)

    ## Register the classes
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    ## Register the custom Properties
    bpy.types.Scene.svr_modname = bpy.props.PointerProperty(type=svr_selectMod)
    bpy.types.Scene.svr_devtex = bpy.props.PointerProperty(type=svr_VMATDevTex)

    

def unregister():
    ## Unload the dev texture previews.
    image_directory = os.path.join(os.path.dirname(__file__),"dev_tex")
    unload_previews(image_directory)

    ##Unregister the classes
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)

    ## Delete the custom porperties
    del bpy.types.Scene.svr_modname
    del bpy.types.Scene.svr_devtex


if __name__ == "__main__":
    register()



