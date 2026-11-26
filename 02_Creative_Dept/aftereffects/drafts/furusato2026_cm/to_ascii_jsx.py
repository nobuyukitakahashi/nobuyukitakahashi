import sys

def convert(src, dst):
    text = open(src, "r", encoding="utf-8").read()
    out_lines = []
    for line in text.splitlines():
        in_str = None
        esc = False
        res = []
        i = 0
        while i < len(line):
            ch = line[i]
            if in_str:
                if esc:
                    res.append(ch)
                    esc = False
                elif ch == "\\":
                    res.append(ch)
                    esc = True
                elif ch == in_str:
                    res.append(ch)
                    in_str = None
                else:
                    res.append("\\u%04x" % ord(ch) if ord(ch) > 127 else ch)
            else:
                if ch in ('"', "'"):
                    in_str = ch
                    res.append(ch)
                elif ch == "/" and i + 1 < len(line) and line[i + 1] == "/":
                    res.append("".join(c for c in line[i:] if ord(c) < 128))
                    break
                else:
                    res.append("\\u%04x" % ord(ch) if ord(ch) > 127 else ch)
            i += 1
        out_lines.append("".join(res))
    ascii_code = "\n".join(out_lines) + "\n"
    non_ascii = [c for c in ascii_code if ord(c) > 127]
    assert not non_ascii, f"Non-ASCII remained: {non_ascii[:10]}"
    open(dst, "w", encoding="ascii").write(ascii_code)
    print(f"CONVERTED OK: {dst} ({len(ascii_code)} bytes)")

if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])
