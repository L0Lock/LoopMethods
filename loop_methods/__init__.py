import bpy
import os
from bpy.utils import previews

bl_info = {
    "name": "Loop Methods",
    "blender": (4, 3, 2),
    "category": "User Interface",
    "author": "L0Lock",
    "description": "Various custom playback loop methods for animation.",
    "version": (1, 0, 1),
    "location": "Timeline Header",
    "warning": "",
    "wiki_url": "https://github.com/L0Lock/LoopMethods",
    "tracker_url": "https://github.com/L0Lock/LoopMethods/issues",
    "support": "COMMUNITY",
}

class Loop_Methods_AddonPreferences(bpy.types.AddonPreferences):
    """Playback Loop Addon Preferences"""
    bl_idname = __package__

    icons_only: bpy.props.BoolProperty(
        name="Icons Only",
        description="Display only Icons in the timeline header. Labels will remain visible in the dropw-down menu.",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "icons_only", text="Display only Icons in header.")

icon_collections = {}

def load_icons():
    global icon_collections
    pcoll = previews.new()
    icons_path = os.path.join(os.path.dirname(__file__), "icons")

    pcoll.load("PBLM_icon_Loop", os.path.join(icons_path, "Loop.png"), 'IMAGE')
    pcoll.load("PBLM_icon_ping_pong", os.path.join(icons_path, "PingPong.png"), 'IMAGE')
    pcoll.load("PBLM_icon_restore", os.path.join(icons_path, "Revert.png"), 'IMAGE')
    pcoll.load("PBLM_icon_start", os.path.join(icons_path, "Start.png"), 'IMAGE')
    pcoll.load("PBLM_icon_stop", os.path.join(icons_path, "Stop.png"), 'IMAGE')

    icon_collections["main"] = pcoll

def unload_icons():
    for pcoll in icon_collections.values():
        previews.remove(pcoll)
    icon_collections.clear()

def get_playback_modes(self, context):
    icons = icon_collections.get("main", {})
    
    return [
        (
            'PBLM_method_Loop',
            "Loop (default)",
            "Standard looping playback (default)",
            icons.get("PBLM_icon_Loop").icon_id if "PBLM_icon_Loop" in icons else "",
            0
        ),
        (
            'PBLM_method_stop',
            "Play Once & Stop",
            "Play once and stop at the End Frame.",
            icons.get("PBLM_icon_stop").icon_id if "PBLM_icon_stop" in icons else "",
            1
        ),
        (
            'PBLM_method_restore',
            "Play Once & Restore",
            "Play once and jump back to the frame you started the playback from.",
            icons.get("PBLM_icon_restore").icon_id if "PBLM_icon_restore" in icons else "",
            2
        ),
        (
            'PBLM_method_start',
            "Play Once & Jump Start",
            "Play once and jump back to the Start Frame.",
            icons.get("PBLM_icon_start").icon_id if "PBLM_icon_start" in icons else "",
            3
        ),
        (
            'PBLM_method_ping_pong',
            "Ping-Pong",
            "Loop back and forth between the Start and end Frames",
            icons.get("PBLM_icon_ping_pong").icon_id if "PBLM_icon_ping_pong" in icons else "",
            4
        ),
    ]

def loop_methods_playback_handler(scene):
    """Handles playback behavior based on the selected loop method."""

    if not bpy.context.screen.is_animation_playing:
        return # Necessary to trigger ONLY on playback and not other frame changes

    mode = scene.Loop_Methods_Settings.playback_mode

    if mode == 'PBLM_method_stop' and scene.frame_current == scene.frame_end:
        bpy.ops.screen.animation_cancel(restore_frame=False)
    elif mode == 'PBLM_method_restore' and scene.frame_current == scene.frame_end:
        bpy.ops.screen.animation_cancel(restore_frame=True)
    elif mode == 'PBLM_method_start' and scene.frame_current == scene.frame_end:
        bpy.ops.screen.animation_cancel(restore_frame=False)
        scene.frame_current = scene.frame_start
    elif mode == 'PBLM_method_ping_pong' and (scene.frame_current == scene.frame_end or scene.frame_current == scene.frame_start):
        bpy.ops.screen.animation_cancel(restore_frame=False)
        bpy.ops.screen.animation_play(reverse=(scene.frame_current == scene.frame_end))


class Loop_Methods_Settings(bpy.types.PropertyGroup):
    playback_mode: bpy.props.EnumProperty(
        name="Loop Methods",
        description="Select playback behavior",
        items=get_playback_modes,
        update=lambda self, context: context.area.tag_redraw(),
        default=0  # Set default to index 0 (Loop)
    )

def draw_playback_mode_dropdown(self, context):
    layout = self.layout
    scene = context.scene
    addon_prefs = bpy.context.preferences.addons[__package__].preferences

    if context.area.type == 'DOPESHEET_EDITOR':
        row = layout.row()
        row.prop(scene.Loop_Methods_Settings, "playback_mode", text="", icon_only=addon_prefs.icons_only)

def register():

    load_icons()

    bpy.utils.register_class(Loop_Methods_Settings)
    bpy.utils.register_class(Loop_Methods_AddonPreferences)

    bpy.types.Scene.Loop_Methods_Settings = bpy.props.PointerProperty(type=Loop_Methods_Settings)

    bpy.types.DOPESHEET_HT_header.append(draw_playback_mode_dropdown)

    if loop_methods_playback_handler not in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.append(loop_methods_playback_handler)

def unregister():

    unload_icons()

    bpy.utils.unregister_class(Loop_Methods_Settings)
    bpy.utils.unregister_class(Loop_Methods_AddonPreferences)

    del bpy.types.Scene.Loop_Methods_Settings

    bpy.types.DOPESHEET_HT_header.remove(draw_playback_mode_dropdown)

    if loop_methods_playback_handler in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(loop_methods_playback_handler)

if __package__ == "__main__":
    register()
