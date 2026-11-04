# -*- coding: utf-8 -*-
"""
株式会社CVN キャラクター「いい-NETくん（胸ロゴ：LILI-net）」
Blender 5.2 3Dモデリング・リギング・マテリアル・レンダリング一括構築スクリプト (v3: アーム完全整合＆視覚監査仕上げ版)
"""

import os
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

FRONT_REF_PATH = os.path.join(REF_DIR, "05_front.png")
SIDE_REF_PATH = os.path.join(REF_DIR, "03_side.png")
LOGO_DECAL_PATH = os.path.join(DRAFTS_DIR, "lili_net_logo_decal.png")
BODY_TEX_PATH = os.path.join(DRAFTS_DIR, "body_pink_with_logo.png")
GLOBE_TEX_PATH = os.path.join(DRAFTS_DIR, "globe_texture.png")

BLEND_OUT_PATH = os.path.join(OUTPUT_DIR, "cvn_iinet_kun.blend")
GLB_OUT_PATH = os.path.join(OUTPUT_DIR, "cvn_iinet_kun.glb")

HERO_IMG_PATH = os.path.join(OUTPUT_DIR, "iinet_kun_hero_3quarter.png")
BOARD_IMG_PATH = os.path.join(OUTPUT_DIR, "iinet_kun_front_and_side.png")
SHEET_IMG_PATH = os.path.join(OUTPUT_DIR, "iinet_kun_5views_sheet.png")


# ==========================================
# 1. 画像ロード・プロファイル解析・テクスチャ抽出
# ==========================================
def load_image_rgba_uint8(filepath):
    """Blenderのbpy.data.imagesを用いてPNGを(H, W, 4) uint8配列(上端y=0)として取得"""
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


