/* SRB2 RAM: the songs that play from the disc's CD audio, and their tracks
 * (made by tools/make_cdtracks.py from tools/cdtracks.txt - do not edit) */
static const struct { char lump[8]; unsigned char track; } srb_cdtracks[] = {
	{ "VGM_GFZ1", 2 },
	{ "VGM_GFZ2", 3 },
	{ "VGM_THZ1", 4 },
	{ "VGM_THZ2", 5 },
	{ "VGM_CEZ1", 6 },
	{ "VGM_BOSS", 7 },
	{ "VGM_NTRO", 8 },
	{ "VGM_SS", 9 },
	{ "VGM_INVC", 10 },
	{ "VGM_SHOE", 11 },
	{ "VGM_ACLR", 12 },
	{ "VGM_OVER", 13 },
	{ "VGM_CRED", 14 },
	{ "", 0 }
};
