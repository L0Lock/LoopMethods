> [!WARNING]
> This addon is in the process of being merged into [dr.sybren's "Unlooped" extension](https://extensions.blender.org/add-ons/unlooped/) (source on [GitLab](https://gitlab.com/dr.sybren/unlooped)), since it was already there and going for the same goal. You can see [my fork on Gitlab](https://gitlab.com/Lauloque/unlooped) to watch the merging progress.
> Once this is done and merged, LoopMethods' repository will be archived, any further updates will be done on Unlooped instead. You can still download and use [LoopMethod's latest release](https://github.com/L0Lock/LoopMethods/releases) if you want to.

------

[![GitHub license](https://img.shields.io/github/license/L0Lock/LoopMethods?style=for-the-badge)](https://github.com/L0Lock/LoopMethods/blob/master/LICENSE) ![Latest Supported Blender Version](https://img.shields.io/badge/Blender-v3.6%20LTS-red?style=for-the-badge&logo=blender) ![Latest Supported Blender Version](https://img.shields.io/badge/Blender-v4.3.0-green?style=for-the-badge&logo=blender) [![ko-fi](https://github.com/L0Lock/LoopMethods/blob/main/Prez/SupportOnKofi.jpg?raw=true)](https://ko-fi.com/lauloque) [![source](https://github.com/L0Lock/LoopMethods/blob/main/Prez/SourceCodeGithub.jpg?raw=true)](https://github.com/L0Lock/LoopMethods)

-----

![feature](https://github.com/L0Lock/LoopMethods/blob/main/Prez/feature.jpg?raw=true)

Provides extra Playback looping methods to Blender via a drop-down menu in the timeline header.

## Features

Adds a menu in the Timeline header (and other animation editors) to change the Playback's Loop Method:

![menu](https://github.com/L0Lock/LoopMethods/blob/main/Prez/menu.png?raw=true)

- **Loop**: Standard looping playback (default);  
    ![demo_1_loop](https://github.com/L0Lock/LoopMethods/blob/main/Prez/demo_1_loop.gif?raw=true)
- **Play Once & Stop**: Play once and stop at the End Frame;  
    ![demo_2_stop](https://github.com/L0Lock/LoopMethods/blob/main/Prez/demo_2_stop.gif?raw=true)
- **Play Once & Restore**: Play once and jump back to the frame you started the playback from;  
    ![demo_3_restore](https://github.com/L0Lock/LoopMethods/blob/main/Prez/demo_3_restore.gif?raw=true)
- **Play Once & Jump Start**: Play once and jump back to the Start Frame;  
    ![demo_4_start](https://github.com/L0Lock/LoopMethods/blob/main/Prez/demo_4_start.gif?raw=true)
- **Ping-Pong**: Loop back and forth between the Start and end Frames.  
    ![demo_5_pingpong](https://github.com/L0Lock/LoopMethods/blob/main/Prez/demo_5_pingpong.gif?raw=true)

In the addon preferences, chose whether to show only the current loop method's Icon in the header (default), or also show its label (takes more header space):

![menu](https://github.com/L0Lock/LoopMethods/blob/main/Prez/preferences.png?raw=true)

## Installation

You can download the extension either from:

- [This repository's releases page](https://github.com/L0Lock/LoopMethods/releases).

The installation process is well explained by Blender's official extensions platform documentation:

[About — Blender Extensions](https://extensions.blender.org/about/)
