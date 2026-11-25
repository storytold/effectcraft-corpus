# AEP generation and inspection tools

The tools that generate and prepare the AEP fixtures. Start with
[`GENERATING.md`](GENERATING.md) (generation order, run order, the three preset cases); the cleanup and
inspection tools are `scrub.py`, `scrub-uninit.py`, `layers-comps-scrub-aepx.py`, `patch-text.py`, `stubicc.rs`,
`inspect-embedded.py` with its tests `test_inspect_embedded.py`, and `chunk-compare.py` (see below).
The importer samples of 2026-11-05 are made by the scripts in `importer-samples/jsx/` and the media
generators `make_crypto_exr.py`, `make_crypto_exr_uint.py` and `make_id_exr.py`; see
[`docs/aep/2026-11-05-importer-samples.md`](../../docs/aep/2026-11-05-importer-samples.md).

When contributing them, document:

- the generation order, authoring application version and required automation interface;
- original starting projects and media, and the recipes that create them;
- manual steps and contributor-created presets where automation cannot set a property;
- removal of identifying metadata and replacement of vendor profile payloads;
- independent inspection of the resulting files, including raw, base64 and AEPX hex data;
- the exact commands used to regenerate hashes and run the consuming tests.

The current contributor's generation notes are in
[EffectCraft's AEP fixture tools](https://github.com/storytold/effectcraft/blob/bb54a0a0ec9fadc4222a2624b3dbd1fedd72d14c/crates/aep/tests/fixtures/tools/README.md).
Use that pinned reference as context while preparing a reviewed contribution here. Add the
actual tools and required inputs, or identify what remains external or unavailable.

Keep generation notes in [`docs/aep/`](../../docs/aep/), finished fixture payloads in
[`aep/`](../../aep/), reviewed presets and starting projects in
[`aep/inputs/`](../../aep/inputs/), and original media in [`aep/media/`](../../aep/media/).
Configure paths to those inputs explicitly. The earlier scripts' `combined/gen/`, `synthetic/`
and `presets/` paths describe the contributor's working layout; document how they map to the
published inputs and keep temporary generation outputs outside the reviewed collection.

A cleanup tool must not be the sole evidence that its outputs contain no unwanted embedded
assets.
