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
AUDIT_OVERLAY_PATH = os.path.join(SCRIPT_DIR, "audit_overlay_pair.png")
REF_PAIR_PATH = os.path.join(SCRIPT_DIR, "ref_20261110_pair_balance.png")

# 原画 ref_20261110_pair_balance.png (1024x680) と 3D空間(m)の厳密なスケール変換係数:
# いい-NETくん全高 555.0 px = 2.0080 m -> 276.3944223 px/m
PX_PER_M_REF = 555.0 / 2.0080


# ==========================================
# 1. 原画 ref_20261110_pair_balance.png からの直接プロファイル＆3Dメッシュ生成
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


def extract_pair_face_profile_from_ref(im_ref, cx_body_px, foot_y_px, cx_face_px, cy_face_px, x_min_lim, x_max_lim, y_top_body):
    """
    原画 ref_20261110_pair_balance.png から各キャラクターの顔枠(青枠)と画面(クリーム色)の極座標LUTを直接抽出
    （アンチエイリアス付きの3Dスケール m で返却）
    """
    h_img, w_img, _ = im_ref.shape
    R = im_ref[:, :, 0].astype(int)
    G = im_ref[:, :, 1].astype(int)
    B = im_ref[:, :, 2].astype(int)
    A = im_ref[:, :, 3].astype(int)

    # 画面(クリーム色)マスク（内部の目・口も塗りつぶした凸領域として扱えるよう走査）
    screen_mask = (A > 128) & (R > 230) & (G > 210) & (B > 135)
    frame_mask = (A > 128) & (B > 130) & (R < 95) & (G < 145)
    frame_mask[:y_top_body + 3, :] = False
    frame_mask[:, :x_min_lim] = False
    frame_mask[:, x_max_lim:] = False
    screen_mask[:, :x_min_lim] = False
    screen_mask[:, x_max_lim:] = False

    n_theta = 360
    thetas = np.linspace(0.0, 2.0 * math.pi, n_theta, endpoint=False)
    r_in_raw = np.zeros(n_theta, dtype=np.float64)
    r_out_raw = np.zeros(n_theta, dtype=np.float64)

    rs_probe = np.linspace(25.0, 260.0, 471)
    for i, th in enumerate(thetas):
        ct, st = math.cos(th), math.sin(th)
        pxs = np.clip(np.round(cx_face_px + rs_probe * ct).astype(int), 0, w_img - 1)
        pys = np.clip(np.round(cy_face_px - rs_probe * st).astype(int), 0, h_img - 1)

        in_scr = screen_mask[pys, pxs]
        scr_idx = np.where(in_scr)[0]
        if len(scr_idx) > 0:
            idx_in = int(scr_idx[-1])
            r_in_raw[i] = float(rs_probe[idx_in]) / PX_PER_M_REF
            idx_out = idx_in
            entered = False
            gaps = 0
            for j in range(idx_in + 1, len(rs_probe)):
                if frame_mask[pys[j], pxs[j]]:
                    entered = True
                    idx_out = j
                    gaps = 0
                else:
                    if entered:
                        gaps += 1
                        if gaps >= 3:
                            break
                    elif j - idx_in > 6:
                        break
            r_out_raw[i] = float(rs_probe[idx_out]) / PX_PER_M_REF
        else:
            r_in_raw[i] = 0.65
            r_out_raw[i] = 0.72

    pad_k = 9
    kern = np.exp(-0.5 * (np.arange(-pad_k, pad_k + 1) / 3.2) ** 2)
    kern /= kern.sum()
    r_in_lut = np.convolve(np.pad(r_in_raw, pad_k, mode='wrap'), kern, mode='valid')
    r_out_lut = np.convolve(np.pad(r_out_raw, pad_k, mode='wrap'), kern, mode='valid')

    return {
        "thetas": thetas,
        "r_in_lut": r_in_lut,
        "r_out_lut": r_out_lut,
        "face_cx": (cx_face_px - cx_body_px) / PX_PER_M_REF,
        "face_cz": (foot_y_px - cy_face_px) / PX_PER_M_REF,
    }


def create_pair_face_screen_and_frame(surf_model, prof, prefix):
    """
    原画 ref_20261110_pair_balance.png から直接抽出した r_in_lut, r_out_lut, (face_cx, face_cz) を
    そのままボディ前面曲面にコンフォーマル投影して顔スクリーン＆青枠メッシュを生成
    """
    n_ang = 180
    n_rad = 28
    n_prof = 24
    ang_grid = np.linspace(0.0, 2.0 * math.pi, n_ang, endpoint=False)
    r_in = np.interp(ang_grid, prof["thetas"], prof["r_in_lut"])
    r_out = np.interp(ang_grid, prof["thetas"], prof["r_out_lut"])
    xc = prof["face_cx"]
    zc = prof["face_cz"]

    # 1) Screen Mesh
    bm_s = bmesh.new()
    y_c, nx_c, ny_c, nz_c = surf_model.front_surface_y_and_normal(np.array([xc]), np.array([zc]))
    c_off = 0.0007
    center_v = bm_s.verts.new((float(xc + c_off * nx_c[0]), float(y_c[0] + c_off * ny_c[0]), float(zc + c_off * nz_c[0])))

    rings_s = []
    for ir in range(1, n_rad + 1):
        frac = (ir / n_rad) ** 0.85
        rs = r_in * frac
        xs = xc + rs * np.cos(ang_grid)
        zs = zc + rs * np.sin(ang_grid)
        ys, nxs, nys, nzs = surf_model.front_surface_y_and_normal(xs, zs)
        ring_v = []
        for ia in range(n_ang):
            ring_v.append(bm_s.verts.new((
                float(xs[ia] + c_off * nxs[ia]),
                float(ys[ia] + c_off * nys[ia]),
                float(zs[ia] + c_off * nzs[ia]),
            )))
        rings_s.append(ring_v)

    for ia in range(n_ang):
        ia_next = (ia + 1) % n_ang
        bm_s.faces.new((center_v, rings_s[0][ia], rings_s[0][ia_next]))
    for ir in range(n_rad - 1):
        for ia in range(n_ang):
            ia_next = (ia + 1) % n_ang
            bm_s.faces.new((rings_s[ir][ia], rings_s[ir + 1][ia], rings_s[ir + 1][ia_next], rings_s[ir][ia_next]))

    bmesh.ops.recalc_face_normals(bm_s, faces=bm_s.faces[:])
    scr_mesh = bpy.data.meshes.new(prefix + "_Face_Screen_Mesh")
    bm_s.to_mesh(scr_mesh)
    bm_s.free()
    scr_obj = bpy.data.objects.new(prefix + "_Face_Screen", scr_mesh)
    bpy.context.collection.objects.link(scr_obj)
    for poly in scr_mesh.polygons:
        poly.use_smooth = True
    if hasattr(scr_obj, "visible_shadow"):
        scr_obj.visible_shadow = False

    # 2) Frame Mesh
    bm_f = bmesh.new()
    s_vals = np.linspace(0.0, 1.0, n_prof)
    rings_f = []
    for s in s_vals:
        rs = r_in + (r_out - r_in) * s
        xs = xc + rs * np.cos(ang_grid)
        zs = zc + rs * np.sin(ang_grid)
        ys, nxs, nys, nzs = surf_model.front_surface_y_and_normal(xs, zs)
        ring_v = []
        for ia in range(n_ang):
            ring_v.append(bm_f.verts.new((
                float(xs[ia] + c_off * nxs[ia]),
                float(ys[ia] + c_off * nys[ia]),
                float(zs[ia] + c_off * nzs[ia]),
            )))
        rings_f.append(ring_v)

    for ip in range(n_prof - 1):
        for ia in range(n_ang):
            ia_next = (ia + 1) % n_ang
            bm_f.faces.new((rings_f[ip][ia], rings_f[ip][ia_next], rings_f[ip + 1][ia_next], rings_f[ip + 1][ia]))

    bmesh.ops.recalc_face_normals(bm_f, faces=bm_f.faces[:])
    frm_mesh = bpy.data.meshes.new(prefix + "_Face_Frame_Mesh")
    bm_f.to_mesh(frm_mesh)
    bm_f.free()
    frm_obj = bpy.data.objects.new(prefix + "_Face_Frame", frm_mesh)
    bpy.context.collection.objects.link(frm_obj)
    for poly in frm_mesh.polygons:
        poly.use_smooth = True
    if hasattr(frm_obj, "visible_shadow"):
        frm_obj.visible_shadow = False

    return scr_obj, frm_obj