def extract_textures_and_profiles():
    """05_front.png と 03_side.png から正確な輪郭LUTと高解像度テクスチャを生成"""
    im_f = load_image_rgba_uint8(FRONT_REF_PATH)
    im_s = load_image_rgba_uint8(SIDE_REF_PATH)

    # --- (A) 胸元ロゴ「LILI-net」の透過デカール＆一体型ボディテクスチャ生成 ---
    crop = im_f[815:915, 192:628].astype(np.float32)
    R, G, B = crop[:, :, 0], crop[:, :, 1], crop[:, :, 2]
    pink_frac = np.clip(B / 160.0, 0.0, 1.0)
    alpha = 1.0 - pink_frac
    alpha_sharp = np.clip((alpha - 0.06) / 0.88, 0.0, 1.0)
    R_clean = np.where(alpha > 0.02, np.clip((R - 240.0 * pink_frac) / np.maximum(alpha, 0.02), 0, 255), 0)
    G_clean = np.where(alpha > 0.02, np.clip((G - 80.0 * pink_frac) / np.maximum(alpha, 0.02), 0, 255), 0)
    B_clean = np.zeros_like(B)

    logo_rgba = np.stack([R_clean, G_clean, B_clean, alpha_sharp * 255.0], axis=-1).astype(np.uint8)
    h0, w0, _ = logo_rgba.shape
    scale = 4
    y_idx = np.clip(np.linspace(0, h0 - 1, h0 * scale), 0, h0 - 1)
    x_idx = np.clip(np.linspace(0, w0 - 1, w0 * scale), 0, w0 - 1)
    y0 = np.floor(y_idx).astype(int)
    y1 = np.minimum(y0 + 1, h0 - 1)
    wy = (y_idx - y0)[:, None, None]
    x0 = np.floor(x_idx).astype(int)
    x1 = np.minimum(x0 + 1, w0 - 1)
    wx = (x_idx - x0)[None, :, None]

    logo_f = logo_rgba.astype(np.float32)
    top_interp = logo_f[y0][:, x0] * (1 - wx) + logo_f[y0][:, x1] * wx
    bot_interp = logo_f[y1][:, x0] * (1 - wx) + logo_f[y1][:, x1] * wx
    logo_hi = (top_interp * (1 - wy) + bot_interp * wy).astype(np.uint8)
    save_rgba_uint8_as_png(logo_hi, LOGO_DECAL_PATH)

    bw, bh = 2048, 1024
    body_tex = np.zeros((bh, bw, 4), dtype=np.uint8)
    body_pink = np.array([242, 78, 160], dtype=np.float32)
    body_tex[:, :, 0] = 242
    body_tex[:, :, 1] = 78
    body_tex[:, :, 2] = 160
    body_tex[:, :, 3] = 255

    u0_px, u1_px = int(bw * 0.15), int(bw * 0.85)
    v0_px, v1_px = int(bh * 0.25), int(bh * 0.75)
    target_w = u1_px - u0_px
    target_h = v1_px - v0_px

    ly = np.clip(np.linspace(0, logo_hi.shape[0] - 1, target_h), 0, logo_hi.shape[0] - 1).astype(int)
    lx = np.clip(np.linspace(0, logo_hi.shape[1] - 1, target_w), 0, logo_hi.shape[1] - 1).astype(int)
    sub_logo = logo_hi[ly][:, lx].astype(np.float32)
    sub_a = sub_logo[:, :, 3:4] / 255.0
    comp_rgb = sub_logo[:, :, :3] * sub_a + body_pink[None, None, :] * (1.0 - sub_a)
    r_start = bh - v1_px
    r_end = bh - v0_px
    body_tex[r_start:r_end, u0_px:u1_px, :3] = np.clip(comp_rgb, 0, 255).astype(np.uint8)
    save_rgba_uint8_as_png(body_tex, BODY_TEX_PATH)

    # --- (B) 頭上の地球儀テクスチャ生成 (1024x512 Equirectangular) ---
    gw, gh = 1024, 512
    u_grid = np.linspace(0.0, 1.0, gw, endpoint=False)[None, :]
    v_grid = np.linspace(0.0, 1.0, gh)[:, None]
    lon = (u_grid - 0.5) * 2.0 * math.pi
    lat = (0.5 - v_grid) * math.pi

    nz = np.sin(lat)
    globe_tex = np.zeros((gh, gw, 4), dtype=np.uint8)
    globe_tex[:, :, 0] = 16
    globe_tex[:, :, 1] = 196
    globe_tex[:, :, 2] = 238
    globe_tex[:, :, 3] = 255

    front_mask = np.abs(lon) < (0.50 * math.pi)
    lon_clamped = np.clip(lon, -0.499 * math.pi, 0.499 * math.pi)
    nx_proj = np.cos(lat) * np.sin(lon_clamped)
    nz_proj = nz

    px_x = np.clip(np.round(393.5 + nx_proj * 71.0).astype(int), 321, 466)
    px_y = np.clip(np.round(73.0 - nz_proj * 71.0).astype(int), 2, 144)

    sampled = im_f[px_y, px_x]
    is_land = front_mask & (sampled[:, :, 1] > 125) & (sampled[:, :, 0] < 70) & (sampled[:, :, 2] < 130)
    globe_tex[is_land, 0] = 0
    globe_tex[is_land, 1] = 153
    globe_tex[is_land, 2] = 51
    save_rgba_uint8_as_png(globe_tex, GLOBE_TEX_PATH)

    # --- (C) ボディ輪郭LUTの構築 ---
    alpha_f = im_f[:, :, 3] > 128
    outer_dx = np.zeros(1024, dtype=np.float64)
    for y in range(218, 1023):
        xs = np.where(alpha_f[y, :])[0]
        if len(xs) > 0:
            outer_dx[y] = 393.5 - xs.min()

    # 腕が突出する y=745..912 の外輪郭も別途保存してから胴体輪郭をブリッジする
    arm_front_outer_dx = outer_dx.copy()

    y_fit = np.concatenate([np.arange(670, 745), np.arange(915, 965)])
    p_outer = np.poly1d(np.polyfit(y_fit, outer_dx[y_fit], 3))
    for y in range(745, 915):
        outer_dx[y] = p_outer(y)

    dxs = np.linspace(0.0, 366.5, 500)
    y_top_lut = np.interp(dxs, outer_dx[218:561], np.arange(218, 561))

    y_bot_crotch_lut = np.zeros_like(dxs)
    y_bot_egg_lut = np.zeros_like(dxs)
    for i, dx in enumerate(dxs):
        if dx <= 103.5:
            x = int(round(393.5 - dx))
            ys = np.where(alpha_f[560:, x])[0] + 560
            y_bot_crotch_lut[i] = ys.max()
            y_bot_egg_lut[i] = 1022.0
        else:
            val = np.interp(dx, outer_dx[560:1023][::-1], np.arange(560, 1023)[::-1])
            y_bot_crotch_lut[i] = val
            y_bot_egg_lut[i] = val

    kernel = np.array([1, 2, 4, 6, 4, 2, 1], dtype=np.float64)
    kernel /= kernel.sum()
    y_top_lut = np.convolve(np.pad(y_top_lut, 3, mode='edge'), kernel, mode='valid')
    y_bot_crotch_lut = np.convolve(np.pad(y_bot_crotch_lut, 3, mode='edge'), kernel, mode='valid')
    y_bot_egg_lut = np.convolve(np.pad(y_bot_egg_lut, 3, mode='edge'), kernel, mode='valid')

    Z_top_lut = (1022.0 - y_top_lut) / 400.0
    Z_bot_crotch_lut = (1022.0 - y_bot_crotch_lut) / 400.0
    Z_bot_egg_lut = (1022.0 - y_bot_egg_lut) / 400.0
    X_lut = dxs / 400.0

    # --- (D) フェイスフレーム＆スクリーンの輪郭抽出 ---
    r_f, g_f, b_f = im_f[:, :, 0], im_f[:, :, 1], im_f[:, :, 2]
    frame_mask = alpha_f & (r_f == 60) & (g_f == 90) & (b_f == 170)
    screen_mask = alpha_f & (((r_f == 250) & (g_f == 230) & (b_f == 170)) | ((r_f == 50) & (g_f == 80) & (b_f == 170)))
    full_face_mask = frame_mask | screen_mask

    n_angles = 360
    thetas = np.linspace(0.0, 2.0 * math.pi, n_angles, endpoint=False)
    r_in_lut = np.zeros(n_angles, dtype=np.float64)
    r_out_lut = np.zeros(n_angles, dtype=np.float64)

    cx_face, cy_face = 393.0, 523.5
    rs_probe = np.linspace(10.0, 380.0, 740)
    for i, th in enumerate(thetas):
        ct, st = math.cos(th), math.sin(th)
        pxs = np.clip(np.round(cx_face + rs_probe * ct).astype(int), 0, 788)
        pys = np.clip(np.round(cy_face - rs_probe * st).astype(int), 0, 1023)
        in_scr = screen_mask[pys, pxs]
        in_frm = full_face_mask[pys, pxs]
        if np.any(in_scr):
            r_in_lut[i] = rs_probe[np.where(in_scr)[0][-1]] / 400.0
        if np.any(in_frm):
            r_out_lut[i] = rs_probe[np.where(in_frm)[0][-1]] / 400.0

    pad_k = 5
    k_ang = np.exp(-0.5 * (np.arange(-pad_k, pad_k + 1) / 2.2) ** 2)
    k_ang /= k_ang.sum()
    r_in_lut = np.convolve(np.pad(r_in_lut, pad_k, mode='wrap'), k_ang, mode='valid')
    r_out_lut = np.convolve(np.pad(r_out_lut, pad_k, mode='wrap'), k_ang, mode='valid')

    # --- (E) 背面S字アンテナの中心軌道抽出 ---
    r_s, g_s, b_s, a_s = im_s[:, :, 0], im_s[:, :, 1], im_s[:, :, 2], im_s[:, :, 3]
    stem_s = (a_s > 128) & (r_s == 58) & (g_s == 91) & (b_s == 167) & (np.arange(im_s.shape[1])[None, :] > 640)
    stem_ys, stem_xs = [], []
    for y in range(75, 775, 5):
        xs = np.where(stem_s[y, :])[0]
        if len(xs) > 0:
            stem_ys.append(y)
            stem_xs.append(0.5 * (xs.min() + xs.max()))
    stem_ys = np.array(stem_ys, dtype=np.float64)
    stem_xs = np.array(stem_xs, dtype=np.float64)

    # --- (F) 側面図・正面図からのアーム輪郭LUT抽出 ---
    arm_s = (a_s > 128) & (r_s == 232) & (g_s == 63) & (b_s == 150)
    arm_y_px = np.arange(718, 910, dtype=np.float64)
    arm_half_d = np.zeros_like(arm_y_px)
    arm_mid_s = np.zeros_like(arm_y_px)
    arm_front_x = np.zeros_like(arm_y_px)
    body_torso_x = np.zeros_like(arm_y_px)
    for i, y in enumerate(arm_y_px.astype(int)):
        xs = np.where(arm_s[y, :])[0]
        if len(xs) > 0:
            arm_half_d[i] = 0.5 * (xs.max() - xs.min()) / 400.0
            arm_mid_s[i] = (0.5 * (xs.max() + xs.min()) - 342.5) / 400.0
        arm_front_x[i] = arm_front_outer_dx[y] / 400.0
        body_torso_x[i] = outer_dx[y] / 400.0

    arm_z_lut = (1022.0 - arm_y_px) / 400.0  # 降順 (0.760 -> 0.280)

    return {
        "X_lut": X_lut,
        "Z_top_lut": Z_top_lut,
        "Z_bot_crotch_lut": Z_bot_crotch_lut,
        "Z_bot_egg_lut": Z_bot_egg_lut,
        "thetas": thetas,
        "r_in_lut": r_in_lut,
        "r_out_lut": r_out_lut,
        "face_center_Z": (1022.0 - cy_face) / 400.0,
        "stem_Z": (1022.0 - stem_ys) / 400.0,
        "stem_Y": (stem_xs - 342.5) / 400.0,
        "arm_z_lut": arm_z_lut[::-1],
        "arm_half_d": arm_half_d[::-1],
        "arm_mid_y": arm_mid_s[::-1],
        "arm_front_x": arm_front_x[::-1],
        "body_torso_x": body_torso_x[::-1],
    }


