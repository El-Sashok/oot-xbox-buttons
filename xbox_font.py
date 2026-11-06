"""Redraws the External font glyphs as the Xbox LB, RB, LT, RT, Menu and View buttons."""
import io
import struct

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont

MAGIC = 0x7F9A0218
L_KEY, R_KEY, ZL_KEY, ZR_KEY, B_BUTTON = 0xE044, 0xE045, 0xE046, 0xE047, 0xE041
PLUS, MINUS = 0xE04B, 0xE04C
KEPT_NAME_IDS = (1, 2, 4, 6)
STROKE = 43
LETTER_GAP = 32


def decode(data):
    key = struct.unpack(">I", data[:4])[0] ^ MAGIC
    words = struct.unpack(f">{len(data) // 4}I", data[:len(data) // 4 * 4])
    plain = struct.pack(f">{len(words)}I", *(word ^ key for word in words))
    size, = struct.unpack(">I", plain[4:8])
    return key, plain[8:8 + size]


def encode(font, key):
    padded = font + bytes(-len(font) % 4)
    plain = struct.pack(">II", MAGIC, len(font)) + padded
    words = struct.unpack(f">{len(plain) // 4}I", plain)
    return struct.pack(f">{len(words)}I", *(word ^ key for word in words))


def contours(glyph_set, name):
    pen = DecomposingRecordingPen(glyph_set)
    glyph_set[name].draw(pen)
    result, current = [], []
    for op, args in pen.value:
        current.append((op, args))
        if op in ("closePath", "endPath"):
            result.append(current)
            current = []
    return result


def bounds(contour):
    points = [point for _, args in contour for point in args]
    return (min(p[0] for p in points), min(p[1] for p in points),
            max(p[0] for p in points), max(p[1] for p in points))


def letter_bounds(letter):
    boxes = [bounds(contour) for contour in letter]
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))


def moved(letter, x, y):
    left, bottom, _, _ = letter_bounds(letter)
    dx, dy = x - left, y - bottom
    return [[(op, tuple((px + dx, py + dy) for px, py in args)) for op, args in contour]
            for contour in letter]


def polygon(points):
    contour = [("moveTo", (points[0],))]
    contour += [("lineTo", (point,)) for point in points[1:]]
    return contour + [("closePath", ())]


def rectangle(left, bottom, right, top):
    return polygon(((left, top), (right, top), (right, bottom), (left, bottom)))


def letter_t(x, y, width, height):
    center = x + width // 2
    half = STROKE // 2
    top = y + height
    return [polygon(((x, top), (x + width, top), (x + width, top - STROKE),
                     (center + half, top - STROKE), (center + half, y), (center - half, y),
                     (center - half, top - STROKE), (x, top - STROKE)))]


def menu_icon(disc):
    left, bottom, right, top = bounds(disc)
    center_x, center_y = (left + right) // 2, (bottom + top) // 2
    radius = (right - left) // 2
    half_width, half_height, step = radius * 50 // 100, radius * 8 // 100, radius * 34 // 100
    return [rectangle(center_x - half_width, center_y + offset - half_height,
                      center_x + half_width, center_y + offset + half_height)
            for offset in (step, 0, -step)]


def view_icon(disc):
    left, bottom, right, top = bounds(disc)
    radius = (right - left) // 2
    side, shift, stroke = radius * 72 // 100, radius * 30 // 100, radius * 13 // 100
    total = side + shift
    x, y = (left + right - total) // 2, (bottom + top - total) // 2
    front_left, front_top = x + shift, y + side
    back_top = y + total
    back = polygon(((x, back_top), (x + side, back_top), (x + side, back_top - stroke),
                    (x + stroke, back_top - stroke), (x + stroke, y + shift), (x, y + shift)))
    front_outer = rectangle(front_left, y, front_left + side, front_top)
    front_inner = polygon(((front_left + stroke, y + stroke),
                           (front_left + side - stroke, y + stroke),
                           (front_left + side - stroke, front_top - stroke),
                           (front_left + stroke, front_top - stroke)))
    return [back, front_outer, front_inner]


def key_shape(glyph_contours):
    return max(glyph_contours, key=lambda c: (lambda b: (b[2] - b[0]) * (b[3] - b[1]))(bounds(c)))


def letters_of(glyph_contours):
    shape = key_shape(glyph_contours)
    return [contour for contour in glyph_contours if contour is not shape]


def replace_glyph(font, name, glyph_contours):
    cff = font["CFF "].cff
    top = cff.topDictIndex[0]
    private = top.Private
    advance = font["hmtx"][name][0]
    width = None if advance == private.defaultWidthX else advance - private.nominalWidthX
    pen = T2CharStringPen(width, font.getGlyphSet())
    for contour in glyph_contours:
        for op, args in contour:
            getattr(pen, op)(*args)
    charstrings = top.CharStrings
    charstrings.charStringsIndex[charstrings.charStrings[name]] = pen.getCharString(
        private=private, globalSubrs=cff.GlobalSubrs)


def split_two_letters(glyph_contours):
    letters = letters_of(glyph_contours)
    left_edge = min(bounds(contour)[0] for contour in letters)
    first = [c for c in letters if bounds(c)[0] == left_edge]
    return first, [c for c in letters if c not in first]


def patch(font):
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    shapes = {code: contours(glyph_set, cmap[code])
              for code in (L_KEY, R_KEY, ZL_KEY, ZR_KEY, B_BUTTON, PLUS, MINUS)}
    letter_l = letters_of(shapes[L_KEY])
    letter_r = letters_of(shapes[R_KEY])
    letter_b = letters_of(shapes[B_BUTTON])

    def pair(first, second, x, y):
        box = letter_bounds(first)
        return moved(first, x, y) + moved(second, x + box[2] - box[0] + LETTER_GAP, y)

    def with_t(code, first):
        _, z_letter_y, _, top = letter_bounds(split_two_letters(shapes[code])[0])
        left, _, right, _ = letter_bounds(letters_of(shapes[code]))
        box = letter_bounds(first)
        t_x = left + box[2] - box[0] + LETTER_GAP
        return (moved(first, left, z_letter_y) +
                letter_t(t_x, z_letter_y, right - t_x, top - z_letter_y))

    y_l = letter_bounds(letter_l)[1]
    y_r = letter_bounds(letter_r)[1]
    new = {
        L_KEY: pair(letter_l, letter_b, LB_X, y_l),
        R_KEY: pair(letter_r, letter_b, RB_X, y_r),
        ZL_KEY: with_t(ZL_KEY, letter_l),
        ZR_KEY: with_t(ZR_KEY, letter_r),
        PLUS: menu_icon(key_shape(shapes[PLUS])),
        MINUS: view_icon(key_shape(shapes[MINUS])),
    }
    for code, letters in new.items():
        replace_glyph(font, cmap[code], [key_shape(shapes[code])] + letters)


LB_X = 215
RB_X = 172


def patch_font_file(original):
    key, plain = decode(original)
    font = TTFont(io.BytesIO(plain), recalcTimestamp=False)
    patch(font)
    del font["DSIG"]
    font["name"].names = [record for record in font["name"].names
                          if record.nameID in KEPT_NAME_IDS and record.platformID == 3]
    buffer = io.BytesIO()
    font.save(buffer)
    encoded = encode(buffer.getvalue(), key)
    if len(encoded) > len(original):
        raise ValueError(f"font grew from {len(original)} to {len(encoded)} bytes")
    return encoded
