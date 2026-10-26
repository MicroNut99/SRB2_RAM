# SRB2 RAM: Sonic Robo Blast 32X from the CD, on the Mega EverDrive PRO

**Sonic Robo Blast 32X** on a **Genesis + Sega CD + 32X**, started from a **Mega EverDrive PRO**, with the
**Sonic Robo Blast 2 Official Soundtrack** playing as CD audio.

1. You start a small launcher (`EDCD_<name>.32X`) from the EverDrive's menu, with the disc in the Sega CD.
2. The disc's boot stack shows a loading screen and copies the game from the CD into the EverDrive's RAM.
3. Sonic Robo Blast 32X then runs from the EverDrive as from its own cartridge. The zone music, the boss,
   the title, the special stages and the jingles come off the disc as CD audio.

This is an example, made for the Sonic Robo Blast 32X developers to look at: one way the game could use a
Sega CD next to a 32X. It is a fan project with no connection to Sonic Team Jr., the SRB32X team or Sega.

## What it is, and what it isn't

**It is:**
- Sonic Robo Blast 32X's own engine and data, unchanged in what it does: the same levels, the same physics,
  the same FM music and sound effects where no CD track is used.
- A "RAM game": the CD carries the game, the EverDrive holds it while it runs. Nothing is flashed or kept;
  each start loads from the CD again (about 90 seconds).
- 13 of the game's 16 songs played from the CD, from the official soundtrack (the list is below).
- Saves kept: the game's save data goes to the EverDrive's battery RAM, which the EverDrive keeps on its SD
  card (as `MEGA/gamedata/EDCD_<name>.32X/bram.srm`).
- Every change made to the game behind one build switch (`SRB_ED=1`). Built without it, the source makes the
  game's original ROM byte for byte.

**It isn't:**
- A new release of the game, or a new version of it. The source here is the SRB32X source this was made
  from, a little older than the released v0.2a. The game's data (its WAD) is taken from your own v0.2a ROM
  at build time.
- A disc with the game's data on it. You build the disc from your own files (`data/`, never committed).
- Something for a plain cartridge or for an emulator without the EverDrive. The launcher talks to the
  EverDrive's own registers.
- Tested on the console yet. So far it was run in ares with the Mega EverDrive PRO emulated: the launcher,
  the loading screen, the title, the menus and Greenflower Act 1 with the CD audio, and the options saved to
  the EverDrive's battery RAM and read back at the next start. (ares shows the game's "this emulator exhibits
  graphical glitches" notice first; press Start.)

## The CD audio

`tools/cdtracks.txt` lists which of the game's songs play from the disc, and which track of the soundtrack
each one is. The disc's audio tracks are made in that order, from track 2.

| Game song | Soundtrack track (v2.1) | Where |
|---|---|---|
| `GFZ1` | 101 Greenflower Zone Act 1 | MAP01; MAP03 after the boss |
| `GFZ2` | 102 Greenflower Zone Act 2 | MAP02 |
| `THZ1` | 103 Techno Hill Zone Act 1 | MAP04; MAP06 after the boss |
| `THZ2` | 104 Techno Hill Zone Act 2 | MAP05 |
| `CEZ1` | 107 Castle Eggman Zone Act 1 | MAP10 |
| `BOSS` | 115 Boss Theme | MAP03, MAP06 |
| `NTRO` | 134 Title Screen | the title |
| `SS` | 117 Special 1: Floral Field Zone | the special stages |
| `INVC` | 127 Invincibility | |
| `SHOE` | 128 Super Sneakers | |
| `ACLR` | 131 Act Clear | |
| `OVER` | 137 Game Over | |
| `CRED` | 138 Credits | |

Kept on FM: `1UP` (Extra Life) and `DRWN` (Drowning), short jingles timed to the game, where a CD seek
would make them late; `CHAO` (an emerald), which has no soundtrack version.

The game's own options still choose: with the disc's CD audio available the music option starts on CD; set to
FM, every song is the FM version as before. A song not in the table always plays its FM version.

## What you need

To build:
- **Your Sonic Robo Blast 32X ROM** (`SRB32X_v0.2a.32x` or the same build), in `data/`. Its WAD is the game's
  data.
- Optional: **the Sonic Robo Blast 2 Official Soundtrack** (v2.1, the files named `NNN - Title.mp3`), in
  `data/ost/` or `OST=<folder>`. Without it, the disc has no CD audio and all music is FM.
