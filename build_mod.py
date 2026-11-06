#!/usr/bin/env python3
"""Builds the Xbox button mod from your own copy of the game and installs it for Lichii."""
import argparse
import hashlib
import os
import shutil
import sys
from pathlib import Path

from nup import Nup, ZsCodec, decompress, sarc_file
from xbox_font import patch_font_file
from xbox_layout import patch_archive

MOD_NAME = "XboxButtons"
TITLE_ID = "0400486024DEC000"
DICTIONARY = "/romfs/Pack/ZsDic.pack.zs"
LAYOUT_ARCHIVE = "/romfs/UI/Layout2Archive/Common.Product.100.Nin_Ounce_NVN2.blarc.zs"
FONT = "/romfs/Font2/Scalable/External.Nin_Ounce_NVN2.bfotf.zs"
EXPECTED_SHA256 = {
    LAYOUT_ARCHIVE: "0e377658dfc5e68e21aad87c6fa77ea86df8b3261b65c70cb0e985138d67c4ef",
    FONT: "fb371ef34f505da2c16fcac49a764798143cb5368f4e6482fa4d16afaff3d578",
}


def read_checked(game, path):
    data = game.read(path)
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256[path]:
        sys.exit(f"Unsupported game version: {path} does not match.")
    return data


def default_mod_directory():
    if sys.platform == "win32":
        data = Path(os.environ["APPDATA"])
    else:
        data = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
    return data / "eden" / "load" / TITLE_ID


def build(game_path, directory):
    game = Nup(game_path)
    layout_archive = read_checked(game, LAYOUT_ARCHIVE)
    font = read_checked(game, FONT)
    codec = ZsCodec(sarc_file(decompress(game.read(DICTIONARY)), "zs.zsdic"))

    mod = directory / MOD_NAME
    if mod.exists():
        shutil.rmtree(mod)
    for path, data in (
        (LAYOUT_ARCHIVE, patch_archive(codec.decompress(layout_archive))),
        (FONT, patch_font_file(codec.decompress(font))),
    ):
        target = mod / path.lstrip("/")
        target.parent.mkdir(parents=True)
        target.write_bytes(codec.compress(data))
    print(f"Mod installed in {mod}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game", nargs="?", help="path to the game's .nup file")
    parser.add_argument("--output", type=Path, default=default_mod_directory(),
                        help="folder to install the mod in (default: Lichii's mod folder)")
    args = parser.parse_args()
    game = args.game or input("Path to the game's .nup file: ").strip().strip('"')
    build(game, args.output)
    if getattr(sys, "frozen", False) and sys.stdin.isatty():
        input("Press Enter to close.")


if __name__ == "__main__":
    main()
