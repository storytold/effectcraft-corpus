// g3-thirdparty.jsx: importer samples for issue #3112 (CC Color Neutralizer, EXtractoR, IDentifier).
// Run in a fresh empty project; save it afterwards as aep/1300-thirdparty.aep.
// Every effect is looked up in app.effects first (match name, then display name) and skipped with a
// note when it is not loaded. EXtractoR / IDentifier pick their channels in a plug-in dialog, which
// scripting cannot reach: their channel choice comes from the user's presets (skipped while missing).
(function () {
    var R = $.global.AEB_ROOT ? String($.global.AEB_ROOT) : new File($.fileName).parent.parent.fsName.replace(/\/g, "/");
    $.evalFile(new File(R + "/jsx/lib.jsx"));
    AEB.runGroup({
        group: "1300-thirdparty",
        needSrc: true,
        needExr: true,
        effects: [
            { key: "ccneutral", spec: { mn: ["CS Color Neutralizer", "CC Color Neutralizer"], dn: "CC Color Neutralizer" }, source: "SRC" },
            {
                key: "extractor", spec: { mn: ["EXtractoR"], dn: "EXtractoR" }, source: "EXR",
                presets: [{ name: "channel-z", file: "extractor-z.ffx" }]
            },
            {
                key: "identifier", spec: { mn: ["IDentifier"], dn: "IDentifier" }, source: "EXR",
                presets: [{ name: "channel-id", file: "identifier-id.ffx" }]
            }
        ]
    });
})();
$.global.AEB_RESULT;
