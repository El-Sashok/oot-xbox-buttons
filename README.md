# Ocarina of Time: Xbox buttons

A mod for The Legend of Zelda: Ocarina of Time (Switch 2) on the Lichii emulator. It makes the on-screen buttons match an Xbox controller.

- The action button cross moves to the Xbox layout: Y top, X left, A bottom, B right.
- Button icons change: L and R become LB and RB, ZL and ZR become LT and RT, + becomes Menu, - becomes View.

The mod only changes what is displayed. Your controller bindings stay as they are.

This repository contains no game files. The script builds the mod from your own copy of the game.

## Requirements

- **Lichii with LayeredFS support for NUP titles.** Official builds ignore RomFS mods on `.nup` files until [PR #203](https://github.com/zortos293/Lichii/pull/203) is merged. Until then, use a build that includes it, such as the [`oot-nx2` branch of this fork](https://github.com/El-Sashok/Lichii/tree/oot-nx2).
- **The game as a `.nup` file**, in the supported version. The script stops with an error if your version differs.
- **Python 3 and the `zstd` command line tool.**

Tested on Linux only.

## Installation

1. Get the code and install the Python dependency:

   ```
   git clone https://github.com/El-Sashok/oot-xbox-buttons.git
   cd oot-xbox-buttons
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

2. Build the mod from your game:

   ```
   .venv/bin/python build_mod.py "/path/to/game.nup"
   ```

   This writes `out/XboxButtons/` and `out/XboxButtons.zip`.

3. Close Lichii, then copy the mod folder to the game's mod directory:

   ```
   mkdir -p ~/.local/share/eden/load/0400486024DEC000
   cp -r out/XboxButtons ~/.local/share/eden/load/0400486024DEC000/
   ```

   You can also right-click the game in Lichii and choose "Open Mod Data Location" to find this folder. Lichii's Add-Ons tab can import `out/XboxButtons.zip` too, but that route has not been tested yet.

4. Start the game. The mod is enabled by default and can be turned off in the game's Add-Ons tab.

To uninstall, delete the `XboxButtons` folder from the mod directory.

If the game stays on a black screen, delete the mod folder and open an issue with your Lichii version.

## Limitations

- Stick icons and the D-pad icons keep their Switch look.
- The controller diagrams are images and still show a Switch Pro Controller.

## Credits

- [zortos293/Lichii#203](https://github.com/zortos293/Lichii/pull/203) by DrSergioRFilho, which makes mods load on NUP titles.
- [totk-pc-recomp#211](https://github.com/valentderah/totk-pc-recomp/pull/211), for the approach of redrawing the icons in the button font.
