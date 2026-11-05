// g2-lumetri.jsx: importer samples for issue #3111 (Lumetri Color). Run in a fresh empty project; save
// it afterwards as aep/1200-lumetri.aep.
// The generic plan gives: defaults, set-all, one variant per section (Basic Correction, Creative,
// Curves, Color Wheels, HSL Secondary, Vignette and their sub-sections, as After Effects marks them),
// valid min / max of every slider, checkboxes toggled, every popup item once, a keyed slider and
// colour, and an expression. The Input LUT and Look popups are never iterated (one of their items is
// "Browse...", a file dialog); LUTs and the curves come from the user's presets (presets/*.ffx, made
// by hand, see user-presets.md) and are skipped cleanly while a preset is missing.
(function () {
    var R = $.global.AEB_ROOT ? String($.global.AEB_ROOT) : new File($.fileName).parent.parent.fsName.replace(/\/g, "/");
    $.evalFile(new File(R + "/jsx/lib.jsx"));
    AEB.runGroup({
        group: "1200-lumetri",
        needSrc: true,
        needExr: false,
        effects: [
            {
                key: "lumetri", spec: { mn: ["ADBE Lumetri"], dn: "Lumetri Color" }, source: "SRC",
                noTouch: /LUT|Look|Browse/i,
                presets: [
                    { name: "input-lut", file: "lumetri-input-lut.ffx" },
                    { name: "look-lut", file: "lumetri-look-lut.ffx" },
                    { name: "curves-rgb", file: "lumetri-curves-rgb.ffx" },
                    { name: "curves-huesat", file: "lumetri-curves-huesat.ffx" },
                    { name: "wheels", file: "lumetri-wheels.ffx" }
                ]
            }
        ]
    });
})();
$.global.AEB_RESULT;
