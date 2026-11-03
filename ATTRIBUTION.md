# Asset attribution

Every fixture, authoring input, supporting media file and reference output is listed here.
The first batch (2026-11-03) holds 17 After Effects projects and 3 authoring presets; no media or
reference outputs.

| Asset | Author | Source / generation recipe | License |
|---|---|---|---|
| `aep/inputs/curves-red-mid-down.ffx` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/inputs/curves-rgb-two-points.ffx` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |
| `aep/inputs/meshwarp-3x3-center-right.ffx` | vangel76 (contributor) | Adobe After Effects 2026, tools/aep/GENERATING.md | MIT OR Apache-2.0 |

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
