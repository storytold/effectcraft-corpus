// lib.jsx: shared helpers of the importer sample block (ES3 / ExtendScript).
//
// Runs inside the current project. It never creates, opens or closes a project (the caller does that
// between groups), never calls undo or undo groups, never touches buttons, layer/mask parameters or
// custom-data parameters, and never sets popups whose name or items look like a file chooser.
// Everything is wrapped in try/catch: a failing variant is recorded and removed, the group goes on.
//
// Output (under AEB.ROOT):
//   json/<group>.json        per effect: resolved match name, the parameter dump of the defaults
//                            instance, and per variant what was set and what After Effects read back
//   json/<group>.log         progress log (flushed after every effect)
//   json/<group>.done        written last (done marker for run-jsx.ps1)
//   json/<group>-renders.json  batch.run ops that re-render every variant (fallback, one scripted call)
//   renders/<comp>.png       one raw frame per variant comp (saveFrameToPng, written asynchronously)

var AEB = {};
AEB.ROOT = ($.global.AEB_ROOT ? String($.global.AEB_ROOT) : new File($.fileName).parent.parent.fsName.replace(/\/g, "/"));
AEB.W = 320;
AEB.H = 180;
AEB.FPS = 25;
AEB.DUR = 2;
AEB.RENDER_T = 0.5;
AEB.MAX_POPUP_ITEMS = 40;
AEB.POPUP_GUARD = /LUT|Look|Browse|Custom|\.\.\./i; // never iterate these popups (file dialogs)

// ---------------------------------------------------------------- JSON and files
AEB.q = function (s) {
    s = String(s);
    var out = '"';
    for (var i = 0; i < s.length; i++) {
        var c = s.charAt(i), n = s.charCodeAt(i);
        if (c === '"') out += '\\"';
        else if (c === "\\") out += "\\\\";
        else if (c === "\n") out += "\\n";
        else if (c === "\r") out += "\\r";
        else if (c === "\t") out += "\\t";
        else if (n < 32 || n > 126) { var h = n.toString(16); while (h.length < 4) h = "0" + h; out += "\\u" + h; }
        else out += c;
    }
    return out + '"';
};
AEB.json = function (v, depth) {
    depth = depth || 0;
    if (depth > 40) return '"<depth>"';
    if (v === null || v === undefined) return "null";
    var t = typeof v;
    if (t === "number") return isFinite(v) ? String(v) : "null";
    if (t === "boolean") return v ? "true" : "false";
    if (t === "string") return AEB.q(v);
    if (t === "function") return '"<function>"';
    if (v instanceof Array) {
        var a = [];
        for (var i = 0; i < v.length; i++) a.push(AEB.json(v[i], depth + 1));
        return "[" + a.join(",") + "]";
    }
    var parts = [];
    for (var k in v) {
        if (v.hasOwnProperty(k)) parts.push(AEB.q(k) + ":" + AEB.json(v[k], depth + 1));
    }
    return "{" + parts.join(",") + "}";
};
AEB.mkdir = function (p) { var f = new Folder(p); if (!f.exists) f.create(); return f.exists; };
AEB.write = function (path, text) {
    var f = new File(path);
    f.encoding = "UTF-8";
    f.lineFeed = "Unix";
    if (!f.open("w")) throw new Error("cannot write " + path);
    f.write(text);
    f.close();
};
AEB.err = function (e) { try { return String(e) + (e && e.line ? " (line " + e.line + ")" : ""); } catch (x) { return "error"; } };

AEB.logLines = [];
AEB.log = function (s) { AEB.logLines.push(s); };
AEB.flush = function (state) {
    try { AEB.write(AEB.ROOT + "/json/" + state.group + ".log", AEB.logLines.join("\n") + "\n"); } catch (e) {}
    try { AEB.write(AEB.ROOT + "/json/" + state.group + ".json", AEB.json(state.out)); } catch (e2) {}
    try { AEB.write(AEB.ROOT + "/json/" + state.group + "-renders.json", AEB.json({ ops: state.renderOps })); } catch (e3) {}
};

