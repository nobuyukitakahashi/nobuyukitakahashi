import bpy
import math
import os
import random
from mathutils import Vector

# ==============================================================================
# Paths
# ==============================================================================
WORKSPACE = "/Users/takahashinobuyuki/Library/CloudStorage/GoogleDrive-nobuyukitakahashi@gmail.com/マイドライブ/git/nobuyukitakahashi"
FINAL_DIR = os.path.join(WORKSPACE, "02_Creative_Dept/blender/final_outputs")
DELIVERY_DIR = os.path.join(WORKSPACE, "04_Delivery_Dept/outputs/blender")
os.makedirs(FINAL_DIR, exist_ok=True)
os.makedirs(DELIVERY_DIR, exist_ok=True)

OUT_PNG = os.path.join(FINAL_DIR, "cvn_gold_logo.png")
OUT_BLEND = os.path.join(FINAL_DIR, "cvn_gold_logo.blend")
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Black.ttf"

# ==============================================================================
# 1. Clean Scene (Preserve UI layout & user preferences)
# ==============================================================================
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for col in list(bpy.data.collections):
    bpy.data.collections.remove(col)
for mesh in list(bpy.data.meshes):
    bpy.data.meshes.remove(mesh)
for curve in list(bpy.data.curves):
    bpy.data.curves.remove(curve)
for light in list(bpy.data.lights):
    bpy.data.lights.remove(light)
for cam in list(bpy.data.cameras):
    bpy.data.cameras.remove(cam)
for mat in list(bpy.data.materials):
    bpy.data.materials.remove(mat)
for world in list(bpy.data.worlds):
    bpy.data.worlds.remove(world)
for ng in list(bpy.data.node_groups):
    bpy.data.node_groups.remove(ng)

# ==============================================================================
# 2. Render Engine & GPU (Cycles + Metal)
# ==============================================================================
scene.render.engine = 'CYCLES'
cycles_prefs = bpy.context.preferences.addons.get('cycles')
if cycles_prefs:
    cp = cycles_prefs.preferences
    cp.compute_device_type = 'METAL'
    cp.get_devices()
    for d in cp.devices:
        d.use = (d.type == 'METAL')
scene.cycles.device = 'GPU'
scene.cycles.samples = 160
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.01
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 6
scene.cycles.glossy_bounces = 4
scene.cycles.diffuse_bounces = 3
scene.cycles.transmission_bounces = 2
scene.cycles.transparent_max_bounces = 4

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '8'

# Color Management: AgX Punchy for rich, jewel-like 24K gold tones
scene.view_settings.view_transform = 'AgX'
try:
    scene.view_settings.look = 'AgX - Punchy'
except Exception:
    try:
        scene.view_settings.look = 'AgX - High Contrast'
    except Exception:
        scene.view_settings.look = 'None'
scene.view_settings.exposure = -0.55
scene.view_settings.gamma = 1.0

# ==============================================================================
# 3. Helper: Find node by type
# ==============================================================================
def find_node_by_type(node_tree, node_type):
    for n in node_tree.nodes:
        if n.type == node_type:
            return n
    return None

