import os
import sys
import math
import numpy as np
import bpy
import bmesh
from mathutils import Vector, Matrix

# ==========================================
# パス設定 & 既存単体モジュール読み込み
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import build_iinet_kun as mod_iinet
import build_iich_kun as mod_iich

DEPT_DIR = os.path.dirname(SCRIPT_DIR)
FINAL_DIR = os.path.join(DEPT_DIR, "final_outputs")
os.makedirs(FINAL_DIR, exist_ok=True)

PAIR_BLEND_PATH = os.path.join(FINAL_DIR, "cvn_iich_and_iinet_pair.blend")
PAIR_GLB_PATH = os.path.join(FINAL_DIR, "cvn_iich_and_iinet_pair.glb")
PAIR_FRONT_PATH = os.path.join(FINAL_DIR, "pair_iich_and_iinet_front.png")
PAIR_HERO_PATH = os.path.join(FINAL_DIR, "pair_iich_and_iinet_hero_3quarter.png")
PAIR_BOARD_PATH = os.path.join(FINAL_DIR, "pair_iich_and_iinet_board.png")


# ==========================================
# 1. メッシュ変換＆ペア用いい-chアンテナ・地球儀生成
# ==========================================
def transform_mesh_vertices(obj, scale_xyz=(1.0, 1.0, 1.0), offset_xyz=(0.0, 0.0, 0.0)):
    sx, sy, sz = scale_xyz
    ox, oy, oz = offset_xyz
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for v in bm.verts:
        v.co.x = v.co.x * sx + ox
        v.co.y = v.co.y * sy + oy
        v.co.z = v.co.z * sz + oz
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def create_iich_pair_antenna_and_globe(sx=0.842, sy=0.835, sz=0.829):
    """
    pair_balance_ref.png の実測バランスに準拠した「いい-ch」用アンテナ＆地球儀:
    - 地球儀半径: r_globe = 0.196 m (いい-NETくん r=0.200m の約98%)
    - 地球儀中心: (X=0.0, Y=0.551 m, Z=2.023 m)
    - 尻尾(Antenna): お尻下部の付け根 (Z=0.439m, Y=0.547m) から後方突出点 (Z=1.050m, Y=0.785m) を経て
      地球儀下部 (Z=1.880m, Y=0.551m) へ滑らかな単一C字アーチで接続
    """
    globe_y = 0.551
    globe_z = 2.023
    globe_radius = 0.196
    y_peak = 0.785
    z_peak = 1.050

    root_z_in = 0.480 * sz
    root_y_in = 0.420 * sy
    surf_z = 0.530 * sz  # 0.439 m
    surf_y = 0.655 * sy  # 0.547 m
    top_z = 1.880

    root_z = np.linspace(root_z_in, surf_z - 0.004, 16)
    root_y = np.linspace(root_y_in, surf_y - 0.005, 16)

    u_low = np.linspace(0.0, 1.0, 60)
    z_low = surf_z + (z_peak - surf_z) * u_low
    y_low = surf_y + (y_peak - surf_y) * np.sin(0.5 * math.pi * u_low)

    u_up = np.linspace(0.015, 1.0, 80)
    z_up = z_peak + (top_z - z_peak) * u_up
    y_up = y_peak - (y_peak - globe_y) * (u_up ** 1.85)

    ctrl_z = np.concatenate([root_z, z_low, z_up])
    ctrl_y = np.concatenate([root_y, y_low, y_up])

    n_pts = 160
    t_raw = np.linspace(0.0, 1.0, len(ctrl_z))
    t_fine = np.linspace(0.0, 1.0, n_pts)
    z_fine = np.interp(t_fine, t_raw, ctrl_z)
    y_fine = np.interp(t_fine, t_raw, ctrl_y)

    k_sm = np.exp(-0.5 * (np.arange(-6, 7) / 2.5) ** 2)
    k_sm /= k_sm.sum()
    z_fine = np.convolve(np.pad(z_fine, 6, mode='edge'), k_sm, mode='valid')
    y_fine = np.convolve(np.pad(y_fine, 6, mode='edge'), k_sm, mode='valid')
    z_fine[0], y_fine[0] = root_z_in, root_y_in
    z_fine[-1], y_fine[-1] = top_z, globe_y

    r_pipe = 0.036
    n_ring = 36
    ang = np.linspace(0.0, 2.0 * math.pi, n_ring, endpoint=False)

    bm = bmesh.new()
    rings = []
    for i in range(n_pts):
        if i == 0:
            dy = y_fine[1] - y_fine[0]
            dz = z_fine[1] - z_fine[0]
        elif i == n_pts - 1:
            dy = y_fine[-1] - y_fine[-2]
            dz = z_fine[-1] - z_fine[-2]
        else:
            dy = y_fine[i + 1] - y_fine[i - 1]
            dz = z_fine[i + 1] - z_fine[i - 1]
        t_len = math.hypot(dy, dz)
        ty, tz = dy / t_len, dz / t_len
        b2y, b2z = -tz, ty

        ring_v = []
        for ia in range(n_ring):
            ca, sa = math.cos(ang[ia]), math.sin(ang[ia])
            vx = r_pipe * ca
            vy = y_fine[i] + r_pipe * sa * b2y
            vz = z_fine[i] + r_pipe * sa * b2z
            ring_v.append(bm.verts.new((float(vx), float(vy), float(vz))))
        rings.append(ring_v)

    for i in range(n_pts - 1):
        for ia in range(n_ring):
            ia_next = (ia + 1) % n_ring
            bm.faces.new((rings[i][ia], rings[i][ia_next], rings[i + 1][ia_next], rings[i + 1][ia]))

    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    ant_mesh = bpy.data.meshes.new("IICh_Antenna_Mesh")
    bm.to_mesh(ant_mesh)
    bm.free()

    ant_obj = bpy.data.objects.new("IICh_Antenna", ant_mesh)
    bpy.context.collection.objects.link(ant_obj)
    for poly in ant_mesh.polygons:
        poly.use_smooth = True

    globe_center = Vector((0.0, globe_y, globe_z))
    bm_g = bmesh.new()
    bmesh.ops.create_uvsphere(bm_g, u_segments=64, v_segments=32, radius=globe_radius)
    uv_layer = bm_g.loops.layers.uv.new("UVMap")

    for face in bm_g.faces:
        face.smooth = True
        non_pole_us = []
        loop_uvs = []
        for loop in face.loops:
            co = loop.vert.co.normalized()
            nx, ny, nz = float(co.x), float(co.y), float(co.z)
            lat = math.asin(max(-1.0, min(1.0, nz)))
            v = 0.5 + lat / math.pi
            if math.hypot(nx, ny) < 1e-5:
                loop_uvs.append([None, v])
            else:
                lon = math.atan2(nx, -ny)
                u = 0.5 + lon / (2.0 * math.pi)
                non_pole_us.append(u)
                loop_uvs.append([u, v])

        if non_pole_us and (max(non_pole_us) - min(non_pole_us) > 0.5):
            for item in loop_uvs:
                if item[0] is not None and item[0] < 0.5:
                    item[0] += 1.0
            non_pole_us = [item[0] for item in loop_uvs if item[0] is not None]

        avg_u = (sum(non_pole_us) / len(non_pole_us)) if non_pole_us else 0.5
        for loop, (u, v) in zip(face.loops, loop_uvs):
            loop[uv_layer].uv = (avg_u if u is None else u, v)

    for v in bm_g.verts:
        v.co += globe_center

    globe_mesh = bpy.data.meshes.new("IICh_Globe_Mesh")
    bm_g.to_mesh(globe_mesh)
    bm_g.free()

    globe_obj = bpy.data.objects.new("IICh_Globe", globe_mesh)
    bpy.context.collection.objects.link(globe_obj)

    return ant_obj, globe_obj


