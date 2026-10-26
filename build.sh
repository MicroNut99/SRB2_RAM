#!/bin/bash
# SRB2 RAM - Sonic Robo Blast 32X as a CD32X "RAM game" for the Mega EverDrive PRO: a disc (the game +
# the Sonic Robo Blast 2 Official Soundtrack as CD audio) and the launcher the EverDrive starts it with.
# README.md tells how. One command:
#
#   bash build.sh 2>&1 | tee build_log.txt
#
# Needs (in data/, never committed):
#   - your Sonic Robo Blast 32X ROM (any *.32x there, e.g. SRB32X_v0.2a.32x): its WAD is the game's data
#   - optional: the Sonic Robo Blast 2 Official Soundtrack (v2.1, "NNN - Title.mp3") in data/ost/ or
#     OST=<folder>: the CD audio (tools/cdtracks.txt says which songs); without it all music is FM
#   - optional: data/splash.png, the picture of the loading screen
# and: the D32XR team's devkit (viciious/32XDK 20220418) for the game (GENDEV, default
# /opt/d32xr-dk/opt/toolchains/sega), Chilly Willy's toolchain in /opt/toolchains/sega for the boot
# stack, the CD32X BootCamp next to this folder (BOOTCAMP=<folder>, default ../CD32X-BootCamp) for the
# launcher, python3 with Pillow, ffmpeg (the soundtrack), genisoimage (else tools/mkiso.py is used).
#
# Settings: NAME=<name> (the disc and launcher name, default SRB2_RAM_R1); OST=<folder>; SPLASH_TEXT=...
# (the line under the loading bar); GENDEV=<devkit>; BOOTCAMP=<folder>; EDCD=0 (the disc only).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
trap 'echo; echo "*** BUILD FAILED at line $LINENO: $BASH_COMMAND"' ERR
NAME="${NAME:-SRB2_RAM_R1}"
GENDEV="${GENDEV:-/opt/d32xr-dk/opt/toolchains/sega}"
DATA="$HERE/data"
B="$HERE/build"
ROMS="$HERE/cd32x/subcpu/ROMS"
mkdir -p "$B" "$ROMS"
[ -x "$GENDEV/sh-elf/bin/sh-elf-gcc" ] || { echo "*** no D32XR devkit at $GENDEV (GENDEV=<folder>) - stopping"; exit 1; }
[ -x /opt/toolchains/sega/sh-elf/bin/sh-elf-gcc ] || { echo "*** no Chilly Willy toolchain in /opt/toolchains/sega - stopping"; exit 1; }
# no genisoimage: tools/mkiso.py stands in (the Sub-CPU Makefile calls genisoimage)
if ! command -v genisoimage > /dev/null; then
  mkdir -p "$B/bin"
  printf '#!/bin/sh\nexec python3 "%s/tools/mkiso.py" "$@"\n' "$HERE" > "$B/bin/genisoimage"
  chmod +x "$B/bin/genisoimage"; export PATH="$B/bin:$PATH"
  echo "    (no genisoimage: tools/mkiso.py makes the ISO)"
fi

echo "==> game data (from your SRB32X ROM)"
ROM="$(ls "$DATA"/*.32x "$DATA"/*.32X 2>/dev/null | head -1 || true)"
[ -n "$ROM" ] || { echo "*** put your Sonic Robo Blast 32X ROM (.32x) in $DATA - stopping"; exit 1; }
python3 "$HERE/tools/extract_wad.py" "$ROM" "$B/srb2.wad"

echo "==> CD audio (the Sonic Robo Blast 2 Official Soundtrack, tools/cdtracks.txt)"
OST="${OST:-$DATA/ost}"
rm -rf "$B/music"
if [ -d "$OST" ]; then python3 "$HERE/tools/make_cdtracks.py" "$HERE/tools/cdtracks.txt" "$OST" "$B/music" "$HERE/srb2/srb2_cdtracks.h"
else echo "    no soundtrack folder ($OST): all music FM"
     python3 "$HERE/tools/make_cdtracks.py" "$HERE/tools/cdtracks.txt" - "$B/music" "$HERE/srb2/srb2_cdtracks.h"; fi

echo "==> game (SRB32X with SRB_ED=1)"
( cd "$HERE/srb2" && make clean > /dev/null 2>&1; PATH="$GENDEV/bin:$PATH" make ROOTDIR="$GENDEV" WAD="$B/srb2.wad" SRB_ED=1 release > "$B/game_log.txt" 2>&1 ) \
  || { tail -30 "$B/game_log.txt"; echo "*** the game did not build"; exit 1; }
cp "$HERE/srb2/D32XR.32x" "$B/SRB2_ED.32x"
( cd "$HERE/srb2" && make clean > /dev/null 2>&1 ) || true
python3 "$HERE/tools/prep_openlara_cd.py" --mode1 "$B/SRB2_ED.32x" "$ROMS/D32XR.32X"

echo "==> the loader's tables (no preload: the game is the whole 4 MB)"
mkdir -p "$B/no_preload"
python3 "$HERE/tools/make_preload.py" plan "$B/no_preload" "$B/preload.json" "$B/cd32x_preload.h" "$HERE/cd32x/subcpu/preload_names.h"
python3 "$HERE/tools/make_preload.py" loader "$B/preload.json" "$ROMS/D32XR.32X" "$HERE/cd32x/sh2/preload.h"

