# Importer samples and version copies (2026-11-05)

The second AEP batch: projects, presets, media and reference output made for EffectCraft's `.aep`
importer work on 2026-11-05, all by the contributor (vangel76) with Adobe After Effects 2026 (26.2.1x2,
Windows 11). It supports these EffectCraft changes:

| EffectCraft | what it needs from the corpus |
|---|---|
| [#3109](https://github.com/storytold/effectcraft/pull/3109) Cryptomatte | `aep/cryptomatte.aep` (one ignored test) |
| [#3136](https://github.com/storytold/effectcraft/pull/3136) version in the import report, 25.x and 24.x copies | `aep/<family>-26.aep`, `-25x.aep`, `-24x.aep` for 12 families (two ignored tests) |
| [#3119](https://github.com/storytold/effectcraft/pull/3119) HDR, Echo, Linear Wipe, Offset, Color Stabilizer; [#3129](https://github.com/storytold/effectcraft/pull/3129) Lumetri Color; [#3120](https://github.com/storytold/effectcraft/pull/3120) CC Color Neutralizer, EXtractoR, IDentifier | the expected values their unit tests quote come from `aep/readbacks/` and `aep/renders/`; the projects are the files those values were read from. No test opens them yet. |

Every file is hashed in [`SHA256SUMS`](../../SHA256SUMS) and listed in
[`ATTRIBUTION.md`](../../ATTRIBUTION.md); each has a `.attribution` sidecar.

## What is in the batch

| files | count | size | what |
|---|---|---|---|
| `aep/1100-quickwins.aep` | 1 | 4.3 MB | HDR Highlight Compression, Echo, Linear Wipe, Offset, Color Stabilizer: 75 variants (compositions) |
| `aep/1110-extra.aep` | 1 | 1.6 MB | HDR Amount 25/50/75 and Echo Blend variants: 26 variants |
| `aep/1200-lumetri.aep` | 1 | 5.2 MB | Lumetri Color: 63 variants, five of them from presets |
| `aep/1300-thirdparty.aep` | 1 | 1.9 MB | CC Color Neutralizer, EXtractoR, IDentifier: 31 variants |
| `aep/1310-identifier-uint.aep` | 1 | 0.6 MB | IDentifier on an EXR with UINT channels: 10 variants |
| `aep/cryptomatte.aep` | 1 | 0.5 MB | Cryptomatte: 8 variants (this is group `1400-cryptomatte`, see below) |
| `aep/<family>-26.aep`, `-25x.aep`, `-24x.aep` | 36 | 87 MB | 12 families saved three ways for the version tests |
| `aep/inputs/*.ffx` | 10 | 0.5 MB | the contributor's own animation presets (Lumetri 5, EXtractoR 1, IDentifier 2, Cryptomatte 2) |
| `aep/media/` | 5 | 2.0 MB | three EXRs, the manifest of the first, and the Blender scene of the third |
| `aep/readbacks/*.json` | 6 | 0.5 MB | what the scripts set and what After Effects read back, per group |
| `aep/renders/*.png` | 185 | 0.4 MB | one frame per variant as After Effects draws it |

The tools and scripts are in [`tools/aep/`](../../tools/aep/) (`importer-samples/jsx/`,
`make_crypto_exr.py`, `make_crypto_exr_uint.py`, `make_id_exr.py`, `scrub-uninit.py` with
`test_scrub_uninit.py`, `chunk-compare.py`).

**Size.** The 36 version copies are 87 of the 104 MB, which is over the 50 MB the README aims
for; the maintainers decide whether that is acceptable. The copies are separate files in the flat
`aep/` folder because the tests look them up by name there. The batch is a 2.9 MB pack in git (the
saved projects are mostly zeros and repeated structure), and the copies are in their own commit so
they can be dropped from the batch without touching the rest. EffectCraft's `xtask aep-corpus` fetches
the whole pinned commit and installs only the files its `corpus.lock` lists, so the app side can
choose which of these it installs (the 37 files its tests read are 88 MB).

## How the files were made

1. **Importer samples (1100, 1110, 1200, 1300, 1310, 1400).** One group per script in
   [`tools/aep/importer-samples/jsx/`](../../tools/aep/importer-samples/jsx/), all built on `lib.jsx`.
   Run each in a fresh empty project (32 bits per channel, working space None) with
   `AEB_ROOT` set to a working folder that holds `jsx/` (these scripts), `media/` (the EXRs of
   `aep/media/`), `presets/` (the presets of `aep/inputs/`) and empty `aep/`, `json/` and `renders/`;
   then save the project as `aep/<group>.aep`. For every effect the library makes a
   composition per variant: the defaults, every parameter set, minimum and maximum, every popup item once, a
   keyed parameter, an expression, and the preset variants. It reads every value back from After
   Effects and renders one frame per composition (`saveFrameToPng` at 0.5 s). The
   `$.fileName`-relative default of `AEB_ROOT` was added when the scripts were copied here and has
   not been run in After Effects; the original runs set `AEB_ROOT` explicitly.
2. **Sources.** `SRC` is a 320 x 180 test card the script builds from solids (no footage). The EXRs are
   made by [`make_crypto_exr.py`](../../tools/aep/make_crypto_exr.py) and
   [`make_crypto_exr_uint.py`](../../tools/aep/make_crypto_exr_uint.py) (standard library only;
   running them again gives the exact bytes in `aep/media/`) and, for `id-scene-320x180.exr`, by
   [`make_id_exr.py`](../../tools/aep/make_id_exr.py) in Blender 3.0 (Cycles, our own primitives).
3. **Presets (by hand).** The Lumetri curves and look-up tables, the EXtractoR and IDentifier channel
   choice and the Cryptomatte selection live in arbitrary-data parameters that scripting cannot
   set. Each preset was made in the user interface: `u0-preset-setup.jsx` builds a 320 x 180
   composition with the EXR layer and a coloured solid; add the effect, set it as the sidecar of the
   preset says, select the effect, Animation > Save Animation Preset, delete the effect. No Adobe
   preset was used. The scripts skip a preset variant cleanly while its file is missing.
4. **Version copies (by hand).** For each of 12 families, After Effects 2026 saved the project
   normally (`<family>-26.aep`), then File > Save a Copy As 25.x (`-25x`) and File > Save a Copy As
   24.x (`-24x`) from the same open project, in the user interface. A probe of the scripting
   interface (version 26.2.1x2) found no method for the copies, only the two menu commands. The families are the contributor's projects of the same names as the first batch's combined
   projects (`3d`, `effects`, `footage-precomp`, `keyframes`, `layers-comps`, `markers`, `masks`,
   `settings-a`, `shapes`, `styles`, `text`), saved this way, and `1200-lumetri` from an earlier run of the Lumetri group
   (58 variants; `aep/1200-lumetri.aep` is the later run with the five preset variants added).
   The `-26` file of a family is therefore not byte-identical to the unversioned file of the first
   batch.
5. **`cryptomatte.aep` is group `1400-cryptomatte`.** The scripts and read-back call the group 1400;
   the file is named `cryptomatte.aep` because the test of #3109 reads that name. It is the same
   project, not a second copy.

Unavailable or external inputs: the EXR footage the projects link is not stored in the projects
(neutral placeholder paths; the EXRs are in `aep/media/`, relink them to use the projects with footage).
The Lumetri look-up tables `ALEXA_Default_LogC2Rec709` and `Fuji F125 Kodak 2393 (by Adobe)` are
tables of the application; the two presets and the projects store only their names. The plug-ins
(Cryptomatte, EXtractoR, IDentifier, CC Color Neutralizer) are not included; the projects store only
their settings.

## Changes made after saving

Every project goes through the same three steps, in this order, starting from the project as After
Effects saved it (the 36 version copies were regenerated from their raw saves in this order and are
byte for byte the committed files). `scrub-uninit.py` changes only same-size records and `stubicc.rs`
only the profile; the XMP packet and footage link are the first batch's recipe.

1. [`scrub.py`](../../tools/aep/scrub.py): footage alias paths replaced by neutral ones of the same
   length, the host name replaced by `HOST000...`, neutral ascend counts, the XMP packet replaced by
   the one of `empty.aep`. (The scripts' working folder and the machine's host name were stored in
   the link of the EXR footage of 1100, 1110, 1300, 1310, 1400 and of the `effects`, `layers-comps` and
   `styles` families.)
2. **New: [`scrub-uninit.py`](../../tools/aep/scrub-uninit.py).** After Effects wrote some fixed-size
   records without clearing the memory first. Four kinds of records were found to carry leftovers:
   - the footage options (`opti`, tag `oEXR`, 9750 bytes) of an EXR footage item: bytes 0 to 46 are
     options, the rest is uninitialised. In 1110, 1310 and 1400 it held about 9.5 kB of source text of
     an unrelated local scripting tool; in 1300 and in the `footage-precomp` 25.x/24.x copies, binary
     leftovers. The tool zeroes bytes 47 to the end (a clean save of the same footage, as in
     1100, has zeros there);
   - IDentifier's Channel Info (`aRbp`, 148 bytes; the importer reads only the channel name
     NUL-terminated from byte 19): UTF-16 fragments of local folder paths (the user profile, the
     working folder, the EXR path) in the bytes around the name. The tool zeroes runs of UTF-16
     characters outside the name (and a half character in front of it) in a record that has such a
     run: 8 of the records of 1300 (125 bytes) and 9 of 1310 (178 bytes). Records without a run are
     left alone. The ten presets were checked the same way: none has a run;
   - Lumetri Color's data (`sdat`, tag `lumt`, 104 bytes; the importer does not read it): bytes 48 and up
    are uninitialised. They held UTF-16 pieces of a local folder path (`path = "E:/Projek`,
    `-corpus/samples/2`) and of the source text of a local scripting tool. The tool zeroes the
    characters in a record that has a run of two or more: 7 records of `1200-lumetri.aep`, and in
    `1200-lumetri-26` 7, in `-25x` 4 and in `-24x` 9;
  - Lumetri Color's time-based ids (`<guid>`): a version 1 UUID ends in the MAC address of a network
     adapter of the machine (here the address of a virtual adapter). The 12 hex digits were zeroed in `1200-lumetri.aep` (6 ids), in each of the three `1200-lumetri-*` copies
     (4 ids each) and in `lumetri-input-lut.ffx` and `lumetri-look-lut.ffx` (1 each); the time part stays,
     so the ids stay distinct and well formed.
3. **Colour profile payloads replaced.** The projects embed After Effects' working-space profile (HP
   sRGB IEC61966-2.1) as base64 in the settings JSON; [`stubicc.rs`](../../tools/aep/stubicc.rs)
   replaced it by a description-only stub as in the first batch. The six projects have working
   space None; 1100, 1110, 1300, 1310 and `cryptomatte.aep` still held one profile each (one stub each now),
   `1200-lumetri.aep` none. In the 25.x/24.x copies After Effects also embeds a
   profile in each solid's colour settings; all were stubbed (up to 27 in one file).

Three smaller edits:

- `aep/media/id-scene.blend`: Blender had stored the file browser's start folder (a path in the user
  profile) and the absolute path of the render result image. Both strings were replaced with a
  same-length edit (empty, and `//id-scene-320x180.exr`), 100 bytes in all. The file loads in Blender
  3.0 with its six objects.
