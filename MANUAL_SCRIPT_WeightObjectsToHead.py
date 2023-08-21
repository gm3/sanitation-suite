bl_info = {
    "name": "Load, Merge Armatures, and Export VRM",
    "author": "OpenAI",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Object > Load, Merge Armatures, and Export VRM",
    "description": "Loads a VRM, merges all armatures, and exports it",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}

import bpy

class OBJECT_OT_load_merge_export_vrm(bpy.types.Operator):
    bl_idname = "object.load_merge_export_vrm"
    bl_label = "Load, Merge Armatures, and Export VRM"
    bl_options = {'REGISTER', 'UNDO'}

    input_path: bpy.props.StringProperty(name="Input Path", subtype='FILE_PATH')
    output_path: bpy.props.StringProperty(name="Output Path", subtype='FILE_PATH')

    def execute(self, context):
        try:
            # Print paths for debugging
            print("Input Path:", self.input_path)
            print("Output Path:", self.output_path)

            # Import VRM file
            bpy.ops.import_scene.vrm(filepath=self.input_path)

            # List to collect all armature objects
            armature_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']

            if len(armature_objects) > 1:
                # Set active object to first armature
                bpy.context.view_layer.objects.active = armature_objects[0]
                # Select all armature objects
                for armature in armature_objects:
                    armature.select_set(True)
                # Join them into one (active object should be an armature)
                bpy.ops.object.join()
                print("Armatures merged")
            else:
                print("Only one or no armature found. No merge needed.")

            # Export to VRM
            bpy.ops.export_scene.vrm(filepath=self.output_path)
            print("Exported VRM file")

        except Exception as e:
            self.report({'ERROR'}, str(e))
            print("Exception:", str(e))
            return {'CANCELLED'}

        self.report({'INFO'}, "Process completed successfully")
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_load_merge_export_vrm.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_load_merge_export_vrm)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_load_merge_export_vrm)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()
