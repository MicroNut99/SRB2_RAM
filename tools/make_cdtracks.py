#!/usr/bin/env python3
"""make_cdtracks.py <cdtracks.txt> <OST folder or -> <WAV folder> <header>

The disc's CD audio from the Sonic Robo Blast 2 Official Soundtrack (v2.1: "NNN - Title.mp3"):
for every song in cdtracks.txt (in its order) the OST file NNN is turned into a CD audio track
(44.1 kHz, 16-bit stereo WAV: TrackNN.wav from Track02 on, ffmpeg), and the game's table of
which song plays which disc track is written as a C header (srb2/srb2_cdtracks.h, compiled with
SRB_ED=1: marssound.c S_StartSong).

With "-" (no soundtrack), or for a song whose file is missing, no track is made and the song
keeps its FM version: the header lists only the songs that have a track.
"""
import os
import re
import subprocess
import sys


def main():
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    table, ost, wavdir, header = sys.argv[1:]
    songs = []
    for line in open(table):
        line = line.split('#')[0].split()
        if len(line) == 2:
            songs.append((line[0], line[1]))
    files = {}
    if ost != '-':
        for f in os.listdir(ost):
            m = re.match(r'(\d{3}) - .*\.(mp3|ogg|flac|wav)$', f, re.I)
            if m:
                files[m.group(1)] = os.path.join(ost, f)
    os.makedirs(wavdir, exist_ok=True)
    entries, track = [], 2
    for lump, num in songs:
        src = files.get(num)
        if not src:
            print('    %-9s OST %s: no file - stays FM' % (lump, num))
            continue
        out = os.path.join(wavdir, 'Track%02d.wav' % track)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-ar', '44100', '-ac', '2',
                        '-sample_fmt', 's16', '-map_metadata', '-1', '-fflags', '+bitexact',
                        '-flags:a', '+bitexact', out], check=True)
        print('    track %2d  %-9s %s' % (track, lump, os.path.basename(src)))
        entries.append((lump, track))
        track += 1
    with open(header, 'w') as h:
        h.write('/* SRB2 RAM: the songs that play from the disc\'s CD audio, and their tracks\n'
                ' * (made by tools/make_cdtracks.py from tools/cdtracks.txt - do not edit) */\n')
        h.write('static const struct { char lump[8]; unsigned char track; } srb_cdtracks[] = {\n')
        for lump, t in entries:
            h.write('\t{ "%s", %d },\n' % (lump, t))
        h.write('\t{ "", 0 }\n};\n')
    print('    %d CD audio tracks; %s' % (len(entries), header))


if __name__ == '__main__':
    main()
