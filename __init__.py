import math
import winreg
import json


svr_modspath = ""
mod_names = []

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



def getMods() -> list[str]:
    """Gets a list of SteamVR Home mods."""
    global mod_names
    global svr_modspath
    ## Get location of steam downloads
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,"SOFTWARE\\WOW6432Node\\Valve\\Steam")
    value,_ = winreg.QueryValueEx(key,"InstallPath")
    winreg.CloseKey(key)
    library = open(value + "\\steamapps\\libraryfolders.vdf")

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

prev_name = ""

def get_image_enum_items(self,context):
    """Returns image enum"""
    return IMAGE_ENUM


## -------------------------------------------------------
## Blender Addon General Info
## -------------------------------------------------------
bl_info = {
    "name": "SteamVR Home Blender Tools",
    "description": "Tools for SteamVR Home Development..",
    "author": "KartMakerBrosU",
    "version": (1, 2, 0),
    "blender": (4, 2, 0),
    "location": "3D View > Tools",
    "warning":"", # used for warning icon and text in addons panel
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

class refPerson_3DCurRotation(bpy.types.AddonPreferences):
    bl_idname = __name__

    bool_Cur3DRotation: bpy.props.BoolProperty(
        name = "Refrence Chracter matches 3D Cursor Rotation",
        description="If on, the added refrence character would have the same rotation as the 3D cursor.",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'bool_Cur3DRotation', expand=True)
        



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

## Finds the dictionary file by name
def findDictItem(listDict:list[dict], name):
    for item in listDict:
        if item == name:
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
        thumb = pcoll.load(file,filepath,'IMAGE') ## Load the thumbnails.

        curritem = findDictItem(filedict, filedict[idx-1])
        ##TODO: Replace the file.replace with the referenced name in the txt
        IMAGE_ENUM.append((curritem['file'],curritem['displayname'],"",thumb.icon_id,idx))

def unload_previews(directory):
    """Unloads the dropdown previews."""
    for pcoll in preview_collections.values():
        bpy_previews.remove(pcoll)
    preview_collections.clear()

def scene_has_empty(context = bpy.context):
    return any(obj.type == 'EMPTY' for obj in context.scene.objects)

def get_saved_selectedMod() -> str:
    openPath = os.path.join(os.path.dirname(__file__), "settings.json")
    with open(openPath, mode = 'r', encoding="utf-8") as read_file:
        settings_data = json.load(read_file)
        return settings_data["selected_mod"]

def get_prefs(context):
    return context.preferences.addons[__name__].preferences

def refChar_draw(self,context):
    self.layout.operator(svr_addRef.bl_idname, icon="ARMATURE_DATA")


def onVMATChanged(self,context, newName:str) -> int:
    curr_mod = context.scene.svr_modname.preset_enum

    full_path = os.path.join(svr_modspath,curr_mod, newName)
    if os.path.exists(full_path):
        return True
    else:
        return False
    
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
        ##If there arent any empties. 
        if not scene_has_empty(context):
            self.report({'WARNING'}, "No empties in scene. Export cancelled.")
            return {'CANCELLED'}
        
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
    #After location is confirmed.
    def execute(self, context):
        global svr_modspath

        svr_modpath = os.path.join(svr_modspath + "\\",context.scene.svr_modname.preset_enum)
        
        ##At this point, filepath should JUST be the reltive path from the mod. If not, the full path is provided and thus contains "C:"
        filepath = str(self.filepath).replace(svr_modpath + "\\","")
        
        ##If the filepath is relative. 
        if ":" not in filepath:
            bpy.context.active_object.active_material["FBX_vmatPath"] = filepath
        else:
            self.report({'ERROR_INVALID_INPUT'},"Selected VMAT not from current mod.")

        return {'FINISHED'}
    
    ## Set the ImportHelper default open directory.
    ## Runs before the File Explorer is shown. 
    def invoke(self, context, event):
        if(bpy.context.active_object.active_material):
            ##Set default directory. ("models" adds the currently selected folder, so the "materials" folder is in view.)
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
            mat["FBX_vmatPath"] = "materials\\dev\\reflectivity_50.vmat"
            bpy.context.scene.svr_devtex.dev_enum = "materials\\dev\\reflectivity_50"
            return {'FINISHED'}
        else:
            self.report({'ERROR'},"Empty material list.")
            return {'CANCELLED'}

class svr_selectMod(PropertyGroup):
    """Contains dropdown for svr mod selection"""
    bl_idname = "svr.selectmod"
    bl_label = "Select Mod"

    def mod_select_changed(self,context):
        savepath = os.path.join(os.path.dirname(__file__), "settings.json")
        with open(savepath, 'w') as f:
            json.dump({"selected_mod":self.preset_enum}, f)

    preset_enum : bpy.props.EnumProperty(
        items = getMods(),
        name = "",
        description="Select SteamVR Home Mod",
        update=mod_select_changed,
        default=get_saved_selectedMod(),

    ) # type: ignore

    def draw(self,context):
        layout = self.layout
        layout.prop(self,"preset_enum")


class svr_VMATDevTex(PropertyGroup):
    """Contains enum to select dev texture."""

    dev_enum: bpy.props.EnumProperty(
        name = "Dev Tex Picker",
        description="Select a Dev Texture",
        items = get_image_enum_items,
    ) #type: ignore

class svr_addRef(Operator):
    """Adds a 6ft reference person in the scene."""
    bl_idname = "svr.addref"
    bl_label = "Add Reference Character"

    def execute(self, context):
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        obj_path = os.path.join(addon_dir, "models", "ue4_mannequin.obj")
        bpy.ops.wm.obj_import(filepath=obj_path)
        obj = context.active_object
        obj.location = context.scene.cursor.location

        prefs = get_prefs(context)
        if prefs.bool_Cur3DRotation:
            obj.rotation_euler = context.scene.cursor.rotation_euler.copy()
            obj.rotation_euler.x += math.radians(90)
        return {'FINISHED'}
    
class setDevMat(Operator):
    """Sets the current dev texture."""
    bl_idname = "svr.setdevmat"
    bl_label = "Set"

    def execute(self, context):
        newname = bpy.context.scene.svr_devtex.dev_enum
        mat = bpy.context.active_object.active_material
        if mat and mat.get("FBX_vmatPath"):
            mat["FBX_vmatPath"] = f"{newname}.vmat"
            for area in bpy.context.screen.areas:
                area.tag_redraw()
        return {'FINISHED'}

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

class SVR_PT_MatPanel(SVR_PT_CustomPanel):
    """SVR Material subpanel"""
    bl_label = "Material Tools"
    bl_idname = "SVR_PT_matPanel"
    bl_parent_id = "SVR_PT_mainPanel"

    def draw(self,context):
        global prev_name
        layout = self.layout
        props = context.scene.svr_devtex
        sel_obj = bpy.context.selected_objects

        ## If the selectd object is a mesh.
        if sel_obj and sel_obj[0].type == 'MESH':
            mat = bpy.context.active_object.active_material
            ## If selected material has custom property, show dev tex menu.
            if mat and mat.get("FBX_vmatPath"):
                layout.operator("svr.openvmat",icon='MATERIAL')

                dev_box = layout.box()
                dev_box.label(text="Dev Texture:")
                dev_row = dev_box.split(factor=0.8)
                dev_row.prop(props,"dev_enum",text="")
                dev_row.operator( setDevMat.bl_idname)

                vmatNames = mat.get("FBX_vmatPath").split("\\")
                vmatName = vmatNames[len(vmatNames)-1]

                if(prev_name != vmatName):
                    onVMATChanged(self,context,mat.get("FBX_vmatPath"))
                prev_name = vmatName
                layout.label(text=f"Current VMAT: {vmatName}")
            else:
                layout.operator("svr.addvmat",icon = "PROPERTIES")
        ## If not, tell user. 
        else:
            layout.label(text="Select an Object")
               
class SVR_PT_ModelPanel(SVR_PT_CustomPanel):
    """SVR Model SubPanel"""
    bl_label = "Model Tools"
    bl_idname = "SVR_PT_modelPanel"
    bl_parent_id = "SVR_PT_mainPanel"

    def draw(self,content):
        layout = self.layout

        layout.operator("svr.exportatt",icon="EMPTY_ARROWS")
        layout.operator("svr.addref", icon="ARMATURE_DATA")

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------
##Classes to be registered
classes = (
    svr_selectMod,
    SVR_PT_MainPanel,
    SVR_PT_MatPanel,
    SVR_PT_ModelPanel,
    svr_exportAttatchments,
    svr_openVMAT,
    svd_addVMATPath,
    svr_VMATDevTex,
    svr_addRef,
    refPerson_3DCurRotation,
    setDevMat,
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

    bpy.types.VIEW3D_MT_mesh_add.append(refChar_draw)

def unregister():
    ## Unload the dev texture previews.
    image_directory = os.path.join(os.path.dirname(__file__),"dev_tex")
    unload_previews(image_directory)

    ##Unregister the classes
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    ## Delete the custom porperties
    del bpy.types.Scene.svr_modname
    del bpy.types.Scene.svr_devtex

    bpy.types.VIEW3D_MT_mesh_add.remove(refChar_draw)

if __name__ == "__main__":
    register()



