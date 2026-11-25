# Renders a small multilayer EXR with real Cryptomatte, Object/Material Index and Z passes (Cycles),
# for After Effects samples of Cryptomatte, EXtractoR and IDentifier. Our own scene, no third-party assets.
import bpy, sys, os
out_dir = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 32
sc.cycles.device = 'CPU'
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 320, 180, 100
sc.frame_start = sc.frame_end = 1
def mat(name, rgb, index):
    m = bpy.data.materials.new(name); m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*rgb, 1)
    m.pass_index = index
    return m
def add(op, name, loc, m, index, **kw):
    op(location=loc, **kw); o = bpy.context.active_object; o.name = name
    o.data.materials.append(m); o.pass_index = index; return o
add(bpy.ops.mesh.primitive_plane_add, "floor", (0, 0, 0), mat("grey_mat", (0.5, 0.5, 0.5), 4), 4, size=12)
add(bpy.ops.mesh.primitive_cube_add, "box_red", (-2.2, 0, 1), mat("red_paint", (0.8, 0.05, 0.05), 1), 1, size=1.6)
add(bpy.ops.mesh.primitive_uv_sphere_add, "ball_green", (0, 0, 1), mat("green_paint", (0.05, 0.7, 0.1), 2), 2, radius=0.9)
add(bpy.ops.mesh.primitive_cone_add, "cone_blue", (2.2, 0, 1), mat("blue_paint", (0.05, 0.15, 0.8), 3), 3, radius1=0.9, depth=1.8)
bpy.ops.object.camera_add(location=(0, -8, 4.5), rotation=(1.1, 0, 0)); sc.camera = bpy.context.active_object
bpy.ops.object.light_add(type='SUN', location=(3, -3, 6)); bpy.context.active_object.data.energy = 4
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[1].default_value = 0.3
vl = sc.view_layers[0]
vl.use_pass_z = True
vl.use_pass_object_index = True
vl.use_pass_material_index = True
vl.use_pass_cryptomatte_object = True
vl.use_pass_cryptomatte_material = True
vl.use_pass_cryptomatte_asset = True
vl.pass_cryptomatte_depth = 2
r = sc.render.image_settings
r.file_format = 'OPEN_EXR_MULTILAYER'; r.color_depth = '32'; r.exr_codec = 'ZIP'
sc.render.filepath = os.path.join(out_dir, "id-scene-320x180.exr")
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, "id-scene.blend"))
print("WROTE", sc.render.filepath)