# ==============================================================================
# 4. Materials (Saturated 24K Jewel Gold + Seamless Infinite Obsidian Floor)
# ==============================================================================
def create_jewel_gold_material(
    name="Jewel24KGold",
    base_rgb=(0.96, 0.52, 0.045),
    edge_rgb=(1.0, 0.80, 0.22),
    rough_min=0.045,
    rough_max=0.125,
    bump_str=0.005,
):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links

    bsdf = find_node_by_type(nt, 'BSDF_PRINCIPLED')

    # Rich 24K gold color with warm champagne grazing angle shift
    lw = nodes.new('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.32
    lw.location = (-600, 260)

    mix_col = nodes.new('ShaderNodeMix')
    mix_col.data_type = 'RGBA'
    mix_col.inputs['A'].default_value = (*base_rgb, 1.0)
    mix_col.inputs['B'].default_value = (*edge_rgb, 1.0)
    mix_col.location = (-320, 260)
    links.new(lw.outputs['Facing'], mix_col.inputs['Factor'])
    links.new(mix_col.outputs['Result'], bsdf.inputs['Base Color'])

    # Ultra-fine horizontal brushed satin micro-grain
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-960, -140)

    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (4.0, 28.0, 28.0)
    mapping.location = (-760, -140)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 55.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.50
    noise.location = (-520, -140)
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])

    map_rough = nodes.new('ShaderNodeMapRange')
    map_rough.inputs['From Min'].default_value = 0.25
    map_rough.inputs['From Max'].default_value = 0.75
    map_rough.inputs['To Min'].default_value = rough_min
    map_rough.inputs['To Max'].default_value = rough_max
    map_rough.location = (-280, -80)
    links.new(noise.outputs['Fac'], map_rough.inputs['Value'])
    links.new(map_rough.outputs['Result'], bsdf.inputs['Roughness'])

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = bump_str
    bump.inputs['Distance'].default_value = 0.0015
    bump.location = (-260, -280)
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    bsdf.inputs['Metallic'].default_value = 1.0
    if 'Anisotropic' in bsdf.inputs:
        bsdf.inputs['Anisotropic'].default_value = 0.28
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.30
    if 'Coat Roughness' in bsdf.inputs:
        bsdf.inputs['Coat Roughness'].default_value = 0.02
    if 'Coat IOR' in bsdf.inputs:
        bsdf.inputs['Coat IOR'].default_value = 1.65

    return mat


def create_infinite_obsidian_floor():
    """Pure black mirror floor: reflects only the gold logo right underneath, zero visible horizon!"""
    mat = bpy.data.materials.new(name="InfiniteObsidianFloor")
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (520, 0)

    # Mix glossy mirror (near logo) with pure black Diffuse(0) outside tight ellipse
    mix_s = nodes.new('ShaderNodeMixShader')
    mix_s.location = (280, 0)
    links.new(mix_s.outputs['Shader'], out.inputs['Surface'])

    black_bsdf = nodes.new('ShaderNodeBsdfDiffuse')
    black_bsdf.inputs['Color'].default_value = (0.0, 0.0, 0.0, 1.0)
    black_bsdf.location = (0, 120)
    links.new(black_bsdf.outputs['BSDF'], mix_s.inputs[1])

    glossy = nodes.new('ShaderNodeBsdfGlossy')
    glossy.inputs['Color'].default_value = (0.45, 0.40, 0.32, 1.0)
    glossy.location = (0, -80)
    links.new(glossy.outputs['BSDF'], mix_s.inputs[2])

    # Elliptical reflection mask centered around the logo footprint (zero horizon line!)
    tc = nodes.new('ShaderNodeTexCoord')
    tc.location = (-980, 0)

    map_ell = nodes.new('ShaderNodeMapping')
    map_ell.inputs['Location'].default_value = (0.0, 0.45, 0.0)
    map_ell.inputs['Scale'].default_value = (0.36, 0.62, 1.0)
    map_ell.location = (-740, 160)
    links.new(tc.outputs['Object'], map_ell.inputs['Vector'])

    vlen = nodes.new('ShaderNodeVectorMath')
    vlen.operation = 'LENGTH'
    vlen.location = (-500, 160)
    links.new(map_ell.outputs['Vector'], vlen.inputs[0])

    mask = nodes.new('ShaderNodeMapRange')
    mask.clamp = True
    mask.interpolation_type = 'SMOOTHERSTEP'
    mask.inputs['From Min'].default_value = 0.25
    mask.inputs['From Max'].default_value = 1.05
    mask.inputs['To Min'].default_value = 0.48
    mask.inputs['To Max'].default_value = 0.0
    mask.location = (-240, 200)
    links.new(vlen.outputs['Value'], mask.inputs['Value'])
    links.new(mask.outputs['Result'], mix_s.inputs['Fac'])

    # Micro floor roughness variation for natural luxury stone/glass sheen
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 7.5
    noise.inputs['Detail'].default_value = 5.0
    noise.inputs['Roughness'].default_value = 0.55
    noise.location = (-720, -160)
    links.new(tc.outputs['Object'], noise.inputs['Vector'])

    map_r = nodes.new('ShaderNodeMapRange')
    map_r.inputs['From Min'].default_value = 0.28
    map_r.inputs['From Max'].default_value = 0.72
    map_r.inputs['To Min'].default_value = 0.04
    map_r.inputs['To Max'].default_value = 0.11
    map_r.location = (-440, -160)
    links.new(noise.outputs['Fac'], map_r.inputs['Value'])
    links.new(map_r.outputs['Result'], glossy.inputs['Roughness'])

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.006
    bump.inputs['Distance'].default_value = 0.004
    bump.location = (-240, -280)
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], glossy.inputs['Normal'])

    return mat