// ---------------------------------------------------------------- project and sources
AEB.prepareFolders = function () {
    AEB.mkdir(AEB.ROOT);
    var subs = ["aep", "json", "renders", "media", "presets"];
    for (var i = 0; i < subs.length; i++) AEB.mkdir(AEB.ROOT + "/" + subs[i]);
};
AEB.setupProject = function () {
    var p = app.project, w = [];
    try { p.bitsPerChannel = 32; } catch (e1) { w.push("bitsPerChannel: " + AEB.err(e1)); }
    try { p.workingSpace = "None"; } catch (e2) { w.push("workingSpace: " + AEB.err(e2)); }
    try { p.linearBlending = false; } catch (e3) { w.push("linearBlending: " + AEB.err(e3)); }
    var s = {};
    try { s.bitsPerChannel = p.bitsPerChannel; } catch (e4) {}
    try { s.workingSpace = p.workingSpace; } catch (e5) {}
    try { s.linearBlending = p.linearBlending; } catch (e6) {}
    s.warnings = w;
    return s;
};
AEB.findItem = function (name) {
    for (var i = 1; i <= app.project.numItems; i++) if (app.project.item(i).name === name) return app.project.item(i);
    return null;
};
// SRC: a 320x180 test card built from solids only (no footage): a horizontal black-to-white ramp,
// six 40x40 colour squares and a white 30x30 square moving left to right over the 2 s.
AEB.makeSrc = function () {
    var old = AEB.findItem("SRC");
    if (old) return old;
    var c = app.project.items.addComp("SRC", AEB.W, AEB.H, 1, AEB.DUR, AEB.FPS);
    var bg = c.layers.addSolid([0.5, 0.5, 0.5], "src-ramp", AEB.W, AEB.H, 1, AEB.DUR);
    var r = bg.property("ADBE Effect Parade").addProperty("ADBE Ramp");
    r.property(1).setValue([0, 90]);
    r.property(2).setValue([0, 0, 0, 1]);
    r.property(3).setValue([320, 90]);
    r.property(4).setValue([1, 1, 1, 1]);
    var cols = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [0, 1, 1], [1, 0, 1]];
    for (var i = 0; i < cols.length; i++) {
        var s = c.layers.addSolid(cols[i], "src-sq" + (i + 1), 40, 40, 1, AEB.DUR);
        s.property("ADBE Transform Group").property("ADBE Position").setValue([30 + i * 52, 45]);
    }
    var m = c.layers.addSolid([1, 1, 1], "src-move", 30, 30, 1, AEB.DUR);
    var pos = m.property("ADBE Transform Group").property("ADBE Position");
    pos.setValueAtTime(0, [20, 130]);
    pos.setValueAtTime(AEB.DUR, [300, 130]);
    pos.valueAtTime(1, false); // read once so the first key's speed is written (corpus lesson 3)
    return c;
};
AEB.importExr = function () {
    var exrName = $.global.AEB_EXR ? String($.global.AEB_EXR) : "crypto-320x180.exr";
    var old = AEB.findItem(exrName);
    if (old) return old;
    var f = new File(AEB.ROOT + "/media/" + exrName);
    if (!f.exists) throw new Error("missing " + f.fsName);
    return app.project.importFile(new ImportOptions(f));
};

