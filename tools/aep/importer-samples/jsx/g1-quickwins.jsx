// g1-quickwins.jsx: importer samples for issue #3110 (HDR Highlight Compression, Echo, Linear Wipe,
// Offset, Color Stabilizer). Run in a fresh empty project; save it afterwards as aep/1100-quickwins.aep.
// HDR Highlight Compression only acts above 1.0, so it runs on the synthetic EXR (values up to 4.0) in
// the 32 bpc project; the others run on the SRC test card (with a moving square for the time effects).
(function () {
    var R = $.global.AEB_ROOT ? String($.global.AEB_ROOT) : new File($.fileName).parent.parent.fsName.replace(/\/g, "/");
    $.evalFile(new File(R + "/jsx/lib.jsx"));
    AEB.runGroup({
        group: "1100-quickwins",
        needSrc: true,
        needExr: true,
        effects: [
            { key: "hdr", spec: { mn: ["ADBE HDR ToneMap"], dn: "HDR Highlight Compression" }, source: "EXR" },
            { key: "echo", spec: { mn: ["ADBE Echo"], dn: "Echo" }, source: "SRC" },
            { key: "linwipe", spec: { mn: ["ADBE Linear Wipe"], dn: "Linear Wipe" }, source: "SRC" },
            { key: "offset", spec: { mn: ["ADBE Offset"], dn: "Offset" }, source: "SRC" },
            { key: "colstab", spec: { mn: ["ADBE Deflicker"], dn: "Color Stabilizer" }, source: "SRC" }
        ]
    });
})();
$.global.AEB_RESULT;
