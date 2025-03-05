# SPDX-License-Identifier: GPL-3.0-or-later

# pylint: disable=W0613,E0401,C0114
# pylint: disable=too-few-public-methods
# flake8: noqa: F722

import pathlib
import bpy
from bpy.utils import previews
from bpy.utils import register_classes_factory

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


class LoopMethodsAddonPreferences(bpy.types.AddonPreferences):
    """Playback Loop Addon Preferences"""
    bl_idname = __package__

    icons_only: bpy.props.BoolProperty(
        name="Icons Only",
        description="Display only Icons in the timeline header."
        "Labels will remain visible in the dropw-down menu.",
        default=True
    )

    def draw(self, context: bpy.types.Context):
        """Draw addon preferences."""
        layout = self.layout
        layout.prop(self, "icons_only", text="Display only Icons in header.")


icon_collection: bpy.utils.previews.ImagePreviewCollection = None
playback_modes: list[tuple[str, str, str, int | str, int]] = []


# pylint: disable=W0603
def load_icons():
    """Load custom icons for the addon."""
    global icon_collection

    pcoll = previews.new()
    icons_path = pathlib.Path(__file__).parent/"icons"
    print(f"Icons path: {icons_path}")
    print(f"Icons directory contents: {list(icons_path.iterdir())}")

    pcoll.load("PBLM_icon_Loop", str(icons_path/"Loop.png"), 'IMAGE')
    pcoll.load("PBLM_icon_ping_pong", str(icons_path/"PingPong.png"), 'IMAGE')
    pcoll.load("PBLM_icon_restore", str(icons_path/"Revert.png"), 'IMAGE')
    pcoll.load("PBLM_icon_start", str(icons_path/"Start.png"), 'IMAGE')
    pcoll.load("PBLM_icon_stop", str(icons_path/"Stop.png"), 'IMAGE')

    icon_collection = pcoll
    print(f"Loaded icons: {len(icon_collection)}")

    playback_modes.clear()
    playback_modes.extend(update_playback_modes())


def unload_icons():
    """Unloads custom addon icons when unregistered."""
    global icon_collection

    if icon_collection:
        previews.remove(icon_collection)
    icon_collection = None


def update_playback_modes() -> list[tuple[str, str, str, int | str, int]]:
    """Update the playbak modes list when icons are loaded"""
    icons = icon_collection

    return [
        (
            'PBLM_method_Loop',
            "Loop (default)",
            "Standard looping playback (default)",
            icons.get("PBLM_icon_Loop").icon_id
            if "PBLM_icon_Loop" in icons else "",
            0
        ),
        (
            'PBLM_method_stop',
            "Play Once & Stop",
            "Play once and stop at the End Frame.",
            icons.get("PBLM_icon_stop").icon_id
            if "PBLM_icon_stop" in icons else "",
            1
        ),
        (
            'PBLM_method_restore',
            "Play Once & Restore",
            "Play once and jump back to the frame you started from.",
            icons.get("PBLM_icon_restore").icon_id
            if "PBLM_icon_restore" in icons else "",
            2
        ),
        (
            'PBLM_method_start',
            "Play Once & Jump Start",
            "Play once and jump back to the Start Frame.",
            icons.get("PBLM_icon_start").icon_id
            if "PBLM_icon_start" in icons else "",
            3
        ),
        (
            'PBLM_method_ping_pong',
            "Ping-Pong",
            "Loop back and forth between the Start and end Frames",
            icons.get("PBLM_icon_ping_pong").icon_id
            if "PBLM_icon_ping_pong" in icons else "",
            4
        ),
    ]


def loop_methods_playback_handler(scene: bpy.types.Scene) -> None:
    """Handles playback behavior based on the selected loop method."""

    if not bpy.context.screen.is_animation_playing:
        # Necessary to trigger ONLY on playback and not other frame changes
        return

    mode = scene.loop_methods_settings.playback_mode

    if (
        mode == 'PBLM_method_stop' and
        scene.frame_current == scene.frame_end
    ):
        bpy.ops.screen.animation_cancel(restore_frame=False)
    elif (
        mode == 'PBLM_method_restore' and
        scene.frame_current == scene.frame_end
    ):
        bpy.ops.screen.animation_cancel(restore_frame=True)
    elif (
        mode == 'PBLM_method_start' and
        scene.frame_current == scene.frame_end
    ):
        bpy.ops.screen.animation_cancel(restore_frame=False)
        scene.frame_current = scene.frame_start
    elif (
        mode == 'PBLM_method_ping_pong' and
        (
            scene.frame_current in (scene.frame_end, scene.frame_start)
        )
    ):
        bpy.ops.screen.animation_cancel(restore_frame=False)
        bpy.ops.screen.animation_play(reverse=(
            scene.frame_current == scene.frame_end
        ))


class LoopMethodsSettings(bpy.types.PropertyGroup):
    """
    Stores properties for controlling loop methods in the addon.

    Attributes:
        loop_method (EnumProperty): The currently selected loop method.
    """

    playback_mode: bpy.props.EnumProperty(
        name="Loop Methods",
        description="Select playback behavior",
        items=lambda self, context: playback_modes,
        update=lambda self, context: context.area.tag_redraw(),
        default=0  # Set default to index 0 (Loop)
    )


def draw_loop_methods_dropdown(self, context: bpy.types.Context):
    """Draws the loop methods' dropdown in the Dopesheet headers."""
    layout = self.layout
    scene = context.scene
    addon_prefs = context.preferences.addons[__package__].preferences

    if context.area.type == 'DOPESHEET_EDITOR':
        row = layout.row()
        row.prop(
            scene.loop_methods_settings,
            "playback_mode",
            text="",
            icon_only=addon_prefs.icons_only
        )


classes = (
    LoopMethodsSettings,
    LoopMethodsAddonPreferences,
)

register_classes, unregister_classes = register_classes_factory(classes)


def register() -> None:
    """Registers addon classes, properties, handlers, and loads icons."""
    load_icons()
    register_classes()

    bpy.types.Scene.loop_methods_settings = \
        bpy.props.PointerProperty(type=LoopMethodsSettings)
    bpy.types.DOPESHEET_HT_header.append(draw_loop_methods_dropdown)

    if loop_methods_playback_handler not in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.append(loop_methods_playback_handler)


def unregister() -> None:
    """Unregisters addon classes, properties, handlers, and unloads icons."""
    unload_icons()

    del bpy.types.Scene.loop_methods_settings
    bpy.types.DOPESHEET_HT_header.remove(draw_loop_methods_dropdown)

    if loop_methods_playback_handler in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(loop_methods_playback_handler)

    unregister_classes()


if __package__ == "__main__":
    register()