def create_spark_material(name="GoldSpark", color=(1.0, 0.76, 0.22), strength=3.2):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()
    em = nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*color, 1.0)
    em.inputs['Strength'].default_value = strength
    out = nodes.new('ShaderNodeOutputMaterial')
    links.new(em.outputs['Emission'], out.inputs['Surface'])
    if hasattr(mat, 'cycles') and hasattr(mat.cycles, 'emission_sampling'):
        mat.cycles.emission_sampling = 'NONE'
    return mat


gold_main_mat = create_jewel_gold_material()
floor_mat = create_infinite_obsidian_floor()
# Dust stays below Streaks threshold (4.5) so it renders as soft golden bokeh embers, NOT distracting crosses!
dust_mat = create_spark_material("GoldDust", color=(1.0, 0.74, 0.20), strength=2.6)
# Hero glints sit right above Streaks threshold so ONLY the logo bevel peaks emit crisp star flares!
glint_mat = create_spark_material("HeroGlint", color=(1.0, 0.94, 0.72), strength=30.0)

# ==============================================================================
# 5. World Procedural Dark Luxury Studio (Pure Black BG + Sculpted Reflection Bands)
# ==============================================================================
world = bpy.data.worlds.new("LuxuryStudioWorld")
scene.world = world
world.use_nodes = True
wnt = world.node_tree
wnodes = wnt.nodes
wlinks = wnt.links
wnodes.clear()

w_out = wnodes.new('ShaderNodeOutputWorld')
w_out.location = (760, 0)

lp = wnodes.new('ShaderNodeLightPath')
lp.location = (220, 320)

mix_sh = wnodes.new('ShaderNodeMixShader')
mix_sh.location = (520, 0)
wlinks.new(lp.outputs['Is Camera Ray'], mix_sh.inputs['Fac'])
wlinks.new(mix_sh.outputs['Shader'], w_out.inputs['Surface'])

# Camera ray: pure deep luxury black
bg_cam = wnodes.new('ShaderNodeBackground')
bg_cam.inputs['Color'].default_value = (0.001, 0.001, 0.0015, 1.0)
bg_cam.inputs['Strength'].default_value = 1.0
bg_cam.location = (220, 140)
wlinks.new(bg_cam.outputs['Background'], mix_sh.inputs[2])

# Reflection ray: dark bronze-black void with crisp diagonal warm-gold light ribbons
# Masking lower hemisphere (Z < 0.08) prevents bright world bands from bleeding into the floor!
tc = wnodes.new('ShaderNodeTexCoord')
tc.location = (-1100, -160)

sep = wnodes.new('ShaderNodeSeparateXYZ')
sep.location = (-860, 40)
wlinks.new(tc.outputs['Generated'], sep.inputs['Vector'])

hemi_mask = wnodes.new('ShaderNodeMapRange')
hemi_mask.clamp = True
hemi_mask.inputs['From Min'].default_value = 0.02
hemi_mask.inputs['From Max'].default_value = 0.28
hemi_mask.inputs['To Min'].default_value = 0.0
hemi_mask.inputs['To Max'].default_value = 1.0
hemi_mask.location = (-600, 40)
wlinks.new(sep.outputs['Z'], hemi_mask.inputs['Value'])

mapping_w = wnodes.new('ShaderNodeMapping')
mapping_w.inputs['Rotation'].default_value = (math.radians(24), math.radians(-26), math.radians(38))
mapping_w.location = (-860, -220)
wlinks.new(tc.outputs['Generated'], mapping_w.inputs['Vector'])

wave = wnodes.new('ShaderNodeTexWave')
wave.wave_type = 'BANDS'
wave.bands_direction = 'DIAGONAL'
wave.wave_profile = 'SIN'
wave.inputs['Scale'].default_value = 2.6
wave.inputs['Distortion'].default_value = 0.0
wave.location = (-600, -220)
wlinks.new(mapping_w.outputs['Vector'], wave.inputs['Vector'])