// ---------------------------------------------------------------- effects and properties
AEB.listEffects = function () {
    var out = [];
    try {
        for (var i = 0; i < app.effects.length; i++) {
            var e = app.effects[i];
            out.push({ displayName: e.displayName, matchName: e.matchName, category: e.category, version: e.version });
        }
    } catch (x) {}
    return out;
};
// spec: { mn: [candidate match names], dn: display name }. Returns the app.effects entry or null.
AEB.resolve = function (spec, all) {
    var i, j;
    for (j = 0; j < spec.mn.length; j++)
        for (i = 0; i < all.length; i++) if (all[i].matchName === spec.mn[j]) return all[i];
    if (spec.dn)
        for (i = 0; i < all.length; i++) if (String(all[i].displayName).toLowerCase() === spec.dn.toLowerCase()) return all[i];
    return null;
};
AEB.pvtName = function (t) {
    var names = ["NO_VALUE", "ThreeD_SPATIAL", "ThreeD", "TwoD_SPATIAL", "TwoD", "OneD", "COLOR", "CUSTOM_VALUE",
        "MARKER", "LAYER_INDEX", "MASK_INDEX", "SHAPE", "TEXT_DOCUMENT"];
    for (var i = 0; i < names.length; i++) {
        try { if (t === PropertyValueType[names[i]]) return names[i]; } catch (e) {}
    }
    return String(t);
};
AEB.ptName = function (t) {
    if (t === PropertyType.PROPERTY) return "PROPERTY";
    if (t === PropertyType.INDEXED_GROUP) return "INDEXED_GROUP";
    if (t === PropertyType.NAMED_GROUP) return "NAMED_GROUP";
    return String(t);
};
AEB.isInt = function (v) { return typeof v === "number" && Math.floor(v) === v; };
// kind: group | novalue | custom | layer | mask | color | point2 | point3 | checkbox | popup | popupish | slider | other
AEB.kind = function (p) {
    if (p.propertyType !== PropertyType.PROPERTY) return "group";
    var t = p.propertyValueType;
    if (t === PropertyValueType.NO_VALUE) return "novalue";
    if (t === PropertyValueType.CUSTOM_VALUE) return "custom";
    if (t === PropertyValueType.LAYER_INDEX) return "layer";
    if (t === PropertyValueType.MASK_INDEX) return "mask";
    if (t === PropertyValueType.COLOR) return "color";
    if (t === PropertyValueType.TwoD_SPATIAL || t === PropertyValueType.TwoD) return "point2";
    if (t === PropertyValueType.ThreeD_SPATIAL || t === PropertyValueType.ThreeD) return "point3";
    if (t !== PropertyValueType.OneD) return "other";
    var dd = false;
    try { dd = p.isDropdownEffect; } catch (e) {}
    if (dd) return "popup";
    var v = null, lo = null, hi = null;
    try { v = p.value; } catch (e1) {}
    try { if (p.hasMin) lo = p.minValue; } catch (e2) {}
    try { if (p.hasMax) hi = p.maxValue; } catch (e3) {}
    if (lo === 0 && hi === 1 && AEB.isInt(v)) return "checkbox";
    if (lo === 1 && hi !== null && AEB.isInt(hi) && hi <= 64 && AEB.isInt(v)) return "popupish";
    return "slider";
};
AEB.safe = function (f) { try { return f(); } catch (e) { return undefined; } };
AEB.dumpProp = function (p, path, section, depth) {
    var d = { path: path, name: AEB.safe(function () { return p.name; }), matchName: AEB.safe(function () { return p.matchName; }),
        propertyType: AEB.ptName(p.propertyType), kind: AEB.kind(p), section: section };
    if (p.propertyType === PropertyType.PROPERTY) {
        d.propertyValueType = AEB.pvtName(p.propertyValueType);
        d.hasMin = AEB.safe(function () { return p.hasMin; });
        d.hasMax = AEB.safe(function () { return p.hasMax; });
        if (d.hasMin) d.minValue = AEB.safe(function () { return p.minValue; });
        if (d.hasMax) d.maxValue = AEB.safe(function () { return p.maxValue; });
        if (d.kind !== "novalue" && d.kind !== "custom") d.value = AEB.safe(function () { return p.value; });
        d.isDropdownEffect = AEB.safe(function () { return p.isDropdownEffect; });
        d.propertyParameters = AEB.safe(function () { return p.propertyParameters; });
        d.canVaryOverTime = AEB.safe(function () { return p.canVaryOverTime; });
        d.canSetExpression = AEB.safe(function () { return p.canSetExpression; });
        d.isSpatial = AEB.safe(function () { return p.isSpatial; });
        d.unitsText = AEB.safe(function () { return p.unitsText; });
        d.numKeys = AEB.safe(function () { return p.numKeys; });
        d.expression = AEB.safe(function () { return p.expression; });
        d.expressionEnabled = AEB.safe(function () { return p.expressionEnabled; });
        d.isModified = AEB.safe(function () { return p.isModified; });
    } else if (depth < 6) {
        d.children = [];
        for (var i = 1; i <= p.numProperties; i++) d.children.push(AEB.dumpProp(p.property(i), path.concat([i]), section, depth + 1));
    }
    return d;
};
AEB.dumpEffect = function (fx) {
    var d = { matchName: fx.matchName, name: fx.name, numProperties: fx.numProperties,
        enabled: AEB.safe(function () { return fx.enabled; }), props: [] };
    var section = "";
    for (var i = 1; i <= fx.numProperties; i++) {
        var p = fx.property(i);
        if (p.propertyType === PropertyType.PROPERTY && p.propertyValueType === PropertyValueType.NO_VALUE) section = p.name;
        d.props.push(AEB.dumpProp(p, [i], section, 0));
    }
    return d;
};
// Settable leaves of an effect (top level only; the Compositing Options group is left alone).
AEB.leaves = function (dump) {
    var out = [];
    for (var i = 0; i < dump.props.length; i++) {
        var p = dump.props[i];
        if (p.kind === "group" || p.kind === "novalue" || p.kind === "custom" || p.kind === "layer" || p.kind === "mask" || p.kind === "other") continue;
        out.push(p);
    }
    return out;
};
AEB.r3 = function (v) { return Math.round(v * 1000) / 1000; };
// A distinctive value for leaf p (k = a running number so every parameter gets its own value).
AEB.distinct = function (p, k) {
    var v = p.value;
    if (p.kind === "checkbox") return v ? 0 : 1;
    if (p.kind === "color") return [AEB.r3((0.15 + 0.07 * k) % 1), 0.55, 0.85, 1];
    if (p.kind === "point2") return [40 + (k * 37) % 240, 30 + (k * 23) % 120];
    if (p.kind === "point3") return [40 + (k * 37) % 240, 30 + (k * 23) % 120, 10 + k];
    if (typeof v !== "number") return v;
    var lo = (p.hasMin && typeof p.minValue === "number") ? p.minValue : -1e6;
    var hi = (p.hasMax && typeof p.maxValue === "number") ? p.maxValue : 1e6;
    var up = hi - v, down = v - lo;
    var dir = up >= down ? 1 : -1;
    var room = dir > 0 ? up : down;
    var mag;
    if (hi - lo <= 2) mag = room * (0.3 + 0.05 * (k % 5));
    else mag = Math.min(room * 0.37, 10 + 3 * (k % 10));
    return AEB.r3(v + dir * mag);
};
AEB.propAt = function (fx, path) {
    var p = fx;
    for (var i = 0; i < path.length; i++) p = p.property(path[i]);
    return p;
};
AEB.readback = function (p) {
    var r = {};
    try { r.value = p.value; } catch (e) {}
    try { if (p.numKeys > 0) { r.keys = []; for (var i = 1; i <= p.numKeys; i++) r.keys.push([p.keyTime(i), p.keyValue(i)]); } } catch (e2) {}
    try { if (p.expression) { r.expression = p.expression; r.expressionEnabled = p.expressionEnabled; r.expressionError = p.expressionError; } } catch (e3) {}
    return r;
};

