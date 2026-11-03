# Corpus tools

Keep generators, scrubbers and inspection tools beside the collections they support:

- [`aep/`](aep/): tools for the After Effects project corpus.

Document each tool's inputs, dependencies, application version where relevant, output paths
and invocation. Generate into a separate working directory so a failed run does not overwrite
the last reviewed fixtures. Review and validate the outputs before moving them into a
collection and updating the manifest.

No generators are included in the initial repository setup.