echo "==> loading screen"
if [ -f "$DATA/splash.png" ]; then python3 "$HERE/tools/make_splash.py" "$DATA/splash.png" "$ROMS/IMAGE.RAW"
else                               python3 "$HERE/tools/make_splash.py" - "$ROMS/IMAGE.RAW"; fi

echo "==> SH2 loader"
( cd "$HERE/cd32x/sh2" && make -f Makefile.cdloader clean > /dev/null \
  && make -f Makefile.cdloader LOADER_DEFS="-DCDL_TARGET_OPENLARA=0 -DCDL_SPLASH=1 -DCDL_D32XR_PAGE=1" > "$B/loader_log.txt" 2>&1 ) \
  || { tail -20 "$B/loader_log.txt"; echo "*** the loader did not build"; exit 1; }

echo "==> Sub-CPU and 68000 listener, the data track"
( cd "$HERE/cd32x/subcpu" && make clean > /dev/null \
  && make cd CART_DEFS=-DCART_PAGED GAME_DEFS="-DD32XR_CD=1" VOLID=SRB2_RAM > "$B/subcpu_log.txt" 2>&1 ) \
  || { tail -20 "$B/subcpu_log.txt"; echo "*** the Sub-CPU program did not build"; exit 1; }
ISO="$HERE/cd32x/subcpu/CDROMPlayer.iso"
grep -a -q "SH2-D32XR-CD-M1-LOADER" "$ISO" || { echo "*** the disc does not hold the loader - stopping"; exit 1; }
for f in APP.BIN CDLOADER.BIN D32XR.32X IMAGE.RAW; do
  [ -f "$HERE/cd32x/subcpu/cd/$f" ] || { echo "*** $f is not on the disc - stopping"; exit 1; }
done
cmp -s "$HERE/cd32x/subcpu/cd/D32XR.32X" "$ROMS/D32XR.32X" || { echo "*** the disc has an old game - stopping"; exit 1; }

echo "==> the disc (data track + CD audio)"
WAVS=$(ls "$B"/music/Track*.wav 2>/dev/null || true)
if [ -z "$WAVS" ]; then     # no soundtrack: one silent track (a Sega CD disc wants one)
  python3 - "$B/music/Track02.wav" <<'PY'
import sys, wave
w = wave.open(sys.argv[1], "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(44100)
w.writeframes(bytes(4 * 44100 * 2)); w.close()
PY
  WAVS="$B/music/Track02.wav"
fi
( cd "$HERE/cd32x/subcpu" && python3 make_mixed_cd2.py CDROMPlayer.iso $WAVS --out "$NAME" > "$B/disc_log.txt" ) \
  || { cat "$B/disc_log.txt"; echo "*** the disc image failed"; exit 1; }
mkdir -p "$HERE/discs/$NAME" && mv -f "$HERE/cd32x/subcpu/$NAME.bin" "$HERE/cd32x/subcpu/$NAME.cue" "$HERE/discs/$NAME/"
SECTORS=$(( $(stat -c %s "$HERE/discs/$NAME/$NAME.bin") / 2352 ))
printf "    discs/%s/%s.cue: %d sectors = %d:%02d\n" "$NAME" "$NAME" $SECTORS $((SECTORS / 4500)) $((SECTORS % 4500 / 75))

# the launcher (CD32X BootCamp docs/12): the disc's Sub-CPU program built a second time for the cartridge
# boot (MODE1=1, M1PAGE=1: the EverDrive's banks as the stack's pages), in a copy of cd32x/subcpu (the disc
# keeps the normal program); EDCD_SAVE=1: its header declares save RAM, so the EverDrive OS keeps bank 31
# (the game's saves) on the SD card
if [ "${EDCD:-1}" = 1 ]; then
  BC="${BOOTCAMP:-$HERE/../CD32X-BootCamp}"
  [ -f "$BC/edboot/build_edcd.sh" ] || { echo "*** the launcher needs the CD32X BootCamp next to this folder (or BOOTCAMP=<folder>): not at $BC"; exit 1; }
  echo "==> the launcher EDCD_$NAME.32X (started from the EverDrive menu with the disc in the Sega CD)"
  T="$B/edcd"; rm -rf "$T"; mkdir -p "$T/subcpu/ROMS" "$T/sh2"
  find "$HERE/cd32x/subcpu" -maxdepth 1 -type f -exec cp {} "$T/subcpu/" \;
  cp "$HERE/cd32x/sh2/CDLOADER.32x" "$T/sh2/"
  ( cd "$T/subcpu" && make clean > /dev/null && make CDROMPlayer.bin MODE1=1 M1CTRL0=0x8000 M1PAGE=1 CART_DEFS=-DCART_PAGED GAME_DEFS="-DD32XR_CD=1" > "$T/mode1.log" 2>&1 ) \
    || { tail -20 "$T/mode1.log"; echo "*** the MODE1 Sub-CPU program did not build"; exit 1; }
  EDCD_SAVE=1 bash "$BC/edboot/build_edcd.sh" "$T/subcpu/CDROMPlayer.bin" "$HERE/cd32x/sh2/CDLOADER.32x" "$HERE/discs/$NAME/EDCD_$NAME.32X"
  rm -rf "$T"
fi
echo
echo "==> done: discs/$NAME/ - $NAME.cue + .bin (burn it, or load it as the Sega CD's disc)$( [ "${EDCD:-1}" = 1 ] && echo ", EDCD_$NAME.32X (copy it to the EverDrive's SD card and start it from the menu, not \"Run Mega-CD\")")"
