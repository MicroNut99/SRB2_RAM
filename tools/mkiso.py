#!/usr/bin/env python3
"""mkiso.py - a plain ISO 9660 image, for builds on a system without genisoimage.

    python3 tools/mkiso.py -sysid "SEGA SEGACD" -volid NAME -generic-boot BOOT.BIN -o out.iso <folder>

Does what cd32x/subcpu/Makefile asks genisoimage for: the boot block (the Sega CD's system area,
-generic-boot) in sectors 0-15, a primary volume descriptor, the path tables, the folder's files
(subfolders too) with ISO 9660 level-2 names as given plus ";1" (-full-iso9660-filenames). Enough
for the stack's disc reader (cd32x/subcpu/cdfs.s) and for the Sega CD BIOS. Not byte-identical to
genisoimage's output (dates, file order): build.sh uses genisoimage when it is installed.
"""
import os
import struct
import sys

SECTOR = 2048


def both16(v):
    return struct.pack('<H', v) + struct.pack('>H', v)


def both32(v):
    return struct.pack('<I', v) + struct.pack('>I', v)


def dirdate():
    return bytes([126, 10, 26, 12, 0, 0, 0])        # 2026-10-26 12:00:00, GMT


def voldate():
    return b'2026102612000000' + b'\0'


def record(name, extent, size, is_dir):
    n = len(name)
    rec_len = 33 + n + (1 if n % 2 == 0 else 0)
    r = bytes([rec_len, 0]) + both32(extent) + both32(size) + dirdate()
    r += bytes([2 if is_dir else 0, 0, 0]) + both16(1) + bytes([n]) + name
    if n % 2 == 0:
        r += b'\0'
    return r


class Dir:
    def __init__(self, path, name, parent):
        self.path, self.name, self.parent = path, name, parent
        self.files, self.dirs = [], []
        self.extent = self.size = 0
        self.number = 0


def scan(path, name=b'\0', parent=None):
    d = Dir(path, name, parent)
    for e in sorted(os.listdir(path)):
        p = os.path.join(path, e)
        if os.path.isdir(p):
            d.dirs.append(scan(p, e.upper().encode('ascii'), d))
        else:
            d.files.append([e.upper().encode('ascii') + b';1', p, os.path.getsize(p), 0])
    return d


def walk(d):
    out = [d]
    for s in d.dirs:
        out += walk(s)
    return out


def dir_records(d):
    recs = [record(b'\0', d.extent, d.size, True),
            record(b'\1', (d.parent or d).extent, (d.parent or d).size, True)]
    entries = [(s.name, s.extent, s.size, True) for s in d.dirs] + \
              [(f[0], f[3], f[2], False) for f in d.files]
    for name, ext, size, is_dir in sorted(entries, key=lambda t: t[0]):
        recs.append(record(name, ext, size, is_dir))
    # records never cross a sector boundary
    data, cur = b'', b''
    for r in recs:
        if len(cur) + len(r) > SECTOR:
            data += cur.ljust(SECTOR, b'\0')
            cur = b''
        cur += r
    return data + cur.ljust(SECTOR, b'\0')


def main():
    a = sys.argv[1:]
    opts = {}
    while a and a[0].startswith('-'):
        k = a.pop(0)
        if k == '-full-iso9660-filenames':
            continue
        opts[k] = a.pop(0)
    if len(a) != 1 or '-o' not in opts:
        sys.exit(__doc__)
    root = scan(a[0])
    dirs = walk(root)
    # numbering for the path table: breadth first by parent
    order = [root]
    for d in order:
        order += d.dirs
    for i, d in enumerate(order):
        d.number = i + 1

    # layout: 0-15 system area, 16 PVD, 17 terminator, 18 / 19 L / M path tables, then the
    # directories, then the files
    lba = 20
    for d in dirs:                                  # sizes first (one pass is enough: names fixed)
        d.size = len(dir_records(d))
        d.extent = lba
        lba += d.size // SECTOR
    for d in dirs:
        for f in d.files:
            f[3] = lba
            lba += (f[2] + SECTOR - 1) // SECTOR
    total = lba

    def ptable(big):
        t = b''
        for d in order:
            name = d.name if d is not root else b'\0'
            parent = (d.parent or d).number
            t += bytes([len(name), 0]) + (struct.pack('>I', d.extent) if big else struct.pack('<I', d.extent))
            t += (struct.pack('>H', parent) if big else struct.pack('<H', parent)) + name
            if len(name) % 2:
                t += b'\0'
        return t
    lpt, mpt = ptable(False), ptable(True)
    assert len(lpt) <= SECTOR

    boot = b''
    if '-generic-boot' in opts:
        boot = open(opts['-generic-boot'], 'rb').read()
    sysarea = boot[:16 * SECTOR].ljust(16 * SECTOR, b'\0')

    def achars(s, n):
        return s.encode('ascii')[:n].ljust(n, b' ')
    pvd = b'\1CD001\1\0' + achars(opts.get('-sysid', ''), 32) + achars(opts.get('-volid', ''), 32)
    pvd += b'\0' * 8 + both32(total) + b'\0' * 32 + both16(1) + both16(1) + both16(SECTOR)
    pvd += both32(len(lpt)) + struct.pack('<I', 18) + struct.pack('<I', 0)
    pvd += struct.pack('>I', 19) + struct.pack('>I', 0)
    pvd += record(b'\0', root.extent, root.size, True)
    pvd += b' ' * 128 + b' ' * 128 + b' ' * 128 + b' ' * 128       # volume set, publisher, preparer, application
    pvd += b' ' * 37 * 3                                         # copyright, abstract, bibliographic
    pvd += voldate() * 2 + (b'0' * 16 + b'\0') * 2 + b'\1\0'
    pvd = pvd.ljust(SECTOR, b'\0')
    term = (b'\xffCD001\1').ljust(SECTOR, b'\0')

    with open(opts['-o'], 'wb') as o:
        o.write(sysarea + pvd + term + lpt.ljust(SECTOR, b'\0') + mpt.ljust(SECTOR, b'\0'))
        for d in dirs:
            o.write(dir_records(d))
        for d in dirs:
            for f in d.files:
                data = open(f[1], 'rb').read()
                o.write(data + b'\0' * ((-len(data)) % SECTOR))
    print('%s: %d sectors, %d files' % (opts['-o'], total, sum(len(d.files) for d in dirs)))


if __name__ == '__main__':
    main()