ramp = wnodes.new('ShaderNodeValToRGB')
ramp.location = (-340, -220)
cr = ramp.color_ramp
cr.elements[0].position = 0.0
cr.elements[0].color = (0.012, 0.006, 0.001, 1.0)     # Deep dark bronze shadow
cr.elements[1].position = 0.56
cr.elements[1].color = (0.09, 0.048, 0.008, 1.0)      # Rich molten amber gold
e2 = cr.elements.new(0.82)
e2.color = (0.95, 0.66, 0.16, 1.0)                    # Vivid 24K pure gold sweep
e3 = cr.elements.new(0.95)
e3.color = (1.0, 0.92, 0.66, 1.0)                     # Sharp white-gold specular edge
wlinks.new(wave.outputs['Fac'], ramp.inputs['Fac'])

# Multiply reflection color by upper-hemisphere mask so floor stays dark & clean
mul_col = wnodes.new('ShaderNodeMix')
mul_col.data_type = 'RGBA'
mul_col.blend_type = 'MULTIPLY'
mul_col.inputs['Factor'].default_value = 1.0
mul_col.location = (-40, -140)
wlinks.new(ramp.outputs['Color'], mul_col.inputs['A'])
wlinks.new(hemi_mask.outputs['Result'], mul_col.inputs['B'])

bg_refl = wnodes.new('ShaderNodeBackground')
bg_refl.inputs['Strength'].default_value = 1.35
bg_refl.location = (200, -140)
wlinks.new(mul_col.outputs['Result'], bg_refl.inputs['Color'])
wlinks.new(bg_refl.outputs['Background'], mix_sh.inputs[1])

# ==============================================================================
# 6. Build 3D Text Logo "cvn" with Ultra-Clean Jewel-Cut Chamfered Bevel
# ==============================================================================
font = bpy.data.fonts.load(FONT_PATH)

txt_curve = bpy.data.curves.new(type='FONT', name='CVN_TextCurve')
txt_curve.body = "cvn"
txt_curve.font = font
txt_curve.size = 2.4
txt_curve.align_x = 'CENTER'
txt_curve.align_y = 'BOTTOM'
txt_curve.space_character = 1.15
txt_curve.resolution_u = 36

# Deep solid sculptural extrusion + razor-clean luxury jewel-cut 45° bevel with micro-rounded seams
txt_curve.extrude = 0.30
txt_curve.bevel_depth = 0.072
txt_curve.bevel_resolution = 14
txt_curve.bevel_mode = 'PROFILE'

prof = txt_curve.bevel_profile
prof.use_clip = True
pts = prof.points
while len(pts) > 2:
    pts.remove(pts[-1])
pts[0].location = (0.0, 1.0)
pts[0].handle_type_1 = pts[0].handle_type_2 = 'VECTOR'
pts[1].location = (1.0, 0.0)
pts[1].handle_type_1 = pts[1].handle_type_2 = 'VECTOR'
# Clean luxury single wide 45-degree chamfer with crisp micro-filleted corners (catches razor-bright specular lines!)
p1 = pts.add(0.10, 0.96)
p1.handle_type_1 = p1.handle_type_2 = 'AUTO'
p2 = pts.add(0.18, 0.88)
p2.handle_type_1 = p2.handle_type_2 = 'VECTOR'
p3 = pts.add(0.84, 0.22)
p3.handle_type_1 = p3.handle_type_2 = 'VECTOR'
p4 = pts.add(0.94, 0.08)
p4.handle_type_1 = p4.handle_type_2 = 'AUTO'
prof.update()

txt_obj = bpy.data.objects.new(name='CVN_Logo_Main', object_data=txt_curve)
scene.collection.objects.link(txt_obj)
txt_obj.rotation_euler = (math.radians(90), 0.0, 0.0)
txt_obj.data.materials.append(gold_main_mat)

# Ground logo precisely on Z = 0
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
eval_o = txt_obj.evaluated_get(depsgraph)
all_z = [(eval_o.matrix_world @ Vector(c)).z for c in eval_o.bound_box]
all_x = [(eval_o.matrix_world @ Vector(c)).x for c in eval_o.bound_box]

