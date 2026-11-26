"""Reads the configs of other mods straight out of their PBOs, without unpacking anything else and without HEMTT.

Only a PBO's header and its config files are read: config.bin (rapified) is decoded, a config.cpp is taken as text
with the files it #includes from the same PBO put in their place. Both come back as the same tree:

    {"__parent": "Base" or None, "property": value, "__classes": {"Name": {...}}}

A class that is only declared (class Name;) has "__extern": True. Used by tools/generate_compat_ww2.py.

    python tools/pbo_config.py some.pbo        lists the root classes of its configs
"""
import re
import struct
import sys

PACKED = 0x43707273
VERSION = 0x56657273
TOKEN = re.compile(r'"(?:[^"]|"")*"|[A-Za-z0-9_.\-+$\\/]+|[{};:=\[\],]')


def unpack(data, size):
    """The LZSS packing of PBO entries."""
    out = bytearray()
    at = 0

    while len(out) < size and at < len(data):
        flags = data[at]
        at += 1

        for bit in range(8):
            if len(out) >= size or at >= len(data):
                break

            if flags & (1 << bit):
                out.append(data[at])
                at += 1
            else:
                low, high = data[at], data[at + 1]
                at += 2
                start = len(out) - (low | ((high & 0xF0) << 4))

                for step in range((high & 0x0F) + 3):
                    if len(out) >= size:
                        break

                    out.append(out[start + step] if start + step >= 0 else 0x20)

    return bytes(out)


def _text(handle):
    out = bytearray()

    while True:
        char = handle.read(1)

        if not char or char == b"\0":
            return out.decode("utf-8", errors="replace")

        out += char

        if len(out) > 4096:
            raise ValueError("not a PBO header")


def entries(pbo):
    """[(name, packing, unpacked size, stored size, offset)] of a PBO."""
    found = []

    with open(pbo, "rb") as handle:
        first = True

        while True:
            name = _text(handle)
            packing, original, _, _, size = struct.unpack("<IIIII", handle.read(20))

            if first and not name and packing == VERSION:
                while _text(handle):
                    _text(handle)
            elif not name:
                break
            else:
                found.append((name.replace("/", "\\"), packing, original, size))

            first = False

            if len(found) > 200000:
                raise ValueError("not a PBO header")

        offset = handle.tell()

    out = []

    for name, packing, original, size in found:
        out.append((name, packing, original, size, offset))
        offset += size

    return out


def read(pbo, entry, packed=None):
    """An entry's bytes. Some PBOs store packed data with equal sizes: packed=True unpacks those too."""
    _, packing, original, size, offset = entry

    with open(pbo, "rb") as handle:
        handle.seek(offset)
        data = handle.read(size)

    if packing == PACKED and original and (original != size or packed):
        data = unpack(data, original)

    return data


class _Rap:
    def __init__(self, data):
        self.data = data

    def text(self, at):
        end = self.data.index(b"\0", at)
        return self.data[at:end].decode("utf-8", errors="replace"), end + 1

    def number(self, at):
        value = self.data[at]
        at += 1

        if value & 0x80:
            value &= 0x7F
            shift = 7

            while True:
                byte = self.data[at]
                at += 1
                value |= (byte & 0x7F) << shift
                shift += 7

                if not byte & 0x80:
                    break

        return value, at

    def value(self, kind, at):
        if kind in (0, 4):
            return self.text(at)

        if kind == 1:
            return struct.unpack_from("<f", self.data, at)[0], at + 4

        if kind == 2:
            return struct.unpack_from("<i", self.data, at)[0], at + 4

        if kind == 6:
            return struct.unpack_from("<q", self.data, at)[0], at + 8

        raise ValueError(f"unknown value type {kind}")

    def array(self, at):
        count, at = self.number(at)
        out = []

        for _ in range(count):
            kind = self.data[at]
            at += 1
            item, at = self.array(at) if kind == 3 else self.value(kind, at)
            out.append(item)

        return out, at

    def body(self, at, wanted=None):
        parent, at = self.text(at)
        count, at = self.number(at)
        tree = {"__parent": parent or None}
        classes = {}

        for _ in range(count):
            kind = self.data[at]
            at += 1

            if kind == 0:
                name, at = self.text(at)
                offset = struct.unpack_from("<I", self.data, at)[0]
                at += 4

                if wanted is None or name.lower() in wanted:
                    classes[name] = self.body(offset)
            elif kind == 1:
                sub = self.data[at]
                name, at = self.text(at + 1)
                tree[name], at = self.value(sub, at)
            elif kind in (2, 5):
                if kind == 5:
                    at += 4

                name, at = self.text(at)
                tree[name], at = self.array(at)
            elif kind == 3:
                name, at = self.text(at)

                if wanted is None or name.lower() in wanted:
                    classes.setdefault(name, {"__extern": True, "__parent": None})
            elif kind == 4:
                _, at = self.text(at)
            else:
                raise ValueError(f"unknown entry type {kind}")

        if classes:
            tree["__classes"] = classes

        return tree


