# sanitation-suite
## Batch process a Folder OF VRMs, and add weights to unweighted objects to specific bones

-- batch all files in a folder and weight everything not named "BBody" to the head bone, with the exception of "Chain" and "Backpack" which get weighed to the SPine bone. This is for boomboxhead oncyber fix

This script is a Blender add-on that allows for batch processing of 3D files in the context of adding weights to a specific bone in an armature. The script allows the user to specify an input folder and an output folder, along with a chosen file format and export format.

The script iterates through each file in the input folder that matches the chosen file format, and loads the file into the scene based on the chosen file format. The script then adds an armature modifier to the object, if not already present, and assigns a new vertex group to the object, with a weight of 1.0, to the bone of interest. The script then exports the file in the chosen export format to the output folder, and deletes any temporary data from the scene.

The script requires the presence of a base mesh object called "BBody" that has an armature modifier. The script also looks for a bone called "Head_bind" in the armature to use as the bone of interest for weight assignment.

The script defines several functions and classes:

* execute_script(script_code): This function takes a string of Python code as input and executes it in a namespace with built-in functions. It is used to execute the user-defined script file in the add-on.

* BatchVRMProcessProperties: This is a class that defines the properties for the add-on. It defines three string properties (input_folder, output_folder, and script_file), and two enum properties (export_format and file_format) that allow the user to choose the export and file formats.

* BATCH_OT_execute_script: This is a Blender operator class that defines the "Execute Script" button in the add-on. When the button is clicked, this operator performs the batch processing of files.

* BATCH_PT_vrm_process_panel: This is a Blender panel class that defines the UI layout for the add-on. It allows the user to input the necessary properties and execute the script.

* register(): This function registers the classes with Blender's Python API.

* unregister(): This function unregisters the classes from Blender's Python API.

* The BATCH_OT_execute_script operator performs the following tasks when executed:

* It gets the necessary input parameters from the BatchVRMProcessProperties properties.

* It checks if the user-defined script file exists, and if not, it returns an error message and cancels the operator.

* It iterates through all files in the input folder that match the chosen file format, and loads the file into the scene based on the chosen file format.

* It finds the base mesh object called "BBody", and checks if it has an armature modifier. It also finds the bone of interest called "Head_bind" in the armature.

* It adds an armature modifier to the object, if not already present, and assigns a new vertex group to the object, with a weight of 1.0, to the bone of interest.

* It exports the file in the chosen export format to the output folder.

* It deletes any temporary data from the scene.

* It updates the progress bar to show the progress of the batch processing.

* When all files have been processed, it displays a message to the user that the batch processing has completed successfully.

## Usage

To use the add-on, the user can navigate to the "Tools" category in the 3D Viewport and access the "Batch Everything" panel.


