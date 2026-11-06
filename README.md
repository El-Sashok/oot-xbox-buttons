# Ocarina of Time: Xbox buttons

A mod for The Legend of Zelda: Ocarina of Time (Switch 2) on the Lichii emulator. It makes the on-screen buttons match an Xbox controller.

- The action button cross moves to the Xbox layout: Y top, X left, A bottom, B right.
- Button icons change: L and R become LB and RB, ZL and ZR become LT and RT, + becomes Menu, - becomes View.

The mod only changes what is displayed. Your controller bindings stay as they are.

This repository contains no game files. The installer builds the mod from your own copy of the game.

## Requirements

- **Lichii with LayeredFS support for NUP titles.** Official builds ignore RomFS mods on `.nup` files until [PR #203](https://github.com/zortos293/Lichii/pull/203) is merged. Until then, use a build that includes it, such as the [`oot-nx2` branch of this fork](https://github.com/El-Sashok/Lichii/tree/oot-nx2).
- **The game as a `.nup` file**, in the supported version. The installer stops with an error if your version differs.

Nothing else is needed: the installer includes everything it uses.

## Installation

Close Lichii first, and download the installer for your system from the [latest release](https://github.com/El-Sashok/oot-xbox-buttons/releases/latest).

**Windows**

Drag your `.nup` file onto `oot-xbox-buttons-windows.exe`. If Windows SmartScreen warns about the file, choose "More info" then "Run anyway": the installer is not signed.

**Linux**

```
chmod +x oot-xbox-buttons-linux
./oot-xbox-buttons-linux "/path/to/game.nup"
```

The installer builds the mod from your game and puts it in Lichii's mod folder. Start the game: the mod is enabled by default and can be turned off in the game's Add-Ons tab.

The Windows installer has not been tested with the game yet. Reports are welcome.

**Portable Lichii:** if you use a `user` folder next to Lichii, add `--output "<user folder>/load/0400486024DEC000"`.

## Uninstall

In Lichii, right-click the game, choose "Open Mod Data Location" and delete the `XboxButtons` folder.

## Troubleshooting

- **The mod has no effect:** your Lichii build does not include PR #203.
- **Black screen:** delete the mod folder and open an issue with your Lichii version.

## Running from source

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build_mod.py "/path/to/game.nup"
```

## Limitations

- Stick icons and the D-pad icons keep their Switch look.
- The controller diagrams are images and still show a Switch Pro Controller.

## Credits

- [zortos293/Lichii#203](https://github.com/zortos293/Lichii/pull/203) by DrSergioRFilho, which makes mods load on NUP titles.
- [totk-pc-recomp#211](https://github.com/valentderah/totk-pc-recomp/pull/211), for the approach of redrawing the icons in the button font.
