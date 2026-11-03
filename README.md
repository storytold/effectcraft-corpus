<h1 align="center">EffectCraft Corpus</h1>

<p align="center">
  <b>Reproducible file-format fixtures for EffectCraft and the Crafting Apps.</b>
</p>

<p align="center">
  Small, original projects with documented inputs and expected results.<br>
  Kept outside the app repository, pinned by commit and verified with SHA-256.
</p>

<p align="center">
  <a href="LICENSE-MIT">MIT</a> OR <a href="LICENSE-APACHE">Apache-2.0</a> ·
  <a href="https://github.com/storytold/effectcraft">EffectCraft on GitHub</a> ·
  <a href="https://getartcraft.com/apps/effectcraft">EffectCraft</a> ·
  <a href="https://discord.gg/artcraft">Community on Discord</a>
</p>

> [!NOTE]
> This repository currently contains the corpus layout and contribution instructions.
> The first reviewed AEP fixtures, generators and checksum entries will be added separately.
> EffectCraft's pinned corpus fetch command is still pending.

**Contents:** [What this is](#what-this-is) · [Layout](#layout) ·
[Using the corpus](#using-the-corpus) · [Verifying](#verifying) ·
[Adding files](#adding-or-regenerating-files) · [Pinning](#pinning-workflow) ·
[Provenance](#provenance) · [License and credits](#license-and-credits)

## What this is

This repository holds test projects and supporting data for
[EffectCraft](https://github.com/storytold/effectcraft), the ArtCraft motion graphics and
visual effects app. The first collection is [`aep/`](aep/): After Effects projects in `.aep`
and `.aepx` form, used to check parsing, import fidelity and loss reporting.

Each collection documents how its files were made and what the tests should recover from
them. A project file is not automatically a rendering oracle: any reference renders or
read-back results need their own generation notes and attribution.

The layout follows [PhotoCraft Corpus](https://github.com/storytold/photocraft-corpus).
Keeping fixtures here avoids putting large binaries in EffectCraft's history. Consuming
apps must use a **pinned commit** and verify the selected files against a **SHA-256 manifest**.
Tests should not change because somebody updated this repository's `main`.

## Layout

```text
effectcraft-corpus/
├── aep/                    # Reviewed .aep/.aepx fixtures and their .attribution sidecars
│   └── media/              # Original supporting media, when a case needs it
├── tools/
│   └── aep/                # Generation, scrubbing and inspection tools
├── docs/
│   └── aep/                # Generation notes, case coverage and validation results
├── ATTRIBUTION.md          # Asset index; each asset also has a sidecar
├── SHA256SUMS              # Repository-relative paths and hashes for corpus payloads
├── AGENTS.md               # Contributor and automation rules
├── LICENSE-MIT
├── LICENSE-APACHE
└── NOTICE
```

Keep the `.aep` and `.aepx` files directly in `aep/` so that it can be passed to
`EFFECTCRAFT_AEP_FIXTURES`. Group future formats in their own top-level directories, with
matching tools and documentation. Add feature subdirectories only when the consumer supports
them.

## Using the corpus

| Copy | Purpose |
|---|---|
| **Authoring clone:** `effectcraft-corpus/`, beside `effectcraft/` | Edit generators, regenerate fixtures, review changes and commit here. |
| **Consuming copy:** `effectcraft/corpus/aep/` | A gitignored, verified snapshot at the app's chosen commit. Treat it as read-only. |
| **Local review:** point `EFFECTCRAFT_AEP_FIXTURES` at the authoring clone's `aep/` | Test a proposed fixture batch before publishing it; record its commit and any uncommitted changes. |

The consuming copy is a plain directory, not a submodule or subtree. A future fetcher should
download the pinned snapshot, reject missing files or hash mismatches, and install it only
after verification.

To work on this repository:

```sh
git clone https://github.com/storytold/effectcraft-corpus.git
```

Once the first fixture batch is available, from an EffectCraft checkout that includes the
AEP importer:

```sh
EFFECTCRAFT_AEP_FIXTURES="$(cd ../effectcraft-corpus/aep && pwd)" \
EFFECTCRAFT_AEP_FIXTURES_REQUIRED=1 \
cargo test --locked -p effectcraft-aep -- --nocapture
```

`EFFECTCRAFT_AEP_FIXTURES_REQUIRED=1` makes a missing fixture fail instead of silently
skipping. Record actual passed, failed and ignored counts, and explain ignored cases.
The initial empty layout is not a passing corpus run.

## Verifying

After fixtures and their checksums have been added, run from this repository's root:

```sh
sha256sum -c SHA256SUMS      # Linux
shasum -a 256 -c SHA256SUMS  # macOS alternative
```

`SHA256SUMS` currently has no entries because no corpus payloads have been added. It must
cover every fixture, supporting media file and reference output in a published batch. Use
repository-relative paths, sorted by path. Attribution sidecars and documentation are tracked
alongside the files; their revision is fixed by the commit pin.

Hash verification proves file identity. It does not establish provenance or prove that a
cleanup tool removed every embedded payload; those checks are part of reviewing a batch.

## Adding or regenerating files

1. **Create original test content.** Use small, focused projects generated from known inputs.
   Keep the generator under `tools/aep/`. Document any manual authoring steps that cannot be
   automated, including application version, settings and required starting inputs.
2. **Inspect the saved files.** Remove personal paths and metadata. Inspect embedded assets,
   including ICC profiles in raw bytes, JSON/base64 and AEPX hex. A working-space name or a
   cleanup tool's success message is not sufficient evidence.
3. **Record provenance.** Add a sidecar next to every asset and a row in
   [`ATTRIBUTION.md`](ATTRIBUTION.md). Document generated media, fonts referenced by name,
   contributor-created presets and any unavailable inputs in [`docs/aep/`](docs/aep/).
4. **Validate the resulting files.** Run the required corpus tests and compare the affected
   settings and outputs. Explain any expected-result change; do not change expectations just
   to make a regenerated file pass. Save the commands, source revisions and results in the
   batch's validation notes.
5. **Update `SHA256SUMS` in the same change.** Review the exact files, sidecars, generation
   notes and hashes together before publication.

Prefer compact scenes and feature-specific names. Combined projects are useful when their
case map is documented. Aim for collections around 50 MB or less; discuss larger additions
and keep them separately selectable so the default download stays small.

## Pinning workflow

1. Review and publish a complete fixture batch here, with its manifest and supporting notes.
2. In a separate EffectCraft change, pin that exact commit and update the app's expected
   SHA-256 manifest. The fetcher must verify files before installing them.
3. Run the tests with the required-fixture setting and record the results with the pin bump.

Old pins must remain fetchable. **Do not force-push or rewrite published history.** Do not
bring unreviewed historical fixture commits into this repository as part of its initialization.

## Provenance

This repository is for original contributor-authored test content, licensed to the project
under MIT OR Apache-2.0. Third-party corpora should be fetched from their own upstreams with
separate pins and licence checks, following PhotoCraft's pattern.

Do not include vendor artwork, sample projects, fonts, presets or colour-profile payloads.
Using an application to create an original project does not make every automatically embedded
asset ours. Disable embedding where possible, or replace the payload with original synthetic
data and verify the resulting files independently.

Description-only ICC stubs can exercise profile-name parsing; they are not colour-transform
oracles. Keep that distinction explicit in the case documentation. See
[`AGENTS.md`](AGENTS.md) and the [AEP collection notes](aep/README.md).

## License and credits

EffectCraft Corpus is dual-licensed under [MIT](LICENSE-MIT) or
[Apache-2.0](LICENSE-APACHE), at your option. Required notices are in [NOTICE](NOTICE).
Asset origins and licences are recorded in [ATTRIBUTION.md](ATTRIBUTION.md) and individual
sidecars.

Part of the [ArtCraft](https://getartcraft.com/) family of open-source creative tools.
Artists, developers and contributors are welcome in the [community](https://discord.gg/artcraft).

Adobe and After Effects are trademarks of Adobe Inc. This project is independent and is not
affiliated with, sponsored by or endorsed by Adobe Inc.