def create_pair_mouth_mesh(surf_model, name, x0_arc, z_arc_center, r_arc, r_tube, max_ang_deg):
    """
    原画 ref_20261110_pair_balance.png 実測アークパラメータ (x0_arc, z_arc_center, r_arc, r_tube, max_ang_deg) に
    100%一致するスマイル口メッシュを生成
    """
    max_ang = math.radians(max_ang_deg)
    n_spine = 64
    n_cap = 24
    n_prof = 24

    spine_pts_x, spine_pts_z, spine_tx, spine_tz, spine_r_scale = [], [], [], [], []

    for ic in range(n_cap):
        u = ic / n_cap
        alpha = 0.5 * math.pi * u
        th = -max_ang
        tx, tz = math.cos(th), math.sin(th)
        ext = math.cos(alpha) * r_tube
        cx = x0_arc + r_arc * math.sin(th) - tx * ext
        cz = z_arc_center - r_arc * math.cos(th) - tz * ext
        r_sc = math.sin(max(alpha, 0.01))
        spine_pts_x.append(cx)
        spine_pts_z.append(cz)
        spine_tx.append(tx)
        spine_tz.append(tz)
        spine_r_scale.append(r_sc)

    for iseg in range(n_spine):
        th = -max_ang + 2.0 * max_ang * (iseg / (n_spine - 1))
        cx = x0_arc + r_arc * math.sin(th)
        cz = z_arc_center - r_arc * math.cos(th)
        tx, tz = math.cos(th), math.sin(th)
        spine_pts_x.append(cx)
        spine_pts_z.append(cz)
        spine_tx.append(tx)
        spine_tz.append(tz)
        spine_r_scale.append(1.0)

    for ic in range(1, n_cap + 1):
        u = 1.0 - (ic / n_cap)
        alpha = 0.5 * math.pi * u
        th = max_ang
        tx, tz = math.cos(th), math.sin(th)
        ext = math.cos(alpha) * r_tube
        cx = x0_arc + r_arc * math.sin(th) + tx * ext
        cz = z_arc_center - r_arc * math.cos(th) + tz * ext
        r_sc = math.sin(max(alpha, 0.01))
        spine_pts_x.append(cx)
        spine_pts_z.append(cz)
        spine_tx.append(tx)
        spine_tz.append(tz)
        spine_r_scale.append(r_sc)

    bm = bmesh.new()
    s_vals = np.linspace(-1.0, 1.0, n_prof)
    h_flat = 0.0014
    rings = []
    for i in range(len(spine_pts_x)):
        cx, cz = spine_pts_x[i], spine_pts_z[i]
        tx, tz = spine_tx[i], spine_tz[i]
        nx_2d, nz_2d = -tz, tx
        rad = r_tube * spine_r_scale[i]

        xs = cx + nx_2d * rad * s_vals
        zs = cz + nz_2d * rad * s_vals
        ys, nxs, nys, nzs = surf_model.front_surface_y_and_normal(xs, zs)

        ring_v = []
        for ip in range(n_prof):
            ring_v.append(bm.verts.new((
                float(xs[ip] + h_flat * nxs[ip]),
                float(ys[ip] + h_flat * nys[ip]),
                float(zs[ip] + h_flat * nzs[ip]),
            )))
        rings.append(ring_v)

    for i in range(len(rings) - 1):
        for ip in range(n_prof - 1):
            bm.faces.new((rings[i][ip], rings[i + 1][ip], rings[i + 1][ip + 1], rings[i][ip + 1]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True
    if hasattr(obj, "visible_shadow"):
        obj.visible_shadow = False
    return obj


def create_pair_logo_3d_mesh(surf_scaled, name, char_type="iich"):
    """
    オーナー指示に基づき、胸元の立体テキストロゴは単体モデル（build_iich_kun.py / build_iinet_kun.py）の
    直線的でシャープなかっこいい3Dテキストロゴ（LILI-ch / LILI-net）を使用し、
    ペアモデルのボディ前面曲面 surf_scaled に沿って寸分の狂いなく密着・立体突出させる。
    """
    if char_type == "iich":
        im_f = mod_iich.load_image_rgba_uint8(mod_iich.FRONT_HIGHRES_PATH)
        crop = im_f[886:966, 272:588].astype(np.float32)
        R, G, B = crop[:, :, 0], crop[:, :, 1], crop[:, :, 2]
        y_raw = np.clip(((R - 136.0) * 1.15 + (G - 195.0) * 0.55 - (B - 79.0) * 0.45) / 145.0, 0.0, 1.0)
        thresh = 0.42
        x0_px, y0_px = 272.0, 886.0
        cx_px, foot_px = 429.5, 1022.0
        z_off_base = 0.025
        # ペアモデル（いい-ch）の胸元スケール（sx=0.8473, sz=0.8262）と青枠下端〜股下の中心高さに合わせる
        scale_x = 0.985 * 0.880
        scale_z = 0.855
        z_shift = 0.008
    else:
        im_f = mod_iinet.load_image_rgba_uint8(mod_iinet.FRONT_REF_PATH)
        crop = im_f[815:915, 192:628].astype(np.float32)
        R, G, B = crop[:, :, 0], crop[:, :, 1], crop[:, :, 2]
        y_raw = np.clip((0.5 * (R + G) - B) / 190.0, 0.0, 1.0)
        thresh = 0.36
        x0_px, y0_px = 192.0, 815.0
        cx_px, foot_px = 393.5, 1022.0
        z_off_base = 0.022
        # ペアモデル（いい-NETくん）の胸元スケール（sx=0.9971, sz=0.9733）に合わせる
        scale_x = 0.985 * 0.997
        scale_z = 0.973
        z_shift = 0.004

    k1d = np.array([0.12, 0.23, 0.30, 0.23, 0.12], dtype=np.float32)
    y_smooth = np.apply_along_axis(lambda m: np.convolve(np.pad(m, 2, mode='edge'), k1d, mode='valid'), 0, y_raw)
    y_smooth = np.apply_along_axis(lambda m: np.convolve(np.pad(m, 2, mode='edge'), k1d, mode='valid'), 1, y_smooth)

    H, W = y_smooth.shape
    cell_mask = (0.25 * (y_smooth[:-1, :-1] + y_smooth[1:, :-1] + y_smooth[:-1, 1:] + y_smooth[1:, 1:]) > thresh).copy()

    for _ in range(2):
        for r in range(H - 2):
            for c in range(W - 2):
                if cell_mask[r, c] and cell_mask[r + 1, c + 1] and not cell_mask[r + 1, c] and not cell_mask[r, c + 1]:
                    cell_mask[r + 1, c] = True
                elif cell_mask[r + 1, c] and cell_mask[r, c + 1] and not cell_mask[r, c] and not cell_mask[r + 1, c + 1]:
                    cell_mask[r, c] = True

    bm = bmesh.new()
    v_grid = {}
    for r in range(H):
        for c in range(W):
            if (
                (r < H - 1 and c < W - 1 and cell_mask[r, c])
                or (r > 0 and c < W - 1 and cell_mask[r - 1, c])
                or (r < H - 1 and c > 0 and cell_mask[r, c - 1])
                or (r > 0 and c > 0 and cell_mask[r - 1, c - 1])
            ):
                x_px = x0_px + float(c)
                y_px = y0_px + float(r)
                x_logo = ((x_px - cx_px) / 400.0) * scale_x
                z_logo = (((foot_px - y_px) / 400.0) + z_off_base) * scale_z + z_shift
                v_grid[(r, c)] = bm.verts.new((x_logo, z_logo, 0.0))

    for r in range(H - 1):
        for c in range(W - 1):
            if cell_mask[r, c]:
                bm.faces.new((v_grid[(r + 1, c)], v_grid[(r + 1, c + 1)], v_grid[(r, c + 1)], v_grid[(r, c)]))

    for step_idx in range(12):
        lam = 0.48 if (step_idx % 2 == 0) else -0.50
        updates = {}
        for v in bm.verts:
            if v.is_boundary:
                nb = [e.other_vert(v) for e in v.link_edges if e.is_boundary]
                if len(nb) == 2:
                    avg = 0.5 * (nb[0].co + nb[1].co)
                    updates[v] = v.co + lam * (avg - v.co)
            else:
                nb = [e.other_vert(v) for e in v.link_edges]
                if nb:
                    avg = sum((n.co for n in nb), Vector((0.0, 0.0, 0.0))) / len(nb)
                    updates[v] = v.co + 0.45 * (avg - v.co)
        for v, co in updates.items():
            v.co = co

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    base_faces = bm.faces[:]

    ret = bmesh.ops.extrude_face_region(bm, geom=base_faces)
    extruded_verts = [ele for ele in ret["geom"] if isinstance(ele, bmesh.types.BMVert)]
    top_faces = [ele for ele in ret["geom"] if isinstance(ele, bmesh.types.BMFace)]
    extruded_set = set(extruded_verts)

    top_face_set = set(top_faces)
    base_face_set = set(base_faces)
    for f in list(bm.faces):
        if f in top_face_set:
            f.material_index = 0
            f.smooth = True
        elif f in base_face_set:
            bm.faces.remove(f)
        else:
            f.material_index = 1
            f.smooth = True

    bevel_updates = {}
    for v in extruded_verts:
        if any(f.material_index == 1 for f in v.link_faces):
            in_nbs = [
                e.other_vert(v) for e in v.link_edges
                if (e.other_vert(v) in extruded_set) and not any(f.material_index == 1 for f in e.other_vert(v).link_faces)
            ]
            if in_nbs:
                avg_in = sum((n.co for n in in_nbs), Vector((0.0, 0.0, 0.0))) / len(in_nbs)
                bevel_updates[v] = v.co + 0.28 * (avg_in - v.co)
    for v, co in bevel_updates.items():
        v.co = co

    all_verts = list(bm.verts)
    xs = np.array([v.co.x for v in all_verts], dtype=np.float64)
    zs = np.array([v.co.y for v in all_verts], dtype=np.float64)
    ys, nxs, nys, nzs = surf_scaled.front_surface_y_and_normal(xs, zs)

    for idx, v in enumerate(all_verts):
        h_off = 0.018 if (v in extruded_set) else -0.005
        v.co = Vector((
            float(xs[idx] + h_off * nxs[idx]),
            float(ys[idx] + h_off * nys[idx]),
            float(zs[idx] + h_off * nzs[idx]),
        ))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True
    return obj


# ==========================================
# 2. 3D空間曲線アンテナ＆地球儀生成
# ==========================================
def build_3d_tube_from_curve(name, x_pts, y_pts, z_pts, r_pipe, n_ring=36, round_tip=True):
    bm = bmesh.new()
    n_pts = len(z_pts)
    ang = np.linspace(0.0, 2.0 * math.pi, n_ring, endpoint=False)

    pts = [Vector((float(x_pts[i]), float(y_pts[i]), float(z_pts[i]))) for i in range(n_pts)]
    tangents = []
    for i in range(n_pts):
        if i == 0:
            t_vec = pts[1] - pts[0]
        elif i == n_pts - 1:
            t_vec = pts[-1] - pts[-2]
        else:
            t_vec = pts[i + 1] - pts[i - 1]
        tangents.append(t_vec.normalized())

    rings = []
    for i in range(n_pts):
        T = tangents[i]
        ref = Vector((1.0, 0.0, 0.0)) if abs(T.x) < 0.85 else Vector((0.0, 1.0, 0.0))
        N2 = T.cross(ref).normalized()
        N1 = N2.cross(T).normalized()

        ring_v = []
        for ia in range(n_ring):
            ca, sa = math.cos(ang[ia]), math.sin(ang[ia])
            v_pos = pts[i] + r_pipe * (ca * N1 + sa * N2)
            ring_v.append(bm.verts.new(v_pos))
        rings.append(ring_v)

    if round_tip:
        T_end = tangents[-1]
        ref_end = Vector((1.0, 0.0, 0.0)) if abs(T_end.x) < 0.85 else Vector((0.0, 1.0, 0.0))
        N2_end = T_end.cross(ref_end).normalized()
        N1_end = N2_end.cross(T_end).normalized()
        n_cap = 6
        for ic in range(1, n_cap):
            phi = (0.5 * math.pi) * (ic / n_cap)
            r_c = r_pipe * math.cos(phi)
            h_c = r_pipe * math.sin(phi)
            ring_v = []
            for ia in range(n_ring):
                ca, sa = math.cos(ang[ia]), math.sin(ang[ia])
                v_pos = pts[-1] + h_c * T_end + r_c * (ca * N1_end + sa * N2_end)
                ring_v.append(bm.verts.new(v_pos))
            rings.append(ring_v)
        tip_pole = bm.verts.new(pts[-1] + r_pipe * T_end)
    else:
        tip_pole = None

    for i in range(len(rings) - 1):
        for ia in range(n_ring):
            ia_next = (ia + 1) % n_ring
            bm.faces.new((rings[i][ia], rings[i][ia_next], rings[i + 1][ia_next], rings[i + 1][ia]))

    bm.faces.new(rings[0][::-1])
    if tip_pole is not None:
        last_ring = rings[-1]
        for ia in range(n_ring):
            ia_next = (ia + 1) % n_ring
            bm.faces.new((last_ring[ia], last_ring[ia_next], tip_pole))
    else:
        bm.faces.new(rings[-1])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True
    return obj


def create_tilted_globe(name, center_xyz, radius, roll_y_deg=0.0, yaw_z_deg=0.0):
    bm_g = bmesh.new()
    bmesh.ops.create_uvsphere(bm_g, u_segments=64, v_segments=32, radius=radius)
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

    rot_mat = Matrix.Rotation(math.radians(roll_y_deg), 3, 'Y') @ Matrix.Rotation(math.radians(yaw_z_deg), 3, 'Z')
    center_vec = Vector(center_xyz)
    for v in bm_g.verts:
        v.co = (rot_mat @ v.co) + center_vec

    bmesh.ops.recalc_face_normals(bm_g, faces=bm_g.faces[:])
    globe_mesh = bpy.data.meshes.new(name + "_Mesh")
    bm_g.to_mesh(globe_mesh)
    bm_g.free()

    globe_obj = bpy.data.objects.new(name, globe_mesh)
    bpy.context.collection.objects.link(globe_obj)
    return globe_obj


def create_iich_pair_antenna_and_globe(sx=0.8473, sy=0.8350, sz=0.8262):
    globe_x = -0.2460
    globe_y = 0.5500
    globe_z = 2.0514
    globe_radius = 0.1664

    y_peak = 0.7850
    z_peak = 1.0500
    root_z_in = 0.480 * sz
    root_y_in = 0.420 * sy
    surf_z = 0.530 * sz
    surf_y = 0.655 * sy
    top_z = globe_z
    tip_y = globe_y

    root_z = np.linspace(root_z_in, surf_z - 0.004, 16)
    root_y = np.linspace(root_y_in, surf_y - 0.005, 16)

    u_low = np.linspace(0.0, 1.0, 60)
    z_low = surf_z + (z_peak - surf_z) * u_low
    y_low = surf_y + (y_peak - surf_y) * np.sin(0.5 * math.pi * u_low)

    u_up = np.linspace(0.015, 1.0, 90)
    z_up = z_peak + (top_z - z_peak) * u_up
    y_up = y_peak - (y_peak - tip_y) * (u_up ** 1.55)

    ctrl_z = np.concatenate([root_z, z_low, z_up])
    ctrl_y = np.concatenate([root_y, y_low, y_up])

    n_pts = 180
    t_raw = np.linspace(0.0, 1.0, len(ctrl_z))
    t_fine = np.linspace(0.0, 1.0, n_pts)
    z_fine = np.interp(t_fine, t_raw, ctrl_z)
    y_fine = np.interp(t_fine, t_raw, ctrl_y)

    k_sm = np.exp(-0.5 * (np.arange(-6, 7) / 2.5) ** 2)
    k_sm /= k_sm.sum()
    z_fine = np.convolve(np.pad(z_fine, 6, mode='edge'), k_sm, mode='valid')
    y_fine = np.convolve(np.pad(y_fine, 6, mode='edge'), k_sm, mode='valid')
    z_fine[0], y_fine[0] = root_z_in, root_y_in
    z_fine[-1], y_fine[-1] = top_z, tip_y

    x_fine = np.zeros_like(z_fine)
    for i, z in enumerate(z_fine):
        if z <= 0.850:
            x_fine[i] = 0.0
        elif z <= 1.6751:
            u = (z - 0.850) / (1.6751 - 0.850)
            s = (u ** 2) * (3.0 - 2.0 * u)
            x_fine[i] = -0.06555 * s
        else:
            u2 = float(np.clip((z - 1.6751) / (top_z - 1.6751), 0.0, 1.0))
            x_fine[i] = -0.06555 + (globe_x - (-0.06555)) * (0.42 * u2 + 0.58 * (u2 ** 1.65))

    x_fine = np.convolve(np.pad(x_fine, 4, mode='edge'), k_sm[2:-2] / k_sm[2:-2].sum(), mode='valid')
    x_fine[0] = 0.0
    x_fine[-1] = globe_x

    ant_obj = build_3d_tube_from_curve("IICh_Antenna", x_fine, y_fine, z_fine, r_pipe=0.0245, n_ring=36, round_tip=False)
    globe_obj = create_tilted_globe(
        "IICh_Globe",
        center_xyz=(globe_x, globe_y, globe_z),
        radius=globe_radius,
        roll_y_deg=-26.0,
        yaw_z_deg=-18.0,
    )
    return ant_obj, globe_obj


def create_iinet_pair_antenna_and_globe(data_iinet, sz_iinet=0.97334):
    raw_z = data_iinet["stem_Z"][::-1] * sz_iinet
    raw_y = data_iinet["stem_Y"][::-1]

    globe_x = +0.3256
    globe_y = 1.0500
    globe_z = 2.2829
    globe_radius = 0.1845
    tip_z = globe_z
    tip_y = globe_y

    root_z = np.linspace(0.475, float(raw_z[0]) - 0.008, 22)
    root_y = np.linspace(0.350, float(raw_y[0]) - 0.015, 22)

    low_mask = raw_z <= (1.060 * sz_iinet)
    low_z = raw_z[low_mask]
    low_y = raw_y[low_mask]
    z_peak = float(low_z[-1])
    y_peak = float(low_y[-1])

    z_valley = 1.640 * sz_iinet
    y_valley = 0.975
    u_mid = np.linspace(0.02, 1.0, 42)
    mid_z = z_peak + (z_valley - z_peak) * u_mid
    mid_y = y_peak - (y_peak - y_valley) * 0.5 * (1.0 - np.cos(math.pi * u_mid))

    u_arc = np.linspace(0.02, 1.0, 56)
    arc_z = z_valley + (tip_z - z_valley) * u_arc
    arc_y = y_valley + (tip_y - y_valley) * 0.5 * (1.0 - np.cos(math.pi * u_arc))

    ctrl_z = np.concatenate([root_z, low_z, mid_z, arc_z])
    ctrl_y = np.concatenate([root_y, low_y, mid_y, arc_y])

    n_pts = 180
    t_raw = np.linspace(0.0, 1.0, len(ctrl_z))
    t_fine = np.linspace(0.0, 1.0, n_pts)
    z_fine = np.interp(t_fine, t_raw, ctrl_z)
    y_fine = np.interp(t_fine, t_raw, ctrl_y)

    k_sm = np.exp(-0.5 * (np.arange(-8, 9) / 3.2) ** 2)
    k_sm /= k_sm.sum()
    z_fine = np.convolve(np.pad(z_fine, 8, mode='edge'), k_sm, mode='valid')
    y_fine = np.convolve(np.pad(y_fine, 8, mode='edge'), k_sm, mode='valid')
    z_fine[0], y_fine[0] = 0.475, 0.350
    z_fine[-1], y_fine[-1] = tip_z, tip_y

    x_fine = np.zeros_like(z_fine)
    for i, z in enumerate(z_fine):
        if z <= 1.0086:
            x_fine[i] = 0.0
        elif z <= 2.0189:
            u = (z - 1.0086) / (2.0189 - 1.0086)
            x_fine[i] = +0.11491 * (u ** 2.20)
        else:
            u2 = float(np.clip((z - 2.0189) / (tip_z - 2.0189), 0.0, 1.0))
            x_fine[i] = +0.11491 + (globe_x - 0.11491) * (0.38 * u2 + 0.62 * (u2 ** 1.55))

    x_fine = np.convolve(np.pad(x_fine, 4, mode='edge'), k_sm[4:-4] / k_sm[4:-4].sum(), mode='valid')
    x_fine[0] = 0.0
    x_fine[-1] = globe_x

    ant_obj = build_3d_tube_from_curve("IINet_Antenna", x_fine, y_fine, z_fine, r_pipe=0.0255, n_ring=36, round_tip=False)
    globe_obj = create_tilted_globe(
        "IINet_Globe",
        center_xyz=(globe_x, globe_y, globe_z),
        radius=globe_radius,
        roll_y_deg=-24.0,
        yaw_z_deg=-22.0,
    )
    return ant_obj, globe_obj


def move_objects_to_collection(objs, coll):
    for obj in objs:
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        coll.objects.link(obj)


def create_seamless_arm_meshes_for_char(
    surf_model, sx_val, sy_val, sz_val, z_min_raw,
    z_min, z_armpit, z_peak, z_max,
    x_tip_bot, x_armpit, x_peak,
    base_half_y, root_flare_gain, mid_y_base,
    prefix
):
    """
    原画の正面2D輪郭（z_min..z_max, z_peak, x_peak, x_tip_bot, 脇下アーチ x_armpit）を1px精度で厳密に保持しつつ、
    下端から上端まで水平段差・くびれが一切ない滑らかな3Dパドルアームを生成し、
    脇下より上（Z > z_armpit）の内側のみを胴体内部へ深く延長して Boolean Union + Voxel Remesh に備える。
    """
    xs_raw = np.linspace(surf_model.x_foot, surf_model.W_max, 400)
    zs_raw = surf_model._eval_lower_z(xs_raw, np.zeros_like(xs_raw))
    xs_test = xs_raw * sx_val
    zs_test = (zs_raw - z_min_raw) * sz_val

    arms = []
    for side_sign, name in [(+1.0, f"{prefix}_Arm.L"), (-1.0, f"{prefix}_Arm.R")]:
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=2.0)
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=36, use_grid_fill=True)

        verts = bm.verts
        verts.ensure_lookup_table()
        coords = np.array([v.co[:] for v in verts], dtype=np.float64)
        tan_c = np.tan(coords * (math.pi / 4.0))
        unit_p = tan_c / np.linalg.norm(tan_c, axis=1, keepdims=True)
        ux, uy, uz = unit_p[:, 0], unit_p[:, 1], unit_p[:, 2]

        Z = 0.5 * (z_min + z_max) + 0.5 * (z_max - z_min) * uz
        env_z = np.sqrt(np.maximum(1.0 - uz * uz, 0.0))

        r_horiz = np.sqrt(np.maximum(ux * ux + uy * uy, 1e-12))
        cy = uy / r_horiz
        cx = ux / r_horiz

        x_body_surf = np.interp(Z, zs_test, xs_test)
        x_tip_top = float(np.interp(z_max, zs_test, xs_test)) - 0.004

        t_bot = np.clip((Z - z_min) / (z_peak - z_min), 0.0, 1.0)
        u_up = np.clip((Z - z_peak) / (z_max - z_peak), 0.0, 1.0)
        x_outer = np.where(
            Z <= z_peak,
            x_tip_bot + (x_peak - x_tip_bot) * np.sqrt(t_bot * (2.0 - t_bot)),
            x_tip_top + (x_peak - x_tip_top) * ((1.0 - (u_up ** 1.38)) ** 0.90),
        )

        # 内側輪郭 x_inner(Z): 下端から脇下(z_armpit, x_armpit)を通り、その上では胴体内部(x_body_surf - 0.085m)へ滑らかに入る
        s_in = np.clip((Z - z_min) / (z_armpit - z_min), 0.0, 1.0)
        x_inner_paddle = x_tip_bot - (x_tip_bot - x_armpit) * (s_in ** 0.68)
        u_top_in = np.clip((Z - (z_max - 0.08)) / 0.08, 0.0, 1.0)
        env_top_in = np.sqrt(np.maximum(1.0 - u_top_in * u_top_in, 0.0))
        x_inner_body = x_tip_top * (1.0 - env_top_in) + (x_body_surf - 0.085) * env_top_in
        w_in = np.clip((Z - (z_armpit - 0.015)) / 0.055, 0.0, 1.0)
        w_in = w_in * w_in * (3.0 - 2.0 * w_in)
        x_inner = (1.0 - w_in) * x_inner_paddle + w_in * x_inner_body

        # 最大厚み軸 x_root(Z): 脇下より上では胴体内部(x_body_surf - 0.080m)へ引き込み、
        # 胴体表面から腕先端まで |Y| が単調減少（V字の谷ゼロ）になるようにする
        x_mid_paddle = 0.5 * (x_outer + x_inner_paddle)
        x_root_body = x_tip_top * (1.0 - env_top_in) + (x_body_surf - 0.080) * env_top_in
        w_root = np.clip((Z - (z_armpit - 0.035)) / 0.110, 0.0, 1.0)
        w_root = w_root * w_root * (3.0 - 2.0 * w_root)
        x_root = (1.0 - w_root) * x_mid_paddle + w_root * x_root_body

        cx_pos = np.maximum(cx, 0.0)
        cx_neg = np.maximum(-cx, 0.0)
        X_abs = np.where(
            cx >= 0.0,
            x_root + (x_outer - x_root) * (cx_pos ** 0.80),
            x_root - (x_root - x_inner) * (cx_neg ** 0.85),
        )

        # 前後厚み half_y: パドル外側(X_abs >= x_body_surf + 0.025m)では一切膨らませず水平くびれをゼロに保ち、
        # 胴体交差部〜胴体内部(X_abs <= x_body_surf + 0.025m)のみを胴体厚みに向かってフレア拡大してV字谷を埋める
        u_in_seam = np.clip(((x_body_surf + 0.025) - X_abs) / 0.115, 0.0, 1.0)
        w_flare_x = u_in_seam * u_in_seam * (3.0 - 2.0 * u_in_seam)
        u_z_flare = np.clip((Z - (z_armpit - 0.025)) / 0.075, 0.0, 1.0)
        w_flare_z = (u_z_flare * u_z_flare * (3.0 - 2.0 * u_z_flare)) * (env_top_in ** 0.70)
        w_flare = w_flare_x * w_flare_z
        half_y = base_half_y * (env_z ** 0.92) * (1.0 + root_flare_gain * w_flare)
        mid_y = mid_y_base - 0.012 * uz
        Y = mid_y + half_y * cy

        X = side_sign * X_abs
        for i, v in enumerate(verts):
            v.co = Vector((float(X[i]), float(Y[i]), float(Z[i])))

        for it in range(4):
            tip_updates = {}
            for v in verts:
                if it < 2 or v.co.z < (z_min + 0.035):
                    nb = [e.other_vert(v) for e in v.link_edges]
                    if nb:
                        w_lap = 0.25 if it < 2 else 0.45
                        tip_updates[v] = (1.0 - w_lap) * v.co + w_lap * (sum((n.co for n in nb), Vector((0.0, 0.0, 0.0))) / len(nb))
            for v, co in tip_updates.items():
                v.co = co

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        mesh = bpy.data.meshes.new(name + "_Mesh")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        for poly in mesh.polygons:
            poly.use_smooth = True
        arms.append(obj)

    return arms[0], arms[1], zs_test, xs_test