// ---------------------------------------------------------------- variants
// A variant: { name, sets: [{path, value}], keys: [{path, t0, v0, t1, v1}], exprs: [{path, text}], preset: file }
AEB.planVariants = function (fxc, dump) {
    var L = AEB.leaves(dump), V = [], i, k = 0, p;
    var settable = [], sliders = [], checks = [], popups = [], multis = [];
    for (i = 0; i < L.length; i++) {
        p = L[i];
        if (p.kind === "popup" || p.kind === "popupish") popups.push(p);
        else { settable.push(p); if (p.kind === "slider") sliders.push(p); if (p.kind === "checkbox") checks.push(p); if (p.kind === "color" || p.kind === "point2" || p.kind === "point3") multis.push(p); }
    }
    var setsFor = function (list) { var s = []; for (var j = 0; j < list.length; j++) s.push({ path: list[j].path, value: AEB.distinct(list[j], k++) }); return s; };
    if (settable.length) V.push({ name: "set-all", sets: setsFor(settable) });
    // one variant per section (NO_VALUE marker) when there is more than one
    var secs = [], bySec = {};
    for (i = 0; i < settable.length; i++) {
        var s = settable[i].section || "";
        if (!bySec.hasOwnProperty("s_" + s)) { bySec["s_" + s] = []; secs.push(s); }
        bySec["s_" + s].push(settable[i]);
    }
    if (secs.length > 1) for (i = 0; i < secs.length; i++) V.push({ name: "sec-" + AEB.slug(secs[i] || "top"), sets: setsFor(bySec["s_" + secs[i]]) });
    var mins = [], maxs = [];
    for (i = 0; i < sliders.length; i++) {
        p = sliders[i];
        if (p.hasMin && typeof p.minValue === "number") mins.push({ path: p.path, value: p.minValue });
        if (p.hasMax && typeof p.maxValue === "number") maxs.push({ path: p.path, value: p.maxValue });
    }
    if (mins.length) V.push({ name: "min", sets: mins });
    if (maxs.length) V.push({ name: "max", sets: maxs });
    if (checks.length) { var cs = []; for (i = 0; i < checks.length; i++) cs.push({ path: checks[i].path, value: checks[i].value ? 0 : 1 }); V.push({ name: "chk-toggled", sets: cs }); }
    for (i = 0; i < popups.length; i++) {
        p = popups[i];
        var guard = AEB.POPUP_GUARD.test(String(p.name)) || (fxc.noTouch && fxc.noTouch.test(String(p.name)));
        if (!guard && p.propertyParameters && p.propertyParameters.length) {
            for (var g = 0; g < p.propertyParameters.length; g++) if (AEB.POPUP_GUARD.test(String(p.propertyParameters[g]))) guard = true;
        }
        if (guard) { V.push({ name: "skip-pop" + p.path.join("_"), skipped: "popup guarded (file chooser risk): " + p.name }); continue; }
        var n = (p.hasMax && typeof p.maxValue === "number") ? Math.min(p.maxValue, AEB.MAX_POPUP_ITEMS) : 0;
        for (var it = 1; it <= n; it++) if (it !== p.value) V.push({ name: "pop" + p.path.join("_") + "-" + it, sets: [{ path: p.path, value: it }] });
    }
    var keys = [], exprs = [];
    for (i = 0; i < sliders.length && keys.length < 1; i++) if (sliders[i].canVaryOverTime) keys.push({ path: sliders[i].path, t0: 0, v0: sliders[i].value, t1: 1, v1: AEB.distinct(sliders[i], k++) });
    for (i = 0; i < multis.length && keys.length < 2; i++) if (multis[i].canVaryOverTime) keys.push({ path: multis[i].path, t0: 0, v0: multis[i].value, t1: 1, v1: AEB.distinct(multis[i], k++) });
    if (keys.length) V.push({ name: "keys", keys: keys });
    for (i = 0; i < sliders.length && exprs.length < 1; i++) if (sliders[i].canSetExpression) exprs.push({ path: sliders[i].path, text: String(AEB.distinct(sliders[i], k++)) });
    for (i = 0; i < multis.length && exprs.length < 2; i++) if (multis[i].canSetExpression) exprs.push({ path: multis[i].path, text: "value" });
    if (exprs.length) V.push({ name: "expr", exprs: exprs });
    if (fxc.extra) for (i = 0; i < fxc.extra.length; i++) V.push(fxc.extra[i]);
    if (fxc.presets) for (i = 0; i < fxc.presets.length; i++) V.push({ name: "preset-" + fxc.presets[i].name, preset: fxc.presets[i].file, optional: true });
    return V;
};
AEB.slug = function (s) { return String(s).replace(/[^A-Za-z0-9]+/g, "-").replace(/^-+|-+$/g, "").toLowerCase().substr(0, 24); };
AEB.pad2 = function (n) { return n < 10 ? "0" + n : String(n); };

