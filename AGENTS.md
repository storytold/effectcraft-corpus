# Working on EffectCraft Corpus

Read [README.md](README.md), the relevant collection README, and
[EffectCraft's contributor rules](https://github.com/storytold/effectcraft/blob/main/AGENTS.md)
before changing fixtures or tools. Follow the current host's build and publication rules too.

## Content and provenance

- Keep original `.aep` and `.aepx` fixtures in `aep/`, reviewed presets and starting projects
  in `aep/inputs/`, supporting media in `aep/media/`, generators in `tools/aep/`, and generation
  and validation notes in `docs/aep/`.
- Commit reproducible generation instructions. If a step requires manual authoring, record
  the application version, settings and inputs. Identify unavailable inputs explicitly.
- Do not copy vendor code, application-bundle contents, artwork, fonts, presets, samples or
  ICC payloads. Do not read or copy third-party parser implementations to develop a format.
  Contributor-created presets need their own documented origins and authoring steps;
  observing their application is different from reading their implementation.
- Never include personal or private material. Scrub paths, account names, host names and
  identifying metadata before a file is committed.
- Inspect embedded contents, not just filenames: raw profiles, JSON/base64 and AEPX hex all
  need coverage. Verify the exact output files after cleanup. A changed description or a
  zero-replacement success message does not establish that a file is clean.
- Add an `X.attribution` sidecar for every asset `X` and an entry in `ATTRIBUTION.md`.
  Unclear provenance means the asset is not ready to be added.

## Validation and publication

- Update `SHA256SUMS` with every fixture batch. Include all fixture, authoring-input, media
  and reference-output payloads, using repository-relative paths sorted by path.
- Submit contributions through a pull request from a fork, with the files and validation
  evidence together. Direct push access is not required to contribute.
- Run the consuming tests with `EFFECTCRAFT_AEP_FIXTURES_REQUIRED=1`. Record the tested app
  revision, corpus revision or file hashes, commands, actual counts and explained ignores.
- Explain changes to expected results before accepting them. Description-only profile stubs
  test metadata parsing; they do not validate rendering or colour transforms.
- Keep binary fixtures out of app repositories. Consumers use a pinned snapshot and verify
  hashes before installing it; their pin bumps receive their own review.
- Do not rewrite published history or import old, unreviewed binary ancestry. Old pins must
  remain fetchable.
- Do not add agent, model or tool signatures to commits, PRs or comments.