def fuse_body_and_arms_seamless(
    body_obj, arm_l_obj, arm_r_obj,
    surf_scaled, zs_test, xs_test,
    z_arm_min, z_armpit, z_arm_peak, z_arm_max,
    x_tip_bot, x_peak,
    x_safe_margin, mid_y_equator
):
    """
    Body と Arm.L / Arm.R を Boolean Union + 高解像度 Voxel Remesh (voxel_size=0.0075m) で完全一体成型ソフビメッシュ化し、
    交差シーム曲線 |X| = x_body_surf(Z) を中心とするガウシアン帯域のみに限定した
    1) Seam_Smooth_3D (3Dラプラシアン平滑化)
    2) Seam_Smooth_Y (正面2Dシルエット(X,Z)を100%不変に保つ純Y方向ラプラシアン調和曲面平滑化)
    を適用することで、腕の水平くびれや段差を一切生じさせずに斜めの交差境界筋・法線段差を完全にゼロ化する。
    """
    bpy.context.view_layer.objects.active = body_obj
    for arm_part in (arm_l_obj, arm_r_obj):
        mod_b = body_obj.modifiers.new(name="Bool_Arm", type='BOOLEAN')
        mod_b.operation = 'UNION'
        mod_b.object = arm_part
        bpy.ops.object.modifier_apply(modifier=mod_b.name)
        bpy.data.objects.remove(arm_part, do_unlink=True)

    mod_rem = body_obj.modifiers.new(name="Voxel_Remesh", type='REMESH')
    mod_rem.mode = 'VOXEL'
    mod_rem.voxel_size = 0.0075
    mod_rem.use_smooth_shade = True
    bpy.ops.object.modifier_apply(modifier=mod_rem.name)

    mesh = body_obj.data
    n_verts = len(mesh.vertices)
    coords = np.empty(n_verts * 3, dtype=np.float32)
    mesh.vertices.foreach_get("co", coords)
    coords = coords.reshape(-1, 3)

    vx = coords[:, 0].astype(np.float64)
    vy = coords[:, 1].astype(np.float64)
    vz = coords[:, 2].astype(np.float64)
    abs_x = np.abs(vx)
    xb = np.interp(vz, zs_test, xs_test)
    x_safe = xb - x_safe_margin

    # 交差シーム曲線 |X| = xb(Z) からの水平距離 d_seam
    d_seam = np.abs(abs_x - xb)

    # 1) Seam_Smooth_3D: 交差シーム周辺のガウシアン帯域 (sigma=0.055m) を3D平滑化（外縁シルエットと下端先端は完全保護）
    w_x3d = np.exp(-0.5 * (d_seam / 0.055) ** 2)
    u_z3d_low = np.clip((vz - (z_armpit - 0.025)) / 0.035, 0.0, 1.0)
    u_z3d_high = np.clip(((z_arm_max + 0.025) - vz) / 0.035, 0.0, 1.0)
    w_z3d = (u_z3d_low * u_z3d_low * (3.0 - 2.0 * u_z3d_low)) * (u_z3d_high * u_z3d_high * (3.0 - 2.0 * u_z3d_high))
    rim_protect_3d = np.clip((np.abs(vy - mid_y_equator) - 0.024) / 0.020, 0.0, 1.0)
    u_safe = np.clip((abs_x - x_safe) / 0.030, 0.0, 1.0)
    safe_mask = u_safe * u_safe * (3.0 - 2.0 * u_safe)
    w_3d = w_x3d * w_z3d * safe_mask * rim_protect_3d

    # 2) Seam_Smooth_Y: (X,Z)座標を完全固定したまま、交差シーム〜腕パドル全域のY奥行きを調和曲面平滑化し法線変化を完全連続化
    u_out_y = np.clip(((xb + 0.140) - abs_x) / 0.065, 0.0, 1.0)
    w_xy = safe_mask * (u_out_y * u_out_y * (3.0 - 2.0 * u_out_y))
    u_zl = np.clip((vz - (z_arm_min + 0.015)) / 0.045, 0.0, 1.0)
    u_zh = np.clip(((z_arm_max + 0.035) - vz) / 0.040, 0.0, 1.0)
    w_zy = (u_zl * u_zl * (3.0 - 2.0 * u_zl)) * (u_zh * u_zh * (3.0 - 2.0 * u_zh))
    eq_protect = np.clip((np.abs(vy - mid_y_equator) - 0.018) / 0.020, 0.0, 1.0)
    w_y = w_xy * w_zy * eq_protect

    vg_3d = body_obj.vertex_groups.new(name="Seam_Smooth_3D")
    idx_3d = np.where(w_3d > 1e-3)[0]
    for idx in idx_3d:
        vg_3d.add([int(idx)], float(w_3d[idx]), 'REPLACE')

    vg_y = body_obj.vertex_groups.new(name="Seam_Smooth_Y")
    idx_y = np.where(w_y > 1e-3)[0]
    for idx in idx_y:
        vg_y.add([int(idx)], float(w_y[idx]), 'REPLACE')

    mod_sm3d = body_obj.modifiers.new(name="Smooth_Seam_3D", type='SMOOTH')
    mod_sm3d.use_x = True
    mod_sm3d.use_y = True
    mod_sm3d.use_z = True
    mod_sm3d.factor = 0.55
    mod_sm3d.iterations = 45
    mod_sm3d.vertex_group = vg_3d.name
    bpy.ops.object.modifier_apply(modifier=mod_sm3d.name)

    mod_smy = body_obj.modifiers.new(name="Smooth_Seam_Y", type='SMOOTH')
    mod_smy.use_x = False
    mod_smy.use_y = True
    mod_smy.use_z = False
    mod_smy.factor = 0.68
    mod_smy.iterations = 180
    mod_smy.vertex_group = vg_y.name
    bpy.ops.object.modifier_apply(modifier=mod_smy.name)

    for vg_name in ("Seam_Smooth_3D", "Seam_Smooth_Y"):
        vg_ref = body_obj.vertex_groups.get(vg_name)
        if vg_ref is not None:
            body_obj.vertex_groups.remove(vg_ref)

    # Boolean / Remesh で生成された空マテリアルスロットをクリアし、後続のメインマテリアル(slot 0)が確実に適用されるようにする
    body_obj.data.materials.clear()
    for poly in body_obj.data.polygons:
        poly.use_smooth = True
        poly.material_index = 0
    body_obj.data.update()


