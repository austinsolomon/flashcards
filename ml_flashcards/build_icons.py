#!/usr/bin/env python3
"""Generate minimalist app icons (no external deps) — a small neural-node
motif (nodes + edges) in cyan/violet on the dark app background."""
import zlib, struct, math

BG     = (10, 14, 22)      # #0a0e16
CYAN   = (92, 214, 239)    # #5cd6ef
VIOLET = (139, 123, 255)   # #8b7bff

def lerp(a, b, t): return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

def make(size, path):
    px = [[BG[0], BG[1], BG[2]] for _ in range(size * size)]
    def put(x, y, col, alpha=1.0):
        if 0 <= x < size and 0 <= y < size:
            i = (y * size + x)
            base = px[i]
            px[i] = [round(base[k] + (col[k] - base[k]) * alpha) for k in range(3)]
    def disc(cx, cy, r, col):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                d = math.hypot(x - cx, y - cy)
                if d <= r:
                    put(x, y, col)
                elif d <= r + 1.3:                      # soft edge
                    put(x, y, col, max(0.0, (r + 1.3 - d) / 1.3))
    def line(p, q, col, w):
        steps = int(math.hypot(q[0]-p[0], q[1]-p[1])) * 2 + 1
        for s in range(steps + 1):
            t = s / steps
            x = p[0] + (q[0]-p[0]) * t
            y = p[1] + (q[1]-p[1]) * t
            disc(x, y, w, col)

    # layout: a tiny 3-layer "network"
    S = size
    nodes = [
        (S*0.24, S*0.32), (S*0.24, S*0.68),                 # input layer
        (S*0.50, S*0.22), (S*0.50, S*0.50), (S*0.50, S*0.78),# hidden layer
        (S*0.76, S*0.40), (S*0.76, S*0.62),                 # output layer
    ]
    edges = [(0,2),(0,3),(0,4),(1,2),(1,3),(1,4),(2,5),(3,5),(3,6),(4,6)]
    for a, b in edges:
        line(nodes[a], nodes[b], lerp(CYAN, VIOLET, 0.5), max(1.0, S*0.006))
    for k, (x, y) in enumerate(nodes):
        col = CYAN if k < 2 else (VIOLET if k >= 5 else lerp(CYAN, VIOLET, 0.5))
        disc(x, y, S*0.045, col)

    # encode PNG
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            raw.extend(px[y * size + x])
    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(raw), 9)
    with open(path, "wb") as f:
        f.write(sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b""))
    print("wrote", path, size)

if __name__ == "__main__":
    import os
    os.makedirs("ml_flashcards/icons", exist_ok=True)
    make(192, "ml_flashcards/icons/icon-192.png")
    make(512, "ml_flashcards/icons/icon-512.png")
