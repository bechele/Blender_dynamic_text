bl_info = {
    "name": "Dynamic Text Object",
    "author": "Rolf Jethon, ChatGPT",
    "version": (1, 10, 7),
    "blender": (4, 2, 0),
    "location": "Add > Dynamic Text",
    "description": "Text object with live marker substitution.",
    "category": "Object",
}

import bpy
import re
from bpy.app.handlers import persistent

# Regular expression to recognize markers like {speed}, but not \{speed}
MARKER_PATTERN = re.compile(r"(?<!\\){(\w+)}")

# Reentrancy-protection against undesired recursive calls
is_substituting = False


# Marker data structure for each text object
class DynamicTextProperty(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Marker Name")
    value: bpy.props.FloatProperty(name="Value", update=lambda self, ctx: update_dynamic_text(ctx.object))
    format_string: bpy.props.StringProperty(name="Format", default="%.2f", update=lambda self, ctx: update_dynamic_text(ctx.object))


# Menu entry "Add > Text > Dynamic Text"
class OBJECT_OT_add_dynamic_text(bpy.types.Operator):
    bl_idname = "object.add_dynamic_text"
    bl_label = "Dynamic Text"
    bl_description = "Add a dynamic text object to the scene"

    def execute(self, context):
        # create a new text object
        bpy.ops.object.text_add(enter_editmode=False)
        obj = context.object
        obj["is_dynamic_text"] = True  # Marker for later check
        obj["dynamic_raw_text"] = "Text"  # raw text including markers
        obj.data.body = "Text"  # display text
        return {'FINISHED'}


# replaces all {marker}-place-holders by formatted values
def get_substituted_text(obj, raw_text):
    global is_substituting
    if is_substituting:
        return obj.data.body  # prevent of double processing

    is_substituting = True
    try:
        # remove double markers - keep the order of the markers
        markers = list(dict.fromkeys(MARKER_PATTERN.findall(raw_text)))

        if not hasattr(obj, "dynamic_text_values"):
            return raw_text

        # get existing marker names
        existing_names = {m.name for m in obj.dynamic_text_values}

        # add new markers
        for marker in markers:
            if marker not in existing_names:
                new = obj.dynamic_text_values.add()
                new.name = marker
                new.value = 0.0
                new.format_string = "%.2f"

        # remove unused markers
        valid_names = set(markers)
        for i in reversed(range(len(obj.dynamic_text_values))):
            if obj.dynamic_text_values[i].name not in valid_names:
                obj.dynamic_text_values.remove(i)

        # replace the values
        final_text = raw_text
        for marker in markers:
            match = next((m for m in obj.dynamic_text_values if m.name == marker), None)
            if match:
                try:
                    value_str = match.format_string % match.value
                except:
                    value_str = "<err>"
                final_text = final_text.replace(f"{{{marker}}}", value_str)

        # allows escaping of curly braces
        final_text = final_text.replace(r"\{", "{").replace(r"\}", "}")
        return final_text

    finally:
        is_substituting = False


# Update text content when marker values are changing
def update_dynamic_text(obj):
    if obj and obj.get("is_dynamic_text") and obj.mode == 'OBJECT':
        substituted = get_substituted_text(obj, obj.get("dynamic_raw_text", ""))
        obj.data.body = substituted

# Update on frame change
@persistent
def on_frame_change(scene):
    for obj in scene.objects:
        if obj.type == 'FONT' and obj.get("is_dynamic_text"):
            if obj.mode == 'OBJECT':
                substituted = get_substituted_text(obj, obj.get("dynamic_raw_text", ""))
                if obj.data.body != substituted:
                    obj.data.body = substituted


# Handler, will be run during mode change Edit/Object
@persistent
def update_on_mode_change(scene):
    for obj in scene.objects:
        if obj.type != 'FONT' or not obj.get("is_dynamic_text"):
            continue      

        current_mode = obj.mode
        previous_mode = obj.get("_last_mode", None)

        if current_mode != previous_mode:
            obj["_last_mode"] = current_mode  # note

            if current_mode == 'EDIT':
                # Show raw text including markers in edit mode
                raw = obj.get("dynamic_raw_text", "")
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.font.select_all()
                bpy.ops.font.delete()
                bpy.ops.font.text_insert(text=raw)

            elif current_mode == 'OBJECT':
                # In Object-Mode: Replace markers - update viewport
                current = obj.data.body.strip()
                obj["dynamic_raw_text"] = current
                substituted = get_substituted_text(obj, current)
                obj.data.body = substituted

        # forced text-update in OBJECT-Mode
        if obj.mode == 'OBJECT':
            substituted = get_substituted_text(obj, obj.get("dynamic_raw_text", ""))
            if obj.data.body != substituted:
                obj.data.body = substituted                  


# Side panel: Setting of marker values to be shown in text object - for example delivered by drivers
class DynamicTextPanel(bpy.types.Panel):
    bl_label = "Dynamic Text Markers"
    bl_idname = "OBJECT_PT_dynamic_text"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'FONT' and obj.get("is_dynamic_text")

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if not hasattr(obj, "dynamic_text_values"):
            layout.label(text="No markers found.")
            return

        layout.label(text="Edit markers inside Text (Edit Mode)")
        layout.label(text="use {marker}, \\{ shows curly brace ")

        for item in obj.dynamic_text_values:
            box = layout.box()
            box.prop(item, "name", text="Name")
            box.prop(item, "value", text="Value")
            box.prop(item, "format_string", text="Format")


# registration of components
classes = (
    DynamicTextProperty,
    OBJECT_OT_add_dynamic_text,
    DynamicTextPanel,
)

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_add_dynamic_text.bl_idname, icon='FONT_DATA')

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.dynamic_text_values = bpy.props.CollectionProperty(type=DynamicTextProperty)
    bpy.types.VIEW3D_MT_add.append(menu_func)
    bpy.app.handlers.frame_change_post.append(on_frame_change)
    bpy.app.handlers.depsgraph_update_post.append(update_on_mode_change)

def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(update_on_mode_change)
    bpy.app.handlers.frame_change_post.remove(on_frame_change)    
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    del bpy.types.Object.dynamic_text_values
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