def move_objects_to_collection(objs, coll):
    for obj in objs:
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        coll.objects.link(obj)


# ==========================================
# 2. 2キャラクター構築（Collection_IICh & Collection_IINet）
# ==========================================
def build_iich_character(coll_iich, mat_globe):
    data_iich = mod_iich.extract_iich_profiles()
    surf_iich = mod_iich.IIChSurfaceModel(data_iich)

    body_obj = mod_iich.create_body_mesh(surf_iich, res=136)
    logo_obj = mod_iich.create_logo_3d_mesh(surf_iich)
    screen_obj = mod_iich.create_face_screen_mesh(surf_iich, data_iich, flat_mode=True)
    frame_obj = mod_iich.create_face_frame_mesh(surf_iich, data_iich, flat_mode=True)
    eye_l_obj = mod_iich.create_eye_mesh(surf_iich, "Eye.L", cx_eye=+0.3145, cz_eye=1.1075, rx_eye=0.0890, rz_eye=0.1182, w_ring=0.0155)
    eye_r_obj = mod_iich.create_eye_mesh(surf_iich, "Eye.R", cx_eye=-0.3145, cz_eye=1.1075, rx_eye=0.0890, rz_eye=0.1182, w_ring=0.0155)
    mouth_obj = mod_iich.create_mouth_mesh(surf_iich)
    arm_l_obj, arm_r_obj = mod_iich.create_arm_meshes(surf_iich)

    # 足底を Z=0.000m に厳密接地させた上で、(sx=0.842, sy=0.835, sz=0.829) スケールを適用
    z_min_raw = min(v.co.z for v in body_obj.data.vertices)
    sx, sy, sz = 0.842, 0.835, 0.829

    scaled_parts = [body_obj, logo_obj, screen_obj, frame_obj, eye_l_obj, eye_r_obj, mouth_obj, arm_l_obj, arm_r_obj]
    for obj in scaled_parts:
        transform_mesh_vertices(obj, scale_xyz=(1.0, 1.0, 1.0), offset_xyz=(0.0, 0.0, -z_min_raw))
        transform_mesh_vertices(obj, scale_xyz=(sx, sy, sz), offset_xyz=(0.0, 0.0, 0.0))

    ant_obj, globe_obj = create_iich_pair_antenna_and_globe(sx=sx, sy=sy, sz=sz)

    # マテリアル作成＆割り当て
    mat_body_green = mod_iich.create_matte_material("IICh_Mat_Body_Green", (134, 194, 78))
    mat_arm_green = mod_iich.create_matte_material("IICh_Mat_Arm_Green", (128, 188, 72))
    mat_frame_blue = mod_iich.create_matte_material("IICh_Mat_Frame_Blue", (52, 114, 182))
    mat_feature_blue = mod_iich.create_matte_material("IICh_Mat_Feature_Blue", (22, 96, 172))
    mat_eye_outer_blue = mod_iich.create_matte_material("IICh_Mat_Eye_Outer_Blue", (64, 134, 204))
    mat_eye_inner_navy = mod_iich.create_matte_material("IICh_Mat_Eye_Inner_Navy", (10, 68, 142))
    mat_stem_blue = mod_iich.create_matte_material("IICh_Mat_Stem_Blue", (52, 114, 182))
    mat_screen_cream = mod_iich.create_matte_material("IICh_Mat_Screen_Cream", (253, 250, 210))
    mat_logo_yellow = mod_iich.create_matte_material("IICh_Mat_Logo_Yellow", (252, 242, 20))
    mat_logo_side = mod_iich.create_matte_material("IICh_Mat_Logo_Side", (185, 130, 0))

    body_obj.data.materials.append(mat_body_green)
    logo_obj.data.materials.append(mat_logo_yellow)
    logo_obj.data.materials.append(mat_logo_side)
    arm_l_obj.data.materials.append(mat_arm_green)
    arm_r_obj.data.materials.append(mat_arm_green)
    frame_obj.data.materials.append(mat_frame_blue)
    screen_obj.data.materials.append(mat_screen_cream)
    eye_l_obj.data.materials.append(mat_eye_outer_blue)
    eye_l_obj.data.materials.append(mat_eye_inner_navy)
    eye_r_obj.data.materials.append(mat_eye_outer_blue)
    eye_r_obj.data.materials.append(mat_eye_inner_navy)
    mouth_obj.data.materials.append(mat_feature_blue)
    ant_obj.data.materials.append(mat_stem_blue)
    globe_obj.data.materials.append(mat_globe)

    all_meshes = [
        body_obj, logo_obj, screen_obj, frame_obj,
        eye_l_obj, eye_r_obj, mouth_obj,
        arm_l_obj, arm_r_obj,
        ant_obj, globe_obj,
    ]

    # オブジェクト・メッシュ名を IICh_ プレフィックスに統一
    rename_map = [
        (body_obj, "IICh_Body"),
        (logo_obj, "IICh_Logo_LILI_ch"),
        (screen_obj, "IICh_Face_Screen"),
        (frame_obj, "IICh_Face_Frame"),
        (eye_l_obj, "IICh_Eye.L"),
        (eye_r_obj, "IICh_Eye.R"),
        (mouth_obj, "IICh_Mouth"),
        (arm_l_obj, "IICh_Arm.L"),
        (arm_r_obj, "IICh_Arm.R"),
        (ant_obj, "IICh_Antenna"),
        (globe_obj, "IICh_Globe"),
    ]
    for obj, new_name in rename_map:
        obj.name = new_name
        obj.data.name = new_name + "_Mesh"

    # アーマチュア構築＆スキニング
    arm_data = bpy.data.armatures.new("IICh_Armature_Data")
    arm_obj = bpy.data.objects.new("IICh_Armature", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    eb = arm_data.edit_bones
    b_root = eb.new("Root")
    b_root.head = (0.0, 0.0, 0.0)
    b_root.tail = (0.0, 0.0, 0.14)

    b_body = eb.new("Body")
    b_body.head = (0.0, 0.0, 0.14)
    b_body.tail = (0.0, 0.0, 1.62)
    b_body.parent = b_root

    b_leg_l = eb.new("Leg.L")
    b_leg_l.head = (0.2625 * sx, 0.0, 0.14)
    b_leg_l.tail = (0.2625 * sx, 0.0, 0.0)
    b_leg_l.parent = b_body

    b_leg_r = eb.new("Leg.R")
    b_leg_r.head = (-0.2625 * sx, 0.0, 0.14)
    b_leg_r.tail = (-0.2625 * sx, 0.0, 0.0)
    b_leg_r.parent = b_body

    b_arm_l = eb.new("Arm.L")
    b_arm_l.head = (0.82 * sx, 0.03, 0.52 * sz)
    b_arm_l.tail = (1.03 * sx, 0.03, 0.28 * sz)
    b_arm_l.parent = b_body

    b_arm_r = eb.new("Arm.R")
    b_arm_r.head = (-0.82 * sx, 0.03, 0.52 * sz)
    b_arm_r.tail = (-1.03 * sx, 0.03, 0.28 * sz)
    b_arm_r.parent = b_body

    b_ant1 = eb.new("Antenna_1")
    b_ant1.head = (0.0, 0.547, 0.439)
    b_ant1.tail = (0.0, 0.785, 1.050)
    b_ant1.parent = b_body

    b_ant2 = eb.new("Antenna_2")
    b_ant2.head = (0.0, 0.785, 1.050)
    b_ant2.tail = (0.0, 0.551, 1.880)
    b_ant2.parent = b_ant1
    b_ant2.use_connect = True

    b_globe = eb.new("Globe")
    b_globe.head = (0.0, 0.551, 1.880)
    b_globe.tail = (0.0, 0.551, 2.219)
    b_globe.parent = b_ant2

    bpy.ops.object.mode_set(mode='OBJECT')

    for obj in all_meshes:
        obj.parent = arm_obj
        mod = obj.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = arm_obj
        short_name = obj.name.replace("IICh_", "")
        if short_name == "Body":
            vg_body = obj.vertex_groups.new(name="Body")
            vg_leg_l = obj.vertex_groups.new(name="Leg.L")
            vg_leg_r = obj.vertex_groups.new(name="Leg.R")
            for v in obj.data.vertices:
                z, x = v.co.z, v.co.x
                if z < 0.16:
                    w_leg = float(np.clip((0.16 - z) / 0.13, 0.0, 1.0))
                    if x >= 0:
                        vg_leg_l.add([v.index], w_leg, 'REPLACE')
                    else:
                        vg_leg_r.add([v.index], w_leg, 'REPLACE')
                    vg_body.add([v.index], 1.0 - w_leg, 'REPLACE')
                else:
                    vg_body.add([v.index], 1.0, 'REPLACE')
        elif short_name in ("Face_Screen", "Face_Frame", "Eye.L", "Eye.R", "Mouth", "Logo_LILI_ch"):
            vg = obj.vertex_groups.new(name="Body")
            vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
        elif short_name == "Arm.L":
            vg = obj.vertex_groups.new(name="Arm.L")
            vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
        elif short_name == "Arm.R":
            vg = obj.vertex_groups.new(name="Arm.R")
            vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
        elif short_name == "Globe":
            vg = obj.vertex_groups.new(name="Globe")
            vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
        elif short_name == "Antenna":
            vg1 = obj.vertex_groups.new(name="Antenna_1")
            vg2 = obj.vertex_groups.new(name="Antenna_2")
            for v in obj.data.vertices:
                if v.co.z < 1.050:
                    vg1.add([v.index], 1.0, 'REPLACE')
                else:
                    vg2.add([v.index], 1.0, 'REPLACE')

    # 左側 (-X) に配置: X_iich = -0.955 m, Y = -0.025 m, Z = 0.000 m
    arm_obj.location = Vector((-0.955, -0.025, 0.000))
    move_objects_to_collection([arm_obj] + all_meshes, coll_iich)
    return arm_obj, all_meshes


def build_iinet_character(coll_iinet, mat_globe):
    data_iinet = mod_iinet.extract_textures_and_profiles()
    surf_iinet = mod_iinet.IINetSurfaceModel(data_iinet)

    body_obj = mod_iinet.create_body_mesh(surf_iinet, res=136)
    logo_obj = mod_iinet.create_logo_3d_mesh(surf_iinet)
    screen_obj = mod_iinet.create_face_screen_mesh(surf_iinet, data_iinet, flat_mode=True)
    frame_obj = mod_iinet.create_face_frame_mesh(surf_iinet, data_iinet, flat_mode=True)
    eye_l_obj = mod_iinet.create_eye_mesh(surf_iinet, "Eye.L", cx_eye=+0.3055, cz_eye=1.2535, radius=0.0630)
    eye_r_obj = mod_iinet.create_eye_mesh(surf_iinet, "Eye.R", cx_eye=-0.3055, cz_eye=1.2535, radius=0.0630)
    mouth_obj = mod_iinet.create_mouth_mesh(surf_iinet)
    arm_l_obj, arm_r_obj = mod_iinet.create_arm_meshes(data_iinet, surf_iinet)
    ant_obj, globe_obj = mod_iinet.create_antenna_and_globe(data_iinet)

    all_meshes = [
        body_obj, logo_obj, screen_obj, frame_obj,
        eye_l_obj, eye_r_obj, mouth_obj,
        arm_l_obj, arm_r_obj,
        ant_obj, globe_obj,
    ]

    # 足底を Z=0.000m に厳密接地
    z_min_raw = min(v.co.z for v in body_obj.data.vertices)
    for obj in [body_obj, logo_obj, screen_obj, frame_obj, eye_l_obj, eye_r_obj, mouth_obj, ant_obj]:
        transform_mesh_vertices(obj, scale_xyz=(1.0, 1.0, 1.0), offset_xyz=(0.0, 0.0, -z_min_raw))

    # pair_balance_ref.png の両腕スパンに合わせて、胴体上部の接合部は100%維持したまま下端パドル先端のみを滑らかに広げる
    for arm_obj_part in (arm_l_obj, arm_r_obj):
        bm_a = bmesh.new()
        bm_a.from_mesh(arm_obj_part.data)
        for v in bm_a.verts:
            z_orig = v.co.z
            abs_x = abs(v.co.x)
            u_low = float(np.clip((0.55 - z_orig) / (0.55 - 0.34), 0.0, 1.0))
            w_z = (u_low ** 2) * (3.0 - 2.0 * u_low)
            u_out = float(np.clip((abs_x - 0.76) / (0.875 - 0.76), 0.0, 1.0))
            dx_flare = 0.080 * w_z * (u_out ** 1.2)
            sign_x = 1.0 if v.co.x >= 0.0 else -1.0
            v.co.x = sign_x * (abs_x + dx_flare)
            v.co.z = z_orig - z_min_raw
        bmesh.ops.recalc_face_normals(bm_a, faces=bm_a.faces[:])
        bm_a.to_mesh(arm_obj_part.data)
        bm_a.free()
        arm_obj_part.data.update()

    # pair_balance_ref.png の地球儀仕様 (半径 0.200m, 中心 Z=2.356m) に合わせて地球儀を再設定
    bm_g = bmesh.new()
    bm_g.from_mesh(globe_obj.data)
    old_center = Vector((0.0, 1.190, 2.3725))
    new_center = Vector((0.0, 1.190, 2.356))
    scale_g = 0.200 / 0.180
    for v in bm_g.verts:
        rel = v.co - old_center
        v.co = new_center + rel * scale_g
    bmesh.ops.recalc_face_normals(bm_g, faces=bm_g.faces[:])
    bm_g.to_mesh(globe_obj.data)
    bm_g.free()
    globe_obj.data.update()

    # マテリアル作成＆割り当て
    mat_body_pink = mod_iinet.create_matte_material("IINet_Mat_Body_Pink", (245, 82, 164))
    mat_arm_pink = mod_iinet.create_matte_material("IINet_Mat_Arm_Pink", (236, 66, 154))
    mat_frame_blue = mod_iinet.create_matte_material("IINet_Mat_Frame_Blue", (58, 90, 174))
    mat_feature_blue = mod_iinet.create_matte_material("IINet_Mat_Feature_Blue", (46, 76, 168))
    mat_stem_blue = mod_iinet.create_matte_material("IINet_Mat_Stem_Blue", (58, 92, 172))
    mat_screen_cream = mod_iinet.create_matte_material("IINet_Mat_Screen_Cream", (250, 228, 156))
    mat_logo_yellow = mod_iinet.create_matte_material("IINet_Mat_Logo_Yellow", (255, 242, 15))
    mat_logo_side = mod_iinet.create_matte_material("IINet_Mat_Logo_Side", (185, 125, 0))

    body_obj.data.materials.append(mat_body_pink)
    logo_obj.data.materials.append(mat_logo_yellow)
    logo_obj.data.materials.append(mat_logo_side)
    arm_l_obj.data.materials.append(mat_arm_pink)
    arm_r_obj.data.materials.append(mat_arm_pink)
    frame_obj.data.materials.append(mat_frame_blue)
    screen_obj.data.materials.append(mat_screen_cream)
    eye_l_obj.data.materials.append(mat_feature_blue)
    eye_r_obj.data.materials.append(mat_feature_blue)
    mouth_obj.data.materials.append(mat_feature_blue)
    ant_obj.data.materials.append(mat_stem_blue)
    globe_obj.data.materials.append(mat_globe)

    # オブジェクト・メッシュ名を IINet_ プレフィックスに統一
    rename_map = [
        (body_obj, "IINet_Body"),
        (logo_obj, "IINet_Logo_LILI_net"),
        (screen_obj, "IINet_Face_Screen"),
        (frame_obj, "IINet_Face_Frame"),
        (eye_l_obj, "IINet_Eye.L"),
        (eye_r_obj, "IINet_Eye.R"),
        (mouth_obj, "IINet_Mouth"),
        (arm_l_obj, "IINet_Arm.L"),
        (arm_r_obj, "IINet_Arm.R"),
        (ant_obj, "IINet_Antenna"),
        (globe_obj, "IINet_Globe"),
    ]
    for obj, new_name in rename_map:
        obj.name = new_name
        obj.data.name = new_name + "_Mesh"

    # アーマチュア構築＆スキニング
    arm_data = bpy.data.armatures.new("IINet_Armature_Data")
    arm_obj = bpy.data.objects.new("IINet_Armature", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    eb = arm_data.edit_bones
    b_root = eb.new("Root")
    b_root.head = (0.0, 0.0, 0.0)
    b_root.tail = (0.0, 0.0, 0.18)

    b_body = eb.new("Body")
    b_body.head = (0.0, 0.0, 0.18)
    b_body.tail = (0.0, 0.0, 1.95)
    b_body.parent = b_root

    b_leg_l = eb.new("Leg.L")
    b_leg_l.head = (0.245, 0.0, 0.18)
    b_leg_l.tail = (0.230, 0.0, 0.0)
    b_leg_l.parent = b_body

    b_leg_r = eb.new("Leg.R")
    b_leg_r.head = (-0.245, 0.0, 0.18)
    b_leg_r.tail = (-0.230, 0.0, 0.0)
    b_leg_r.parent = b_body

    b_arm_l = eb.new("Arm.L")
    b_arm_l.head = (0.64, 0.0, 0.68)
    b_arm_l.tail = (0.85, 0.0, 0.32)
    b_arm_l.parent = b_body

    b_arm_r = eb.new("Arm.R")
    b_arm_r.head = (-0.64, 0.0, 0.68)
    b_arm_r.tail = (-0.85, 0.0, 0.32)
    b_arm_r.parent = b_body

    b_ant1 = eb.new("Antenna_1")
    b_ant1.head = (0.0, 0.65, 0.56)
    b_ant1.tail = (0.0, 1.09, 1.20)
    b_ant1.parent = b_body

    b_ant2 = eb.new("Antenna_2")
    b_ant2.head = (0.0, 1.09, 1.20)
    b_ant2.tail = (0.0, 0.96, 1.65)
    b_ant2.parent = b_ant1
    b_ant2.use_connect = True

    b_ant3 = eb.new("Antenna_3")
    b_ant3.head = (0.0, 0.96, 1.65)
    b_ant3.tail = (0.0, 1.205, 2.20)
    b_ant3.parent = b_ant2
    b_ant3.use_connect = True

    b_globe = eb.new("Globe")
    b_globe.head = (0.0, 1.205, 2.20)
    b_globe.tail = (0.0, 1.205, 2.55)
    b_globe.parent = b_ant3

    bpy.ops.object.mode_set(mode='OBJECT')

    for obj in all_meshes:
        obj.parent = arm_obj
        mod = obj.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = arm_obj
        short_name = obj.name.replace("IINet_", "")
        if short_name == "Body":
            vg_body = obj.vertex_groups.new(name="Body")
            vg_leg_l = obj.vertex_groups.new(name="Leg.L")
            vg_leg_r = obj.vertex_groups.new(name="Leg.R")
            for v in obj.data.vertices:
                z, x = v.co.z, v.co.x
                if z < 0.24:
                    w_leg = float(np.clip((0.24 - z) / 0.16, 0.0, 1.0))
                    if x >= 0:
                        vg_leg_l.add([v.index], w_leg, 'REPLACE')
                    else:
                        vg_leg_r.add([v.index], w_leg, 'REPLACE')
                    vg_body.add([v.index], 1.0 - w_leg, 'REPLACE')
                else:
                    vg_body.add([v.index], 1.0, 'REPLACE')
        elif short_name in ("Face_Screen", "Face_Frame", "Eye.L", "Eye.R", "Mouth", "Logo_LILI_net"):
            vg = obj.vertex_groups.new(name="Body")
            vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
        elif short_name == "Arm.L":
            vg = obj.vertex_groups.new(name="Arm.L")
            vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
        elif short_name == "Arm.R":
            vg = obj.vertex_groups.new(name="Arm.R")
            vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
        elif short_name == "Globe":
            vg = obj.vertex_groups.new(name="Globe")
            vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
        elif short_name == "Antenna":
            vg1 = obj.vertex_groups.new(name="Antenna_1")
            vg2 = obj.vertex_groups.new(name="Antenna_2")
            vg3 = obj.vertex_groups.new(name="Antenna_3")
            for v in obj.data.vertices:
                if v.co.z < 1.20:
                    vg1.add([v.index], 1.0, 'REPLACE')
                elif v.co.z < 1.65:
                    vg2.add([v.index], 1.0, 'REPLACE')
                else:
                    vg3.add([v.index], 1.0, 'REPLACE')

    # 右側 (+X) に配置: X_iinet = +0.885 m, Y = +0.025 m, Z = 0.000 m
    arm_obj.location = Vector((+0.885, +0.025, 0.000))
    move_objects_to_collection([arm_obj] + all_meshes, coll_iinet)
    return arm_obj, all_meshes


# ==========================================
# 3. ペアシーン用ライティング・カメラ・合成
# ==========================================
PAIR_LIGHTS = {}


def setup_pair_lighting_and_world():
    scene = bpy.context.scene
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0.0

    world = bpy.data.worlds.new("PairStudioWorld")
    scene.world = world
    bg_node = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    bg_node.inputs[0].default_value = (1.00, 0.99, 0.99, 1.0)
    bg_node.inputs[1].default_value = 0.21

    PAIR_LIGHTS.clear()
    rig_defs = [
        ("Key_Cam", 480.0, 3.8, (1.00, 0.99, 0.98), True),
        ("Fill_Cam", 65.0, 6.0, (1.00, 0.99, 0.99), True),
        ("Rim_Cam", 125.0, 4.4, (0.98, 0.99, 1.00), True),
        ("Bounce_Cam", 26.0, 5.8, (1.00, 0.99, 0.99), False),
    ]
    for name, energy, size, col, cast_sh in rig_defs:
        ldata = bpy.data.lights.new(name=name, type='AREA')
        ldata.energy = energy
        ldata.color = col
        ldata.size = size
        if hasattr(ldata, "use_shadow"):
            ldata.use_shadow = cast_sh
        lobj = bpy.data.objects.new(name=name, object_data=ldata)
        bpy.context.collection.objects.link(lobj)
        PAIR_LIGHTS[name] = lobj


def update_pair_studio_lights(forward, right, up):
    target = Vector((0.0, 0.10, 1.05))
    placements = {
        "Key_Cam": target - 4.2 * forward - 4.0 * right + 4.0 * up,
        "Fill_Cam": target - 4.6 * forward + 4.8 * right + 0.4 * up,
        "Rim_Cam": target + 4.2 * forward + 2.2 * right + 4.2 * up,
        "Bounce_Cam": target - 4.0 * forward - 4.4 * up,
    }
    for name, lpos in placements.items():
        if name in PAIR_LIGHTS:
            lobj = PAIR_LIGHTS[name]
            lobj.location = lpos
            direction = (target - lpos).normalized()
            lobj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def set_pair_camera_pose(cam_obj, pos, forward, up_hint, ortho=False, ortho_scale=4.35, lens=68.0):
    forward = Vector(forward).normalized()
    up_hint = Vector(up_hint).normalized()
    right = forward.cross(up_hint).normalized()
    up = right.cross(forward).normalized()
    back = -forward

    rot_mat = Matrix((
        (right.x, up.x, back.x),
        (right.y, up.y, back.y),
        (right.z, up.z, back.z),
    ))
    cam_obj.matrix_world = Matrix.Translation(Vector(pos)) @ rot_mat.to_4x4()
    if ortho:
        cam_obj.data.type = 'ORTHO'
        cam_obj.data.ortho_scale = ortho_scale
    else:
        cam_obj.data.type = 'PERSP'
        cam_obj.data.lens = lens

    update_pair_studio_lights(forward, right, up)


def composite_pair_on_card(rgba_arr, has_floor_shadow=True, bg_top=(246, 249, 254), bg_bot=(230, 236, 246), border_col=(205, 215, 232)):
    h, w, _ = rgba_arr.shape
    t = np.linspace(0.0, 1.0, h)[:, None, None]
    bg = np.array(bg_top, dtype=np.float32)[None, None, :] * (1.0 - t) + np.array(bg_bot, dtype=np.float32)[None, None, :] * t

    if has_floor_shadow:
        yy, xx = np.mgrid[0:h, 0:w]
        mask = rgba_arr[:, :, 3] > 32
        shadow_total = np.zeros((h, w), dtype=np.float32)
        mid_x = w // 2
        for x_slice, rx_factor in [(slice(0, mid_x), 0.165), (slice(mid_x, w), 0.180)]:
            sub_mask = mask[:, x_slice]
            ys_op, xs_op = np.where(sub_mask)
            if len(ys_op) > 0:
                xs_op = xs_op + (x_slice.start or 0)
                y_foot_max = float(np.percentile(ys_op, 99.6))
                low_band = ys_op >= (y_foot_max - h * 0.045)
                shadow_cx = float(np.mean(xs_op[low_band])) if np.any(low_band) else float(np.mean(xs_op))
                shadow_cy = min(h * 0.965, y_foot_max - h * 0.003)
                shadow_rx = w * rx_factor
                shadow_ry = h * 0.026
                r2 = ((xx - shadow_cx) / shadow_rx) ** 2 + ((yy - shadow_cy) / shadow_ry) ** 2
                shadow_total = np.maximum(shadow_total, 0.16 * np.exp(-1.8 * r2))
        bg = bg * (1.0 - shadow_total[:, :, None])

    alpha = (rgba_arr[:, :, 3:4].astype(np.float32)) / 255.0
    rgb = rgba_arr[:, :, :3].astype(np.float32)
    comp = rgb * alpha + bg * (1.0 - alpha)

    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[:, :, :3] = np.clip(comp, 0, 255).astype(np.uint8)
    out[:, :, :3][:3, :] = border_col
    out[:, :, :3][-3:, :] = border_col
    out[:, :, :3][:, :3] = border_col
    out[:, :, :3][:, -3:] = border_col
    out[:, :, 3] = 255
    return out


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    mod_iinet.configure_cycles_gpu(scene)

    # コレクション作成
    coll_iich = bpy.data.collections.new("Collection_IICh")
    coll_iinet = bpy.data.collections.new("Collection_IINet")
    scene.collection.children.link(coll_iich)
    scene.collection.children.link(coll_iinet)

    # 地球儀マテリアル生成（日本列島中央配置の世界地図テクスチャ）
    if not os.path.exists(mod_iinet.GLOBE_TEX_PATH):
        mod_iinet.extract_textures_and_profiles()
    mat_globe = mod_iinet.create_globe_material()

    # 左：いい-ch (Collection_IICh)、右：いい-NETくん (Collection_IINet) を構築
    build_iich_character(coll_iich, mat_globe)
    build_iinet_character(coll_iinet, mat_globe)
    bpy.context.view_layer.update()

    # ライティング・カメラ設定
    setup_pair_lighting_and_world()
    mod_iinet.disable_freestyle_outline()

    cam_data = bpy.data.cameras.new("PairRenderCam")
    cam_obj = bpy.data.objects.new("PairRenderCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # 初期カメラを正面オルソに設定して .blend / .glb 保存
    set_pair_camera_pose(cam_obj, (0.0, -7.5, 1.22), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), ortho=True, ortho_scale=4.35)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=PAIR_BLEND_PATH)
    bpy.ops.export_scene.gltf(filepath=PAIR_GLB_PATH, export_format='GLB')

    # レンダリング実行 (1600 x 1200)
    rw, rh = 1600, 1200
    tmp_render = os.path.join(SCRIPT_DIR, "_tmp_pair_render.png")

    # 1) 正面オルソビュー (pair_iich_and_iinet_front.png)
    set_pair_camera_pose(cam_obj, (0.0, -7.5, 1.22), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), ortho=True, ortho_scale=4.35)
    front_raw = mod_iinet.render_view_to_array(cam_obj, rw, rh, tmp_render, transparent=True)
    front_card = composite_pair_on_card(front_raw, has_floor_shadow=True)
    mod_iinet.save_rgba_uint8_as_png(front_card, PAIR_FRONT_PATH)

    # 2) 斜め3/4ヒーロービュー (pair_iich_and_iinet_hero_3quarter.png)
    hero_pos = Vector((3.40, -7.80, 1.80))
    hero_target = Vector((-0.03, 0.10, 1.15))
    set_pair_camera_pose(cam_obj, hero_pos, hero_target - hero_pos, (0.0, 0.0, 1.0), ortho=False, lens=68.0)
    hero_raw = mod_iinet.render_view_to_array(cam_obj, rw, rh, tmp_render, transparent=True)
    hero_card = composite_pair_on_card(hero_raw, has_floor_shadow=True)
    mod_iinet.save_rgba_uint8_as_png(hero_card, PAIR_HERO_PATH)

    # 3) 背面オルソビュー & 3面比較ボード (pair_iich_and_iinet_board.png)
    set_pair_camera_pose(cam_obj, (0.0, 7.5, 1.22), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0), ortho=True, ortho_scale=4.35)
    back_raw = mod_iinet.render_view_to_array(cam_obj, rw, rh, tmp_render, transparent=True)
    back_card = composite_pair_on_card(back_raw, has_floor_shadow=True)

    if os.path.exists(tmp_render):
        os.remove(tmp_render)

    pad = 24
    board_w = rw * 3 + pad * 4
    board_h = rh + pad * 2
    board = np.full((board_h, board_w, 4), 240, dtype=np.uint8)
    board[:, :, 3] = 255
    for idx, panel in enumerate([front_card, hero_card, back_card]):
        x0 = pad + idx * (rw + pad)
        board[pad:pad + rh, x0:x0 + rw] = panel
    mod_iinet.save_rgba_uint8_as_png(board, PAIR_BOARD_PATH)

    print("ALL PAIR RENDERS AND EXPORTS COMPLETED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
