Summary
=======

`ProfileSettingsDumper` - is a plugin for the Ultimaker Cura. It allows you to dump
all profile settings of the current project into an INI-like file. The latter can be used
as a backup or for the comparison between profiles using `diff`, `meld`, `kompare`
or any other tools you want.

This project was inspired by [that plugin](https://github.com/5axes/CuraSettingsWriter).

**WARNING!** Only one extruder is supported!

Requirements
============

Tested with Cura 4.8.0 (AppImage).

Installation
============

Clone this repository into the plugins directory and restart Cura.
Plugins directory: `~/.local/share/cura/$VERSION/plugins`.

Usage
=====

1. Click `File -> Save project...` (or press `Ctrl+S` shortcut);
2. Choose `Profile settings dumps (*.dimp)` as a file type;
3. Specify a file name;
4. Click `Save`;
5. Open the file and examine or compare it;

License
=======

GPL.
