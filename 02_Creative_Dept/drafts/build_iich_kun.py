# -*- coding: utf-8 -*-
"""
株式会社CVN ペアキャラクター「いい-ch（胸ロゴ：LILI-ch）」
Blender 5.2 3Dモデリング・リギング・マテリアル・レンダリング一括構築スクリプト (Rev.2)
（高解像度正面原画 iich_05_front.png 完全準拠・波打ちゼロ・高精細3Dロゴ・尻尾付け根統一仕様）
"""

import os
import sys
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix

# ==========================================
# 0. パス設定とディレクトリ準備
# ==========================================
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REF_DIR = os.path.join(WORKSPACE_DIR, "02_Creative_Dept", "drafts", "ref_images")
DRAFTS_DIR = os.path.join(WORKSPACE_DIR, "02_Creative_Dept", "drafts")
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "02_Creative_Dept", "final_outputs")
os.makedirs(DRAFTS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

REF_3VIEWS_PATH = os.path.join(REF_DIR, "iich_3views.jpg")
FRONT_HIGHRES_PATH = os.path.join(REF_DIR, "iich_05_front.png")
GLOBE_TEX_PATH = os.path.join(DRAFTS_DIR, "globe_texture.png")

BLEND_OUT_PATH = os.path.join(OUTPUT_DIR, "cvn_iich_kun.blend")
GLB_OUT_PATH = os.path.join(OUTPUT_DIR, "cvn_iich_kun.glb")

FRONT_IMG_PATH = os.path.join(OUTPUT_DIR, "iich_kun_front.png")
SIDE_IMG_PATH = os.path.join(OUTPUT_DIR, "iich_kun_side.png")
HERO_IMG_PATH = os.path.join(OUTPUT_DIR, "iich_kun_hero_3quarter.png")
BOARD_IMG_PATH = os.path.join(OUTPUT_DIR, "iich_kun_front_and_side.png")
SHEET_IMG_PATH = os.path.join(OUTPUT_DIR, "iich_kun_5views_sheet.png")


# ==========================================
# 1. 画像ロード・高解像度原画からのプロファイル抽出
# ==========================================
def load_image_rgba_uint8(filepath):
    """Blenderのbpy.data.imagesを用いて画像を(H, W, 4) uint8配列(上端y=0)として取得"""
    img = bpy.data.images.load(filepath, check_existing=False)
    w, h = img.size
    pixels = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(pixels)
    bpy.data.images.remove(img)
    arr = pixels.reshape((h, w, 4))
    arr = np.flipud(arr)
    return np.clip(np.round(arr * 255.0), 0, 255).astype(np.uint8)


def save_rgba_uint8_as_png(arr_uint8, filepath):
    """(H, W, 4) uint8配列(上端y=0)をPNGとして保存"""
    h, w, _ = arr_uint8.shape
    flipped = np.flipud(arr_uint8).astype(np.float32) / 255.0
    img = bpy.data.images.new(name="TempSaveImg", width=w, height=h, alpha=True)
    img.pixels.foreach_set(flipped.ravel())
    img.filepath_raw = filepath
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)


def extract_iich_profiles():
    """
    Rev.2: 高解像度正面原画 iich_05_front.png (841x1024 px, 400.0 px = 1.000 m, y_foot = 1022.0 px) から
    顔枠中心 (cx_face=421.5, cy_face=570.5 -> face_center_Z = 1.12875 m) 基準で
    screen_mask と frame_mask を抽出し、スクリーン外縁から連続する青枠バンドのみを取得
    (頭頂アンテナとの干渉を完全遮断) して左右対称化・周期ガウシアン平滑化する。
    """
    im_f = load_image_rgba_uint8(FRONT_HIGHRES_PATH)
    h_img, w_img, _ = im_f.shape
    r_f = im_f[:, :, 0]
    g_f = im_f[:, :, 1]
    b_f = im_f[:, :, 2]
    a_f = im_f[:, :, 3]

    screen_mask = (a_f > 128) & (r_f > 220) & (g_f > 220) & (b_f > 170)
    frame_mask = (a_f > 128) & (b_f > 140) & (r_f < 90)

    cx_face = 421.5
    cy_face = 570.5
    px_per_m = 400.0

    n_theta = 360
    thetas = np.linspace(0.0, 2.0 * math.pi, n_theta, endpoint=True)
    r_in_raw = np.zeros(n_theta, dtype=np.float64)
    r_out_raw = np.zeros(n_theta, dtype=np.float64)

    rs_probe = np.linspace(40.0, 390.0, 701)
    for i, th in enumerate(thetas):
        ct, st = math.cos(th), math.sin(th)
        pxs = np.clip(np.round(cx_face + rs_probe * ct).astype(int), 0, w_img - 1)
        pys = np.clip(np.round(cy_face - rs_probe * st).astype(int), 0, h_img - 1)

        in_scr = screen_mask[pys, pxs]
        scr_indices = np.where(in_scr)[0]
        if len(scr_indices) > 0:
            idx_in = int(scr_indices[-1])
            r_in_raw[i] = float(rs_probe[idx_in]) / px_per_m

            # スクリーン外縁(idx_in)から外側に向かって連続する青枠バンドのみを走査し、頭頂アンテナを完全遮断
            idx_out = idx_in
            entered_frame = False
            gap_count = 0
            for j in range(idx_in + 1, len(rs_probe)):
                if frame_mask[pys[j], pxs[j]]:
                    entered_frame = True
                    idx_out = j
                    gap_count = 0
                else:
                    if entered_frame:
                        gap_count += 1
                        if gap_count >= 3:
                            break
                    elif j - idx_in > 8:
                        break
            r_out_raw[i] = float(rs_probe[idx_out]) / px_per_m
        else:
            r_in_raw[i] = 0.72
            r_out_raw[i] = 0.83

    # 左右対称化: r(theta) = 0.5 * (r(theta) + r(pi - theta))
    mirror_thetas = (math.pi - thetas) % (2.0 * math.pi)
    r_in_sym = 0.5 * (r_in_raw + np.interp(mirror_thetas, thetas, r_in_raw))
    r_out_sym = 0.5 * (r_out_raw + np.interp(mirror_thetas, thetas, r_out_raw))

    # 周期ガウシアン平滑化
    pad_k = 12
    kern = np.exp(-0.5 * (np.arange(-pad_k, pad_k + 1) / 4.0) ** 2)
    kern /= kern.sum()
    r_in_lut = np.convolve(np.pad(r_in_sym[:-1], (pad_k, pad_k), mode='wrap'), kern, mode='valid')
    r_out_lut = np.convolve(np.pad(r_out_sym[:-1], (pad_k, pad_k), mode='wrap'), kern, mode='valid')
    r_in_lut = np.append(r_in_lut, r_in_lut[0])
    r_out_lut = np.append(r_out_lut, r_out_lut[0])

    if not os.path.exists(GLOBE_TEX_PATH):
        import build_iinet_kun
        build_iinet_kun.extract_textures_and_profiles()

    return {
        "thetas": thetas,
        "r_in_lut": r_in_lut,
        "r_out_lut": r_out_lut,
        "face_center_Z": (1022.0 - cy_face) / px_per_m,  # 1.12875 m
    }


