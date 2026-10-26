#!/usr/bin/env python3
"""extract_wad.py <SRB32X ROM (.32x)> <out.wad>

Takes the game's data out of a Sonic Robo Blast 32X cartridge ROM. The SRB32X build
(srb2/Makefile) appends the IWAD to the program, padded to a multiple of 256 bytes, and pads
the ROM with zeros (dd conv=sync). The WAD is found by its header ("IWAD", lump count, the lump
directory right after the header at offset 12, big-endian as in D32XR's format) and runs to the
end of the ROM's used part.

The WAD (the SRB2 team's and the SRB32X team's work) is never committed: the build takes it
from your own copy of the released ROM (e.g. SRB32X_v0.2a.32x) in data/.
"""
import struct
import sys


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    rom = open(sys.argv[1], 'rb').read()
    if rom[0x100:0x104] != b'SEGA':
        sys.exit('*** %s is not a 32X ROM' % sys.argv[1])
    pos = -1
    i = rom.find(b'IWAD')
    while i >= 0:
        n, ofs = struct.unpack('>II', rom[i + 4:i + 12])
        if i % 256 == 0 and 0 < n < 10000 and ofs == 12:
            pos = i
            break
        i = rom.find(b'IWAD', i + 1)
    if pos < 0:
        sys.exit('*** no IWAD found in %s' % sys.argv[1])
    n, ofs = struct.unpack('>II', rom[pos + 4:pos + 12])
    # the WAD's end: the furthest lump or the directory, whichever ends later
    end = pos + 12 + 16 * n
    for k in range(n):
        p, s = struct.unpack('>II', rom[pos + 12 + 16 * k:pos + 20 + 16 * k])
        end = max(end, pos + p + s)
    names = [rom[pos + 20 + 16 * k:pos + 28 + 16 * k].rstrip(b'\0') for k in range(n)]
    if b'DMAPINFO' not in names:
        sys.exit('*** the WAD in %s has no DMAPINFO: not an SRB32X ROM?' % sys.argv[1])
    open(sys.argv[2], 'wb').write(rom[pos:end])
    title = rom[0x150:0x180].decode('ascii', 'replace').strip()
    print('%s: "%s", IWAD at 0x%X, %d lumps, %d bytes -> %s' % (sys.argv[1], title, pos, n, end - pos, sys.argv[2]))


if __name__ == '__main__':
    main()