min_z, max_z = min(all_z), max(all_z)
min_x, max_x = min(all_x), max(all_x)
logo_height = max_z - min_z
logo_width = max_x - min_x

txt_obj.location.z -= min_z
center_z = logo_height * 0.50

# ==============================================================================
# 7. Seamless Infinite Obsidian Mirror Floor
# ==============================================================================
bpy.ops.mesh.primitive_plane_add(size=24.0, location=(0.0, 0.0, 0.0))
floor = bpy.context.active_object
floor.name = "Obsidian_Floor"
floor.data.materials.append(floor_mat)

# ==============================================================================
# 8. Precision Sculpting Studio Lights (Rich Gold Face + Blazing Bevel Edges!)
# ==============================================================================
def add_area_light(name, location, target, energy, color, size_x, size_y, spread_deg=55):
    ldata = bpy.data.lights.new(name=name, type='AREA')
    ldata.shape = 'RECTANGLE'
    ldata.size = size_x
    ldata.size_y = size_y
    ldata.energy = energy
    ldata.color = color
    if hasattr(ldata, 'spread'):
        ldata.spread = math.radians(spread_deg)
    lobj = bpy.data.objects.new(name=name, object_data=ldata)
    scene.collection.objects.link(lobj)
    lobj.location = Vector(location)
    direction = Vector(target) - Vector(location)
    lobj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return lobj

logo_center = (0.0, 0.0, center_z)

# 1) Diagonal Sculpting Key Strip (High Left: creates rich gradient across face & bright left bevels)
add_area_light(
    "Key_TopLeft_Sculpt",
    location=(-4.8, -2.6, 4.6),
    target=(0.3, 0.0, center_z),
    energy=160.0,
    color=(1.0, 0.86, 0.56),
    size_x=4.2,
    size_y=0.45,
    spread_deg=52,
)

# 2) Overhead Crown Rim Bar (Blazing gold highlight along all top chamfers)
add_area_light(
    "Rim_Top_Crown",
    location=(0.1, 1.4, 4.5),
    target=(0.0, 0.0, center_z + 0.15),
    energy=290.0,
    color=(1.0, 0.90, 0.65),
    size_x=5.8,
    size_y=0.30,
    spread_deg=48,
)

# 3) Right Deep-Gold Rim Kicker (Carves 3D extruded sides of 'c', 'v', 'n' with warm amber gold)
add_area_light(
    "Kicker_Right_Gold",
    location=(5.4, -1.2, 2.0),
    target=(0.5, 0.0, center_z),
    energy=155.0,
    color=(1.0, 0.68, 0.18),
    size_x=1.6,
    size_y=2.4,
    spread_deg=55,
)

# 4) Low Front Warm Rim Catcher (subtle gleam on lower bevel edge without brightening front face)
add_area_light(
    "Fill_LowEdge",
    location=(0.4, -4.4, 0.18),
    target=(0.0, 0.0, 0.25),
    energy=26.0,
    color=(1.0, 0.74, 0.28),
    size_x=4.2,
    size_y=0.15,
    spread_deg=55,
)

# 5) High-Angle Specular Glint Strips (catch only the 45° top bevels, avoiding flat front blowout!)
add_area_light(
    "Bevel_Glint_Left",
    location=(-2.4, -2.5, 4.4),
    target=(-1.1, -0.2, logo_height * 0.85),
    energy=135.0,
    color=(1.0, 0.94, 0.75),
    size_x=0.22,
    size_y=0.22,
    spread_deg=32,
)

add_area_light(
    "Bevel_Glint_Right",
    location=(2.5, -2.5, 4.2),
    target=(1.0, -0.2, logo_height * 0.82),
    energy=125.0,
    color=(1.0, 0.90, 0.68),
    size_x=0.22,
    size_y=0.22,
    spread_deg=32,
)