def parse_text(text):
    """A config.cpp without macros, as far as class trees, values and arrays go."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    lines = []

    for line in text.splitlines():
        quoted = False
        kept = []

        for at, char in enumerate(line):
            if char == '"':
                quoted = not quoted

            if not quoted and line.startswith("//", at):
                break

            kept.append(char)

        if not "".join(kept).lstrip().startswith("#"):
            lines.append("".join(kept))

    tokens = TOKEN.findall("\n".join(lines))
    at = 0

    def number(value):
        try:
            return float(value) if any(c in value.lower() for c in ".e") else int(value)
        except ValueError:
            return value

    def block():
        nonlocal at
        tree = {"__parent": None}
        classes = {}

        while at < len(tokens):
            token = tokens[at]

            if token == "}":
                at += 2 if tokens[at + 1:at + 2] == [";"] else 1
                break

            if token == ";":
                at += 1
            elif token == "class":
                name = tokens[at + 1]
                at += 2
                parent = None

                if tokens[at] == ":":
                    parent = tokens[at + 1]
                    at += 2

                if tokens[at] == ";":
                    at += 1
                    classes.setdefault(name, {"__extern": True, "__parent": None})
                else:
                    at += 1
                    classes[name] = block()
                    classes[name]["__parent"] = parent
            elif token == "delete":
                at += 3
            elif tokens[at + 1:at + 2] == ["["]:
                at += 3
                at += 2 if tokens[at] == "+" else 1
                depth = 0
                values = []

                while at < len(tokens):
                    item = tokens[at]
                    at += 1

                    if item == "{":
                        depth += 1
                    elif item == "}":
                        depth -= 1

                        if depth == 0:
                            break
                    elif item != ",":
                        values.append(number(item) if item[0] != '"' else item.strip('"'))

                tree[token] = values
            else:
                at += 2
                values = []

                while at < len(tokens) and tokens[at] != ";":
                    values.append(tokens[at])
                    at += 1

                joined = " ".join(v.strip('"') for v in values)
                tree[token] = joined if values and values[0][0] == '"' else number(joined)

        if classes:
            tree["__classes"] = classes

        return tree

    return block()


def configs(pbo, wanted=None):
    """[(entry name, tree)] of every config in a PBO; wanted limits the root classes kept (lowercase names)."""
    table = entries(pbo)
    by_name = {entry[0].lower(): entry for entry in table}
    out = []

    for entry in table:
        folder, _, base = entry[0].lower().rpartition("\\")

        if base == "config.bin":
            data = read(pbo, entry)

            if data[:4] == b"\0raP":
                out.append((entry[0], _Rap(data).body(16, wanted)))
        elif base == "config.cpp":
            raw = read(pbo, entry)

            # Packed data whose sizes happen to match is not unpacked by read(): see which reading is a config.
            if entry[1] == PACKED and entry[2] == entry[3]:
                unpacked = read(pbo, entry, True)

                if re.search(rb'#include\s+"|class\s', unpacked):
                    raw = unpacked

            def included(match):
                name = match.group(1).replace("/", "\\").lower()
                target = by_name.get(f"{folder}\\{name}" if folder else name) or by_name.get(name)
                return read(pbo, target, True).decode("utf-8", errors="replace") if target and target != entry else ""

            text = re.sub(r'#include\s+"([^"\r\n]*)"', included, raw.decode("utf-8", errors="replace"))
            tree = parse_text(text)

            if wanted is not None:
                tree["__classes"] = {k: v for k, v in tree.get("__classes", {}).items() if k.lower() in wanted}

            out.append((entry[0], tree))

    return out


if __name__ == "__main__":
    for name, tree in configs(sys.argv[1]):
        print(name, {k: len(v.get("__classes", {})) for k, v in tree.get("__classes", {}).items()})