AEB.newComp = function (state, name, src) {
    var c = app.project.items.addComp(name, AEB.W, AEB.H, 1, AEB.DUR, AEB.FPS);
    var l = c.layers.add(src);
    try { l.name = "SRC"; } catch (e) {}
    return { comp: c, layer: l };
};
AEB.render = function (state, comp) {
    var path = AEB.ROOT + "/renders/" + comp.name + ".png";
    state.renderOps.push({ operation: "render.frame", args: { comp: comp.name, time: AEB.RENDER_T, outPath: path } });
    try { comp.saveFrameToPng(AEB.RENDER_T, new File(path)); return path; } catch (e) { return "render failed: " + AEB.err(e); }
};
// Apply a planned variant to a fresh effect instance on the comp's layer.
AEB.applyVariant = function (fxc, layer, v, rec) {
    var parade = layer.property("ADBE Effect Parade");
    var fx;
    if (v.preset) {
        var pf = new File(AEB.ROOT + "/presets/" + v.preset);
        if (!pf.exists) throw new Error("PRESET_MISSING " + v.preset);
        layer.applyPreset(pf);
        fx = parade.property(parade.numProperties);
        rec.presetApplied = v.preset;
        rec.dump = AEB.dumpEffect(fx);
        return fx;
    }
    for (var pre = 0; fxc.pre && pre < fxc.pre.length; pre++) parade.addProperty(fxc.pre[pre]);
    parade.addProperty(fxc.resolvedMatchName);
    fx = parade.property(parade.numProperties);
    var i, p, r;
    rec.sets = [];
    for (i = 0; v.sets && i < v.sets.length; i++) {
        r = { path: v.sets[i].path, requested: v.sets[i].value };
        try {
            p = AEB.propAt(fx, v.sets[i].path);
            r.name = p.name; r.matchName = p.matchName;
            p.setValue(v.sets[i].value);
            r.readback = AEB.readback(p).value;
        } catch (e) { r.error = AEB.err(e); }
        rec.sets.push(r);
    }
    rec.keys = [];
    for (i = 0; v.keys && i < v.keys.length; i++) {
        r = { path: v.keys[i].path };
        try {
            p = AEB.propAt(fx, v.keys[i].path);
            r.name = p.name; r.matchName = p.matchName;
            p.setValueAtTime(v.keys[i].t0, v.keys[i].v0);
            p.setValueAtTime(v.keys[i].t1, v.keys[i].v1);
            p.valueAtTime(1, false); // corpus lesson 3
            r.readback = AEB.readback(p);
        } catch (e2) { r.error = AEB.err(e2); }
        rec.keys.push(r);
    }
    rec.exprs = [];
    for (i = 0; v.exprs && i < v.exprs.length; i++) {
        r = { path: v.exprs[i].path, text: v.exprs[i].text };
        try {
            p = AEB.propAt(fx, v.exprs[i].path);
            r.name = p.name; r.matchName = p.matchName;
            p.expression = v.exprs[i].text;
            r.readback = AEB.readback(p);
        } catch (e3) { r.error = AEB.err(e3); }
        rec.exprs.push(r);
    }
    // extra variants may name parameters instead of paths: { byName: [[name, value], ...] }
    for (i = 0; v.byName && i < v.byName.length; i++) {
        r = { name: v.byName[i][0], requested: v.byName[i][1] };
        try {
            p = fx.property(v.byName[i][0]);
            r.matchName = p.matchName;
            p.setValue(v.byName[i][1]);
            r.readback = AEB.readback(p).value;
        } catch (e4) { r.error = AEB.err(e4); }
        rec.sets.push(r);
    }
    return fx;
};

