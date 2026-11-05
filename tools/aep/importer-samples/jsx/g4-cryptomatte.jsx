// g4-cryptomatte.jsx: importer samples for issue #3107 (Cryptomatte plug-in). Run in a fresh empty
// project; save it afterwards as aep/1400-cryptomatte.aep.
// Source: media/crypto-320x180.exr, a synthetic EXR made by tools/make_crypto_exr.py (layers
// CryptoObject and CryptoMaterial, objects box_red, disc_green, tri_blue, ramp_hdr). The fresh
// default, every Output item and Selection Mode come from scripting; the layer choice and a picked
// selection live in the plug-in's Settings data, which only its UI sets: they come from the user's
// presets (skipped while missing).
(function () {
    var R = $.global.AEB_ROOT ? String($.global.AEB_ROOT) : new File($.fileName).parent.parent.fsName.replace(/\/g, "/");
    $.evalFile(new File(R + "/jsx/lib.jsx"));
    AEB.runGroup({
        group: "1400-cryptomatte",
        needSrc: false,
        needExr: true,
        effects: [
            {
                key: "crypto", spec: { mn: ["Cryptomatte"], dn: "Cryptomatte" }, source: "EXR",
                presets: [
                    { name: "object-box", file: "crypto-object-box.ffx" },
                    { name: "material-paint", file: "crypto-material-paint.ffx" }
                ]
            }
        ]
    });
})();
$.global.AEB_RESULT;