# ==========================================
# 2. 数学的3Dボディ曲面関数 (Body & Conformal Surface)
# ==========================================
class IINetSurfaceModel:
    def __init__(self, data):
        self.X_lut = data["X_lut"]
        self.Z_top_lut = data["Z_top_lut"]
        self.Z_bot_crotch_lut = data["Z_bot_crotch_lut"]
        self.Z_bot_egg_lut = data["Z_bot_egg_lut"]
        self.W_max = float(self.X_lut[-1])    # 0.91625 m
        self.D_max = 342.0 / 400.0            # 0.85500 m
        self.Z_eq = (1022.0 - 560.0) / 400.0  # 1.15500 m

    def z_top_of_x(self, abs_x):
        return np.interp(np.clip(abs_x, 0.0, self.W_max), self.X_lut, self.Z_top_lut)

    def z_bot_egg_of_x(self, abs_x):
        return np.interp(np.clip(abs_x, 0.0, self.W_max), self.X_lut, self.Z_bot_egg_lut)

    def z_bot_crotch_of_x(self, abs_x):
        return np.interp(np.clip(abs_x, 0.0, self.W_max), self.X_lut, self.Z_bot_crotch_lut)

    def map_unit_sphere_to_body(self, nx, ny, nz):
        X = self.W_max * nx
        abs_x = np.abs(X)
        r_yz = np.sqrt(np.maximum(ny * ny + nz * nz, 1e-12))
        ct = ny / r_yz
        st = nz / r_yz

        p = 2.12
        f_yz = (np.abs(ct) ** p + np.abs(st) ** p) ** (-1.0 / p)

        z_t = self.z_top_of_x(abs_x)
        z_b_egg = self.z_bot_egg_of_x(abs_x)
        z_b_crotch = self.z_bot_crotch_of_x(abs_x)

        Z_egg = np.where(
            st >= 0.0,
            self.Z_eq + (z_t - self.Z_eq) * st * f_yz,
            self.Z_eq - (self.Z_eq - z_b_egg) * (-st) * f_yz,
        )

        crotch_lift = np.maximum(0.0, z_b_crotch - z_b_egg)
        w_st = np.clip((-st - 0.68) / 0.32, 0.0, 1.0) ** 2.2
        w_ct = np.clip(1.0 - (ct / 0.65) ** 2, 0.0, 1.0) ** 1.2
        Z = Z_egg + crotch_lift * w_st * w_ct

        base_d = self.D_max * r_yz
        leg_plump = 1.0 + 0.05 * np.exp(-((abs_x - 0.258) / 0.15) ** 2) * np.clip(-st, 0.0, 1.0) ** 2
        crotch_groove = 1.0 - 0.18 * np.exp(-(abs_x / 0.10) ** 2) * np.clip((-st - 0.78) / 0.22, 0.0, 1.0) ** 1.5
        Y = base_d * ct * f_yz * leg_plump * crotch_groove
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
        z_b_egg = self.z_bot_egg_of_x(abs_x)

        u = np.where(
            Z >= self.Z_eq,
            (Z - self.Z_eq) / np.maximum(z_t - self.Z_eq, 1e-5),
            (Z - self.Z_eq) / np.maximum(self.Z_eq - z_b_egg, 1e-5),
        )
        u = np.clip(u, -0.999, 0.999)
        p = 2.12
        v = -((1.0 - np.abs(u) ** p) ** (1.0 / p))
        st_approx = np.clip(u, -1.0, 1.0)
        leg_plump = 1.0 + 0.05 * np.exp(-((abs_x - 0.258) / 0.15) ** 2) * np.clip(-st_approx, 0.0, 1.0) ** 2
        return self.D_max * r_yz * v * leg_plump