# 6) Subtle Warm Golden Halo Backdrop (soft luxury amber aura directly behind the letters)
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, 4.4, center_z + 0.22))
halo_plane = bpy.context.active_object
halo_plane.name = "Back_Aura_Backdrop"
halo_plane.rotation_euler = (math.radians(90), 0.0, 0.0)
halo_plane.scale = (14.0, 7.0, 1.0)
bpy.ops.object.transform_apply(scale=True)
halo_plane.visible_shadow = False
halo_plane.visible_diffuse = False
halo_plane.visible_glossy = False

aura_mat = bpy.data.materials.new("BackAuraMat")
aura_mat.use_nodes = True
ant = aura_mat.node_tree
anodes, alinks = ant.nodes, ant.links
anodes.clear()
atc = anodes.new('ShaderNodeTexCoord')
amap = anodes.new('ShaderNodeMapping')
amap.inputs['Location'].default_value = (-0.5, -0.46, 0.0)
amap.inputs['Scale'].default_value = (1.65, 2.4, 1.0)
alinks.new(atc.outputs['Generated'], amap.inputs['Vector'])

alen = anodes.new('ShaderNodeVectorMath')
alen.operation = 'LENGTH'
alinks.new(amap.outputs['Vector'], alen.inputs[0])

aramp = anodes.new('ShaderNodeValToRGB')
acr = aramp.color_ramp
acr.interpolation = 'EASE'
acr.elements[0].position = 0.0
acr.elements[0].color = (0.34, 0.16, 0.014, 1.0)   # Rich warm amber-gold backlight halo
acr.elements[1].position = 0.48
acr.elements[1].color = (0.001, 0.001, 0.0015, 1.0)
alinks.new(alen.outputs['Value'], aramp.inputs['Fac'])

aem = anodes.new('ShaderNodeEmission')
aem.inputs['Strength'].default_value = 1.0
alinks.new(aramp.outputs['Color'], aem.inputs['Color'])

aout = anodes.new('ShaderNodeOutputMaterial')
alinks.new(aem.outputs['Emission'], aout.inputs['Surface'])
if hasattr(aura_mat, 'cycles') and hasattr(aura_mat.cycles, 'emission_sampling'):
    aura_mat.cycles.emission_sampling = 'NONE'
halo_plane.data.materials.append(aura_mat)

# ==============================================================================
# 9. Soft Golden Bokeh Dust & 3 Precision Jewel Glints on Bevel Peaks
# ==============================================================================
random.seed(99)
spark_coll = bpy.data.collections.new("GoldSparks")
scene.collection.children.link(spark_coll)

bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0, location=(0, 0, -10))
proto = bpy.context.active_object
proto_mesh = proto.data
proto_mesh.materials.append(dust_mat)
bpy.data.objects.remove(proto, do_unlink=True)

# Subtle fine golden dust bokeh floating softly in depth (strength below Streaks threshold!)
for i in range(48):
    rx = random.uniform(-3.6, 3.6)
    rz = random.uniform(0.10, 2.10)
    ry = random.uniform(-1.4, 2.8)
    if abs(rx) < 2.0 and rz < 1.25 and ry < 0.55:
        ry = random.uniform(0.85, 2.6)
    rad = random.uniform(0.006, 0.016)
    so = bpy.data.objects.new(f"Dust_{i:02d}", proto_mesh)
    spark_coll.objects.link(so)
    so.location = (rx, ry, rz)
    so.scale = (rad, rad, rad)
    so.visible_shadow = False
    so.visible_diffuse = False
    so.visible_glossy = False

# 3 ultra-selective jewel star glints placed cleanly on key bevel highlights
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0, location=(0, 0, -10))
g_proto = bpy.context.active_object
g_mesh = g_proto.data
g_mesh.materials.append(glint_mat)
bpy.data.objects.remove(g_proto, do_unlink=True)

hero_glints = [
    (-logo_width * 0.35, -0.38, logo_height * 0.90, 0.011),  # Upper curve bevel of 'c'
    (-logo_width * 0.12, -0.38, logo_height * 0.95, 0.013),  # Top-left sharp corner of 'v'
    ( logo_width * 0.43, -0.38, logo_height * 0.88, 0.011),  # Upper-right curve bevel of 'n'
]
for idx, (gx, gy, gz, gr) in enumerate(hero_glints):
    go = bpy.data.objects.new(f"HeroGlint_{idx}", g_mesh)
    spark_coll.objects.link(go)
    go.location = (gx, gy, gz)
    go.scale = (gr, gr, gr)
    go.visible_shadow = False
    go.visible_diffuse = False
    go.visible_glossy = False