def assign_seamless_body_vertex_groups(body_obj, zs_test, xs_test, z_leg_top, z_leg_span, z_arm_min, z_arm_max):
    mesh = body_obj.data
    n_verts = len(mesh.vertices)
    coords = np.empty(n_verts * 3, dtype=np.float32)
    mesh.vertices.foreach_get("co", coords)
    coords = coords.reshape(-1, 3)

    vg_body = body_obj.vertex_groups.new(name="Body")
    vg_leg_l = body_obj.vertex_groups.new(name="Leg.L")
    vg_leg_r = body_obj.vertex_groups.new(name="Leg.R")
    vg_arm_l = body_obj.vertex_groups.new(name="Arm.L")
    vg_arm_r = body_obj.vertex_groups.new(name="Arm.R")

    vx, vz = coords[:, 0], coords[:, 2]
    abs_x = np.abs(vx)
    xb = np.interp(vz, zs_test, xs_test)

    for i in range(n_verts):
        z = float(vz[i])
        x = float(vx[i])
        ax = float(abs_x[i])
        x_b = float(xb[i])
        if z < z_leg_top and ax < 0.45:
            # 股の中央(|x|<0.05)で左右脚の反対回転による裂け・筋が出ないよう smoothstep(ax) で内側ウェイトを減衰
            u_leg = float(np.clip((z_leg_top - z) / z_leg_span, 0.0, 1.0))
            ux_leg = float(np.clip((ax - 0.045) / 0.110, 0.0, 1.0))
            w_leg = (u_leg * u_leg * (3.0 - 2.0 * u_leg)) * (ux_leg * ux_leg * (3.0 - 2.0 * ux_leg))
            if x >= 0.0:
                vg_leg_l.add([i], w_leg, 'REPLACE')
            else:
                vg_leg_r.add([i], w_leg, 'REPLACE')
            vg_body.add([i], 1.0 - w_leg, 'REPLACE')
        elif (z_arm_min - 0.015 <= z <= z_arm_max + 0.015) and (ax > x_b - 0.010):
            u_arm = float(np.clip((ax - (x_b - 0.010)) / 0.050, 0.0, 1.0))
            w_arm = u_arm * u_arm * (3.0 - 2.0 * u_arm)
            if x >= 0.0:
                vg_arm_l.add([i], w_arm, 'REPLACE')
            else:
                vg_arm_r.add([i], w_arm, 'REPLACE')
            vg_body.add([i], 1.0 - w_arm, 'REPLACE')
        else:
            vg_body.add([i], 1.0, 'REPLACE')