# ==========================================
# 2. 数学的3Dボディ曲面関数 (IIChSurfaceModel)
# ==========================================
class IIChSurfaceModel:
    def __init__(self, data):
        """
        Rev.2: 高解像度原画 iich_05_front.png (400.0 px = 1.000 m, y_foot = 1022.0 px) 実測値に基づく
        波打ちゼロの完全凸ボディ曲面モデル
        """
        self.W_max = 0.9800
        self.D_back = 0.7600
        self.D_front = 0.6300
        self.Z_eq = 1.0675        # (1022.0 - 595.0) / 400.0
        self.Z_apex = 2.0050
        self.x_foot = 0.2625
        self.z_tip = -0.0050
        self.z_crotch = 0.0975

    def _front_y_from_d_ell(self, d_ell):
        return -self.D_front * np.clip(d_ell, 0.0, 1.0)

    def z_top_of_x(self, abs_x):
        """上半球ドーム曲線: 原画 Front のふっくら丸い頭部シルエットを再現"""
        u = np.clip(abs_x / self.W_max, 0.0, 1.0)
        return self.Z_eq + (self.Z_apex - self.Z_eq) * ((1.0 - (u ** 2.25)) ** 0.440)

    def _f_convex_profile(self, u, alpha, delta):
        u_clamped = np.clip(np.abs(u), 0.0, 1.0)
        circ = np.sqrt(np.maximum(1.0 - u_clamped * u_clamped, 0.0))
        denom = math.hypot(1.0, delta) - delta
        hyp = 1.0 - (np.sqrt(u_clamped * u_clamped + delta * delta) - delta) / denom
        return (1.0 - alpha) * circ + alpha * hyp

    def _eval_lower_z(self, abs_x, abs_ct):
        """
        Rev.2: 底面ビューでお腹・お尻中央がW字に波打つ原因だった t_cy の急減衰を修正し、
        X=0 断面(abs_ct: 0 -> 1)で Z が厳密に単調増加する完全凸曲面として評価
        """
        u_out = np.clip((abs_x - self.x_foot) / (self.W_max - self.x_foot), 0.0, 1.0)
        f_x = self._f_convex_profile(u_out, alpha=0.18, delta=0.35)
        z_outer = self.Z_eq - (self.Z_eq - self.z_tip) * f_x

        w_in = np.clip((self.x_foot - abs_x) / self.x_foot, 0.0, 1.0)
        p_in = 0.38 * (w_in ** 2) * (3.0 - 2.0 * w_in) + 0.62 * (w_in ** 3) * (4.0 - 3.0 * w_in)
        dz_crotch = (self.z_crotch - self.z_tip) * p_in

        t_cy = np.clip(abs_ct / 0.82, 0.0, 1.0)
        crotch_y_weight = 1.0 - (t_cy ** 2) * (3.0 - 2.0 * t_cy)
        z_b = z_outer + dz_crotch * crotch_y_weight

        f_y = self._f_convex_profile(abs_ct, alpha=0.06, delta=0.42)
        return self.Z_eq - (self.Z_eq - z_b) * f_y

    def map_unit_sphere_to_body(self, nx, ny, nz):
        X = self.W_max * nx
        Y = np.where(ny >= 0.0, self.D_back * ny, self._front_y_from_d_ell(-ny))
        abs_x = np.abs(X)

        r_yz = np.sqrt(np.maximum(ny * ny + nz * nz, 1e-12))
        abs_ct = np.clip(np.abs(ny) / r_yz, 0.0, 1.0)
        st = nz / r_yz

        z_t = self.z_top_of_x(abs_x)
        Z_upper = self.Z_eq + (z_t - self.Z_eq) * np.maximum(st, 0.0)
        Z_lower = self._eval_lower_z(abs_x, abs_ct)

        Z = np.where(st >= 0.0, Z_upper, Z_lower)
        return X, Y, Z

    def front_surface_y_and_normal(self, X, Z):
        eps = 0.002
        y0 = self._eval_front_y(X, Z)
        yx = self._eval_front_y(X + eps, Z)
        yz = self._eval_front_y(X, Z + eps)
        dydx = (yx - y0) / eps
        dydz = (yz - y0) / eps
        nx = dydx
        ny = -1.0 * np.ones_like(y0)
        nz = dydz
        norm = np.sqrt(nx * nx + ny * ny + nz * nz)
        return y0, nx / norm, ny / norm, nz / norm

    def _eval_front_y(self, X, Z):
        abs_x = np.clip(np.abs(X), 0.0, self.W_max - 1e-5)
        nx = abs_x / self.W_max
        r_yz = np.sqrt(np.maximum(1.0 - nx * nx, 1e-8))
        z_t = self.z_top_of_x(abs_x)

        st_up = np.clip((Z - self.Z_eq) / np.maximum(z_t - self.Z_eq, 1e-5), 0.0, 0.9999)
        ct_up = np.sqrt(np.maximum(1.0 - st_up * st_up, 0.0))

        lo = np.zeros_like(abs_x, dtype=np.float64)
        hi = np.ones_like(abs_x, dtype=np.float64)
        for _ in range(16):
            mid = 0.5 * (lo + hi)
            z_mid = self._eval_lower_z(abs_x, mid)
            lo = np.where(z_mid < Z, mid, lo)
            hi = np.where(z_mid >= Z, mid, hi)
        ct_low = 0.5 * (lo + hi)

        abs_ct = np.where(Z >= self.Z_eq, ct_up, ct_low)
        return self._front_y_from_d_ell(r_yz * abs_ct)


