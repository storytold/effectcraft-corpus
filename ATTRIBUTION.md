# Asset attribution

Every fixture, authoring input, supporting media file and reference output is listed here.
The first batch (2026-11-03) holds 17 After Effects projects and 3 authoring presets; no media or
reference outputs.

| Asset | Author | Source / generation recipe | License |
|---|---|---|---|
| `aep/3d.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/aepx-pair.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/aepx-pair.aepx` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/cryptomatte.aep` | vangel76 (contributor) | Adobe After Effects 2026, importer sample group 1400-cryptomatte of tools/aep/importer-samples/jsx/g4-cryptomatte.jsx | MIT OR Apache-2.0 |
| `aep/effects.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/empty.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/footage-precomp.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/fx-switch.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/inputs/crypto-material-paint.ffx` | vangel76 (contributor) | Adobe After Effects 2026, hand-made animation preset (docs/aep/2026-11-05-importer-samples.md) | MIT OR Apache-2.0 |
| `aep/inputs/crypto-object-box.ffx` | vangel76 (contributor) | Adobe After Effects 2026, hand-made animation preset (docs/aep/2026-11-05-importer-samples.md) | MIT OR Apache-2.0 |
| `aep/inputs/curves-red-mid-down.ffx` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/inputs/curves-rgb-two-points.ffx` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/inputs/meshwarp-3x3-center-right.ffx` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/keyframes.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/layers-comps.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/markers.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/masks.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/media/crypto-320x180.exr` | vangel76 (contributor) | Original synthetic media, tools/aep/make_crypto_exr.py | MIT OR Apache-2.0 |
| `aep/media/crypto-320x180.json` | vangel76 (contributor) | Original synthetic media, tools/aep/make_crypto_exr.py | MIT OR Apache-2.0 |
| `aep/readbacks/1400-cryptomatte.json` | vangel76 (contributor) | Adobe After Effects 2026, read-back of importer sample group 1400-cryptomatte | MIT OR Apache-2.0 |
| `aep/renders/crypto-00-defaults.png` | vangel76 (contributor) | Adobe After Effects 2026, reference render of crypto-00-defaults | MIT OR Apache-2.0 |
| `aep/renders/crypto-01-set-all.png` | vangel76 (contributor) | Adobe After Effects 2026, reference render of crypto-01-set-all | MIT OR Apache-2.0 |
| `aep/renders/crypto-02-chk-toggled.png` | vangel76 (contributor) | Adobe After Effects 2026, reference render of crypto-02-chk-toggled | MIT OR Apache-2.0 |
| `aep/renders/crypto-03-pop2-2.png` | vangel76 (contributor) | Adobe After Effects 2026, reference render of crypto-03-pop2-2 | MIT OR Apache-2.0 |
| `aep/renders/crypto-04-pop2-3.png` | vangel76 (contributor) | Adobe After Effects 2026, reference render of crypto-04-pop2-3 | MIT OR Apache-2.0 |
| `aep/renders/crypto-05-pop2-4.png` | vangel76 (contributor) | Adobe After Effects 2026, reference render of crypto-05-pop2-4 | MIT OR Apache-2.0 |
| `aep/renders/crypto-06-preset-object-box.png` | vangel76 (contributor) | Adobe After Effects 2026, reference render of crypto-06-preset-object-box | MIT OR Apache-2.0 |
| `aep/renders/crypto-07-preset-material-paint.png` | vangel76 (contributor) | Adobe After Effects 2026, reference render of crypto-07-preset-material-paint | MIT OR Apache-2.0 |
| `aep/settings-a.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/settings-b.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/settings-c.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/shapes.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/styles.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/text.aep` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |

Each asset `X` also needs an adjacent `X.attribution` file:

```text
asset:        <file name>
title:        <what the file tests or provides>
author:       <creator or copyright holder>
source:       <original work; link or path to generation instructions>
license:      MIT OR Apache-2.0
license-file: <relative paths to the applicable license texts>
added:        <YYYY-MM-DD> by @<GitHub username>
notes:        <application/tool versions, inputs, modifications and embedded-content checks>
```

Use the actual creator and source. A container's sidecar does not establish ownership of
unknown embedded assets. List supporting inputs and explain any removal or replacement in
the collection's generation notes.

Presets and starting projects under [`aep/inputs/`](aep/inputs/) are assets too: each needs its
own sidecar, index entry and hash in `SHA256SUMS`, even when used only to generate a fixture.

Documentation credits are in [NOTICE](NOTICE).