def create_micro_grain_material(
    name,
    rgb255,
    bump_dist=0.0042,
    bump_strength=0.45,
    rough_min=0.50,
    rough_max=0.80,
    spec_ior=0.28,
    sheen_weight=0.14,
    coat_weight=0.08,
    coat_rough=0.38,
    fine_scale=68.0,
    mid_scale=18.0,
):
    """
    3Dオブジェクト座標に基づく2階層プロシージャル微細グレイン（高周波シボ粒子 fine_scale + 中周波の光ムラ mid_scale）を
    Bump法線変調・Roughness微小変調・微細Base Color明暗変調としてPrincipled BSDFに統合し、
    「ほんの少しだけざらついた心地よい梨地・フロストソフビ質感」と「微妙な光の陰影・ハイライトのニュアンス」を表現する。
    """
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')

    rgba = mod_iinet.rgb255_to_linear_rgba(*rgb255)
    mat.diffuse_color = rgba

    # 1) 3D Object Texture Coordinate
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-980, 0)

    # 2) 高周波ノイズ（微細な梨地・シボ粒子）
    noise_fine = nodes.new(type='ShaderNodeTexNoise')
    noise_fine.location = (-740, 180)
    noise_fine.inputs["Scale"].default_value = fine_scale
    noise_fine.inputs["Detail"].default_value = 6.0
    noise_fine.inputs["Roughness"].default_value = 0.65
    links.new(tex_coord.outputs["Object"], noise_fine.inputs["Vector"])

    # 3) 中周波ノイズ（微妙な光の揺らぎ・表面ニュアンス）
    noise_mid = nodes.new(type='ShaderNodeTexNoise')
    noise_mid.location = (-740, -120)
    noise_mid.inputs["Scale"].default_value = mid_scale
    noise_mid.inputs["Detail"].default_value = 3.5
    noise_mid.inputs["Roughness"].default_value = 0.55
    links.new(tex_coord.outputs["Object"], noise_mid.inputs["Vector"])

    # 4) 2階層グレイン合成 (74% 高周波シボ + 26% 中周波揺らぎ)
    mix_grain = nodes.new(type='ShaderNodeMix')
    mix_grain.data_type = 'FLOAT'
    mix_grain.location = (-520, 60)
    mix_grain.inputs["Factor"].default_value = 0.26
    links.new(noise_fine.outputs["Fac"], mix_grain.inputs["A"])
    links.new(noise_mid.outputs["Fac"], mix_grain.inputs["B"])

    # FBMノイズの [0.28..0.72] 分布を [0..1] へコントラスト正規化し、繊細な粒子ピークを鮮明化
    norm_grain = nodes.new(type='ShaderNodeMapRange')
    norm_grain.location = (-360, 60)
    norm_grain.inputs["From Min"].default_value = 0.28
    norm_grain.inputs["From Max"].default_value = 0.72
    norm_grain.inputs["To Min"].default_value = 0.0
    norm_grain.inputs["To Max"].default_value = 1.0
    links.new(mix_grain.outputs["Result"], norm_grain.inputs["Value"])

    # 5) Base Color の極微細トーン変調（上品な粒子感を保持しつつ鮮やかな発色を維持）
    r_lin, g_lin, b_lin, a_lin = rgba
    col_dark = (max(0.0, r_lin * 0.925), max(0.0, g_lin * 0.925), max(0.0, b_lin * 0.925), a_lin)
    col_light = (min(1.0, r_lin * 1.055), min(1.0, g_lin * 1.055), min(1.0, b_lin * 1.055), a_lin)
    mix_col = nodes.new(type='ShaderNodeMix')
    mix_col.data_type = 'RGBA'
    mix_col.location = (-180, 260)
    mix_col.inputs["A"].default_value = col_dark
    mix_col.inputs["B"].default_value = col_light
    links.new(norm_grain.outputs["Result"], mix_col.inputs["Factor"])
    links.new(mix_col.outputs["Result"], bsdf.inputs["Base Color"])

    # 6) Roughness の微細変調 (rough_min 〜 rough_max)
    map_rough = nodes.new(type='ShaderNodeMapRange')
    map_rough.location = (-180, 20)
    map_rough.inputs["From Min"].default_value = 0.0
    map_rough.inputs["From Max"].default_value = 1.0
    map_rough.inputs["To Min"].default_value = rough_min
    map_rough.inputs["To Max"].default_value = rough_max
    links.new(norm_grain.outputs["Result"], map_rough.inputs["Value"])
    links.new(map_rough.outputs["Result"], bsdf.inputs["Roughness"])

    # 7) Micro-Grain Bump 法線変調（ハイライト縁や明暗境界に繊細なシボ粒子の光沢ニュアンスを付与）
    bump_node = nodes.new(type='ShaderNodeBump')
    bump_node.location = (-180, -220)
    bump_node.inputs["Strength"].default_value = bump_strength
    bump_node.inputs["Distance"].default_value = bump_dist
    links.new(norm_grain.outputs["Result"], bump_node.inputs["Height"])
    links.new(bump_node.outputs["Normal"], bsdf.inputs["Normal"])

    # 8) Principled BSDF の光沢・フロスト散乱パラメータ設定
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = 0.0
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = spec_ior
    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = sheen_weight
    if "Sheen Roughness" in bsdf.inputs:
        bsdf.inputs["Sheen Roughness"].default_value = 0.42
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = coat_weight
        bsdf.inputs["Coat Roughness"].default_value = coat_rough
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.0
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = 0.0

    return mat


