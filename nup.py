"""Reads files out of a NUP container and handles the game's dictionary-compressed .zs files."""
import struct

import zstandard

SUPERBLOCK_SIZE = 0x80
TOC_HEADER_SIZE = 0x30
PACKAGE_SIZE = 0x40
DIR_SIZE = 0x18
FILE_SIZE = 0x50
CODEC_ZSTD = 1


def decompress(data, dictionary=None):
    with zstandard.ZstdDecompressor(dict_data=dictionary).stream_reader(data) as reader:
        return reader.read()


class Nup:
    def __init__(self, path):
        self.file = open(path, "rb")
        superblock = self.file.read(SUPERBLOCK_SIZE)
        if superblock[:4] != b"NUP\x01":
            raise ValueError(f"{path} is not a NUP file")
        offset, size = struct.unpack_from("<QQ", superblock, 8)
        self.file.seek(offset)
        toc = self.file.read(size)
        _, packages, dirs, files, pool, _, _ = struct.unpack_from("<IIQQQQQ", toc, 0)
        position = TOC_HEADER_SIZE
        roots = []
        for _ in range(packages):
            roots.append(struct.unpack_from("<I", toc, position + 8)[0])
            position += PACKAGE_SIZE

        def text(record):
            name, length = struct.unpack_from("<II", toc, record)
            return toc[pool + name:pool + name + length].decode()

        dir_records = []
        for _ in range(dirs):
            first, count = struct.unpack_from("<II", toc, position + 8)
            dir_records.append((text(position), first, count))
            position += DIR_SIZE
        file_records = []
        for _ in range(files):
            _, extent, extent_size = struct.unpack_from("<QQQ", toc, position + 8)
            file_records.append((text(position), extent, extent_size, toc[position + 0x40]))
            position += FILE_SIZE
        children = struct.unpack_from(f"<{(pool - position) // 4}I", toc, position)

        self.files = {}

        def walk(directory, path):
            _, first, count = dir_records[directory]
            for child in children[first:first + count]:
                if child < dirs:
                    walk(child, f"{path}/{dir_records[child][0]}")
                else:
                    record = file_records[child - dirs]
                    self.files.setdefault(f"{path}/{record[0]}", record)

        for root in roots:
            walk(root, "")

    def read(self, path):
        _, extent, extent_size, codec = self.files[path]
        self.file.seek(extent)
        data = self.file.read(extent_size)
        return decompress(data) if codec == CODEC_ZSTD else data


def sarc_file(data, wanted):
    if data[:4] != b"SARC":
        raise ValueError("not a SARC archive")
    data_start, = struct.unpack_from("<I", data, 12)
    count, = struct.unpack_from("<H", data, 26)
    names = 32 + count * 16 + 8
    for i in range(count):
        _, attrs, start, end = struct.unpack_from("<IIII", data, 32 + i * 16)
        name = names + (attrs & 0xFFFFFF) * 4
        if data[name:data.index(b"\0", name)].decode() == wanted:
            return data[data_start + start:data_start + end]
    raise KeyError(wanted)


class ZsCodec:
    def __init__(self, dictionary):
        self.dictionary = zstandard.ZstdCompressionDict(dictionary)

    def decompress(self, data):
        return decompress(data, self.dictionary)

    def compress(self, data):
        # The game hangs on a frame that has no content size.
        compressor = zstandard.ZstdCompressor(level=19, dict_data=self.dictionary,
                                              write_content_size=True, write_checksum=False)
        return compressor.compress(data)