AEB.runEffect = function (state, fxc, all) {
    var res = { key: fxc.key, spec: fxc.spec, source: fxc.source, variants: [] };
    state.out.effects.push(res);
    var hit = AEB.resolve(fxc.spec, all);
    if (!hit) { res.skipped = "not in app.effects (plug-in not installed or not loaded)"; AEB.log("SKIP " + fxc.key + ": " + res.skipped); return; }
    res.resolved = hit;
    fxc.resolvedMatchName = hit.matchName;
    var src = fxc.source === "EXR" ? state.exr : state.src;
    if (!src) { res.skipped = "source " + fxc.source + " missing"; AEB.log("SKIP " + fxc.key + ": " + res.skipped); return; }
    var n = 0;
    // 00: defaults (the first instance in the project: it carries the parameter definitions)
    var base = AEB.newComp(state, fxc.key + "-00-defaults", src);
    var rec0 = { comp: base.comp.name, name: "defaults" };
    try {
        var fx0 = AEB.applyVariant(fxc, base.layer, { name: "defaults" }, rec0);
        res.dump = AEB.dumpEffect(fx0);
        rec0.render = AEB.render(state, base.comp);
    } catch (e0) {
        res.error = "defaults failed: " + AEB.err(e0);
        AEB.log("FAIL " + fxc.key + " defaults: " + res.error);
        try { base.comp.remove(); } catch (x) {}
        return;
    }
    res.variants.push(rec0);
    var plan = AEB.planVariants(fxc, res.dump);
    for (var i = 0; i < plan.length; i++) {
        var v = plan[i];
        if (v.skipped) { res.variants.push({ name: v.name, skipped: v.skipped }); continue; }
        n++;
        var cname = fxc.key + "-" + AEB.pad2(n) + "-" + v.name;
        var rec = { comp: cname, name: v.name };
        var cl = null;
        try {
            cl = AEB.newComp(state, cname, src);
            AEB.applyVariant(fxc, cl.layer, v, rec);
            rec.render = AEB.render(state, cl.comp);
        } catch (e) {
            rec.error = AEB.err(e);
            if (String(e).indexOf("PRESET_MISSING") >= 0) rec.skipped = "preset not made yet";
            try { if (cl) cl.comp.remove(); } catch (x2) {}
            rec.removed = true;
        }
        res.variants.push(rec);
    }
    AEB.log("OK " + fxc.key + " (" + hit.matchName + "): " + res.variants.length + " variants");
};

