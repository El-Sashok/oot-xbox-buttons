#!/usr/bin/env python3
"""Builds the Xbox button mod from your own copy of the game."""
import argparse
import hashlib
import shutil
import sys
from pathlib import Path

from nup import Nup, ZsCodec, sarc_file, zstd
from xbox_font import patch_font_file
from xbox_layout import patch_archive

MOD_NAME = "XboxButtons"
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game", help="path to the game's .nup file")
    parser.add_argument("--output", default="out", help="output folder (default: out)")
    args = parser.parse_args()

    game = Nup(args.game)
    layout_archive = read_checked(game, LAYOUT_ARCHIVE)
    font = read_checked(game, FONT)
    codec = ZsCodec(sarc_file(zstd(["-dc"], game.read(DICTIONARY)), "zs.zsdic"))

    output = Path(args.output)
    mod = output / MOD_NAME
    if mod.exists():
        shutil.rmtree(mod)
    for path, data in (
        (LAYOUT_ARCHIVE, patch_archive(codec.decompress(layout_archive))),
        (FONT, patch_font_file(codec.decompress(font))),
    ):
        target = mod / path.lstrip("/")
        target.parent.mkdir(parents=True)
        codec.compress(data, target)

    archive = shutil.make_archive(str(output / MOD_NAME), "zip", output, MOD_NAME)
    print(f"Mod folder: {mod}\nZip for Add-Ons import: {archive}")


if __name__ == "__main__":
    main()
