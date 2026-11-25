(function () {
  var R = $.global.AEB_ROOT ? String($.global.AEB_ROOT) : new File($.fileName).parent.parent.fsName.replace(/\/g, "/");
  var done = new File(R + "/json/u0-preset-setup.done");
  var out = { ok: false };
  try {
    app.beginUndoGroup("preset setup");
    var comp = app.project.items.addComp("Presets", 320, 180, 1, 2, 25);
    var exr = app.project.importFile(new ImportOptions(new File(R + "/media/crypto-320x180.exr")));
    var l1 = comp.layers.add(exr); l1.name = "EXR (EXtractoR, IDentifier, Cryptomatte)";
    var s = comp.layers.addSolid([0.8, 0.4, 0.2], "Solid (Lumetri)", 320, 180, 1, 2);
    app.endUndoGroup();
    comp.openInViewer();
    out = { ok: true, layers: comp.numLayers };
  } catch (e) { out = { ok: false, error: String(e) }; }
  done.encoding = "UTF-8"; done.open("w"); done.write(out.toSource ? out.toSource() : String(out.ok)); done.close();
})();