// cfg: { group, needSrc, needExr, effects: [fxc...] }
// fxc: { key, spec: {mn: [...], dn}, source: "SRC"|"EXR", noTouch: /re/, pre: [match names added before],
//        extra: [variants], presets: [{name, file}] }
AEB.runGroup = function (cfg) {
    var state = { group: cfg.group, renderOps: [], out: { group: cfg.group, started: new Date().toString(), ae: {}, effects: [], errors: [] } };
    $.global.AEB_RESULT = null;
    app.beginSuppressDialogs();
    try {
        AEB.prepareFolders();
        try { var df = new File(AEB.ROOT + "/json/" + cfg.group + ".done"); if (df.exists) df.remove(); } catch (x0) {}
        state.out.ae = { version: app.version, buildName: AEB.safe(function () { return app.buildName; }), language: AEB.safe(function () { return String(app.isoLanguage); }) };
        state.out.project = AEB.setupProject();
        var all = AEB.listEffects();
        state.out.appEffectsCount = all.length;
        if (cfg.needSrc) { try { state.src = AEB.makeSrc(); } catch (e1) { state.out.errors.push("SRC: " + AEB.err(e1)); } }
        if (cfg.needExr) { try { state.exr = AEB.importExr(); } catch (e2) { state.out.errors.push("EXR: " + AEB.err(e2)); } }
        for (var i = 0; i < cfg.effects.length; i++) {
            try { AEB.runEffect(state, cfg.effects[i], all); }
            catch (e3) { state.out.errors.push(cfg.effects[i].key + ": " + AEB.err(e3)); AEB.log("FAIL " + cfg.effects[i].key + ": " + AEB.err(e3)); }
            AEB.flush(state);
        }
    } catch (e) {
        state.out.errors.push("group: " + AEB.err(e));
    }
    state.out.finished = new Date().toString();
    AEB.flush(state);
    try { app.endSuppressDialogs(false); } catch (x) {}
    var comps = 0, skipped = [], failed = 0, opt = 0;
    for (var j = 0; j < state.out.effects.length; j++) {
        var ef = state.out.effects[j];
        if (ef.skipped || ef.error) skipped.push(ef.key + ": " + (ef.skipped || ef.error));
        for (var k = 0; k < ef.variants.length; k++) {
            var vr = ef.variants[k];
            if (vr.removed) { if (vr.skipped) opt++; else failed++; } else if (!vr.skipped) comps++;
        }
    }
    var summary = { group: cfg.group, comps: comps, renders: state.renderOps.length, failedVariants: failed, missingPresets: opt,
        skippedEffects: skipped, errors: state.out.errors, json: AEB.ROOT + "/json/" + cfg.group + ".json" };
    try { AEB.write(AEB.ROOT + "/json/" + cfg.group + ".done", AEB.json(summary)); } catch (x3) {}
    $.global.AEB_RESULT = AEB.json(summary);
    return $.global.AEB_RESULT;
};