- `aep/readbacks/*.json`: the absolute folder in the render paths was cut to `renders/`, and the start
  and finish time stamps (which carried the time zone) were reduced to the date.
- The EXR media were not edited; they carry no path, name or host (attributes checked).

## Inspection of the final files

```sh
python -I tools/aep/inspect-embedded.py aep --expect 72 \
  --forbid <user name> --forbid <machine name> --forbid <folder names>
```

72 files (the 20 of the first batch, 6 projects, 36 version copies, 10 presets): all CLEAN, every
profile found is a description-only stub, no vendor string, none of the local user, machine and
folder names (the folder names used were the working folders of the contributor's drives) in ASCII,
UTF-16 LE/BE, hex or base64. The same names were searched in the media, read-backs, renders, scripts
and documents (ASCII, UTF-16, hex, base64): none. The PNGs have only `IHDR`, `IDAT`, `IEND` chunks.

The inspector alone did not find the problems of step 2 (it looks for given names and profiles, and
the fragments were cut off). They came from a review of the bytes of the exported tree: every UTF-16 run
of three or more characters in both alignments with its chunk type, every printable run of 12 or more
bytes per chunk type outside the known text chunks, path patterns, and a search for tool and vendor
names. Only that review found the Lumetri fragments. If you have a
name that must not appear, add it as `--forbid`.

Left as they are, and not private: nine 16-byte `sdat` records of `cryptomatte.aep` that hold
stray pieces of words (`Group`, `complete`, `pti`; the plug-in's sequence data, unread by the importer),
and the Lumetri look names (`SL BLUE ICE`, ...) and look-up-table names that After Effects writes into
Lumetri's popup lists.

### Did the cleanup change anything else?

[`chunk-compare.py`](../../tools/aep/chunk-compare.py) parses before and after into their chunks, requires
the same chunk sequence, and lists the chunks whose bytes differ. For the six importer projects,
comparing the file as After Effects saved it with the final file, the only differences are: the
footage link (`alas`), the settings with the profile (`Utf8`, resized by the stub), the EXR footage options
(`opti`), the IDentifier Channel Info records (`aRbp`), the Lumetri ids (`aRbp`, 4 bytes each), and the
XMP packet after the last chunk. For `cryptomatte.aep` against the staged candidate that an earlier
pass had made without step 2: one chunk, the EXR footage options.

The importer reads the cleaned files identically. A throwaway program imported the file before step 2
and the final file with the importer of the matching EffectCraft branch (project and report as JSON,
compared value by value): 0 differences for all 6 importer projects (1300 and 1310 on the branch of
#3120, which maps IDentifier's channel; `cryptomatte.aep` on the branch of #3109; 1200 and the
`1200-lumetri-*` copies also on the branch of #3129, which maps Lumetri Color; the others on the branch
of #3136) and for all 36 version copies. Against the file as saved, the only differences are the
two footage path strings (project item and missing-footage report).

## What is not in this batch

- `1500-listing.json` and `1500-list-effects-mcp.json`: the list of effects installed on the
  contributor's machine (third-party names); not needed by any test and not original test data.
- The probe scripts for the save-copy method and the effect lists, the `id` probe scripts and their
  renders (`idtest-*`), the `-renders.json` operation lists, `.done` and `.log` files.
- Earlier staged copies of the Cryptomatte, thirdparty and Lumetri projects (`keep-part1/`); superseded
  by the files here.

## Validation

Run with the corpus tree of this branch (`EFFECTCRAFT_AEP_FIXTURES=<corpus>/aep`,
`EFFECTCRAFT_AEP_FIXTURES_REQUIRED=1`, Windows 11, Rust stable, `--release --locked`). The tested
EffectCraft revisions are branch heads, not merges:

| EffectCraft branch (head) | run | passed | failed | ignored |
|---|---|---|---|---|
| `aep-import-versions` (#3136, `835dbf60`) | `effectcraft-aep` unit tests | 34 | 0 | 0 |
| | `effectcraft-aep` integration tests (`it`) | 419 | 0 | 4 |
| | the 2 version tests, run with `--ignored` | 2 | 0 | 0 |
| `aep-import-cryptomatte` (#3109, `fcb0aede`) | `effectcraft-aep` unit tests | 35 | 0 | 0 |
| | `effectcraft-aep` integration tests (`it`) | 421 | 0 | 3 |
| | the Cryptomatte sample test, run with `--ignored` | 1 | 0 | 0 |

```sh
export EFFECTCRAFT_AEP_FIXTURES=<corpus>/aep
export EFFECTCRAFT_AEP_FIXTURES_REQUIRED=1
cargo test --release --locked -p effectcraft-aep
cargo test --release --locked -p effectcraft-aep --test it versions -- --ignored    # aep-import-versions
cargo test --release --locked -p effectcraft-aep --test it cryptomatte -- --ignored # aep-import-cryptomatte
```

- The ignored tests of the full runs are the three samples tests that wait for this batch (the 2 version
  tests; the Cryptomatte test) and the 2 `every_corpus_pair_*` tests that read every `.aep`/`.aepx`
  pair of `AEP_CORPUS`; those 2 were not run again (the batch adds no `.aepx`).
- Negative control: with `cryptomatte.aep` and `text-24x.aep` removed from the folder, the 3 sample
  tests fail with "fixture ... missing (EFFECTCRAFT_AEP_FIXTURES_REQUIRED is set)"; with the batch they
  pass. Without the environment variable they skip, as before.
- The tests are parser and importer checks of the project structure and imported values. The version
  tests compare the import of every `-25x` and `-24x` copy with the `-26` file of its family (same
  project, same report except the version line) and check the version words in `head` and `svap`. No test
  compares a render with `aep/renders/`.
- The branches of #3119, #3129 and #3120 have no test that reads a file of this batch, so they were not
  run against it; their importers were used for the before/after comparison above.
- No expected value was changed.

## Limits

- The profile stubs keep a working-space name, not a colour transform.
- The renders are After Effects' own output of 32-bit linear-light projects saved as 16-bit PNG;
  they are reference images for later render comparisons, not a test yet. Where two groups share a
  composition name (`hdr-*` and `echo-*` in 1100 and 1110, `identifier-00` to `-08` in 1300 and 1310)
  the file is the later run.
- `aep/media/id-scene-320x180.exr` and `id-scene.blend` are not referenced by a project; they are
  the real-renderer counterpart of the synthetic EXRs for the Cryptomatte, EXtractoR and IDentifier tests.
- The tests of #3119, #3129 and #3120 do not read these projects yet; their expected values were taken
  from the read-backs.