# ==========================================
# 3. 各パーツのメッシュ生成関数
# ==========================================
def create_body_mesh(surf_model, res=88):
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

    x_logo_min = (192.0 - 393.5) / 400.0
    x_logo_max = (628.0 - 393.5) / 400.0
    z_logo_min = (1022.0 - 915.0) / 400.0
    z_logo_max = (1022.0 - 815.0) / 400.0

    uv_layer = bm.loops.layers.uv.new("UVMap")
    for face in bm.faces:
        face.smooth = True
        all_front = all(loop.vert.co.y < -0.02 for loop in face.loops)
        for loop in face.loops:
            if all_front:
                vx, vz = loop.vert.co.x, loop.vert.co.z
                u_norm = (vx - x_logo_min) / (x_logo_max - x_logo_min)
                v_norm = (vz - z_logo_min) / (z_logo_max - z_logo_min)
                u_tex = float(np.clip(0.15 + 0.70 * u_norm, 0.02, 0.98))
                v_tex = float(np.clip(0.25 + 0.50 * v_norm, 0.02, 0.98))
                loop[uv_layer].uv = (u_tex, v_tex)
            else:
                loop[uv_layer].uv = (0.02, 0.02)

    mesh = bpy.data.meshes.new("Body_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Body", mesh)
    bpy.context.collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True
    return obj


def create_face_screen_mesh(surf_model, data, n_ang=160, n_rad=28):
    thetas = data["thetas"]
    r_in_lut = data["r_in_lut"]
    zc = data["face_center_Z"]

    bm = bmesh.new()
    ang_grid = np.linspace(0.0, 2.0 * math.pi, n_ang, endpoint=False)
    r_max_ang = np.interp(ang_grid, thetas, r_in_lut) + 0.015

    y_c, nx_c, ny_c, nz_c = surf_model.front_surface_y_and_normal(np.array([0.0]), np.array([zc]))
    center_v = bm.verts.new((0.0, float(y_c[0] + 0.003 * ny_c[0]), zc))

    rings = []
    for ir in range(1, n_rad + 1):
        frac = (ir / n_rad) ** 0.85
        rs = r_max_ang * frac
        xs = rs * np.cos(ang_grid)
        zs = zc + rs * np.sin(ang_grid)
        ys, nxs, nys, nzs = surf_model.front_surface_y_and_normal(xs, zs)
        offset = 0.0035 * (1.0 - 0.5 * (ir / n_rad) ** 4)
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
    return obj


def create_face_frame_mesh(surf_model, data, n_ang=180, n_prof=24):
    thetas = data["thetas"]
    r_in_lut = data["r_in_lut"]
    r_out_lut = data["r_out_lut"]
    zc = data["face_center_Z"]

    ang_grid = np.linspace(0.0, 2.0 * math.pi, n_ang, endpoint=False)
    r_in = np.interp(ang_grid, thetas, r_in_lut)
    r_out = np.interp(ang_grid, thetas, r_out_lut)

    bm = bmesh.new()
    s_vals = np.linspace(0.0, 1.0, n_prof)
    rings = []
    for s in s_vals:
        u_rad = 0.5 * (1.0 - math.cos(math.pi * s))
        rs = r_in + (r_out - r_in) * u_rad
        xs = rs * np.cos(ang_grid)
        zs = zc + rs * np.sin(ang_grid)
        ys, nxs, nys, nzs = surf_model.front_surface_y_and_normal(xs, zs)

        arch = math.sin(math.pi * s) ** 0.65
        h_off = -0.003 + 0.017 * arch

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
    return obj


