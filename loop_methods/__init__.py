import bpy

bl_info = {
    "name": "Loop Methods",
    "blender": (4, 3, 2),  # Blender version required
    "category": "Animation",
    "author": "L0Lock",
    "description": "Various custom playback loop methods for animation.",
    "version": (1, 0, 0),
    "location": "Timeline Header",
    "warning": "",
    "wiki_url": "https://github.com/L0Lock/LoopMethods",
    "tracker_url": "https://github.com/L0Lock/LoopMethods/issues",
    "support": "COMMUNITY",
}

# Enum for the different playback modes
def get_playback_modes(self, context):
    return [
        ('Loop', "Loop (default)", "Standard looping playback (default)"),
        ('PBL_stop', "Play Once", "Play once and stop playback."),
        ('PBL_restore', "Play Once & Restore", "Play once and jump back to where the playback started."),
        ('PBL_start', "Play Once & Jump Start", "Play once and jump to scene Start frame."),
        ('PBL_ping_pong', "Ping-Pong", "Loop back and forth between start and end")
    ]

def PBL_stop(scene):
    if scene.frame_current == scene.frame_end:
        bpy.ops.screen.animation_cancel(restore_frame=False)

def PBL_restore(scene):
    if scene.frame_current == scene.frame_end:
        bpy.ops.screen.animation_cancel(restore_frame=True)

def PBL_start(scene):
    if scene.frame_current == scene.frame_end:
        bpy.ops.screen.animation_cancel(restore_frame=False)
        scene.frame_current = scene.frame_start

def PBL_ping_pong(scene):
    if scene.frame_current == scene.frame_end or scene.frame_current == scene.frame_start:
        bpy.ops.screen.animation_cancel(restore_frame=False)
        bpy.ops.screen.animation_play(reverse=(scene.frame_current == scene.frame_end))

# Remove any existing handlers to avoid duplicates
def update_playback_mode(self, context):
    handlers = bpy.app.handlers.frame_change_pre
    handlers[:] = [h for h in handlers if not h.__name__.startswith("PBL_")]

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

    if context.area.type == 'DOPESHEET_EDITOR':  # Timeline header
        row = layout.row()
        row.prop(scene.pbl_settings, "playback_mode", text="")

def register():
    bpy.utils.register_class(PBL_Settings)
    bpy.types.Scene.pbl_settings = bpy.props.PointerProperty(type=PBL_Settings)

    # Add the draw function to the timeline header
    bpy.types.DOPESHEET_HT_header.append(draw_playback_mode_dropdown)

def unregister():
    bpy.utils.unregister_class(PBL_Settings)
    del bpy.types.Scene.pbl_settings

    # Remove the draw function from the timeline header
    bpy.types.DOPESHEET_HT_header.remove(draw_playback_mode_dropdown)

if __name__ == "__main__":
    register()