```python
import bpy
import os

def execute_script(script_code):
    namespace = {"__builtins__": __builtins__}
    exec(script_code, namespace)

bl_info = {
    "name": "Batch Everything",
    "author": "OpenAI",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tools > Batch Everything",
    "description": "Batch process files with selected script",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}

class BatchVRMProcessProperties(bpy.types.PropertyGroup):
    input_folder: bpy.props.StringProperty(
        name="Input Folder",
        description="Path to the folder containing the files",
        default="",
        maxlen=1024,
        subtype='DIR_PATH',
    )
    
    output_folder: bpy.props.StringProperty(
        name="Output Folder",
        description="Path to the folder where the processed files will be saved",
        default="",
        maxlen=1024,
        subtype='DIR_PATH',
    )
    
    script_file: bpy.props.StringProperty(
        name="Script File",
        description="Path to the script file",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    export_format: bpy.props.EnumProperty(
        name="Export Format",
        description="Choose the export format",
        items=[
            ("VRM", "VRM", "Export as VRM format"),
            ("GLB", "GLB", "Export as GLB format"),
        ],
    )

    file_format: bpy.props.EnumProperty(
        name="File Format",
        description="Choose the file format",
        items=[
            ("OBJ", "OBJ", "Import as OBJ format"),
            ("VRM", "VRM", "Import as VRM format"),
            ("GLB", "GLB", "Import as GLB format"),
            ("FBX", "FBX", "Import as FBX format"),
        ],
    )

class BATCH_OT_execute_script(bpy.types.Operator):
    bl_idname = "object.batch_execute_script"
    bl_label = "Execute Script"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        input_folder = context.scene.batch_vrm_props.input_folder
        output_folder = context.scene.batch_vrm_props.output_folder
        script_file = context.scene.batch_vrm_props.script_file

        if not os.path.exists(script_file):
            self.report({'ERROR'}, "Script file does not exist")
            return {'CANCELLED'}

        with open(script_file) as f:
            script_code = f.read()

        total_files = sum([1 for file in os.listdir(input_folder) if file.endswith(('.obj', '.vrm', '.glb', '.fbx'))])
        bpy.context.window_manager.progress_begin(0, total_files)

        for index, file in enumerate(os.listdir(input_folder)):
            filepath = os.path.join(input_folder, file)

            # Load file into the scene based on the chosen format
            file_format = context.scene.batch_vrm_props.file_format
            if file_format == "OBJ" and file.endswith(".obj"):
                bpy.ops.import_scene.obj(filepath=filepath)
            elif file_format == "VRM" and file.endswith(".vrm"):
                bpy.ops.import_scene.vrm(filepath=filepath)
            elif file_format == "GLB" and file.endswith(".glb"):
                bpy.ops.import_scene.gltf(filepath=filepath)
            elif file_format == "FBX" and file.endswith(".fbx"):
                bpy.ops.import_scene.fbx(filepath=filepath)
            else:
                continue

            # Store the current selection state
            original_selection = []
            for obj in bpy.data.objects:
                original_selection.append(obj.select_get())

            # Store the current active object
            original_active = context.view_layer.objects.active

            # Set the context to a 3D Viewport
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = bpy.context.copy()
                    override['area'] = area
                    override['region'] = area.regions[-1]
                    bpy.ops.object.select_all(action='DESELECT')
                    break

            # Execute the script
            base_mesh_obj = bpy.data.objects.get("BBody")

            if not base_mesh_obj:
                self.report({'ERROR'}, "Base mesh object 'BBody' not found in the scene")
                return {'CANCELLED'}
            else:
                print("Base mesh object: ", base_mesh_obj.name)

            # Check if the base mesh object has an armature modifier
            armature_modifier = None
            for modifier in base_mesh_obj.modifiers:
                if modifier.type == 'ARMATURE':
                    armature_modifier = modifier
                    break

            if not armature_modifier:
                self.report({'ERROR'}, "Base mesh object must have an Armature modifier")
                return {'CANCELLED'}
            else:
                print("Armature modifier found on base mesh object: ", armature_modifier.name)

            # Get the armature object from the modifier
            armature_obj = armature_modifier.object

            if not armature_obj:
                self.report({'ERROR'}, "Armature object not found in the scene")
                return {'CANCELLED'}
            else:
                print("Armature object: ", armature_obj.name)

            # Make sure armature is selected
            bpy.ops.object.select_all(action='DESELECT')
            armature_obj.select_set(True)
            context.view_layer.objects.active = armature_obj

            # Set armature to Pose mode
            bpy.ops.object.mode_set(mode='POSE')

            # Find the head bone
            head_bone = None
            for bone in armature_obj.pose.bones:
                if bone.name == 'Head_bind':
                    head_bone = bone
                    break

            if not head_bone:
                self.report({'ERROR'}, "Head bone not found in armature")
                return {'CANCELLED'}
            else:
                print("Head bone: ", head_bone.name)

            # Iterate through all objects in the scene
            for obj in bpy.data.objects:
                # Check if the object is a mesh and not the base mesh object "BBody"
                if obj.type == 'MESH' and obj != base_mesh_obj:
                    # Add an armature modifier to the object, if not present
                    armature_modifier = None
                    for modifier in obj.modifiers:
                        if modifier.type == 'ARMATURE':
                            armature_modifier = modifier
                            break

                    if not armature_modifier:
                        armature_modifier = obj.modifiers.new('Armature', 'ARMATURE')

                    # Set the armature object in the object's modifier
                    armature_modifier.object = armature_obj

                    # Add a new vertex group to the object and assign it to the appropriate bone
                    if obj.name == 'Backpack':
                        bone_name = 'Spine2_bind'
                    elif obj.name == 'Chain':
                        bone_name = 'Spine2_bind'
                    else:
                        bone_name = head_bone.name
                        
                    vertex_group = obj.vertex_groups.new(name=bone_name)
                    vertices = [v.index for v in obj.data.vertices]
                    vertex_group.add(vertices, 1.0, 'REPLACE')  # 100% weight

            # Set armature back to Object mode
            bpy.ops.object.mode_set(mode='OBJECT')

            self.report({'INFO'}, "Weighted objects to head bone successfully")

            # Reset the context to the original context
            bpy.ops.object.select_all(action='DESELECT')
            for i, obj in enumerate(original_selection):
                if obj:
                    context.view_layer.objects.active = obj
                    obj.select_set(True)

            # Set the active object back to the original active object
            if original_active:
                context.view_layer.objects.active = original_active
            else:
                context.view_layer.objects.active = None

            # Export the file in the chosen format
            output_format = context.scene.batch_vrm_props.export_format
            output_file = os.path.splitext(file)[0] + '.' + output_format.lower()
            output_filepath = os.path.join(output_folder, output_file)
            if output_format == "VRM":
                bpy.ops.export_scene.vrm(filepath=output_filepath)
            elif output_format == "GLB":
                bpy.ops.export_scene.gltf(filepath=output_filepath)

            # Delete objects and related data from the scene
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=True)

            for block in bpy.data.meshes:
                if block.users == 0:
                    bpy.data.meshes.remove(block)

            for block in bpy.data.materials:
                if block.users == 0:
                    bpy.data.materials.remove(block)

            for block in bpy.data.textures:
                if block.users == 0:
                    bpy.data.textures.remove(block)

            for block in bpy.data.images:
                if block.users == 0:
                    bpy.data.images.remove(block)

            for block in bpy.data.armatures:
                if block.users == 0:
                    bpy.data.armatures.remove(block)

            bpy.context.window_manager.progress_update(index + 1)

        bpy.context.window_manager.progress_end()

        self.report({'INFO'}, "Batch processing completed")
        return {'FINISHED'}

class BATCH_PT_vrm_process_panel(bpy.types.Panel):
    bl_label = "Batch Everything"
    bl_idname = "BATCH_PT_vrm_process_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        batch_vrm_props = scene.batch_vrm_props

        layout.prop(batch_vrm_props, "input_folder")
        layout.prop(batch_vrm_props, "output_folder")
        layout.prop(batch_vrm_props, "script_file", text="Script")
        layout.operator("object.batch_execute_script")
        layout.prop(batch_vrm_props, "export_format", text="Export Format")
        layout.prop(batch_vrm_props, "file_format", text="File Format")

def register():
    bpy.utils.register_class(BatchVRMProcessProperties)
    bpy.utils.register_class(BATCH_OT_execute_script)
    bpy.utils.register_class(BATCH_PT_vrm_process_panel)
    bpy.types.Scene.batch_vrm_props = bpy.props.PointerProperty(type=BatchVRMProcessProperties)

def unregister():
    bpy.utils.unregister_class(BatchVRMProcessProperties)
    bpy.utils.unregister_class(BATCH_OT_execute_script)
    bpy.utils.unregister_class(BATCH_PT_vrm_process_panel)
    del bpy.types.Scene.batch_vrm_props

if __name__ == "__main__":
    register()


```
