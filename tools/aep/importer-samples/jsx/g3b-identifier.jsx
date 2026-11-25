// g3b-identifier.jsx: IDentifier on media/crypto-uint-320x180.exr (UINT id channels objectId and
// IndexOB.X; IDentifier lists only UINT channels), with the user's preset (objectId, ID 2).
(function () {
    var R = $.global.AEB_ROOT ? String($.global.AEB_ROOT) : new File($.fileName).parent.parent.fsName.replace(/\/g, "/");
    $.global.AEB_EXR = "crypto-uint-320x180.exr";
    $.evalFile(new File(R + "/jsx/lib.jsx"));
    AEB.runGroup({
        group: "1310-identifier-uint",
        needSrc: false,
        needExr: true,
        effects: [
            {
                key: "identifier", spec: { mn: ["IDentifier"], dn: "IDentifier" }, source: "EXR",
                presets: [{ name: "channel-objectid-id2", file: "identifier-objectid.ffx" }]
            }
        ]
    });
    $.global.AEB_EXR = null;
})();
$.global.AEB_RESULT;