# ==============================================================================
# 10. Hero Camera Setup (Ideal Framing + Balanced Reflection Space)
# ==============================================================================
cam_data = bpy.data.cameras.new("HeroCamera")
cam_data.lens = 60.0
cam_data.sensor_width = 36.0
cam_data.dof.use_dof = True
cam_data.dof.aperture_fstop = 4.8

cam_obj = bpy.data.objects.new("HeroCamera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

cam_pos = Vector((-1.55, -8.8, 1.26))
cam_target = Vector((0.0, 0.0, center_z * 0.68))
cam_obj.location = cam_pos
cam_obj.rotation_euler = (cam_target - cam_pos).to_track_quat('-Z', 'Y').to_euler()
cam_data.dof.focus_distance = (Vector((0.0, 0.0, center_z)) - cam_pos).length

# ==============================================================================
# 11. Compositor (Surgical Bloom + Sharp Jewel 4-Point Cross Streaks)
# ==============================================================================
scene.use_nodes = True
comp_ng = bpy.data.node_groups.new("CVN_Gold_Compositor", "CompositorNodeTree")
scene.compositing_node_group = comp_ng
comp_ng.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')

cnodes = comp_ng.nodes
clinks = comp_ng.links

rl = cnodes.new("CompositorNodeRLayers")
rl.location = (-600, 0)

# Stage 1: Tight Luxury Bloom (enhances bright gold ridges without hazing the letters)
glare_bloom = cnodes.new("CompositorNodeGlare")
glare_bloom.location = (-250, 0)
glare_bloom.inputs["Type"].default_value = "Bloom"
glare_bloom.inputs["Quality"].default_value = "High"
glare_bloom.inputs["Threshold"].default_value = 3.2
glare_bloom.inputs["Smoothness"].default_value = 0.25
glare_bloom.inputs["Strength"].default_value = 0.28
glare_bloom.inputs["Size"].default_value = 0.52
glare_bloom.inputs["Tint"].default_value = (1.0, 0.82, 0.42, 1.0)

# Stage 2: Crisp 4-Point Jewel Star Streaks on peak specular glints ONLY
glare_streaks = cnodes.new("CompositorNodeGlare")
glare_streaks.location = (80, 0)
glare_streaks.inputs["Type"].default_value = "Streaks"
glare_streaks.inputs["Quality"].default_value = "High"
glare_streaks.inputs["Threshold"].default_value = 4.6
glare_streaks.inputs["Strength"].default_value = 0.85
glare_streaks.inputs["Streaks"].default_value = 4
glare_streaks.inputs["Streaks Angle"].default_value = math.radians(24)
glare_streaks.inputs["Iterations"].default_value = 4
glare_streaks.inputs["Fade"].default_value = 0.91
glare_streaks.inputs["Color Modulation"].default_value = 0.08
glare_streaks.inputs["Tint"].default_value = (1.0, 0.88, 0.56, 1.0)

comp_out = cnodes.new("NodeGroupOutput")
comp_out.location = (420, 0)

clinks.new(rl.outputs["Image"], glare_bloom.inputs["Image"])
clinks.new(glare_bloom.outputs["Image"], glare_streaks.inputs["Image"])
clinks.new(glare_streaks.outputs["Image"], comp_out.inputs["Image"])

# Set live Blender viewport to Camera View + Material Preview
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.region_3d.view_perspective = 'CAMERA'
                space.shading.type = 'MATERIAL'

# ==============================================================================
# 12. Save .blend and Render High-Quality PNG
# ==============================================================================
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
scene.render.filepath = OUT_PNG
bpy.ops.render.render(write_still=True)

result = {
    "status": "rendered_v3",
    "logo_width": round(logo_width, 3),
    "logo_height": round(logo_height, 3),
    "out_png": OUT_PNG,
    "out_blend": OUT_BLEND,
    "exists_png": os.path.exists(OUT_PNG),
    "png_size_bytes": os.path.getsize(OUT_PNG) if os.path.exists(OUT_PNG) else 0,
}
