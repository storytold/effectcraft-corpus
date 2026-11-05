# AEP generation and validation notes

Notes per batch. Published so far: [`2026-11-03-initial-corpus.md`](2026-11-03-initial-corpus.md)
(17 projects, 3 presets) and [`2026-11-05-importer-samples.md`](2026-11-05-importer-samples.md)
(importer samples, version copies, presets, media, read-backs and reference renders). The case map of
the first batch is [`CASES.md`](CASES.md).

## Generation notes

Record the authoring application and tool versions, case names and expected properties,
required starting projects, media recipes and relevant font names. Explain any manual
steps, contributor-created presets, unavailable inputs, and changes made after saving.
Link to the actual generators under [`tools/aep/`](../../tools/aep/), reviewed presets and
starting projects under [`aep/inputs/`](../../aep/inputs/), and media under
[`aep/media/`](../../aep/media/). Record the path configuration needed to regenerate a batch.

## Validation notes

Record the EffectCraft revision, corpus commit or exact candidate-file hashes, commands,
passed/failed/ignored counts, and the reason for each ignored case. Confirm that the required
fixture setting was enabled and no cases silently skipped because a file was missing.

Include the embedded-content inspection results for the exact final files, and explain any
changes to expected settings or output after cleanup. Distinguish parser/import checks from
render comparisons and reference-application checks; only claim the checks actually run.

Use a batch-specific filename, such as `YYYY-MM-DD-initial-corpus.md`, so later updates can
retain the evidence for earlier pins. The complete archive of development experiments is
not required.
