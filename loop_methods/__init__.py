import bpy
import os
from bpy.utils import previews

bl_info = {
    "name": "Loop Methods",
    "blender": (4, 3, 2),
    "category": "User Interface",
    "author": "L0Lock",
    "description": "Various custom playback loop methods for animation.",
    "version": (1, 0, 0),
    "location": "Timeline Header",
    "warning": "",
    "wiki_url": "https://github.com/L0Lock/LoopMethods",
    "tracker_url": "https://github.com/L0Lock/LoopMethods/issues",
    "support": "COMMUNITY",
}

class PBL_AddonPreferences(bpy.types.AddonPreferences):
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

    pcoll.load("PBL_Loop", os.path.join(icons_path, "Loop.png"), 'IMAGE')
    pcoll.load("PBL_ping_pong", os.path.join(icons_path, "PingPong.png"), 'IMAGE')
    pcoll.load("PBL_restore", os.path.join(icons_path, "Revert.png"), 'IMAGE')
    pcoll.load("PBL_start", os.path.join(icons_path, "Start.png"), 'IMAGE')
    pcoll.load("PBL_stop", os.path.join(icons_path, "Stop.png"), 'IMAGE')

    icon_collections["main"] = pcoll

def unload_icons():
    for pcoll in icon_collections.values():
        previews.remove(pcoll)
    icon_collections.clear()

def get_playback_modes(self, context):
    icons = icon_collections.get("main", {})
    
    return [
        (
            'Loop',
            "Loop (default)",
            "Standard looping playback (default)",
            icons.get("PBL_Loop").icon_id if "PBL_Loop" in icons else "",
            0
        ),
        (
            'PBL_stop',
            "Play Once",
            "Play once and stop playback.",
            icons.get("PBL_stop").icon_id if "PBL_stop" in icons else "",
            1
        ),
        (
            'PBL_restore',
            "Play Once & Restore",
            "Play once and jump back to where the playback started.",
            icons.get("PBL_restore").icon_id if "PBL_restore" in icons else "",
            2
        ),
        (
            'PBL_start',
            "Play Once & Jump Start",
            "Play once and jump to scene Start frame.",
            icons.get("PBL_start").icon_id if "PBL_start" in icons else "",
            3
        ),
        (
            'PBL_ping_pong',
            "Ping-Pong",
            "Loop back and forth between start and end",
            icons.get("PBL_ping_pong").icon_id if "PBL_ping_pong" in icons else "",
            4
        ),
    ]

def PBL_stop(scene):
    screen = bpy.context.screen
    if not bpy.context.screen.is_animation_playing:
        return
    if scene.frame_current == scene.frame_end:
        bpy.ops.screen.animation_cancel(restore_frame=False)

def PBL_restore(scene):
    screen = bpy.context.screen
    if not bpy.context.screen.is_animation_playing:
        return
    if scene.frame_current == scene.frame_end:
        bpy.ops.screen.animation_cancel(restore_frame=True)

def PBL_start(scene):
    screen = bpy.context.screen
    if not bpy.context.screen.is_animation_playing:
        return
    if scene.frame_current == scene.frame_end:
        bpy.ops.screen.animation_cancel(restore_frame=False)
        scene.frame_current = scene.frame_start

def PBL_ping_pong(scene):
    screen = bpy.context.screen
    if not bpy.context.screen.is_animation_playing:
        return
    if scene.frame_current == scene.frame_end or scene.frame_current == scene.frame_start:
        bpy.ops.screen.animation_cancel(restore_frame=False)
        bpy.ops.screen.animation_play(reverse=(scene.frame_current == scene.frame_end))

def update_playback_mode(self, context):
    handlers = bpy.app.handlers.frame_change_pre
    handlers[:] = [h for h in handlers if not h.__package__.startswith("PBL_")]

    mode = self.playback_mode
    if mode != 'Loop':  # Skip the "Loop" mode for playback control
        handler = globals().get(mode)
        if handler:
            bpy.app.handlers.frame_change_pre.append(handler)

class PBL_Settings(bpy.types.PropertyGroup):
    playback_mode: bpy.props.EnumProperty(
        name="Loop Methods",
        description="Select playback behavior",
        items=get_playback_modes,
        update=update_playback_mode,
        default=0  # Set default to index 0 (Loop)
    )

def draw_playback_mode_dropdown(self, context):
    layout = self.layout
    scene = context.scene
    addon_prefs = bpy.context.preferences.addons[__package__].preferences

    if context.area.type == 'DOPESHEET_EDITOR':
        row = layout.row()
        row.prop(scene.pbl_settings, "playback_mode", text="", icon_only=addon_prefs.icons_only)

def register():
    load_icons()
    bpy.utils.register_class(PBL_Settings)
    bpy.utils.register_class(PBL_AddonPreferences)
    bpy.types.Scene.pbl_settings = bpy.props.PointerProperty(type=PBL_Settings)

    bpy.types.DOPESHEET_HT_header.append(draw_playback_mode_dropdown)

def unregister():
    unload_icons()
    bpy.utils.unregister_class(PBL_Settings)
    bpy.utils.unregister_class(PBL_AddonPreferences)
    del bpy.types.Scene.pbl_settings

    bpy.types.DOPESHEET_HT_header.remove(draw_playback_mode_dropdown)

if __package__ == "__main__":
    register()
