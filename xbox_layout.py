"""Moves the DoCommand_00 button cross to the Xbox layout (A bottom, B right, X left, Y top)."""
import struct

LAYOUT = "DoCommand_00.buil"
PANE_COUNT = 0x40
PANE_NAMES = 0x520
PANE_OFFSETS = 0x320
SCALE = 0x10
TRANSLATE = 0x1C
TEXT_RECORDS = {"T_GuideX_00": 0x52A8, "T_GuideY_00": 0x53F8}
TEXT_ALIGN = (0x70, 0x78)
TEXTURE_REF_PAIRS = ((0x5D68, 0x70E0), (0x5D78, 0x70F0), (0x9840, 0x8490), (0x9850, 0x84A0))
REFLECTED = (
    "P_B_00", "P_X_00", "P_Y_00", "N_BtnA_00",
    "P_A_00", "P_X_02", "P_Y_02", "N_BtnB_00",
    "P_A_02", "P_B_03", "P_Y_04", "N_BtnX_00",
    "P_A_01", "P_B_02", "P_X_03", "N_BtnY_00",
)
MIRRORED_PAIRS = (
    ("P_BaseX_00", "P_BaseY_00"),
    ("W_BaseX_00", "W_BaseY_00"),
    ("W_BaseXDecide_00", "W_BaseYDecide_00"),
    ("T_GuideX_00", "T_GuideY_00"),
)


def cstr(data, offset):
    return data[offset:data.index(b"\0", offset)].decode()


def swap(data, a, b, size):
    data[a:a + size], data[b:b + size] = data[b:b + size], data[a:a + size]


def patch_layout(data):
    panes = {}
    for i in range(PANE_COUNT):
        name, = struct.unpack_from("<Q", data, PANE_NAMES + 8 * i)
        record, = struct.unpack_from("<Q", data, PANE_OFFSETS + 8 * i)
        panes[cstr(data, name)] = record

    for name in REFLECTED:
        offset = panes[name] + TRANSLATE
        x, y = struct.unpack_from("<ff", data, offset)
        struct.pack_into("<ff", data, offset, -y, -x)

    for a, b in MIRRORED_PAIRS:
        swap(data, panes[a] + SCALE, panes[b] + SCALE, 8)
        swap(data, panes[a] + TRANSLATE, panes[b] + TRANSLATE, 8)

    for field in TEXT_ALIGN:
        swap(data, TEXT_RECORDS["T_GuideX_00"] + field, TEXT_RECORDS["T_GuideY_00"] + field, 4)

    for a, b in TEXTURE_REF_PAIRS:
        swap(data, a, b, 8)


def patch_archive(data):
    archive = bytearray(data)
    data_start, = struct.unpack_from("<I", archive, 12)
    count, = struct.unpack_from("<H", archive, 26)
    names = 32 + count * 16 + 8
    patched = 0
    for i in range(count):
        _, attrs, start, end = struct.unpack_from("<IIII", archive, 32 + i * 16)
        if cstr(archive, names + (attrs & 0xFFFFFF) * 4) != LAYOUT:
            continue
        layout = bytearray(archive[data_start + start:data_start + end])
        patch_layout(layout)
        archive[data_start + start:data_start + end] = layout
        patched += 1
    if patched == 0:
        raise ValueError(f"{LAYOUT} not found")
    return bytes(archive)