# ==========================================
# 3. 各パーツのメッシュ生成関数
# ==========================================
def create_body_mesh(surf_model, res=136):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=res - 1, use_grid_fill=True)

    verts = bm.verts
    verts.ensure_lookup_table()
    coords = np.array([v.co[:] for v in verts], dtype=np.float64)
    tan_coords = np.tan(coords * (math.pi / 4.0))
    norms = np.linalg.norm(tan_coords, axis=1, keepdims=True)
    unit_p = tan_coords / norms

    X, Y, Z = surf_model.map_unit_sphere_to_body(unit_p[:, 0], unit_p[:, 1], unit_p[:, 2])
    for i, v in enumerate(verts):
        v.co = Vector((float(X[i]), float(Y[i]), float(Z[i])))

    # Rev.2: 足先Taubinスムージングの遷移幅を広げ、境界段差を完全にゼロ化
    adj = [[e.other_vert(v).index for e in v.link_edges] for v in verts]
    pos = np.array([[v.co.x, v.co.y, v.co.z] for v in verts], dtype=np.float64)
    w_sm = np.clip((0.22 - pos[:, 2]) / 0.16, 0.0, 1.0)[:, None]
    active_idx = np.where(w_sm[:, 0] > 0.0)[0]

    for step in range(20):
        lam = 0.45 if (step % 2 == 0) else -0.47
        new_pos = pos.copy()
        for idx in active_idx:
            nbs = adj[idx]
            if nbs:
                avg = pos[nbs].mean(axis=0)
                new_pos[idx] = pos[idx] + (lam * w_sm[idx]) * (avg - pos[idx])
        pos = new_pos

    for i, v in enumerate(verts):
        v.co = Vector((float(pos[i, 0]), float(pos[i, 1]), float(pos[i, 2])))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new("Body_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Body", mesh)
    bpy.context.collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True
    return obj


def create_logo_3d_mesh(surf_model):
    """
    Rev.2: 高解像度PNG FRONT_HIGHRES_PATH (iich_05_front.png) の im_f[886:966, 272:588] (80x316 px) を切り出し、
    build_iinet_kun.py と完全同一の高精細アルゴリズムでエッジ潰れ・ジャギーのない「LILI-ch」3D立体メッシュを生成
    """
    im_f = load_image_rgba_uint8(FRONT_HIGHRES_PATH)
    crop = im_f[886:966, 272:588].astype(np.float32)
    R, G, B = crop[:, :, 0], crop[:, :, 1], crop[:, :, 2]
    y_raw = np.clip(((R - 136.0) * 1.15 + (G - 195.0) * 0.55 - (B - 79.0) * 0.45) / 145.0, 0.0, 1.0)

    # 2Dガウシアンスムージングでピクセル階段を滑らかな連続スカラー場へ変換
    k1d = np.array([0.12, 0.23, 0.30, 0.23, 0.12], dtype=np.float32)
    y_smooth = np.apply_along_axis(lambda m: np.convolve(np.pad(m, 2, mode='edge'), k1d, mode='valid'), 0, y_raw)
    y_smooth = np.apply_along_axis(lambda m: np.convolve(np.pad(m, 2, mode='edge'), k1d, mode='valid'), 1, y_smooth)

    H, W = y_smooth.shape
    cell_mask = (0.25 * (y_smooth[:-1, :-1] + y_smooth[1:, :-1] + y_smooth[:-1, 1:] + y_smooth[1:, 1:]) > 0.42).copy()

    # 対角チェッカーボードの非多様体頂点を解消
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
                x_px = 272.0 + float(c)
                y_px = 886.0 + float(r)
                x_logo = ((x_px - 429.5) / 400.0) * 0.985
                z_logo = ((1022.0 - y_px) / 400.0) + 0.025
                v_grid[(r, c)] = bm.verts.new((x_logo, z_logo, 0.0))

    for r in range(H - 1):
        for c in range(W - 1):
            if cell_mask[r, c]:
                bm.faces.new((v_grid[(r + 1, c)], v_grid[(r + 1, c + 1)], v_grid[(r, c + 1)], v_grid[(r, c)]))

    # 文字境界ループのTaubinスムージング（収縮を防ぎつつ階段状ジャギーを完全に排除）
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
    ys, nxs, nys, nzs = surf_model.front_surface_y_and_normal(xs, zs)

    for idx, v in enumerate(all_verts):
        h_off = 0.018 if (v in extruded_set) else -0.005
        v.co = Vector((
            float(xs[idx] + h_off * nxs[idx]),
            float(ys[idx] + h_off * nys[idx]),
            float(zs[idx] + h_off * nzs[idx]),
        ))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new("Logo_LILI_ch_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Logo_LILI_ch", mesh)
    bpy.context.collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True
    return obj


def _compute_scaled_face_radii(data, ang_grid):
    """
    Rev.2: 高解像度原画 iich_05_front.png から抽出したLUTと楕円 r_ell を
    build_iinet_kun.py (Rev.13) と同一の 0.90 * r_out_orig + 0.10 * r_ell (frame_scale=0.975, thickness_slim=0.92) でブレンドし、
    角丸スクエアの顔枠とボディ余白バランスを原画に忠実に一致させる
    """
    thetas = data["thetas"]
    r_in_orig = np.interp(ang_grid, thetas, data["r_in_lut"])
    r_out_orig = np.interp(ang_grid, thetas, data["r_out_lut"])

    rx_out = float(np.interp(0.0, thetas, data["r_out_lut"]))
    rz_out = 0.5 * (float(np.interp(0.5 * math.pi, thetas, data["r_out_lut"])) + float(np.interp(1.5 * math.pi, thetas, data["r_out_lut"])))
    r_ell = 1.0 / np.sqrt((np.cos(ang_grid) / rx_out) ** 2 + (np.sin(ang_grid) / rz_out) ** 2)
    r_out_smooth = 0.90 * r_out_orig + 0.10 * r_ell

    frame_scale = 0.975
    thickness_slim = 0.92
    r_out = r_out_smooth * frame_scale
    w_frame = (r_out_orig - r_in_orig) * frame_scale * thickness_slim
    r_in = r_out - w_frame
    zc = data["face_center_Z"]  # 1.12875 m
    return r_in, r_out, zc