def create_micro_grain_globe_material():
    """地球儀テクスチャにもボディと調和する微細グレイン質感＆ソフトな光沢ニュアンスを付与"""
    mat = bpy.data.materials.new(name="Mat_Globe")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')

    tex_node = nodes.new(type='ShaderNodeTexImage')
    tex_node.location = (-550, 260)
    tex_node.image = bpy.data.images.load(mod_iinet.GLOBE_TEX_PATH, check_existing=True)
    tex_node.interpolation = 'Linear'
    links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-920, -100)

    noise_fine = nodes.new(type='ShaderNodeTexNoise')
    noise_fine.location = (-680, -40)
    noise_fine.inputs["Scale"].default_value = 78.0
    noise_fine.inputs["Detail"].default_value = 5.5
    noise_fine.inputs["Roughness"].default_value = 0.62
    links.new(tex_coord.outputs["Object"], noise_fine.inputs["Vector"])

    noise_mid = nodes.new(type='ShaderNodeTexNoise')
    noise_mid.location = (-680, -260)
    noise_mid.inputs["Scale"].default_value = 22.0
    noise_mid.inputs["Detail"].default_value = 3.0
    noise_mid.inputs["Roughness"].default_value = 0.52
    links.new(tex_coord.outputs["Object"], noise_mid.inputs["Vector"])

    mix_grain = nodes.new(type='ShaderNodeMix')
    mix_grain.data_type = 'FLOAT'
    mix_grain.location = (-460, -120)
    mix_grain.inputs["Factor"].default_value = 0.25
    links.new(noise_fine.outputs["Fac"], mix_grain.inputs["A"])
    links.new(noise_mid.outputs["Fac"], mix_grain.inputs["B"])

    map_rough = nodes.new(type='ShaderNodeMapRange')
    map_rough.location = (-240, -40)
    map_rough.inputs["From Min"].default_value = 0.28
    map_rough.inputs["From Max"].default_value = 0.72
    map_rough.inputs["To Min"].default_value = 0.52
    map_rough.inputs["To Max"].default_value = 0.76
    links.new(mix_grain.outputs["Result"], map_rough.inputs["Value"])
    links.new(map_rough.outputs["Result"], bsdf.inputs["Roughness"])

    bump_node = nodes.new(type='ShaderNodeBump')
    bump_node.location = (-240, -240)
    bump_node.inputs["Strength"].default_value = 0.34
    bump_node.inputs["Distance"].default_value = 0.0028
    links.new(mix_grain.outputs["Result"], bump_node.inputs["Height"])
    links.new(bump_node.outputs["Normal"], bsdf.inputs["Normal"])

    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.27
    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = 0.10
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.07
        bsdf.inputs["Coat Roughness"].default_value = 0.38

    return mat