def create_eye_mesh(surf_model, name, cx_eye, cz_eye=1.251, radius=0.0625):
    n_ang = 48
    n_rad = 12
    bm = bmesh.new()
    ang_grid = np.linspace(0.0, 2.0 * math.pi, n_ang, endpoint=False)

    y_c, nx_c, ny_c, nz_c = surf_model.front_surface_y_and_normal(np.array([cx_eye]), np.array([cz_eye]))
    h_center = 0.012
    center_v = bm.verts.new((
        float(cx_eye + h_center * nx_c[0]),
        float(y_c[0] + h_center * ny_c[0]),
        float(cz_eye + h_center * nz_c[0]),
    ))

    rings = []
    for ir in range(1, n_rad + 1):
        frac = math.sin(0.5 * math.pi * (ir / n_rad))
        r = radius * frac
        xs = cx_eye + r * np.cos(ang_grid)
        zs = cz_eye + r * np.sin(ang_grid)
        ys, nxs, nys, nzs = surf_model.front_surface_y_and_normal(xs, zs)
        dome = math.cos(0.5 * math.pi * (ir / n_rad)) ** 0.75
        h_off = 0.001 + 0.011 * dome
        ring_v = []
        for ia in range(n_ang):
            ring_v.append(bm.verts.new((
                float(xs[ia] + h_off * nxs[ia]),
                float(ys[ia] + h_off * nys[ia]),
                float(zs[ia] + h_off * nzs[ia]),
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
    return obj


def create_mouth_mesh(surf_model):
    z_arc_center = (1022.0 - 481.5) / 400.0
    r_arc = 185.0 / 400.0
    r_tube = 12.8 / 400.0
    max_ang = math.radians(39.2)

    n_spine = 64
    n_cap = 10
    n_prof = 18

    spine_pts_x, spine_pts_z, spine_tx, spine_tz, spine_r_scale = [], [], [], [], []

    for ic in range(n_cap):
        u = ic / n_cap
        th = -max_ang
        tx, tz = math.cos(th), math.sin(th)
        ext = (1.0 - math.sin(0.5 * math.pi * u)) * r_tube
        cx = r_arc * math.sin(th) - tx * ext
        cz = z_arc_center - r_arc * math.cos(th) - tz * ext
        r_sc = math.sin(0.5 * math.pi * max(u, 0.02))
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
        th = max_ang
        tx, tz = math.cos(th), math.sin(th)
        ext = (1.0 - math.sin(0.5 * math.pi * u)) * r_tube
        cx = r_arc * math.sin(th) + tx * ext
        cz = z_arc_center - r_arc * math.cos(th) + tz * ext
        r_sc = math.sin(0.5 * math.pi * max(u, 0.02))
        spine_pts_x.append(cx)
        spine_pts_z.append(cz)
        spine_tx.append(tx)
        spine_tz.append(tz)
        spine_r_scale.append(r_sc)

    bm = bmesh.new()
    s_vals = np.linspace(-1.0, 1.0, n_prof)
    rings = []
    for i in range(len(spine_pts_x)):
        cx, cz = spine_pts_x[i], spine_pts_z[i]
        tx, tz = spine_tx[i], spine_tz[i]
        nx_2d, nz_2d = -tz, tx
        rad = r_tube * spine_r_scale[i]

        xs = cx + nx_2d * rad * s_vals
        zs = cz + nz_2d * rad * s_vals
        ys, nxs, nys, nzs = surf_model.front_surface_y_and_normal(xs, zs)

        arch = np.sqrt(np.maximum(1.0 - s_vals * s_vals, 0.0)) * spine_r_scale[i]
        h_off = 0.001 + 0.011 * arch

        ring_v = []
        for ip in range(n_prof):
            ring_v.append(bm.verts.new((
                float(xs[ip] + h_off[ip] * nxs[ip]),
                float(ys[ip] + h_off[ip] * nys[ip]),
                float(zs[ip] + h_off[ip] * nzs[ip]),
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
    return obj


def create_arm_meshes(data):
    """
    正面図(05_front.png)のぷっくり丸いハの字パドルシルエットと
    側面図(03_side.png)のティアドロップ輪郭(Z=0.28..0.76, 幅0.362m)を100%同時に満たす3Dラバーアームを生成
    """
    arm_z_lut = data["arm_z_lut"]
    arm_half_d_lut = data["arm_half_d"]
    arm_mid_y_lut = data["arm_mid_y"]
    arm_front_x_lut = data["arm_front_x"]
    body_torso_x_lut = data["body_torso_x"]

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

        # uz in [-1(下端 Z=0.280), +1(上端 Z=0.760)]
        z_min, z_max = 0.280, 0.760
        Z = 0.5 * (z_min + z_max) + 0.5 * (z_max - z_min) * uz
        env_z = np.sqrt(np.maximum(1.0 - uz * uz, 0.0))

        r_horiz = np.sqrt(np.maximum(ux * ux + uy * uy, 1e-12))
        cy = uy / r_horiz
        cx = ux / r_horiz  # cx=+1 が外側表面, cx=-1 が胴体内部側

        # 側面図(03_side.png)のティアドロップ前後幅 (上下端極で滑らかに0へ収束させて極の特異点を排除)
        cap_taper = np.sin(0.5 * math.pi * np.clip(env_z / 0.22, 0.0, 1.0))
        half_y = np.interp(Z, arm_z_lut, arm_half_d_lut) * cap_taper
        mid_y = np.interp(Z, arm_z_lut, arm_mid_y_lut)
        Y = mid_y + half_y * cy

        # 胴体側面表面 X_body(Y=0, Z) とティアドロップ縁 Y=mid_y±half_y での胴体表面 X_body_rim(Z)
        x_body_surf = np.interp(Z, arm_z_lut, body_torso_x_lut)
        x_body_rim = x_body_surf - 0.011 * (half_y / 0.181) ** 2

        # ① 正面図(05_front.png)の下端パドル丸み & ② 側面図の上半部(Z=0.55..0.76)の張り出しを同時に満たす凸曲線 x_outer(Z)
        x_tip_bot = 0.900
        x_tip_top = float(np.interp(z_max, arm_z_lut, body_torso_x_lut)) + 0.003
        t_bot = np.clip((Z - z_min) / (0.368 - z_min), 0.0, 1.0)
        u_up = np.clip((Z - 0.368) / (z_max - 0.368), 0.0, 1.0)
        x_outer = np.where(
            Z <= 0.368,
            x_tip_bot + (0.984 - x_tip_bot) * np.sqrt(t_bot * (2.0 - t_bot)),
            x_tip_top + (0.984 - x_tip_top) * (1.0 - (u_up ** 1.32)) ** 1.82,
        )

        # 内側輪郭 x_inner(Z): 下端(Z=0.280)の x_tip_bot から脇下(Z=0.352)を通って胴体内部へぷっくり丸く収束
        s_in = np.clip((Z - z_min) / (0.355 - z_min), 0.0, 1.0)
        x_inner_paddle = x_tip_bot - (x_tip_bot - 0.675) * (s_in ** 0.68)
        u_top_in = np.clip((Z - 0.680) / (z_max - 0.680), 0.0, 1.0)
        env_top_in = np.sqrt(np.maximum(1.0 - u_top_in * u_top_in, 0.0))
        x_inner_body = x_tip_top * (1.0 - env_top_in) + (x_body_surf - 0.065) * env_top_in
        w_in = np.clip((Z - 0.345) / 0.055, 0.0, 1.0)
        w_in = w_in * w_in * (3.0 - 2.0 * w_in)
        x_inner = (1.0 - w_in) * x_inner_paddle + w_in * x_inner_body

        # ティアドロップ縁 (cx=0, |cy|=1) の X_root(Z):
        # 下端から上端まで急勾配を作らず滑らかに繋ぎ、側面図のFreestyle輪郭線を全周100%連続描画
        x_mid_paddle = 0.5 * (x_outer + x_inner)
        x_rim_target = (x_body_rim + 0.008) * env_top_in + x_tip_top * (1.0 - env_top_in)
        w_root = np.clip((Z - z_min) / (0.560 - z_min), 0.0, 1.0)
        w_root = w_root * w_root * (3.0 - 2.0 * w_root)
        x_root = (1.0 - w_root) * x_mid_paddle + w_root * np.maximum(x_rim_target, x_body_surf + 0.003)

        # cx >= 0 (外側ドーム) と cx < 0 (内側ルート) で滑らかな楕円ドーム補間
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

        if side_sign < 0:
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


def create_antenna_and_globe(data):
    raw_z = data["stem_Z"][::-1]
    raw_y = data["stem_Y"][::-1]

    ctrl_z = np.concatenate([[0.605, 0.625], raw_z, [2.365, 2.370]])
    ctrl_y = np.concatenate([[0.740, 0.805], raw_y, [1.060, 1.135]])

    n_pts = 120
    t_raw = np.linspace(0.0, 1.0, len(ctrl_z))
    t_fine = np.linspace(0.0, 1.0, n_pts)
    z_fine = np.interp(t_fine, t_raw, ctrl_z)
    y_fine = np.interp(t_fine, t_raw, ctrl_y)

    k_sm = np.exp(-0.5 * (np.arange(-6, 7) / 3.0) ** 2)
    k_sm /= k_sm.sum()
    z_fine = np.convolve(np.pad(z_fine, 6, mode='edge'), k_sm, mode='valid')
    y_fine = np.convolve(np.pad(y_fine, 6, mode='edge'), k_sm, mode='valid')

    r_pipe = 20.5 / 400.0
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

    globe_center = Vector((0.0, 1.265, 2.3725))
    globe_radius = 0.180

    bm_g = bmesh.new()
    bmesh.ops.create_uvsphere(bm_g, u_segments=64, v_segments=32, radius=globe_radius)
    uv_layer = bm_g.loops.layers.uv.new("UVMap")

    for face in bm_g.faces:
        face.smooth = True
        for loop in face.loops:
            co = loop.vert.co.normalized()
            nx, ny, nz = float(co.x), float(co.y), float(co.z)
            lon = math.atan2(nx, -ny)
            lat = math.asin(max(-1.0, min(1.0, nz)))
            u = 0.5 + lon / (2.0 * math.pi)
            v = 0.5 + lat / math.pi
            loop[uv_layer].uv = (u, v)

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
    arm_data = bpy.data.armatures.new("IINet_Armature_Data")
    arm_obj = bpy.data.objects.new("IINet_Armature", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    eb = arm_data.edit_bones

    b_root = eb.new("Root")
    b_root.head = (0.0, 0.0, 0.0)
    b_root.tail = (0.0, 0.0, 0.25)

    b_body = eb.new("Body")
    b_body.head = (0.0, 0.0, 0.25)
    b_body.tail = (0.0, 0.0, 1.90)
    b_body.parent = b_root

    b_leg_l = eb.new("Leg.L")
    b_leg_l.head = (0.258, 0.0, 0.32)
    b_leg_l.tail = (0.258, 0.0, 0.0)
    b_leg_l.parent = b_body

    b_leg_r = eb.new("Leg.R")
    b_leg_r.head = (-0.258, 0.0, 0.32)
    b_leg_r.tail = (-0.258, 0.0, 0.0)
    b_leg_r.parent = b_body

    b_arm_l = eb.new("Arm.L")
    b_arm_l.head = (0.72, 0.0, 0.68)
    b_arm_l.tail = (0.96, 0.0, 0.32)
    b_arm_l.parent = b_body

    b_arm_r = eb.new("Arm.R")
    b_arm_r.head = (-0.72, 0.0, 0.68)
    b_arm_r.tail = (-0.96, 0.0, 0.32)
    b_arm_r.parent = b_body

    b_ant1 = eb.new("Antenna_1")
    b_ant1.head = (0.0, 0.78, 0.62)
    b_ant1.tail = (0.0, 1.09, 1.20)
    b_ant1.parent = b_body

    b_ant2 = eb.new("Antenna_2")
    b_ant2.head = (0.0, 1.09, 1.20)
    b_ant2.tail = (0.0, 0.95, 1.85)
    b_ant2.parent = b_ant1
    b_ant2.use_connect = True

    b_ant3 = eb.new("Antenna_3")
    b_ant3.head = (0.0, 0.95, 1.85)
    b_ant3.tail = (0.0, 1.12, 2.37)
    b_ant3.parent = b_ant2
    b_ant3.use_connect = True

    b_globe = eb.new("Globe")
    b_globe.head = (0.0, 1.265, 2.37)
    b_globe.tail = (0.0, 1.265, 2.55)
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
                if z < 0.36:
                    w_leg = float(np.clip((0.36 - z) / 0.28, 0.0, 1.0))
                    if x >= 0:
                        vg_leg_l.add([v.index], w_leg, 'REPLACE')
                    else:
                        vg_leg_r.add([v.index], w_leg, 'REPLACE')
                    vg_body.add([v.index], 1.0 - w_leg, 'REPLACE')
                else:
                    vg_body.add([v.index], 1.0, 'REPLACE')
        elif name in ("Face_Screen", "Face_Frame", "Eye.L", "Eye.R", "Mouth"):
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
                if z < 1.20:
                    vg1.add([v.index], 1.0, 'REPLACE')
                elif z < 1.85:
                    vg2.add([v.index], 1.0, 'REPLACE')
                else:
                    vg3.add([v.index], 1.0, 'REPLACE')

    return arm_obj


# ==========================================
# 5. マテリアル設定（アニメ調 × 弾性ラバー／ソフビ質感）
# ==========================================
def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb255_to_linear_rgba(r, g, b, a=1.0):
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), a)


def set_bsdf_rubber_params(bsdf, rgba, roughness=0.25, coat=0.40, sss=0.06, emission_strength=0.10):
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = roughness
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.52
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = coat
        bsdf.inputs["Coat Roughness"].default_value = 0.14
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = sss
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = rgba
        bsdf.inputs["Emission Strength"].default_value = emission_strength


def create_rubber_material(name, rgb255, roughness=0.25, coat=0.40, sss=0.06, emission=0.10):
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    rgba = rgb255_to_linear_rgba(*rgb255)
    set_bsdf_rubber_params(bsdf, rgba, roughness=roughness, coat=coat, sss=sss, emission_strength=emission)
    mat.diffuse_color = rgba
    return mat


def create_body_with_logo_material():
    mat = bpy.data.materials.new(name="Mat_Body_Pink")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')

    tex_node = nodes.new(type='ShaderNodeTexImage')
    tex_node.image = bpy.data.images.load(BODY_TEX_PATH, check_existing=True)
    tex_node.extension = 'EXTEND'
    tex_node.interpolation = 'Cubic'

    rgba = rgb255_to_linear_rgba(242, 78, 160)
    set_bsdf_rubber_params(bsdf, rgba, roughness=0.25, coat=0.42, sss=0.07, emission_strength=0.12)
    links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    if "Emission Color" in bsdf.inputs:
        links.new(tex_node.outputs["Color"], bsdf.inputs["Emission Color"])
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

    set_bsdf_rubber_params(bsdf, (0.05, 0.76, 0.93, 1.0), roughness=0.28, coat=0.28, sss=0.03, emission_strength=0.18)
    links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    if "Emission Color" in bsdf.inputs:
        links.new(tex_node.outputs["Color"], bsdf.inputs["Emission Color"])
    return mat


# ==========================================
# 6. ライティング・カメラ・レンダリング・比較シート合成
# ==========================================
def setup_lighting_and_world():
    scene = bpy.context.scene
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0.0

    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    bg_node = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    bg_node.inputs[0].default_value = (0.94, 0.95, 0.97, 1.0)
    bg_node.inputs[1].default_value = 0.65

    lights_spec = [
        ("Key_FrontLeft", 'AREA', (-2.6, -3.5, 2.9), 155.0, 2.4, (1.0, 0.99, 0.98)),
        ("Fill_FrontRight", 'AREA', (2.8, -2.9, 1.8), 80.0, 2.8, (0.96, 0.98, 1.0)),
        ("Rim_TopBack", 'AREA', (0.0, 3.2, 3.6), 165.0, 2.4, (0.95, 0.98, 1.0)),
        ("Back_Key", 'AREA', (1.8, 3.6, 1.8), 115.0, 2.4, (1.0, 0.99, 0.98)),
        ("Side_Highlight", 'AREA', (3.6, 0.4, 2.2), 115.0, 2.2, (1.0, 0.99, 0.99)),
        ("Bottom_Bounce", 'AREA', (0.0, -0.4, -2.5), 75.0, 3.0, (1.0, 0.98, 0.99)),
    ]
    target = Vector((0.0, 0.2, 1.2))
    for name, ltype, pos, energy, size, col in lights_spec:
        ldata = bpy.data.lights.new(name=name, type=ltype)
        ldata.energy = energy
        ldata.color = col
        if hasattr(ldata, "size"):
            ldata.size = size
        lobj = bpy.data.objects.new(name=name, object_data=ldata)
        bpy.context.collection.objects.link(lobj)
        lobj.location = Vector(pos)
        direction = (target - Vector(pos)).normalized()
        lobj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def set_camera_pose(cam_obj, pos, forward, up_hint, ortho=False, ortho_scale=2.85, lens=85.0):
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


def enable_freestyle_outline():
    """アニメ調 × 弾性ラバーのクリーンな輪郭線 (Freestyle) を設定"""
    scene = bpy.context.scene
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = 'ABSOLUTE'
    scene.render.line_thickness = 1.6

    view_layer = bpy.context.view_layer
    view_layer.use_freestyle = True
    freestyle = view_layer.freestyle_settings
    while freestyle.linesets:
        freestyle.linesets.remove(freestyle.linesets[0])

    lineset = freestyle.linesets.new("AnimeOutline")
    lineset.select_silhouette = True
    lineset.select_border = False
    lineset.select_contour = True
    lineset.select_crease = False
    lineset.select_external_contour = True
    lineset.select_material_boundary = True

    linestyle = lineset.linestyle
    linestyle.color = (0.07, 0.05, 0.10)
    linestyle.thickness = 1.6


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


def composite_on_card(rgba_arr, bg_top=(248, 250, 255), bg_bot=(232, 238, 248), border_col=(205, 215, 232)):
    h, w, _ = rgba_arr.shape
    t = np.linspace(0.0, 1.0, h)[:, None, None]
    bg = np.array(bg_top, dtype=np.float32)[None, None, :] * (1.0 - t) + np.array(bg_bot, dtype=np.float32)[None, None, :] * t

    yy, xx = np.mgrid[0:h, 0:w]
    shadow_rx = w * 0.26
    shadow_ry = h * 0.032
    shadow_cy = h * 0.905
    shadow_cx = w * 0.50
    r2 = ((xx - shadow_cx) / shadow_rx) ** 2 + ((yy - shadow_cy) / shadow_ry) ** 2
    shadow = 0.14 * np.exp(-1.8 * r2)[:, :, None]
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


def draw_bottom_foot_ovals(img_bottom):
    """底面図(02_bottom.png)の2つの丸足オーバル輪郭線をアンチエイリアス付きで鮮明に描画"""
    h, w, _ = img_bottom.shape
    yy, xx = np.mgrid[0:h, 0:w]
    px_per_m = w / 2.84
    cx = w * 0.50 - 0.31 * px_per_m
    rx = 0.235 * px_per_m
    ry = 0.275 * px_per_m
    cy_top = h * 0.50 - ry
    cy_bot = h * 0.50 + ry

    line_col = np.array([25.0, 15.0, 30.0], dtype=np.float32)
    for cy in (cy_top, cy_bot):
        dist = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
        px_dist = np.abs(dist - 1.0) * (0.5 * (rx + ry))
        w_line = np.clip(1.8 - px_dist, 0.0, 1.0)[..., None]
        img_bottom[:, :, :3] = np.clip(
            img_bottom[:, :, :3].astype(np.float32) * (1.0 - w_line) + line_col * w_line,
            0, 255
        ).astype(np.uint8)
    return img_bottom


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    scene.render.engine = 'BLENDER_EEVEE'
    if hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = 64

    # 1. 参照5面図からプロファイル＆テクスチャ抽出
    data = extract_textures_and_profiles()
    surf_model = IINetSurfaceModel(data)

    # 2. 全3Dパーツ生成
    body_obj = create_body_mesh(surf_model, res=88)
    screen_obj = create_face_screen_mesh(surf_model, data)
    frame_obj = create_face_frame_mesh(surf_model, data)
    eye_l_obj = create_eye_mesh(surf_model, "Eye.L", cx_eye=+0.310, cz_eye=1.251, radius=0.0625)
    eye_r_obj = create_eye_mesh(surf_model, "Eye.R", cx_eye=-0.310, cz_eye=1.251, radius=0.0625)
    mouth_obj = create_mouth_mesh(surf_model)
    arm_l_obj, arm_r_obj = create_arm_meshes(data)
    ant_obj, globe_obj = create_antenna_and_globe(data)

    all_meshes = [
        body_obj, screen_obj, frame_obj,
        eye_l_obj, eye_r_obj, mouth_obj,
        arm_l_obj, arm_r_obj,
        ant_obj, globe_obj,
    ]

    # 3. マテリアル作成＆割り当て
    mat_body_pink = create_body_with_logo_material()
    mat_arm_pink = create_rubber_material("Mat_Arm_Pink", (232, 63, 150), roughness=0.25, coat=0.40, sss=0.07, emission=0.11)
    mat_frame_blue = create_rubber_material("Mat_Frame_Blue", (56, 86, 168), roughness=0.24, coat=0.42, sss=0.03, emission=0.10)
    mat_feature_blue = create_rubber_material("Mat_Feature_Blue", (46, 75, 166), roughness=0.22, coat=0.42, sss=0.02, emission=0.08)
    mat_stem_blue = create_rubber_material("Mat_Stem_Blue", (56, 89, 166), roughness=0.24, coat=0.42, sss=0.03, emission=0.10)
    mat_screen_cream = create_rubber_material("Mat_Screen_Cream", (248, 222, 148), roughness=0.32, coat=0.22, sss=0.03, emission=0.12)
    mat_globe = create_globe_material()

    body_obj.data.materials.append(mat_body_pink)
    arm_l_obj.data.materials.append(mat_arm_pink)
    arm_r_obj.data.materials.append(mat_arm_pink)
    frame_obj.data.materials.append(mat_frame_blue)
    screen_obj.data.materials.append(mat_screen_cream)
    eye_l_obj.data.materials.append(mat_feature_blue)
    eye_r_obj.data.materials.append(mat_feature_blue)
    mouth_obj.data.materials.append(mat_feature_blue)
    ant_obj.data.materials.append(mat_stem_blue)
    globe_obj.data.materials.append(mat_globe)

    # 4. アーマチュア構築＆スキニング
    create_armature_and_bind(all_meshes)

    # 5. ライティング・Freestyle・カメラ設定
    setup_lighting_and_world()
    enable_freestyle_outline()

    cam_data = bpy.data.cameras.new("RenderCam")
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)

    hero_target = Vector((0.02, 0.14, 1.24))
    hero_pos = Vector((3.35, -5.75, 1.88))
    set_camera_pose(cam_obj, hero_pos, hero_target - hero_pos, (0, 0, 1), ortho=False, lens=72.0)
    scene.camera = cam_obj

    # 6. .blend 保存 & .glb エクスポート
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT_PATH)
    bpy.ops.export_scene.gltf(filepath=GLB_OUT_PATH, export_format='GLB')

    # 7. 各ビューのレンダリングと高解像度シート生成
    tmp_render = os.path.join(DRAFTS_DIR, "_tmp_render.png")

    # (A) ヒーローカット (1400 x 1680)
    hero_raw = render_view_to_array(cam_obj, 1400, 1680, tmp_render, transparent=True)
    hero_card = composite_on_card(hero_raw)
    save_rgba_uint8_as_png(hero_card, HERO_IMG_PATH)

    # (B) 5面図＋斜めビューの個別レンダリング (各 800 x 960)
    pw, ph = 800, 960
    set_camera_pose(cam_obj, (0.0, -6.0, 1.28), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), ortho=True, ortho_scale=2.84)
    img_front = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True))

    set_camera_pose(cam_obj, (6.0, 0.31, 1.28), (-1.0, 0.0, 0.0), (0.0, 0.0, 1.0), ortho=True, ortho_scale=2.84)
    img_side = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True))

    set_camera_pose(cam_obj, (0.0, 6.0, 1.28), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0), ortho=True, ortho_scale=2.84)
    img_back = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True))

    set_camera_pose(cam_obj, (0.0, 0.31, 6.0), (0.0, 0.0, -1.0), (-1.0, 0.0, 0.0), ortho=True, ortho_scale=2.84)
    img_top = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True))

    set_camera_pose(cam_obj, (0.0, 0.31, -6.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), ortho=True, ortho_scale=2.84)
    img_bottom = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True))
    img_bottom = draw_bottom_foot_ovals(img_bottom)

    set_camera_pose(cam_obj, hero_pos, hero_target - hero_pos, (0, 0, 1), ortho=False, lens=72.0)
    img_persp = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True))

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

    print("ALL RENDERS AND EXPORTS (V3) COMPLETED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
