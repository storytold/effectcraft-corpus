# Initial AEP corpus (2026-11-03)

The first batch: 17 After Effects projects and 3 authoring presets, made by the contributor
(vangel76) for the tests of EffectCraft's `.aep` importer ([#2558](https://github.com/storytold/effectcraft/pull/2558)).
The case map is [`CASES.md`](CASES.md), the generation steps are
[`tools/aep/GENERATING.md`](../../tools/aep/GENERATING.md), every file is hashed in
[`SHA256SUMS`](../../SHA256SUMS) and listed in [`ATTRIBUTION.md`](../../ATTRIBUTION.md).

## What is in the batch

| files | count | what |
|---|---|---|
| `aep/*.aep` | 16 | combined projects: one composition per case, named like the case (see `CASES.md`); `empty.aep` and `fx-switch.aep` are single-case files, `settings-a/b/c.aep` hold the project-settings cases |
| `aep/aepx-pair.aepx` | 1 | the XML form of `aepx-pair.aep` (same projects, saved as `.aep` and then as `.aepx`) |
| `aep/inputs/*.ffx` | 3 | the contributor's own animation presets used by cases 963, 964 and 985 |

No media and no reference renders are included. The footage items of the projects name
contributor-made test media by neutral paths (`C:\fixtures\...`); the tests expect these items to be
**missing placeholders** (intentional), so the corpus needs no media.

## How the files were made

- Application: Adobe After Effects 2026 (26.2.1) on Windows 11, driven through an After Effects MCP
  server (`batch.run` of atomic operations; ExtendScript `eval.run` is disabled there). The
  operation tables are `tools/aep/*.jsx` and `tools/aep/*-to-mcp.js`; run order in `GENERATING.md`.
- Hand-made parts that scripting cannot do: the three presets (Curves and Mesh Warp keep their
  data in an arbitrary-data parameter), the fx switch of `fx-switch.aep`, and the byte edits of the
  text cases 732 and 733 and the cases 988 and 734 (`patch-text.py`). See `GENERATING.md`.
- Presets: made by hand in After Effects 2026 on 2026-10-19 (add the effect, set it, select the
  effect, Animation > Save Animation Preset). No Adobe preset or sample was used.
- Unavailable inputs: the contributor's test media, the earlier single-case projects some cases are
  merged from, the six-preset set (only three are published). Listed in `GENERATING.md`.

## Changes made after saving

1. `scrub.py` (and `layers-comps-scrub-aepx.py`): footage alias paths replaced by neutral ones of
   the same length, host name `HOST000...`, neutral ascend counts, the XMP packet replaced by the
   one of the base project.
2. **Colour profile payloads replaced.** Every project written by After Effects 2026 embeds its
   working-space ICC profile (HP sRGB IEC61966-2.1, 3144 bytes, base64 in the settings JSON), and
   imported footage brings its own. `tools/aep/stubicc.rs` replaced each one by a description-only
   stub (128-byte header, one `desc` tag holding the original profile name, 252 bytes in all, no colour
   data). Saving the projects with working space None was not an option: the importer reads the
   working space's name from the profile and the settings cases (sRGB, Rec.709 Gamma 2.4, gamma)
   test exactly that. `settings-a.aep` has no profile block at all (working space None, its cases are
   623 and friends).