- Optional: `data/splash.png`, a picture for the loading screen (320 x 224 or larger; it is scaled).
- The D32XR team's devkit **`chillys-sega-devkit-20220418`** ([viciious/32XDK releases](https://github.com/viciious/32XDK/releases)),
  for the game: `/opt/d32xr-dk/opt/toolchains/sega` if it is there, else `/opt/toolchains/sega`
  (the same GCC 12.1 devkit), or `GENDEV=<folder>`.
- **Chilly Willy's toolchain** in `/opt/toolchains/sega`, for the boot stack.
- **[CD32X BootCamp](https://github.com/MicroNut99/CD32X-BootCamp)** next to this folder (or `BOOTCAMP=<folder>`),
  for the launcher (`edboot/`).
- `python3` with Pillow, `ffmpeg` (for the soundtrack), and `genisoimage` (if it is missing,
  `tools/mkiso.py` makes the ISO instead).

To play:
- Genesis / Mega Drive + Sega CD / Mega-CD + 32X, the **Mega EverDrive PRO** in the 32X's cartridge slot.
- The disc, burned from the `.cue` / `.bin`.

## Building

One command, from this folder:

```
bash build.sh 2>&1 | tee build_log.txt
```

On Windows, from WSL, for example:

```
cd /mnt/s/KoboPort/sega-toolchain-12.1/sega/SRB2_RAM
bash /mnt/s/KoboPort/sega-toolchain-12.1/sega/SRB2_RAM/build.sh 2>&1 | tee /mnt/s/KoboPort/sega-toolchain-12.1/sega/SRB2_RAM/build_edcd_log.txt
```

It makes `discs/<name>/`:
- `<name>.cue` + `<name>.bin`: the disc (the data track, then the CD audio).
- `EDCD_<name>.32X`: the launcher for the EverDrive.

All settings are environment variables, all optional:

| Setting | Default | What it does |
|---|---|---|
| `NAME=<name>` | `SRB2_RAM_R2` | The disc's and the launcher's name. Give every build you test its own. |
| `OST=<folder>` | `data/ost` | The soundtrack's folder. If it is missing, there is no CD audio. |
| `SPLASH_TEXT="..."` | `LOADING SONIC ROBO BLAST 2 INTO THE RAM CART` | The line under the loading bar. |
| `GENDEV=<folder>` | `/opt/d32xr-dk/opt/toolchains/sega`, else `/opt/toolchains/sega` | The D32XR devkit. |
| `BOOTCAMP=<folder>` | `../CD32X-BootCamp`, else `../../CD32X-BootCamp` | The CD32X BootCamp, for the launcher. |
| `EDCD=0` | `1` | The disc only, no launcher. |

What `build.sh` does, in order:
1. Takes the WAD out of your ROM (`tools/extract_wad.py`).
2. Turns the soundtrack songs in `tools/cdtracks.txt` into CD audio tracks, and writes the table the game
   uses (`srb2/srb2_cdtracks.h`, `tools/make_cdtracks.py`).
3. Builds the game: `make release SRB_ED=1` in `srb2/`, with the D32XR devkit.
4. Prepares it for the boot stack (`tools/prep_openlara_cd.py --mode1`).
5. Builds the loading screen, the SH2 loader and the Sub-CPU program, and the ISO.
6. Makes the disc with the CD audio (`make_mixed_cd2.py`).
7. Builds the Sub-CPU program a second time for the cartridge boot, and the launcher (BootCamp's
   `edboot/build_edcd.sh`, with `EDCD_SAVE=1` so the EverDrive keeps the save bank).

### The game alone

`srb2/` builds as before. `SRB_ED=1` is the only new switch, and it is off by default:

```
cd srb2
make ROOTDIR=/opt/d32xr-dk/opt/toolchains/sega WAD=<the WAD> release            # the original ROM
make ROOTDIR=/opt/d32xr-dk/opt/toolchains/sega WAD=<the WAD> SRB_ED=1 release   # the EverDrive build
```

`ROOTDIR` has to be given: the Makefile's own default for it does not take effect.

## Running it

1. Burn the `.cue` / `.bin` to a CD-R and put it in the Sega CD.
2. Copy `EDCD_<name>.32X` to the EverDrive's SD card.
3. Start it from the EverDrive's menu. Do not use "Run Mega-CD".
4. The loading screen shows the gold bar while the game is copied (about 90 seconds), then the game starts.

If the screen stops on a single colour, the boot stack is telling you why (from the BootCamp's
`docs/12_CARTRIDGE_BOOT.md`):

| You see | Meaning |
|---|---|
| **Cyan** | The 32X did not start the boot stack's SH2 loader. |
| **Blue** | No Sega CD found. |
| **Magenta** | No Sub-CPU BIOS found in the Sega CD's ROM. |
| **Red** | The Sub-CPU did not start. |
| **Yellow** | The boot stack's Sub-CPU program did not hand over. |

## What changed in the game (all under `SRB_ED`)

| File | Change |
|---|---|
| `srb2/Makefile`, `srb2/src-md/Makefile` | `SRB_ED=1` adds `-DSRB_ED` and `--defsym SRB_ED=1`. |
| `srb2/src-md/crt0.s` (68000) | The game starts after the boot stack: it rebuilds the three interrupt jumps in work RAM that the boot stack's 68000 table points at, keeps its stack below them, and clears COMM12-15 (the boot stack leaves its own values there; the game expects zeros, as at power-on). Always uses the EverDrive's mapping. The save RAM is the EverDrive's bank 31, reached through window 1 while both SH2s wait in SDRAM. |
| `srb2/crt0.s` (SH2) | While the 68000 has the cartridge (RV = 1), both SH2s wait in SDRAM with all interrupts masked. The EverDrive answers an SH2's cartridge reads with garbage during that time, where a real cartridge would hold the SH2 off. |
| `srb2/marssound.c` | Songs in the CD table play their disc track; the others play FM. |
| `srb2/marssave.c` | With the disc's audio available, the music option starts on CD. |
| `srb2/srb2_cdtracks.h` | The CD table, made by `tools/make_cdtracks.py`. |

## The boot stack

`cd32x/` is the boot stack from [D32XR CD32X](https://github.com/MicroNut99/D32XR_CD32X), unchanged: the
Sub-CPU program, the 68000 listener and the SH2 loader in its D32XR mode (the loading screen, the board
probe, the copy of the game into the cartridge, and the start of both SH2s from the game's header). How a
disc is started from the EverDrive is in the
[CD32X BootCamp](https://github.com/MicroNut99/CD32X-BootCamp), `docs/12_CARTRIDGE_BOOT.md`.

## Credits

**Sonic Robo Blast 32X** - the game this is:
- SSNTails: project lead, gameplay, engine enhancements, additional art
- Saxman: Mega Drive and 32X assembly, additional programming, tools
- Tracking: Cryptik, Wessquiid, Nerreave, NotQuiteHere, Joy Tay, JustKam, MattM4nia
- Special thanks (from the game's credits): Viciious, Mittens, Chilly Willy, TmEE, James Groth

**Sonic Robo Blast 2** by **Sonic Team Jr.** ([srb2.org](https://www.srb2.org)), the game SRB32X is based on.

**The Sonic Robo Blast 2 Official Soundtrack** - its contributing artists: SSNTails, Michael "Spazzo"
Antonakes, Malcolm Brown, David Bulmer, Cyan Helkaraxe, Pedro "Nev3r" Iceta, Jarel Jones, Stefan Rimalia,
David "Big Wave Dave" Spencer, David "InstantSonic" Spencer Jr., Shane Strife.

**Doom 32X: Resurrection / Doom CD32X Fusion** (the engine SRB32X grew from): Victor Luchits (Viciious) and
Chilly Willy; testing by Matt B (Matteusbeus) and TrekkiesUnite118; VGM music by Spoony Bard.

**Calico DOOM**: James Haley, with code by Samuel Villarreal and Rebecca Heineman, from the original Jaguar
DOOM source by John Carmack and id Software.

**Tools**: Chilly Willy's Sega MD/CD/32X devkit; the D32XR team's 32XDK build of it.

**The boot stack and the EverDrive launcher**: D32XR CD32X and the CD32X BootCamp.

Sonic the Hedgehog is a trademark of Sega. This project is not made, approved or supported by Sega or by
Sonic Team Jr.

## License

The game's source (`srb2/`) keeps its own license: see `srb2/README.md` and `srb2/license.txt`. Code
taken from Jaguar DOOM is under id Software's license for that release; the rest is under the MIT
license, as the SRB32X and D32XR sources say. No game data, soundtrack, BIOS or disc image is in this
repository.