# ==========================================
# 3. 2キャラクター構築（Collection_IICh & Collection_IINet）
# ==========================================
def build_iich_character(coll_iich, mat_globe, im_ref):
    data_iich = mod_iich.extract_iich_profiles()
    surf_iich = mod_iich.IIChSurfaceModel(data_iich)

    body_obj = mod_iich.create_body_mesh(surf_iich, res=136)

    # ボディにスケール(sx=0.8473, sy=0.8350, sz=0.8262)を適用して原画シルエットに完全一致させる
    z_min_raw = min(v.co.z for v in body_obj.data.vertices)
    sx, sy, sz = 0.8473, 0.8350, 0.8262
    transform_mesh_vertices(body_obj, scale_xyz=(1.0, 1.0, 1.0), offset_xyz=(0.0, 0.0, -z_min_raw))
    transform_mesh_vertices(body_obj, scale_xyz=(sx, sy, sz), offset_xyz=(0.0, 0.0, 0.0))

    # スケール後のボディ表面モデル（顔枠・目・口・ロゴのコンフォーマル投影＆シームレス融合用）
    class ScaledSurfaceAdapter:
        def __init__(self, base_surf, sx_val, sy_val, sz_val, z0_off):
            self.base = base_surf
            self.sx = sx_val
            self.sy = sy_val
            self.sz = sz_val
            self.z0 = z0_off

        def front_surface_y_and_normal(self, X, Z):
            bx = np.asarray(X, dtype=np.float64) / self.sx
            bz = np.asarray(Z, dtype=np.float64) / self.sz + self.z0
            by, nx, ny, nz = self.base.front_surface_y_and_normal(bx, bz)
            y_scaled = by * self.sy
            nx_s = nx / self.sx
            ny_s = ny / self.sy
            nz_s = nz / self.sz
            norm = np.sqrt(nx_s * nx_s + ny_s * ny_s + nz_s * nz_s)
            return y_scaled, nx_s / norm, ny_s / norm, nz_s / norm

    surf_scaled = ScaledSurfaceAdapter(surf_iich, sx, sy, sz, z_min_raw)

    arm_l_obj, arm_r_obj, zs_test_iich, xs_test_iich = create_seamless_arm_meshes_for_char(
        surf_iich, sx, sy, sz, z_min_raw,
        z_min=0.245 * sz, z_armpit=0.315 * sz, z_peak=0.320 * sz, z_max=0.555 * sz,
        x_tip_bot=0.905 * sx, x_armpit=0.695 * sx, x_peak=1.048 * sx,
        base_half_y=0.130 * sy, root_flare_gain=0.92, mid_y_base=0.040 * sy,
        prefix="IICh"
    )

    fuse_body_and_arms_seamless(
        body_obj, arm_l_obj, arm_r_obj,
        surf_scaled, zs_test_iich, xs_test_iich,
        z_arm_min=0.245 * sz, z_armpit=0.315 * sz, z_arm_peak=0.320 * sz, z_arm_max=0.555 * sz,
        x_tip_bot=0.905 * sx, x_peak=1.048 * sx,
        x_safe_margin=0.075, mid_y_equator=0.032
    )

    # 原画 ref_20261110_pair_balance.png から直接抽出した顔枠・画面・二重目・口・胸ロゴ「いい-ch」
    prof_face = extract_pair_face_profile_from_ref(
        im_ref, cx_body_px=244.50, foot_y_px=678.0, cx_face_px=245.50, cy_face_px=415.00,
        x_min_lim=0, x_max_lim=490, y_top_body=219
    )
    screen_obj, frame_obj = create_pair_face_screen_and_frame(surf_scaled, prof_face, "IICh")

    # 原画の二重オーバル目: Left Eye cx=-0.2750m, Right Eye cx=+0.3075m, cz=0.8593m, rx=0.0850m, rz=0.1140m, w_ring=0.0200m
    eye_r_obj = mod_iich.create_eye_mesh(surf_scaled, "IICh_Eye.R", cx_eye=-0.2750, cz_eye=0.8593, rx_eye=0.0850, rz_eye=0.1140, w_ring=0.0200)
    eye_l_obj = mod_iich.create_eye_mesh(surf_scaled, "IICh_Eye.L", cx_eye=+0.3075, cz_eye=0.8593, rx_eye=0.0850, rz_eye=0.1140, w_ring=0.0200)

    # 原画の口: x0_arc=+0.0184m, z_arc_center=0.8817m, r_arc=0.3471m, r_tube=0.0253m, max_ang=22.05°
    mouth_obj = create_pair_mouth_mesh(surf_scaled, "IICh_Mouth", x0_arc=+0.0184, z_arc_center=0.8817, r_arc=0.3471, r_tube=0.0253, max_ang_deg=22.05)

    # 胸ロゴ「LILI-ch」（単体モデルの直線的・シャープなデザインをペアボディ曲面へ密着）
    logo_obj = create_pair_logo_3d_mesh(surf_scaled, "IICh_Logo_LILI_ch", char_type="iich")

    ant_obj, globe_obj = create_iich_pair_antenna_and_globe(sx=sx, sy=sy, sz=sz)

    # マテリアル作成＆割り当て（微細グレイン質感＆微妙な光の陰影・ハイライトニュアンス仕様）
    mat_body_green = create_micro_grain_material(
        "IICh_Mat_Body_Green", (134, 194, 78),
        bump_dist=0.0045, bump_strength=0.46, rough_min=0.50, rough_max=0.80,
        spec_ior=0.28, sheen_weight=0.14, coat_weight=0.08, fine_scale=68.0, mid_scale=18.0
    )
    mat_frame_blue = create_micro_grain_material(
        "IICh_Mat_Frame_Blue", (52, 114, 182),
        bump_dist=0.0028, bump_strength=0.34, rough_min=0.54, rough_max=0.78,
        spec_ior=0.26, sheen_weight=0.10, coat_weight=0.06, fine_scale=78.0, mid_scale=22.0
    )
    mat_feature_blue = create_micro_grain_material(
        "IICh_Mat_Feature_Blue", (22, 96, 172),
        bump_dist=0.0022, bump_strength=0.28, rough_min=0.56, rough_max=0.76,
        spec_ior=0.25, sheen_weight=0.08, coat_weight=0.05, fine_scale=85.0, mid_scale=24.0
    )
    mat_eye_outer_blue = create_micro_grain_material(
        "IICh_Mat_Eye_Outer_Blue", (64, 134, 204),
        bump_dist=0.0022, bump_strength=0.26, rough_min=0.54, rough_max=0.74,
        spec_ior=0.26, sheen_weight=0.08, coat_weight=0.06, fine_scale=85.0, mid_scale=24.0
    )
    mat_eye_inner_navy = create_micro_grain_material(
        "IICh_Mat_Eye_Inner_Navy", (10, 68, 142),
        bump_dist=0.0022, bump_strength=0.26, rough_min=0.52, rough_max=0.72,
        spec_ior=0.27, sheen_weight=0.08, coat_weight=0.06, fine_scale=85.0, mid_scale=24.0
    )
    mat_stem_blue = create_micro_grain_material(
        "IICh_Mat_Stem_Blue", (52, 114, 182),
        bump_dist=0.0036, bump_strength=0.40, rough_min=0.52, rough_max=0.78,
        spec_ior=0.28, sheen_weight=0.11, coat_weight=0.07, fine_scale=72.0, mid_scale=20.0
    )
    mat_screen_cream = create_micro_grain_material(
        "IICh_Mat_Screen_Cream", (253, 250, 210),
        bump_dist=0.0028, bump_strength=0.32, rough_min=0.56, rough_max=0.80,
        spec_ior=0.25, sheen_weight=0.12, coat_weight=0.06, fine_scale=75.0, mid_scale=20.0
    )
    mat_logo_yellow = create_micro_grain_material(
        "IICh_Mat_Logo_Yellow", (252, 242, 20),
        bump_dist=0.0028, bump_strength=0.34, rough_min=0.50, rough_max=0.74,
        spec_ior=0.28, sheen_weight=0.10, coat_weight=0.08, fine_scale=80.0, mid_scale=22.0
    )
    mat_logo_side = create_micro_grain_material(
        "IICh_Mat_Logo_Side", (185, 130, 0),
        bump_dist=0.0028, bump_strength=0.34, rough_min=0.54, rough_max=0.76,
        spec_ior=0.26, sheen_weight=0.10, coat_weight=0.06, fine_scale=80.0, mid_scale=22.0
    )

    body_obj.data.materials.append(mat_body_green)
    logo_obj.data.materials.append(mat_logo_yellow)
    logo_obj.data.materials.append(mat_logo_side)
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
        ant_obj, globe_obj,
    ]

    rename_map = [
        (body_obj, "IICh_Body"),
        (logo_obj, "IICh_Logo_LILI_ch"),
        (screen_obj, "IICh_Face_Screen"),
        (frame_obj, "IICh_Face_Frame"),
        (eye_l_obj, "IICh_Eye.L"),
        (eye_r_obj, "IICh_Eye.R"),
        (mouth_obj, "IICh_Mouth"),
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
    b_leg_l.parent = b_root

    b_leg_r = eb.new("Leg.R")
    b_leg_r.head = (-0.2625 * sx, 0.0, 0.14)
    b_leg_r.tail = (-0.2625 * sx, 0.0, 0.0)
    b_leg_r.parent = b_root

    b_arm_l = eb.new("Arm.L")
    b_arm_l.head = (0.82 * sx, 0.03, 0.52 * sz)
    b_arm_l.tail = (1.03 * sx, 0.03, 0.28 * sz)
    b_arm_l.parent = b_body

    b_arm_r = eb.new("Arm.R")
    b_arm_r.head = (-0.82 * sx, 0.03, 0.52 * sz)
    b_arm_r.tail = (-1.03 * sx, 0.03, 0.28 * sz)
    b_arm_r.parent = b_body

    b_ant1 = eb.new("Antenna_1")
    b_ant1.head = (0.0, 0.547, 0.438)
    b_ant1.tail = (0.0, 0.785, 1.050)
    b_ant1.parent = b_body

    b_ant2 = eb.new("Antenna_2")
    b_ant2.head = (0.0, 0.785, 1.050)
    b_ant2.tail = (-0.246, 0.550, 2.051)
    b_ant2.parent = b_ant1
    b_ant2.use_connect = True

    b_globe = eb.new("Globe")
    b_globe.head = (-0.246, 0.550, 1.885)
    b_globe.tail = (-0.246, 0.550, 2.218)
    b_globe.parent = b_ant2

    bpy.ops.object.mode_set(mode='OBJECT')

    for obj in all_meshes:
        obj.parent = arm_obj
        mod = obj.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = arm_obj
        short_name = obj.name.replace("IICh_", "")
        if short_name == "Body":
            assign_seamless_body_vertex_groups(
                obj, zs_test_iich, xs_test_iich,
                z_leg_top=0.16, z_leg_span=0.13,
                z_arm_min=0.245 * sz, z_arm_max=0.555 * sz
            )
        elif short_name in ("Face_Screen", "Face_Frame", "Eye.L", "Eye.R", "Mouth", "Logo_LILI_ch"):
            vg = obj.vertex_groups.new(name="Body")
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

    arm_obj.location = Vector((-0.946, -0.025, 0.0036))
    move_objects_to_collection([arm_obj] + all_meshes, coll_iich)
    return arm_obj, all_meshes


def build_iinet_character(coll_iinet, mat_globe, im_ref):
    data_iinet = mod_iinet.extract_textures_and_profiles()
    surf_iinet = mod_iinet.IINetSurfaceModel(data_iinet)

    body_obj = mod_iinet.create_body_mesh(surf_iinet, res=136)

    z_min_raw = min(v.co.z for v in body_obj.data.vertices)
    sz_iinet = 2.0080 / (2.0080 - z_min_raw)  # 0.97334
    sx_iinet = 1.8126 / 1.8178                 # 0.99714

    transform_mesh_vertices(body_obj, scale_xyz=(1.0, 1.0, 1.0), offset_xyz=(0.0, 0.0, -z_min_raw))
    transform_mesh_vertices(body_obj, scale_xyz=(sx_iinet, 1.0, sz_iinet), offset_xyz=(0.0, 0.0, 0.0))

    class ScaledIINetSurfaceAdapter:
        def __init__(self, base_surf, sx_val, sz_val, z0_off):
            self.base = base_surf
            self.sx = sx_val
            self.sz = sz_val
            self.z0 = z0_off

        def front_surface_y_and_normal(self, X, Z):
            bx = np.asarray(X, dtype=np.float64) / self.sx
            bz = np.asarray(Z, dtype=np.float64) / self.sz + self.z0
            by, nx, ny, nz = self.base.front_surface_y_and_normal(bx, bz)
            nx_s = nx / self.sx
            ny_s = ny
            nz_s = nz / self.sz
            norm = np.sqrt(nx_s * nx_s + ny_s * ny_s + nz_s * nz_s)
            return by, nx_s / norm, ny_s / norm, nz_s / norm

    surf_scaled = ScaledIINetSurfaceAdapter(surf_iinet, sx_iinet, sz_iinet, z_min_raw)

    arm_l_obj, arm_r_obj, zs_test_iinet, xs_test_iinet = create_seamless_arm_meshes_for_char(
        surf_iinet, sx_iinet, 1.0, sz_iinet, z_min_raw,
        z_min=0.2820, z_armpit=0.3460, z_peak=0.3727, z_max=0.6680,
        x_tip_bot=0.8680, x_armpit=0.6850, x_peak=0.9823,
        base_half_y=0.130, root_flare_gain=0.98, mid_y_base=0.048,
        prefix="IINet"
    )

    fuse_body_and_arms_seamless(
        body_obj, arm_l_obj, arm_r_obj,
        surf_scaled, zs_test_iinet, xs_test_iinet,
        z_arm_min=0.2820, z_armpit=0.3460, z_arm_peak=0.3727, z_arm_max=0.6680,
        x_tip_bot=0.8680, x_peak=0.9823,
        x_safe_margin=0.095, mid_y_equator=0.040
    )

    # 原画 ref_20261110_pair_balance.png から直接抽出した顔枠・画面・目・スマイル口・胸ロゴ「いい-net」
    prof_face = extract_pair_face_profile_from_ref(
        im_ref, cx_body_px=749.50, foot_y_px=679.0, cx_face_px=750.50, cy_face_px=335.50,
        x_min_lim=475, x_max_lim=1024, y_top_body=124
    )
    screen_obj, frame_obj = create_pair_face_screen_and_frame(surf_scaled, prof_face, "IINet")

    # 原画の丸目: Left Eye cx=-0.2677m, Right Eye cx=+0.3075m, cz=1.2934m, radius=0.0742m
    eye_r_obj = mod_iinet.create_eye_mesh(surf_scaled, "IINet_Eye.R", cx_eye=-0.2677, cz_eye=1.2934, radius=0.0742)
    eye_l_obj = mod_iinet.create_eye_mesh(surf_scaled, "IINet_Eye.L", cx_eye=+0.3075, cz_eye=1.2934, radius=0.0742)

    # 原画の大きなスマイル口: x0_arc=+0.0109m, z_arc_center=1.5334m, r_arc=0.7229m, r_tube=0.0253m, max_ang=45.11°
    mouth_obj = create_pair_mouth_mesh(surf_scaled, "IINet_Mouth", x0_arc=+0.0109, z_arc_center=1.5334, r_arc=0.7229, r_tube=0.0253, max_ang_deg=45.11)

    # 胸ロゴ「LILI-net」（単体モデルの直線的・シャープなデザインをペアボディ曲面へ密着）
    logo_obj = create_pair_logo_3d_mesh(surf_scaled, "IINet_Logo_LILI_net", char_type="iinet")

    ant_obj, globe_obj = create_iinet_pair_antenna_and_globe(data_iinet, sz_iinet=sz_iinet)

    all_meshes = [
        body_obj, logo_obj, screen_obj, frame_obj,
        eye_l_obj, eye_r_obj, mouth_obj,
        ant_obj, globe_obj,
    ]

    mat_body_pink = create_micro_grain_material(
        "IINet_Mat_Body_Pink", (245, 82, 164),
        bump_dist=0.0045, bump_strength=0.46, rough_min=0.50, rough_max=0.80,
        spec_ior=0.28, sheen_weight=0.14, coat_weight=0.08, fine_scale=68.0, mid_scale=18.0
    )
    mat_frame_blue = create_micro_grain_material(
        "IINet_Mat_Frame_Blue", (58, 90, 174),
        bump_dist=0.0028, bump_strength=0.34, rough_min=0.54, rough_max=0.78,
        spec_ior=0.26, sheen_weight=0.10, coat_weight=0.06, fine_scale=78.0, mid_scale=22.0
    )
    mat_feature_blue = create_micro_grain_material(
        "IINet_Mat_Feature_Blue", (46, 76, 168),
        bump_dist=0.0022, bump_strength=0.28, rough_min=0.56, rough_max=0.76,
        spec_ior=0.25, sheen_weight=0.08, coat_weight=0.05, fine_scale=85.0, mid_scale=24.0
    )
    mat_stem_blue = create_micro_grain_material(
        "IINet_Mat_Stem_Blue", (58, 92, 172),
        bump_dist=0.0036, bump_strength=0.40, rough_min=0.52, rough_max=0.78,
        spec_ior=0.28, sheen_weight=0.11, coat_weight=0.07, fine_scale=72.0, mid_scale=20.0
    )
    mat_screen_cream = create_micro_grain_material(
        "IINet_Mat_Screen_Cream", (250, 228, 156),
        bump_dist=0.0028, bump_strength=0.32, rough_min=0.56, rough_max=0.80,
        spec_ior=0.25, sheen_weight=0.12, coat_weight=0.06, fine_scale=75.0, mid_scale=20.0
    )
    mat_logo_yellow = create_micro_grain_material(
        "IINet_Mat_Logo_Yellow", (255, 242, 15),
        bump_dist=0.0028, bump_strength=0.34, rough_min=0.50, rough_max=0.74,
        spec_ior=0.28, sheen_weight=0.10, coat_weight=0.08, fine_scale=80.0, mid_scale=22.0
    )
    mat_logo_side = create_micro_grain_material(
        "IINet_Mat_Logo_Side", (185, 125, 0),
        bump_dist=0.0028, bump_strength=0.34, rough_min=0.54, rough_max=0.76,
        spec_ior=0.26, sheen_weight=0.10, coat_weight=0.06, fine_scale=80.0, mid_scale=22.0
    )

    body_obj.data.materials.append(mat_body_pink)
    logo_obj.data.materials.append(mat_logo_yellow)
    logo_obj.data.materials.append(mat_logo_side)
    frame_obj.data.materials.append(mat_frame_blue)
    screen_obj.data.materials.append(mat_screen_cream)
    eye_l_obj.data.materials.append(mat_feature_blue)
    eye_r_obj.data.materials.append(mat_feature_blue)
    mouth_obj.data.materials.append(mat_feature_blue)
    ant_obj.data.materials.append(mat_stem_blue)
    globe_obj.data.materials.append(mat_globe)

    rename_map = [
        (body_obj, "IINet_Body"),
        (logo_obj, "IINet_Logo_LILI_net"),
        (screen_obj, "IINet_Face_Screen"),
        (frame_obj, "IINet_Face_Frame"),
        (eye_l_obj, "IINet_Eye.L"),
        (eye_r_obj, "IINet_Eye.R"),
        (mouth_obj, "IINet_Mouth"),
        (ant_obj, "IINet_Antenna"),
        (globe_obj, "IINet_Globe"),
    ]
    for obj, new_name in rename_map:
        obj.name = new_name
        obj.data.name = new_name + "_Mesh"

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
    b_leg_l.parent = b_root

    b_leg_r = eb.new("Leg.R")
    b_leg_r.head = (-0.245, 0.0, 0.18)
    b_leg_r.tail = (-0.230, 0.0, 0.0)
    b_leg_r.parent = b_root

    b_arm_l = eb.new("Arm.L")
    b_arm_l.head = (0.76, 0.015, 0.58)
    b_arm_l.tail = (0.94, 0.015, 0.34)
    b_arm_l.parent = b_body

    b_arm_r = eb.new("Arm.R")
    b_arm_r.head = (-0.76, 0.015, 0.58)
    b_arm_r.tail = (-0.94, 0.015, 0.34)
    b_arm_r.parent = b_body

    b_ant1 = eb.new("Antenna_1")
    b_ant1.head = (0.0, 0.65, 0.55)
    b_ant1.tail = (0.0, 1.09, 1.15)
    b_ant1.parent = b_body

    b_ant2 = eb.new("Antenna_2")
    b_ant2.head = (0.0, 1.09, 1.15)
    b_ant2.tail = (0.04, 0.975, 1.60)
    b_ant2.parent = b_ant1
    b_ant2.use_connect = True

    b_ant3 = eb.new("Antenna_3")
    b_ant3.head = (0.04, 0.975, 1.60)
    b_ant3.tail = (0.3256, 1.050, 2.283)
    b_ant3.parent = b_ant2
    b_ant3.use_connect = True

    b_globe = eb.new("Globe")
    b_globe.head = (0.3256, 1.050, 2.100)
    b_globe.tail = (0.3256, 1.050, 2.467)
    b_globe.parent = b_ant3

    bpy.ops.object.mode_set(mode='OBJECT')

    for obj in all_meshes:
        obj.parent = arm_obj
        mod = obj.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = arm_obj
        short_name = obj.name.replace("IINet_", "")
        if short_name == "Body":
            assign_seamless_body_vertex_groups(
                obj, zs_test_iinet, xs_test_iinet,
                z_leg_top=0.24, z_leg_span=0.16,
                z_arm_min=0.2820, z_arm_max=0.6680
            )
        elif short_name in ("Face_Screen", "Face_Frame", "Eye.L", "Eye.R", "Mouth", "Logo_LILI_net"):
            vg = obj.vertex_groups.new(name="Body")
            vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
        elif short_name == "Globe":
            vg = obj.vertex_groups.new(name="Globe")
            vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
        elif short_name == "Antenna":
            vg1 = obj.vertex_groups.new(name="Antenna_1")
            vg2 = obj.vertex_groups.new(name="Antenna_2")
            vg3 = obj.vertex_groups.new(name="Antenna_3")
            for v in obj.data.vertices:
                if v.co.z < 1.15:
                    vg1.add([v.index], 1.0, 'REPLACE')
                elif v.co.z < 1.60:
                    vg2.add([v.index], 1.0, 'REPLACE')
                else:
                    vg3.add([v.index], 1.0, 'REPLACE')

    arm_obj.location = Vector((+0.881, +0.025, 0.000))
    move_objects_to_collection([arm_obj] + all_meshes, coll_iinet)
    return arm_obj, all_meshes


# ==========================================
# 4. ペアシーン用ライティング・カメラ・合成・オーバーレイ監査
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


def generate_audit_overlay(front_raw_rgba, ref_im):
    rh_ref, rw_ref, _ = ref_im.shape
    h_ren, w_ren, _ = front_raw_rgba.shape
    px_per_m_ren = w_ren / 4.35
    cx_ren = w_ren * 0.5
    cy_ren = h_ren * 0.5  # Z = 1.22 m

    xs_ref = np.arange(rw_ref, dtype=np.float32)
    ys_ref = np.arange(rh_ref, dtype=np.float32)
    X_world = +0.8810 + (xs_ref - 749.50) / PX_PER_M_REF
    Z_world = (679.0 - ys_ref) / PX_PER_M_REF

    rx_f = np.clip(np.round(cx_ren + X_world * px_per_m_ren).astype(int), 0, w_ren - 1)
    ry_f = np.clip(np.round(cy_ren - (Z_world - 1.22) * px_per_m_ren).astype(int), 0, h_ren - 1)

    ren_aligned = front_raw_rgba[ry_f[:, None], rx_f[None, :]]

    panel_w = rw_ref
    panel_h = rh_ref
    comp = np.full((panel_h, panel_w * 3 + 32, 4), 255, dtype=np.uint8)

    def blend_on_white(rgba):
        a = rgba[:, :, 3:4].astype(np.float32) / 255.0
        return np.clip(rgba[:, :, :3].astype(np.float32) * a + 255.0 * (1.0 - a), 0, 255).astype(np.uint8)

    p_ref = blend_on_white(ref_im)
    p_ren = blend_on_white(ren_aligned)
    p_ovl = (0.48 * p_ref.astype(np.float32) + 0.52 * p_ren.astype(np.float32)).astype(np.uint8)

    m_ref = ref_im[:, :, 3] > 128
    m_ren = ren_aligned[:, :, 3] > 128
    edge_ref = m_ref ^ np.roll(m_ref, 1, axis=0) | m_ref ^ np.roll(m_ref, 1, axis=1)
    edge_ren = m_ren ^ np.roll(m_ren, 1, axis=0) | m_ren ^ np.roll(m_ren, 1, axis=1)
    p_ovl[edge_ref] = [255, 30, 30]
    p_ovl[edge_ren] = [0, 180, 255]

    comp[:, 0:panel_w, :3] = p_ref
    comp[:, panel_w + 16:panel_w * 2 + 16, :3] = p_ren
    comp[:, panel_w * 2 + 32:panel_w * 3 + 32, :3] = p_ovl

    inter = np.logical_and(m_ref, m_ren).sum()
    union = np.logical_or(m_ref, m_ren).sum()
    iou = (inter / union) * 100.0 if union > 0 else 0.0
    print(f"=== PAIR SILHOUETTE OVERLAY IoU: {iou:.2f}% ===")

    mod_iinet.save_rgba_uint8_as_png(comp, AUDIT_OVERLAY_PATH)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    mod_iinet.configure_cycles_gpu(scene)
    scene.cycles.samples = 96
    if hasattr(scene.cycles, "denoising_input_passes"):
        scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    if hasattr(scene.cycles, "denoising_prefilter"):
        scene.cycles.denoising_prefilter = 'ACCURATE'

    coll_iich = bpy.data.collections.new("Collection_IICh")
    coll_iinet = bpy.data.collections.new("Collection_IINet")
    scene.collection.children.link(coll_iich)
    scene.collection.children.link(coll_iinet)

    if not os.path.exists(mod_iinet.GLOBE_TEX_PATH):
        mod_iinet.extract_textures_and_profiles()
    mat_globe = create_micro_grain_globe_material()

    im_ref = mod_iinet.load_image_rgba_uint8(REF_PAIR_PATH)

    build_iich_character(coll_iich, mat_globe, im_ref)
    build_iinet_character(coll_iinet, mat_globe, im_ref)
    bpy.context.view_layer.update()

    setup_pair_lighting_and_world()
    mod_iinet.disable_freestyle_outline()

    cam_data = bpy.data.cameras.new("PairRenderCam")
    cam_obj = bpy.data.objects.new("PairRenderCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    set_pair_camera_pose(cam_obj, (0.0, -7.5, 1.22), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), ortho=True, ortho_scale=4.35)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=PAIR_BLEND_PATH)
    bpy.ops.export_scene.gltf(filepath=PAIR_GLB_PATH, export_format='GLB')

    rw, rh = 1600, 1200
    tmp_render = os.path.join(SCRIPT_DIR, "_tmp_pair_render.png")

    # 1) 正面オルソビュー (pair_iich_and_iinet_front.png) & 原画オーバーレイ監査画像
    set_pair_camera_pose(cam_obj, (0.0, -7.5, 1.22), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), ortho=True, ortho_scale=4.35)
    front_raw = mod_iinet.render_view_to_array(cam_obj, rw, rh, tmp_render, transparent=True)
    generate_audit_overlay(front_raw, im_ref)
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
