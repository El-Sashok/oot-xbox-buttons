# Ocarina of Time: Xbox buttons

A mod for The Legend of Zelda: Ocarina of Time (Switch 2) on the Lichii emulator. It makes the on-screen buttons match an Xbox controller.

- The action button cross moves to the Xbox layout: Y top, X left, A bottom, B right.
- Button icons change: L and R become LB and RB, ZL and ZR become LT and RT, + becomes Menu, - becomes View.

The mod only changes what is displayed. Your controller bindings stay as they are.

This repository contains no game files. The script builds the mod from your own copy of the game.

## Requirements

- Lichii with LayeredFS support for NUP titles ([PR #203](https://github.com/zortos293/Lichii/pull/203)). Without it, the mod is listed but ignored.
- The game as a `.nup` file, in the supported version. The script stops if your version differs.
- Python 3, the `zstd` command line tool and fontTools: `pip install -r requirements.txt`

## Build

```
python3 build_mod.py "/path/to/game.nup"
```

This writes `out/XboxButtons/` and `out/XboxButtons.zip`.

## Install

In Lichii, open the game's properties, go to the Add-Ons tab and install `out/XboxButtons.zip`. You can also copy `out/XboxButtons/` to `load/0400486024DEC000/` in the emulator's data folder.

## Limitations

- Stick icons and the D-pad icons keep their Switch look.
- The controller diagrams are images and still show a Switch Pro Controller.

## Credits

- [zortos293/Lichii#203](https://github.com/zortos293/Lichii/pull/203) by DrSergioRFilho, which makes mods load on NUP titles.
- [totk-pc-recomp#211](https://github.com/valentderah/totk-pc-recomp/pull/211), for the approach of redrawing the icons in the button font.
