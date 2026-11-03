# Asset attribution

No corpus assets have been added yet. This index will list every fixture, supporting media
file and reference output when the first reviewed batch is contributed.

| Asset | Author | Source / generation recipe | License |
|---|---|---|---|

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

Documentation credits are in [NOTICE](NOTICE).