The batch was made with the first version of `stubicc.rs`. The current version also covers white
space around the JSON colon, `\/` escapes, `&quot;` quotes and raw profiles in `.aepx` hex, and stops
on a profile it cannot replace (review of storytold/effectcraft#2558). Run over the 17 scrubbed
projects before stubbing (16 of them with the vendor profile), it writes exactly the 17 submitted
files, byte for byte; run over the submitted files, it changes nothing. The fixtures are unchanged.

**Limit:** the stubs keep a working-space *name*. They do not carry a colour transform and say nothing
about rendering or colour management; the corpus has no reference renders. Cases that depend on a
profile's colour data cannot be tested with it.

## Embedded-content inspection (final files)

Run on the exact files of this batch, not on the tool's own report:

```sh
python -I tools/aep/inspect-embedded.py aep --expect 20 --forbid <user name> --forbid <machine name> --forbid <folder names>
```

The script searches directories recursively (`--expect 20` fails unless exactly the 17 projects and
3 presets were inspected). For each file it looks at the raw bytes, every long base64 run and every
long hex run (the `.aepx` `bdata="..."` attributes, decoded up to two levels deep), searches each
for an ICC header (`acsp` at offset 36) and **requires every profile found to be exactly a
description-only stub**: a 128-byte header with only the fixed fields set, one `desc` tag, a printable
ASCII name and nothing else; any other profile, whatever its size, is reported. It searches the raw
bytes and every decoded run for vendor strings (`Hewlett`, `Adobe RGB`, `Apple Computer`) and the
forbidden texts as ASCII, UTF-16 (LE and BE), hex text and base64 text (all three alignments).
Synthetic regression tests: `python -I tools/aep/test_inspect_embedded.py`. Result for the 17
projects and the 3 presets: exit code 0, 20 files inspected.

| result | detail |
|---|---|
| profiles found | 36 in 16 of the 17 projects, every one 252 bytes with 1 tag (the stub); 0 in `settings-a.aep`; 0 in the presets |
| where | 35 as base64 in the settings JSON / footage items (one of them in `aepx-pair.aepx`), 1 raw (the profile chunk of the imported png in `footage-precomp.aep`, also a stub now); no profile in the `.aepx` hex runs |
| descriptions | `sRGB IEC61966-2.1` in all but one; `Rec.709 Gamma 2.4` once (`settings-c.aep`) |
| vendor strings | none |
| user, machine and folder names | none |

What else is embedded and where it comes from: the XMP packets that After Effects writes (creator
tool, timestamps, random document ids; taken from the base project by `scrub.py`), the project
structure and the property names After Effects writes, and the fonts the text cases name
(Times New Roman, referenced by name; no font is embedded).

## Validation

- EffectCraft revision: [`bb54a0a0`](https://github.com/storytold/effectcraft/commit/bb54a0a0ec9fadc4222a2624b3dbd1fedd72d14c)
  (the head of #2558 when this batch was validated).
- Corpus: this batch (hashes in `SHA256SUMS`; verified with `sha256sum -c SHA256SUMS`).
- Machine: Windows 11, Rust 1.99.0 (stable).
- Commands (from the EffectCraft checkout, the corpus beside it):

```sh
export EFFECTCRAFT_AEP_FIXTURES=../effectcraft-corpus/aep
export EFFECTCRAFT_AEP_FIXTURES_REQUIRED=1
cargo test --locked -p effectcraft-aep
cargo test --locked -p effectcraft-engine aep
cargo test --locked -p effectcraft-ui-egui aep
AEP_CORPUS=../effectcraft-corpus/aep cargo test --locked -p effectcraft-aep --test it aepx -- --ignored
```

| run | passed | failed | ignored |
|---|---|---|---|
| `effectcraft-aep` unit tests | 29 | 0 | 0 |
| `effectcraft-aep` integration tests (`it`) | 410 | 0 | 2 |
| `effectcraft-engine` (filter `aep`) | 8 | 0 | 0 |
| `effectcraft-ui-egui` (filter `aep`) | 5 | 0 | 0 |
| the 2 ignored tests, run with `AEP_CORPUS` | 2 | 0 | 0 |

With `EFFECTCRAFT_AEP_FIXTURES_REQUIRED=1` a missing project fails its test; no test printed
`SKIPPED`. The 2 ignored tests (`every_corpus_pair_*`) are `#[ignore]`d by the app because they
read every `.aep`/`.aepx` pair of a folder; they were run separately (1 of 1 pairs in this corpus).

These are parser and importer checks of the project structure and imported values. There is no
render comparison and no comparison with After Effects output in this batch.

## Expected results

No expected value was changed. The tests ran before with the projects as After Effects saved them
(with the vendor profile) and after with the stubs, with the same assertions and the same results.
That includes the working-space cases: the importer takes the name from the `desc` tag, and the stub
keeps it.
