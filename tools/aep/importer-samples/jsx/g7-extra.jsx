// g7-extra.jsx: extra samples for #3123 (HDR Amount 25/50/75) and #3124 (Echo Blend with several echoes).
(function () {
    var R = $.global.AEB_ROOT ? String($.global.AEB_ROOT) : new File($.fileName).parent.parent.fsName.replace(/\/g, "/");
    $.evalFile(new File(R + "/jsx/lib.jsx"));
    AEB.runGroup({
        group: "1110-extra",
        needSrc: true,
        needExr: true,
        effects: [
            { key: "hdr", spec: { mn: ["ADBE HDR ToneMap"], dn: "HDR Highlight Compression" }, source: "EXR",
              extra: [
                { name: "amount-25", byName: [["Amount", 25]] },
                { name: "amount-50", byName: [["Amount", 50]] },
                { name: "amount-75", byName: [["Amount", 75]] }
              ] },
            { key: "echo", spec: { mn: ["ADBE Echo"], dn: "Echo" }, source: "SRC",
              extra: [
                { name: "blend-n3-i1-d1", byName: [["Number Of Echoes", 3], ["Starting Intensity", 1], ["Decay", 1], ["Echo Operator", 7]] },
                { name: "blend-n2-i05-d05", byName: [["Number Of Echoes", 2], ["Starting Intensity", 0.5], ["Decay", 0.5], ["Echo Operator", 7]] },
                { name: "back-n3-d05", byName: [["Echo Time (seconds)", -0.08], ["Number Of Echoes", 3], ["Decay", 0.5], ["Echo Operator", 5]] },
                { name: "front-n3-d05", byName: [["Echo Time (seconds)", -0.08], ["Number Of Echoes", 3], ["Decay", 0.5], ["Echo Operator", 6]] }
              ] }
        ]
    });
})();
$.global.AEB_RESULT;