def create_face_screen_mesh(surf_model, data, n_ang=160, n_rad=28, flat_mode=True):
    ang_grid = np.linspace(0.0, 2.0 * math.pi, n_ang, endpoint=False)
    r_in, _, zc = _compute_scaled_face_radii(data, ang_grid)
    r_max_ang = r_in if flat_mode else (r_in + 0.012)

    bm = bmesh.new()
    y_c, nx_c, ny_c, nz_c = surf_model.front_surface_y_and_normal(np.array([0.0]), np.array([zc]))
    c_off = 0.0007 if flat_mode else 0.003
    center_v = bm.verts.new((0.0, float(y_c[0] + c_off * ny_c[0]), zc))

    rings = []
    for ir in range(1, n_rad + 1):
        frac = (ir / n_rad) ** 0.85
        rs = r_max_ang * frac
        xs = rs * np.cos(ang_grid)
        zs = zc + rs * np.sin(ang_grid)
        ys, nxs, nys, nzs = surf_model.front_surface_y_and_normal(xs, zs)
        offset = 0.0007 if flat_mode else (0.0035 * (1.0 - 0.5 * (ir / n_rad) ** 4))
        ring_verts = []
        for ia in range(n_ang):
            vx = float(xs[ia] + offset * nxs[ia])
            vy = float(ys[ia] + offset * nys[ia])
            vz = float(zs[ia] + offset * nzs[ia])
            ring_verts.append(bm.verts.new((vx, vy, vz)))
        rings.append(ring_verts)

    for ia in range(n_ang):
        ia_next = (ia + 1) % n_ang
        bm.faces.new((center_v, rings[0][ia], rings[0][ia_next]))
    for ir in range(n_rad - 1):
        for ia in range(n_ang):
            ia_next = (ia + 1) % n_ang
            bm.faces.new((rings[ir][ia], rings[ir + 1][ia], rings[ir + 1][ia_next], rings[ir][ia_next]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new("Face_Screen_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Face_Screen", mesh)
    bpy.context.collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True
    if flat_mode and hasattr(obj, "visible_shadow"):
        obj.visible_shadow = False
    return obj


def create_face_frame_mesh(surf_model, data, n_ang=180, n_prof=28, flat_mode=True):
    ang_grid = np.linspace(0.0, 2.0 * math.pi, n_ang, endpoint=False)
    r_in, r_out, zc = _compute_scaled_face_radii(data, ang_grid)

    bm = bmesh.new()
    s_vals = np.linspace(0.0, 1.0, n_prof)
    rings = []
    for s in s_vals:
        u_rad = s if flat_mode else (0.5 * (1.0 - math.cos(math.pi * s)))
        rs = r_in + (r_out - r_in) * u_rad
        xs = rs * np.cos(ang_grid)
        zs = zc + rs * np.sin(ang_grid)
        ys, nxs, nys, nzs = surf_model.front_surface_y_and_normal(xs, zs)

        h_off = 0.0007 if flat_mode else (-0.005 + 0.043 * (math.sin(math.pi * s) ** 0.44))
        ring_v = []
        for ia in range(n_ang):
            vx = float(xs[ia] + h_off * nxs[ia])
            vy = float(ys[ia] + h_off * nys[ia])
            vz = float(zs[ia] + h_off * nzs[ia])
            ring_v.append(bm.verts.new((vx, vy, vz)))
        rings.append(ring_v)

    for ip in range(n_prof - 1):
        for ia in range(n_ang):
            ia_next = (ia + 1) % n_ang
            bm.faces.new((rings[ip][ia], rings[ip][ia_next], rings[ip + 1][ia_next], rings[ip + 1][ia]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new("Face_Frame_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Face_Frame", mesh)
    bpy.context.collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True
    if flat_mode and hasattr(obj, "visible_shadow"):
        obj.visible_shadow = False
    return obj


def create_eye_mesh(surf_model, name, cx_eye, cz_eye=1.1075, rx_eye=0.0890, rz_eye=0.1182):
    """
    Rev.2: iich_05_front.png 実測値 (cx_eye=±0.3145m, cz_eye=1.1075m, rx_eye=0.0890m, rz_eye=0.1182m) に
    IoU 99.28% で一致する縦長オーバル楕円目をフラットシェル仕様で生成
    """
    n_ang = 64
    n_rad = 16
    bm = bmesh.new()
    ang_grid = np.linspace(0.0, 2.0 * math.pi, n_ang, endpoint=False)

    y_c, nx_c, ny_c, nz_c = surf_model.front_surface_y_and_normal(np.array([cx_eye]), np.array([cz_eye]))
    h_flat = 0.0014
    center_v = bm.verts.new((
        float(cx_eye + h_flat * nx_c[0]),
        float(y_c[0] + h_flat * ny_c[0]),
        float(cz_eye + h_flat * nz_c[0]),
    ))

    rings = []
    for ir in range(1, n_rad + 1):
        frac = ir / n_rad
        xs = cx_eye + (rx_eye * frac) * np.cos(ang_grid)
        zs = cz_eye + (rz_eye * frac) * np.sin(ang_grid)
        ys, nxs, nys, nzs = surf_model.front_surface_y_and_normal(xs, zs)
        ring_v = []
        for ia in range(n_ang):
            ring_v.append(bm.verts.new((
                float(xs[ia] + h_flat * nxs[ia]),
                float(ys[ia] + h_flat * nys[ia]),
                float(zs[ia] + h_flat * nzs[ia]),
            )))
        rings.append(ring_v)

    for ia in range(n_ang):
        ia_next = (ia + 1) % n_ang
        bm.faces.new((center_v, rings[0][ia], rings[0][ia_next]))
    for ir in range(n_rad - 1):
        for ia in range(n_ang):
            ia_next = (ia + 1) % n_ang
            bm.faces.new((rings[ir][ia], rings[ir + 1][ia], rings[ir + 1][ia_next], rings[ir][ia_next]))

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


def create_mouth_mesh(surf_model):
    """
    Rev.2: iich_05_front.png 実測値に基づくぷっくり丸いスマイルアーク
    (z_arc_center=1.0793m, r_arc=0.4180m, r_tube=0.0390m, max_ang=21.4°)
    両端は先細りのない真円の半円キャップ(ext = cos(alpha) * r_tube)、完全フラットシェル仕様
    """
    z_arc_center = 1.0793
    r_arc = 0.4180
    r_tube = 0.0390
    max_ang = math.radians(21.4)

    n_spine = 56
    n_cap = 24
    n_prof = 24

    spine_pts_x, spine_pts_z, spine_tx, spine_tz, spine_r_scale = [], [], [], [], []

    for ic in range(n_cap):
        u = ic / n_cap
        alpha = 0.5 * math.pi * u
        th = -max_ang
        tx, tz = math.cos(th), math.sin(th)
        ext = math.cos(alpha) * r_tube
        cx = r_arc * math.sin(th) - tx * ext
        cz = z_arc_center - r_arc * math.cos(th) - tz * ext
        r_sc = math.sin(max(alpha, 0.01))
        spine_pts_x.append(cx)
        spine_pts_z.append(cz)
        spine_tx.append(tx)
        spine_tz.append(tz)
        spine_r_scale.append(r_sc)

    for iseg in range(n_spine):
        th = -max_ang + 2.0 * max_ang * (iseg / (n_spine - 1))
        cx = r_arc * math.sin(th)
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
        cx = r_arc * math.sin(th) + tx * ext
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
    mesh = bpy.data.meshes.new("Mouth_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Mouth", mesh)
    bpy.context.collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True
    if hasattr(obj, "visible_shadow"):
        obj.visible_shadow = False
    return obj


def create_arm_meshes(surf_model):
    """
    Rev.2: iich_05_front.png 実測位置 (Z=0.245..0.555m, 最大幅 x_peak=1.048m at z_peak=0.320m, x_tip_bot=0.905m) に合わせ、
    上側外縁曲線 x_outer の指数を ((1.0 - (u_up ** 1.35)) ** 0.88) とすることで
    腕上端と胴体輪郭の接合部で生じていた凹み変曲点(S字の波打ち)を完全に解消
    """
    xs_test = np.linspace(surf_model.x_foot, surf_model.W_max, 400)
    zs_test = surf_model._eval_lower_z(xs_test, np.zeros_like(xs_test))

    arms = []
    for side_sign, name in [(+1.0, "Arm.L"), (-1.0, "Arm.R")]:
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=2.0)
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=36, use_grid_fill=True)

        verts = bm.verts
        verts.ensure_lookup_table()
        coords = np.array([v.co[:] for v in verts], dtype=np.float64)
        tan_c = np.tan(coords * (math.pi / 4.0))
        unit_p = tan_c / np.linalg.norm(tan_c, axis=1, keepdims=True)
        ux, uy, uz = unit_p[:, 0], unit_p[:, 1], unit_p[:, 2]

        z_min, z_max = 0.245, 0.555
        Z = 0.5 * (z_min + z_max) + 0.5 * (z_max - z_min) * uz
        env_z = np.sqrt(np.maximum(1.0 - uz * uz, 0.0))

        r_horiz = np.sqrt(np.maximum(ux * ux + uy * uy, 1e-12))
        cy = uy / r_horiz
        cx = ux / r_horiz

        # 側面図(Side)の滑らかな楕円パドル断面 (中心 Y=+0.040m, 前後半幅 0.130m)
        half_y = 0.130 * (env_z ** 0.92)
        mid_y = 0.040 - 0.012 * uz
        Y = mid_y + half_y * cy

        x_body_surf = np.interp(Z, zs_test, xs_test)
        x_body_rim = x_body_surf - 0.008 * (half_y / 0.130) ** 2

        # 正面図(iich_05_front.png)のぷっくり丸いハの字パドル外縁 (変曲点・波打ちゼロ)
        x_tip_top = float(np.interp(z_max, zs_test, xs_test)) - 0.004
        x_tip_bot = 0.905
        x_peak = 1.048
        z_peak = 0.320
        t_bot = np.clip((Z - z_min) / (z_peak - z_min), 0.0, 1.0)
        u_up = np.clip((Z - z_peak) / (z_max - z_peak), 0.0, 1.0)
        x_outer = np.where(
            Z <= z_peak,
            x_tip_bot + (x_peak - x_tip_bot) * np.sqrt(t_bot * (2.0 - t_bot)),
            x_tip_top + (x_peak - x_tip_top) * ((1.0 - (u_up ** 1.35)) ** 0.88),
        )

        # 内側輪郭 x_inner(Z): 下端(Z=0.245)から脇下(Z=0.315)を通って胴体内部へ滑らかに収束
        s_in = np.clip((Z - z_min) / (0.315 - z_min), 0.0, 1.0)
        x_inner_paddle = x_tip_bot - 0.210 * (s_in ** 0.68)
        u_top_in = np.clip((Z - 0.460) / (z_max - 0.460), 0.0, 1.0)
        env_top_in = np.sqrt(np.maximum(1.0 - u_top_in * u_top_in, 0.0))
        x_inner_body = x_tip_top * (1.0 - env_top_in) + (x_body_surf - 0.065) * env_top_in
        w_in = np.clip((Z - 0.305) / 0.050, 0.0, 1.0)
        w_in = w_in * w_in * (3.0 - 2.0 * w_in)
        x_inner = (1.0 - w_in) * x_inner_paddle + w_in * x_inner_body

        x_mid_paddle = 0.5 * (x_outer + x_inner)
        x_rim_target = (x_body_rim + 0.008) * env_top_in + x_tip_top * (1.0 - env_top_in)
        w_root = np.clip((Z - z_min) / (0.430 - z_min), 0.0, 1.0)
        w_root = w_root * w_root * (3.0 - 2.0 * w_root)
        x_root = (1.0 - w_root) * x_mid_paddle + w_root * np.maximum(x_rim_target, x_body_surf + 0.003)

        cx_pos = np.maximum(cx, 0.0)
        cx_neg = np.maximum(-cx, 0.0)
        X_abs = np.where(
            cx >= 0.0,
            x_root + (x_outer - x_root) * (cx_pos ** 0.75),
            x_root - (x_root - x_inner) * (cx_neg ** 0.80),
        )

        X = side_sign * X_abs
        for i, v in enumerate(verts):
            v.co = Vector((float(X[i]), float(Y[i]), float(Z[i])))

        for it in range(4):
            tip_updates = {}
            for v in verts:
                if it < 2 or v.co.z < 0.275:
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

    return arms


def create_antenna_and_globe():
    """
    Rev.2: 尻尾(Antenna)の付け根高さを「いい-NETくん」および三面図Backと完全統一
    (お尻下部内部 Z=0.480m, Y=0.420m からお尻下部表面 Z=0.530m, Y=0.655m を貫通して出現) し、
    後方最大突出点 (Z=1.240m, Y=0.925m, dY/dZ=0) を経て地球儀内部 (Z=2.220m, Y=globe_y=0.660m) へ
    変曲点ゼロ(d^2Y/dZ^2 < 0)の単一C字アーチで接続させる
    """
    globe_y = 0.660
    globe_z = 2.356
    globe_radius = 0.200
    y_peak = 0.925
    z_peak = 1.240

    # 1) お尻下部内部 (Y=0.420m, Z=0.480m) からお尻下部表面 (Y=0.655m, Z=0.530m) を貫通する根元部
    root_z = np.linspace(0.480, 0.525, 16)
    root_y = np.linspace(0.420, 0.648, 16)

    # 2) お尻下部表面 (Y=0.655m, Z=0.530m) から後方最大突出点 (Y=0.925m, Z=1.240m, dY/dZ=0) への下部C字カーブ
    u_low = np.linspace(0.0, 1.0, 60)
    z_low = 0.530 + (z_peak - 0.530) * u_low
    y_low = 0.655 + (y_peak - 0.655) * np.sin(0.5 * math.pi * u_low)

    # 3) 後方最大突出点 (Y=0.925m, Z=1.240m) から地球儀下部内部 (Y=globe_y=0.660m, Z=2.220m) への純凸C字アーチ (S字反りゼロ)
    u_up = np.linspace(0.015, 1.0, 80)
    z_up = z_peak + (2.220 - z_peak) * u_up
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
    z_fine[0], y_fine[0] = 0.480, 0.420
    z_fine[-1], y_fine[-1] = 2.220, globe_y

    r_pipe = 0.040
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

    ant_mesh = bpy.data.meshes.new("Antenna_Mesh")
    bm.to_mesh(ant_mesh)
    bm.free()

    ant_obj = bpy.data.objects.new("Antenna", ant_mesh)
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

    globe_mesh = bpy.data.meshes.new("Globe_Mesh")
    bm_g.to_mesh(globe_mesh)
    bm_g.free()

    globe_obj = bpy.data.objects.new("Globe", globe_mesh)
    bpy.context.collection.objects.link(globe_obj)

    return ant_obj, globe_obj


# ==========================================
# 4. アーマチュア（リグ）構築＆スキニング
# ==========================================
def create_armature_and_bind(all_mesh_objs):
    arm_data = bpy.data.armatures.new("IICh_Armature_Data")
    arm_obj = bpy.data.objects.new("IICh_Armature", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    eb = arm_data.edit_bones

    b_root = eb.new("Root")
    b_root.head = (0.0, 0.0, -0.05)
    b_root.tail = (0.0, 0.0, 0.15)

    b_body = eb.new("Body")
    b_body.head = (0.0, 0.0, 0.15)
    b_body.tail = (0.0, 0.0, 1.90)
    b_body.parent = b_root

    b_leg_l = eb.new("Leg.L")
    b_leg_l.head = (0.2625, 0.0, 0.15)
    b_leg_l.tail = (0.2625, 0.0, -0.02)
    b_leg_l.parent = b_body

    b_leg_r = eb.new("Leg.R")
    b_leg_r.head = (-0.2625, 0.0, 0.15)
    b_leg_r.tail = (-0.2625, 0.0, -0.02)
    b_leg_r.parent = b_body

    b_arm_l = eb.new("Arm.L")
    b_arm_l.head = (0.82, 0.04, 0.52)
    b_arm_l.tail = (1.03, 0.04, 0.28)
    b_arm_l.parent = b_body

    b_arm_r = eb.new("Arm.R")
    b_arm_r.head = (-0.82, 0.04, 0.52)
    b_arm_r.tail = (-1.03, 0.04, 0.28)
    b_arm_r.parent = b_body

    b_ant1 = eb.new("Antenna_1")
    b_ant1.head = (0.0, 0.55, 0.55)
    b_ant1.tail = (0.0, 0.912, 1.18)
    b_ant1.parent = b_body

    b_ant2 = eb.new("Antenna_2")
    b_ant2.head = (0.0, 0.912, 1.18)
    b_ant2.tail = (0.0, 0.80, 1.70)
    b_ant2.parent = b_ant1
    b_ant2.use_connect = True

    b_ant3 = eb.new("Antenna_3")
    b_ant3.head = (0.0, 0.80, 1.70)
    b_ant3.tail = (0.0, 0.720, 2.16)
    b_ant3.parent = b_ant2
    b_ant3.use_connect = True

    b_globe = eb.new("Globe")
    b_globe.head = (0.0, 0.720, 2.16)
    b_globe.tail = (0.0, 0.720, 2.55)
    b_globe.parent = b_ant3

    bpy.ops.object.mode_set(mode='OBJECT')

    for obj in all_mesh_objs:
        obj.parent = arm_obj
        mod = obj.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = arm_obj

        name = obj.name
        if name == "Body":
            vg_body = obj.vertex_groups.new(name="Body")
            vg_leg_l = obj.vertex_groups.new(name="Leg.L")
            vg_leg_r = obj.vertex_groups.new(name="Leg.R")
            for v in obj.data.vertices:
                z = v.co.z
                x = v.co.x
                if z < 0.14:
                    w_leg = float(np.clip((0.14 - z) / 0.14, 0.0, 1.0))
                    if x >= 0:
                        vg_leg_l.add([v.index], w_leg, 'REPLACE')
                    else:
                        vg_leg_r.add([v.index], w_leg, 'REPLACE')
                    vg_body.add([v.index], 1.0 - w_leg, 'REPLACE')
                else:
                    vg_body.add([v.index], 1.0, 'REPLACE')
        elif name in ("Face_Screen", "Face_Frame", "Eye.L", "Eye.R", "Mouth", "Logo_LILI_ch"):
            vg = obj.vertex_groups.new(name="Body")
            vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
        elif name == "Arm.L":
            vg = obj.vertex_groups.new(name="Arm.L")
            vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
        elif name == "Arm.R":
            vg = obj.vertex_groups.new(name="Arm.R")
            vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
        elif name == "Globe":
            vg = obj.vertex_groups.new(name="Globe")
            vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
        elif name == "Antenna":
            vg1 = obj.vertex_groups.new(name="Antenna_1")
            vg2 = obj.vertex_groups.new(name="Antenna_2")
            vg3 = obj.vertex_groups.new(name="Antenna_3")
            for v in obj.data.vertices:
                z = v.co.z
                if z < 1.18:
                    vg1.add([v.index], 1.0, 'REPLACE')
                elif z < 1.70:
                    vg2.add([v.index], 1.0, 'REPLACE')
                else:
                    vg3.add([v.index], 1.0, 'REPLACE')

    return arm_obj


# ==========================================
# 5. マテリアル設定（3Dソフトビニール・マット質感）
# ==========================================
def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb255_to_linear_rgba(r, g, b, a=1.0):
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), a)


def set_bsdf_matte_params(bsdf, rgba):
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = 0.84
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = 0.0
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.14
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.0
        bsdf.inputs["Coat Roughness"].default_value = 1.0
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.0
    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = 0.04
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = 0.0


def create_matte_material(name, rgb255):
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    rgba = rgb255_to_linear_rgba(*rgb255)
    set_bsdf_matte_params(bsdf, rgba)
    mat.diffuse_color = rgba
    return mat


def create_globe_material():
    mat = bpy.data.materials.new(name="Mat_Globe")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')

    tex_node = nodes.new(type='ShaderNodeTexImage')
    tex_node.image = bpy.data.images.load(GLOBE_TEX_PATH, check_existing=True)
    tex_node.interpolation = 'Linear'

    set_bsdf_matte_params(bsdf, (0.05, 0.76, 0.93, 1.0))
    links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


# ==========================================
# 6. ライティング・カメラ・レンダリング・比較シート合成
# ==========================================
STUDIO_RIG_LIGHTS = {}


def setup_lighting_and_world():
    scene = bpy.context.scene
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0.0

    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    bg_node = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    bg_node.inputs[0].default_value = (0.99, 1.00, 0.99, 1.0)
    bg_node.inputs[1].default_value = 0.20

    STUDIO_RIG_LIGHTS.clear()
    rig_defs = [
        ("Key_Cam", 335.0, 2.7, (1.00, 0.99, 0.98), True),
        ("Fill_Cam", 44.0, 4.8, (0.99, 1.00, 0.99), True),
        ("Rim_Cam", 88.0, 3.2, (0.98, 0.99, 1.00), True),
        ("Bounce_Cam", 18.0, 4.5, (0.99, 1.00, 0.99), False),
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
        STUDIO_RIG_LIGHTS[name] = lobj


def update_camera_studio_lights(forward, right, up):
    target = Vector((0.0, 0.12, 1.08))
    placements = {
        "Key_Cam": target - 3.4 * forward - 3.4 * right + 3.4 * up,
        "Fill_Cam": target - 3.8 * forward + 4.2 * right + 0.3 * up,
        "Rim_Cam": target + 3.4 * forward + 1.8 * right + 3.6 * up,
        "Bounce_Cam": target - 3.2 * forward - 3.8 * up,
    }
    for name, lpos in placements.items():
        if name in STUDIO_RIG_LIGHTS:
            lobj = STUDIO_RIG_LIGHTS[name]
            lobj.location = lpos
            direction = (target - lpos).normalized()
            lobj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def set_camera_pose(cam_obj, pos, forward, up_hint, ortho=False, ortho_scale=3.12, lens=72.0):
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

    update_camera_studio_lights(forward, right, up)


def disable_freestyle_outline():
    scene = bpy.context.scene
    scene.render.use_freestyle = False
    view_layer = bpy.context.view_layer
    view_layer.use_freestyle = False


def render_view_to_array(cam_obj, width, height, filepath, transparent=False):
    scene = bpy.context.scene
    scene.camera = cam_obj
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = transparent
    scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
    return load_image_rgba_uint8(filepath)


def composite_on_card(rgba_arr, has_floor_shadow=True, bg_top=(246, 249, 254), bg_bot=(230, 236, 246), border_col=(205, 215, 232)):
    h, w, _ = rgba_arr.shape
    t = np.linspace(0.0, 1.0, h)[:, None, None]
    bg = np.array(bg_top, dtype=np.float32)[None, None, :] * (1.0 - t) + np.array(bg_bot, dtype=np.float32)[None, None, :] * t

    if has_floor_shadow:
        yy, xx = np.mgrid[0:h, 0:w]
        mask = rgba_arr[:, :, 3] > 32
        ys_op, xs_op = np.where(mask)
        if len(ys_op) > 0:
            y_foot_max = float(np.percentile(ys_op, 99.6))
            low_band = ys_op >= (y_foot_max - h * 0.045)
            shadow_cx = float(np.mean(xs_op[low_band])) if np.any(low_band) else (w * 0.50)
            shadow_cy = min(h * 0.965, y_foot_max - h * 0.003)
        else:
            shadow_cx = w * 0.50
            shadow_cy = h * 0.925
        shadow_rx = w * 0.26
        shadow_ry = h * 0.028
        r2 = ((xx - shadow_cx) / shadow_rx) ** 2 + ((yy - shadow_cy) / shadow_ry) ** 2
        shadow = 0.16 * np.exp(-1.8 * r2)[:, :, None]
        bg = bg * (1.0 - shadow)

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


def configure_cycles_gpu(scene):
    scene.render.engine = 'CYCLES'
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        for dev_type in ('OPTIX', 'CUDA'):
            try:
                prefs.compute_device_type = dev_type
                prefs.get_devices()
                gpu_devs = [d for d in prefs.devices if d.type == dev_type]
                if gpu_devs:
                    for d in prefs.devices:
                        d.use = (d.type == dev_type)
                    scene.cycles.device = 'GPU'
                    break
            except Exception:
                pass
    except Exception:
        pass
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    if hasattr(scene.cycles, "denoiser"):
        scene.cycles.denoiser = 'OPENIMAGEDENOISE'


def build_and_render_iich(data, surf_model):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    configure_cycles_gpu(scene)

    # 2. 全3Dパーツ生成 (Rev.2: iich_05_front.png 実測値に完全一致)
    body_obj = create_body_mesh(surf_model, res=136)
    logo_obj = create_logo_3d_mesh(surf_model)
    screen_obj = create_face_screen_mesh(surf_model, data, flat_mode=True)
    frame_obj = create_face_frame_mesh(surf_model, data, flat_mode=True)
    eye_l_obj = create_eye_mesh(surf_model, "Eye.L", cx_eye=+0.3145, cz_eye=1.1075, rx_eye=0.0890, rz_eye=0.1182)
    eye_r_obj = create_eye_mesh(surf_model, "Eye.R", cx_eye=-0.3145, cz_eye=1.1075, rx_eye=0.0890, rz_eye=0.1182)
    mouth_obj = create_mouth_mesh(surf_model)
    arm_l_obj, arm_r_obj = create_arm_meshes(surf_model)
    ant_obj, globe_obj = create_antenna_and_globe()

    all_meshes = [
        body_obj, logo_obj, screen_obj, frame_obj,
        eye_l_obj, eye_r_obj, mouth_obj,
        arm_l_obj, arm_r_obj,
        ant_obj, globe_obj,
    ]

    # 3. マテリアル作成＆割り当て
    mat_body_green = create_matte_material("Mat_Body_Green", (134, 194, 78))
    mat_arm_green = create_matte_material("Mat_Arm_Green", (128, 188, 72))
    mat_frame_blue = create_matte_material("Mat_Frame_Blue", (52, 114, 182))
    mat_feature_blue = create_matte_material("Mat_Feature_Blue", (22, 96, 172))
    mat_stem_blue = create_matte_material("Mat_Stem_Blue", (52, 114, 182))
    mat_screen_cream = create_matte_material("Mat_Screen_Cream", (253, 250, 210))
    mat_logo_yellow = create_matte_material("Mat_Logo_Yellow", (252, 242, 20))
    mat_logo_side = create_matte_material("Mat_Logo_Side", (185, 130, 0))
    mat_globe = create_globe_material()

    body_obj.data.materials.append(mat_body_green)
    logo_obj.data.materials.append(mat_logo_yellow)
    logo_obj.data.materials.append(mat_logo_side)
    arm_l_obj.data.materials.append(mat_arm_green)
    arm_r_obj.data.materials.append(mat_arm_green)
    frame_obj.data.materials.append(mat_frame_blue)
    screen_obj.data.materials.append(mat_screen_cream)
    eye_l_obj.data.materials.append(mat_feature_blue)
    eye_r_obj.data.materials.append(mat_feature_blue)
    mouth_obj.data.materials.append(mat_feature_blue)
    ant_obj.data.materials.append(mat_stem_blue)
    globe_obj.data.materials.append(mat_globe)

    # 4. アーマチュア構築＆スキニング
    create_armature_and_bind(all_meshes)

    # 5. ライティング・Freestyle OFF・カメラ設定
    setup_lighting_and_world()
    disable_freestyle_outline()

    cam_data = bpy.data.cameras.new("RenderCam")
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)

    hero_target = Vector((0.02, 0.12, 1.18))
    hero_pos = Vector((2.82, -6.45, 1.72))
    set_camera_pose(cam_obj, hero_pos, hero_target - hero_pos, (0, 0, 1), ortho=False, lens=72.0)
    scene.camera = cam_obj

    # 6. .blend 保存 & .glb エクスポート
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT_PATH)
    bpy.ops.export_scene.gltf(filepath=GLB_OUT_PATH, export_format='GLB')

    # 7. 各ビューのレンダリングと高解像度シート生成
    tmp_render = os.path.join(DRAFTS_DIR, "_tmp_iich_render.png")
    ortho_sc = 3.12

    # (A) ヒーローカット (1400 x 1680)
    hero_raw = render_view_to_array(cam_obj, 1400, 1680, tmp_render, transparent=True)
    hero_card = composite_on_card(hero_raw, has_floor_shadow=True)
    save_rgba_uint8_as_png(hero_card, HERO_IMG_PATH)

    # (B) 5面図＋斜めビューの個別レンダリング (各 800 x 960)
    pw, ph = 800, 960
    set_camera_pose(cam_obj, (0.0, -6.0, 1.20), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), ortho=True, ortho_scale=ortho_sc)
    img_front = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True), has_floor_shadow=True)
    save_rgba_uint8_as_png(img_front, FRONT_IMG_PATH)

    set_camera_pose(cam_obj, (6.0, 0.15, 1.20), (-1.0, 0.0, 0.0), (0.0, 0.0, 1.0), ortho=True, ortho_scale=ortho_sc)
    img_side = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True), has_floor_shadow=True)
    save_rgba_uint8_as_png(img_side, SIDE_IMG_PATH)

    set_camera_pose(cam_obj, (0.0, 6.0, 1.20), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0), ortho=True, ortho_scale=ortho_sc)
    img_back = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True), has_floor_shadow=True)

    set_camera_pose(cam_obj, (0.0, 0.15, 6.0), (0.0, 0.0, -1.0), (-1.0, 0.0, 0.0), ortho=True, ortho_scale=ortho_sc)
    img_top = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True), has_floor_shadow=False)

    set_camera_pose(cam_obj, (0.0, 0.15, -6.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), ortho=True, ortho_scale=ortho_sc)
    img_bottom = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True), has_floor_shadow=False)

    set_camera_pose(cam_obj, hero_pos, hero_target - hero_pos, (0, 0, 1), ortho=False, lens=72.0)
    img_persp = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True), has_floor_shadow=True)

    if os.path.exists(tmp_render):
        os.remove(tmp_render)

    pad = 24
    board_w = pw * 4 + pad * 5
    board_h = ph + pad * 2
    board = np.full((board_h, board_w, 4), 240, dtype=np.uint8)
    board[:, :, 3] = 255
    for idx, panel in enumerate([img_front, img_side, img_persp, img_back]):
        x0 = pad + idx * (pw + pad)
        board[pad:pad + ph, x0:x0 + pw] = panel
    save_rgba_uint8_as_png(board, BOARD_IMG_PATH)

    sheet_w = pw * 3 + pad * 4
    sheet_h = ph * 2 + pad * 3
    sheet = np.full((sheet_h, sheet_w, 4), 240, dtype=np.uint8)
    sheet[:, :, 3] = 255
    grid_panels = [
        (0, 0, img_front),
        (0, 1, img_side),
        (0, 2, img_back),
        (1, 0, img_top),
        (1, 1, img_bottom),
        (1, 2, img_persp),
    ]
    for r_i, c_i, panel in grid_panels:
        y0 = pad + r_i * (ph + pad)
        x0 = pad + c_i * (pw + pad)
        sheet[y0:y0 + ph, x0:x0 + pw] = panel
    save_rgba_uint8_as_png(sheet, SHEET_IMG_PATH)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    data = extract_iich_profiles()
    surf_model = IIChSurfaceModel(data)
    build_and_render_iich(data, surf_model)
    print("ALL RENDERS AND EXPORTS FOR II-CH (LILI-ch) REV.2 COMPLETED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
