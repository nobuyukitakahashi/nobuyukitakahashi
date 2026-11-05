# -*- coding: utf-8 -*-
"""
株式会社CVN キャラクター「いい-NETくん（胸ロゴ：LILI-net）」
Blender 5.2 3Dモデリング・リギング・マテリアル・レンダリング一括構築スクリプト (v3: アーム完全整合＆視覚監査仕上げ版)
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

FRONT_REF_PATH = os.path.join(REF_DIR, "05_front.png")
SIDE_REF_PATH = os.path.join(REF_DIR, "03_side.png")
LOGO_DECAL_PATH = os.path.join(DRAFTS_DIR, "lili_net_logo_decal.png")
BODY_TEX_PATH = os.path.join(DRAFTS_DIR, "body_pink_with_logo.png")
GLOBE_TEX_PATH = os.path.join(DRAFTS_DIR, "globe_texture.png")

BLEND_OUT_PATH = os.path.join(OUTPUT_DIR, "cvn_iinet_kun.blend")
GLB_OUT_PATH = os.path.join(OUTPUT_DIR, "cvn_iinet_kun.glb")

HERO_IMG_PATH = os.path.join(OUTPUT_DIR, "iinet_kun_hero_3quarter.png")
FRONT_IMG_PATH = os.path.join(OUTPUT_DIR, "iinet_kun_front.png")
BOARD_IMG_PATH = os.path.join(OUTPUT_DIR, "iinet_kun_front_and_side.png")
SHEET_IMG_PATH = os.path.join(OUTPUT_DIR, "iinet_kun_5views_sheet.png")

# 別バージョン（顔の青枠＝非立体フラット曲面仕様）出力パス
FLAT_BLEND_OUT_PATH = os.path.join(OUTPUT_DIR, "cvn_iinet_kun_flat_frame.blend")
FLAT_GLB_OUT_PATH = os.path.join(OUTPUT_DIR, "cvn_iinet_kun_flat_frame.glb")
FLAT_HERO_IMG_PATH = os.path.join(OUTPUT_DIR, "iinet_kun_flat_frame_hero_3quarter.png")
FLAT_FRONT_IMG_PATH = os.path.join(OUTPUT_DIR, "iinet_kun_flat_frame_front.png")
FLAT_BOARD_IMG_PATH = os.path.join(OUTPUT_DIR, "iinet_kun_flat_frame_front_and_side.png")
FLAT_SHEET_IMG_PATH = os.path.join(OUTPUT_DIR, "iinet_kun_flat_frame_5views_sheet.png")


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

    # --- (B) 頭上の地球儀テクスチャ生成 (2048x1024 全周360度・世界大陸Equirectangularマップ) ---
    gw, gh = 2048, 1024
    u_grid = np.linspace(0.0, 1.0, gw, endpoint=False)[None, :]
    v_grid = np.linspace(0.0, 1.0, gh)[:, None]
    lon_deg = (u_grid - 0.5) * 360.0
    lat_deg = (0.5 - v_grid) * 180.0
    lon_rad = np.radians(lon_deg)
    lat_rad = np.radians(lat_deg)

    # 3D単位球面上の座標 (経度±180度境界で完全周期・シームレスな海岸線摂動を生成)
    nx_s = np.cos(lat_rad) * np.sin(lon_rad)
    ny_s = -np.cos(lat_rad) * np.cos(lon_rad)
    nz_s = np.sin(lat_rad)

    w_lon = (
        0.45 * np.sin(7.0 * nx_s + 5.0 * ny_s + 4.0 * nz_s)
        + 0.30 * np.cos(13.0 * nx_s - 11.0 * ny_s + 9.0 * nz_s)
        + 0.18 * np.sin(23.0 * nx_s + 19.0 * ny_s - 17.0 * nz_s)
        + 0.10 * np.cos(37.0 * nx_s - 29.0 * ny_s + 31.0 * nz_s)
    )
    w_lat = (
        0.45 * np.cos(6.0 * nx_s - 8.0 * ny_s + 5.0 * nz_s)
        + 0.30 * np.sin(15.0 * nx_s + 12.0 * ny_s - 10.0 * nz_s)
        + 0.18 * np.cos(25.0 * nx_s - 21.0 * ny_s + 19.0 * nz_s)
        + 0.10 * np.sin(41.0 * nx_s + 33.0 * ny_s - 27.0 * nz_s)
    )
    lon_w = ((lon_deg + 2.4 * w_lon + 180.0) % 360.0) - 180.0
    lat_w = np.clip(lat_deg + 1.5 * w_lat, -89.9, 89.9)

    # Rev.9: 正面図(lon=0°, lat=0°付近)の地球儀ど真ん中に日本列島(北海道・本州・四国・九州)がクッキリ独立して見える360度世界地図配置
    continental_polygons = [
        # 1. ユーラシア大陸(東アジア・中国・朝鮮半島・シベリア・カムチャツカ・インド・中央アジア)
        [(-76, 40), (-68, 64), (-42, 70), (-5, 70), (24, 65), (40, 56), (35, 42), (29, 41), (27, 51),
         (12, 49), (-4, 41), (-10, 26), (-8, 11), (-13, 9), (-16, 18), (-23, 15), (-20, 4),
         (-26, -6), (-32, -8), (-31, -18), (-36, -19), (-39, -6), (-45, 4), (-52, 14), (-56, -4), (-62, -2),
         (-68, 16), (-76, 24)],
        # 2. 東南アジア諸島 (スマトラ・ジャワ・ボルネオ・ニューギニア)
        [(-42, -20), (-30, -27), (-18, -28), (-20, -24), (-32, -22), (-40, -17)],
        [(-26, -22), (-14, -22), (-13, -15), (-23, -15)],
        [(10, -24), (30, -25), (32, -18), (12, -17)],
        # 3. オーストラリア大陸・ニュージーランド (正面右下〜側面左下〜底面)
        [(8, -38), (18, -30), (34, -29), (48, -34), (52, -44), (44, -52), (26, -53), (10, -48)],
        [(58, -56), (68, -46), (63, -43), (54, -53)],
        # 4. アラビア半島・アフリカ大陸・マダガスカル (正面左端〜側面〜背面左)
        [(-88, 24), (-76, 26), (-66, 16), (-72, 6), (-82, 8)],
        [(-128, 10), (-130, 22), (-122, 32), (-106, 33), (-96, 29), (-88, 28), (-80, 12), (-78, 8),
         (-86, -4), (-88, -16), (-96, -28), (-104, -36), (-112, -35), (-114, -20), (-116, -6), (-122, 4)],
        [(-82, -15), (-77, -16), (-79, -27), (-84, -28)],
        # 5. ヨーロッパ・スカンジナビア・イギリス・グリーンランド (上面〜背面左)
        [(-126, 37), (-128, 44), (-118, 46), (-114, 52), (-102, 56), (-90, 60), (-74, 62), (-72, 46),
         (-82, 40), (-92, 38), (-100, 42), (-112, 42), (-118, 36)],
        [(-108, 58), (-102, 68), (-88, 71), (-78, 66), (-86, 60), (-98, 57)],
        [(-126, 50), (-122, 58), (-116, 57), (-118, 50)],
        [(164, 60), (158, 72), (172, 80), (192, 77), (188, 65), (174, 59)],
        # 6. 北アメリカ大陸・アラスカ・中央アメリカ (側面右〜背面中央上〜上面)
        [(68, 54), (78, 67), (102, 71), (134, 69), (152, 62), (162, 50), (152, 34), (144, 24),
         (136, 28), (124, 24), (116, 14), (126, 8), (114, 7), (98, 16), (84, 28), (74, 42)],
        # 7. 南アメリカ大陸 (側面右下〜背面中央下〜底面)
        [(118, 10), (144, 7), (164, -4), (174, -12), (168, -26), (152, -40), (136, -51),
         (126, -54), (118, -48), (120, -32), (116, -16), (108, -4), (112, 5)],
        # 8. ハワイ・太平洋諸島
        [(52, 8), (62, 11), (60, 16), (50, 12)],
    ]

    # 日本列島(北海道・本州・四国・九州): 正面カメラ(lon=0°, lat=0°)のど真ん中領域に配置し、
    # 大陸と重ならず日本の弓なりシルエットと4島がクッキリ一目で判別できるように描画
    japan_polygons = [
        # 北海道 (Hokkaido)
        [(11.5, 18.5), (13.8, 24.5), (17.5, 28.5), (22.0, 25.5), (24.8, 22.2), (20.2, 18.8), (15.8, 17.0), (12.2, 16.8)],
        # 本州 (Honshu - 東北〜関東〜中部〜近畿〜中国地方の弓なり形状)
        [(10.8, 14.8), (15.5, 13.8), (16.4, 8.2), (14.5, 2.0), (11.2, -1.2), (7.0, -2.4),
         (2.8, -3.2), (-2.8, -2.5), (-3.8, 0.2), (1.8, 2.2), (6.5, 4.2), (9.0, 8.0), (9.8, 12.2)],
        # 四国 (Shikoku)
        [(0.2, -7.2), (5.6, -5.6), (4.8, -3.8), (-0.4, -5.2)],
        # 九州 (Kyushu)
        [(-6.8, -11.0), (-2.0, -10.0), (-1.2, -4.4), (-5.2, -3.8), (-7.2, -7.2)],
    ]

    def rasterize_polygons(poly_list, lon_field, lat_field, out_mask):
        for poly in poly_list:
            pts = np.asarray(poly, dtype=np.float64)
            px, py = pts[:, 0], pts[:, 1]
            lon0 = 0.5 * (px.min() + px.max())
            lon_rel = lon0 + ((lon_field - lon0 + 180.0) % 360.0) - 180.0
            in_bbox = (
                (lon_rel >= px.min() - 0.5) & (lon_rel <= px.max() + 0.5)
                & (lat_field >= py.min() - 0.5) & (lat_field <= py.max() + 0.5)
            )
            if not np.any(in_bbox):
                continue
            xs = lon_rel[in_bbox]
            ys = lat_field[in_bbox]
            inside = np.zeros(xs.shape, dtype=bool)
            n_v = len(pts)
            j = n_v - 1
            for i in range(n_v):
                xi, yi = px[i], py[i]
                xj, yj = px[j], py[j]
                cond = ((yi > ys) != (yj > ys)) & (xs < (xj - xi) * (ys - yi) / ((yj - yi) + 1e-12) + xi)
                inside ^= cond
                j = i
            out_mask[in_bbox] |= inside

    is_land = np.zeros((gh, gw), dtype=bool)
    rasterize_polygons(continental_polygons, lon_w, lat_w, is_land)
    rasterize_polygons(japan_polygons, np.broadcast_to(lon_deg, (gh, gw)), np.broadcast_to(lat_deg, (gh, gw)), is_land)

    # 海岸線のジャギーを防ぐアンチエイリアス補間
    land_f = is_land.astype(np.float32)
    land_aa = (
        0.52 * land_f
        + 0.12 * (
            np.roll(land_f, 1, axis=1) + np.roll(land_f, -1, axis=1)
            + np.roll(land_f, 1, axis=0) + np.roll(land_f, -1, axis=0)
        )
    )
    ocean_rgb = np.array([16.0, 196.0, 238.0], dtype=np.float32)
    land_rgb = np.array([0.0, 156.0, 52.0], dtype=np.float32)
    globe_rgb = ocean_rgb[None, None, :] * (1.0 - land_aa[:, :, None]) + land_rgb[None, None, :] * land_aa[:, :, None]

    globe_tex = np.zeros((gh, gw, 4), dtype=np.uint8)
    globe_tex[:, :, :3] = np.clip(np.round(globe_rgb), 0, 255).astype(np.uint8)
    globe_tex[:, :, 3] = 255
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
        # Rev.10最終調整: 原画(05_front.png / 03_side.png)のふっくら丸いタマゴ底とスマートな横幅を両立
        self.body_x_scale = 0.940
        self.W_max = float(self.X_lut[-1]) * self.body_x_scale  # 0.86128 m
        self.D_back = 0.74000                                   # 背面奥行き (m)
        self.D_front = 0.70000                                  # 前面奥行き (m)
        self.Z_eq = (1022.0 - 560.0) / 400.0                    # 1.15500 m
        self.Z_apex = 2.01000                                   # 頭頂高さ (m)
        self.x_foot = 0.24200                                   # 左右の足先の中心X座標 (m)
        self.z_tip = -0.06800                                   # 足先の最下端Z座標 (m)
        self.z_crotch = 0.15200                                 # 股下アーチ中央のZ座標 (m)

    def _front_y_from_d_ell(self, d_ell):
        """
        前面(ny < 0)の深さ関数:
        純粋な楕円断面 (-D_front * d_ell) とし、側面図・上面図・斜め3/4ビューで100%滑らかなタマゴ型曲線を実現
        """
        return -self.D_front * np.clip(d_ell, 0.0, 1.0)

    def z_top_of_x(self, abs_x):
        """
        Rev.4: 2D画像のピクセル階段ノイズを完全排除した C^∞ 解析的頭部ドーム曲線
        """
        u = np.clip(abs_x / self.W_max, 0.0, 1.0)
        return self.Z_eq + (self.Z_apex - self.Z_eq) * ((1.0 - u * u) ** 0.480)

    def _f_convex_profile(self, u, alpha, delta):
        """
        u in [0, 1] に対して f(0)=1, f(1)=0, f'(0)=0, f'(1)=-inf かつ
        全区間 u in (0, 1) で二階微分 f''(u) < 0 (変曲点・凹みゼロの完全凸曲線) を満たす解析関数
        """
        u_clamped = np.clip(np.abs(u), 0.0, 1.0)
        circ = np.sqrt(np.maximum(1.0 - u_clamped * u_clamped, 0.0))
        denom = math.hypot(1.0, delta) - delta
        hyp = 1.0 - (np.sqrt(u_clamped * u_clamped + delta * delta) - delta) / denom
        return (1.0 - alpha) * circ + alpha * hyp

    def _eval_lower_z(self, abs_x, abs_ct):
        """
        下半球 (Z <= Z_eq) の高さを、胴体から足先まで一度も凹まない単一の強凸曲面として評価
        前後方向(f_y)に alpha=0.06, delta=0.45 のふっくら丸い楕円弧を採用し、
        側面図(03_side.png)の丸いタマゴ底と斜め3/4ビューの滑らかな曲線を完全再現
        """
        # 1) 外側輪郭 (|X| >= x_foot): 赤道(W_max, Z_eq)から足先(x_foot, z_tip)まで滑らかな単一凸曲線
        u_out = np.clip((abs_x - self.x_foot) / (self.W_max - self.x_foot), 0.0, 1.0)
        f_x = self._f_convex_profile(u_out, alpha=0.28, delta=0.30)
        z_outer = self.Z_eq - (self.Z_eq - self.z_tip) * f_x

        # 2) 内側股下アーチ (|X| < x_foot)
        w_in = np.clip((self.x_foot - abs_x) / self.x_foot, 0.0, 1.0)
        p_in = 0.38 * (w_in ** 2) * (3.0 - 2.0 * w_in) + 0.62 * (w_in ** 3) * (4.0 - 3.0 * w_in)
        dz_crotch = (self.z_crotch - self.z_tip) * p_in

        # お腹・お尻では股下の溝を滑らかにゼロへ減衰させる (0.58まで広く緩やかに減衰させることで底面のくぼみを完全排除)
        t_cy = np.clip(abs_ct / 0.58, 0.0, 1.0)
        crotch_y_weight = (1.0 - t_cy * t_cy) ** 2
        z_b = z_outer + dz_crotch * crotch_y_weight

        # 3) 前後方向 (Y-Z断面): V字の尖りをなくし、原図 03_side.png 通りのふっくら丸い楕円底にするため alpha=0.06, delta=0.45 を使用
        f_y = self._f_convex_profile(abs_ct, alpha=0.06, delta=0.45)
        return self.Z_eq - (self.Z_eq - z_b) * f_y

    def map_unit_sphere_to_body(self, nx, ny, nz):
        X = self.W_max * nx
        Y = np.where(ny >= 0.0, self.D_back * ny, self._front_y_from_d_ell(-ny))
        abs_x = np.abs(X)

        r_yz = np.sqrt(np.maximum(ny * ny + nz * nz, 1e-12))
        abs_ct = np.clip(np.abs(ny) / r_yz, 0.0, 1.0)
        st = nz / r_yz

        # 上半球 (st >= 0): 純粋な楕円断面 × C^∞ 解析ドーム曲線
        z_t = self.z_top_of_x(abs_x)
        Z_upper = self.Z_eq + (z_t - self.Z_eq) * np.maximum(st, 0.0)

        # 下半球 (st < 0): 胴体から足先まで凹みゼロで連続する単一凸曲面
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

        # 上半球 (Z >= Z_eq): 解析解 st = (Z - Z_eq) / (z_t - Z_eq), |ct| = sqrt(1 - st^2)
        st_up = np.clip((Z - self.Z_eq) / np.maximum(z_t - self.Z_eq, 1e-5), 0.0, 0.9999)
        ct_up = np.sqrt(np.maximum(1.0 - st_up * st_up, 0.0))

        # 下半球 (Z < Z_eq): _eval_lower_z(abs_x, abs_ct) = Z を満たす abs_ct in [0, 1] を二分法で高精度逆算
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
def create_body_mesh(surf_model, res=128):
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

    # 足先・股下下部 (Z < 0.24m) に体積収縮のない Taubin スムージングを適用し、胸ロゴ領域(Z>=0.26m)の曲面精度を100%維持
    adj = [[e.other_vert(v).index for e in v.link_edges] for v in verts]
    pos = np.array([[v.co.x, v.co.y, v.co.z] for v in verts], dtype=np.float64)
    w_sm = np.clip((0.24 - pos[:, 2]) / 0.12, 0.0, 1.0)[:, None]
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
    胸元の「LILI-net」ロゴを独立した高精細3D立体メッシュとして生成し、
    ボディ前面曲面に沿って法線方向へ +0.024m ぷっくり張り出させる
    """
    im_f = load_image_rgba_uint8(FRONT_REF_PATH)
    crop = im_f[815:915, 192:628].astype(np.float32)
    R, G, B = crop[:, :, 0], crop[:, :, 1], crop[:, :, 2]
    y_raw = np.clip((0.5 * (R + G) - B) / 190.0, 0.0, 1.0)

    # 2Dガウシアンスムージングでピクセル階段を滑らかな連続スカラー場へ変換
    k1d = np.array([0.12, 0.23, 0.30, 0.23, 0.12], dtype=np.float32)
    y_smooth = np.apply_along_axis(lambda m: np.convolve(np.pad(m, 2, mode='edge'), k1d, mode='valid'), 0, y_raw)
    y_smooth = np.apply_along_axis(lambda m: np.convolve(np.pad(m, 2, mode='edge'), k1d, mode='valid'), 1, y_smooth)

    H, W = y_smooth.shape
    cell_mask = (0.25 * (y_smooth[:-1, :-1] + y_smooth[1:, :-1] + y_smooth[:-1, 1:] + y_smooth[1:, 1:]) > 0.36).copy()

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
                x_px = 192.0 + float(c)
                y_px = 815.0 + float(r)
                # Rev.10改: 画面枠の下のピンク領域中央にバランスよく配置
                x_logo = ((x_px - 393.5) / 400.0) * 0.94
                z_logo = 0.375 + ((1022.0 - y_px) / 400.0 - 0.014 - 0.35) * 0.95
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

    # マテリアル割り当て: 0 = 前面マットイエロー, 1 = 立体側面ウォール
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

    # 前面キャップ縁をごくわずかに内側へインセット(ベベル傾斜)させ、正面からも3D立体側面が自然に見えるようにする
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

    # すべての頂点をボディ前面曲面 (X, Y_surf, Z) + 法線方向オフセット h へ投影
    all_verts = list(bm.verts)
    xs = np.array([v.co.x for v in all_verts], dtype=np.float64)
    zs = np.array([v.co.y for v in all_verts], dtype=np.float64)
    ys, nxs, nys, nzs = surf_model.front_surface_y_and_normal(xs, zs)

    for idx, v in enumerate(all_verts):
        h_off = 0.024 if (v in extruded_set) else -0.005
        v.co = Vector((
            float(xs[idx] + h_off * nxs[idx]),
            float(ys[idx] + h_off * nys[idx]),
            float(zs[idx] + h_off * nzs[idx]),
        ))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new("Logo_LILI_net_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Logo_LILI_net", mesh)
    bpy.context.collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True
    return obj


def _compute_scaled_face_radii(data, ang_grid):
    """
    Rev.10改2: 画面の青枠をひと回り小さく(frame_scale=0.805)調整し、
    さらに四隅の角張りを滑らかな楕円弧とブレンドして上面図・側面図・斜め図での青枠のS字歪みを完全解消
    """
    thetas = data["thetas"]
    r_in_orig = np.interp(ang_grid, thetas, data["r_in_lut"])
    r_out_orig = np.interp(ang_grid, thetas, data["r_out_lut"])

    # 原画の角丸四角形TVモニター形状を82%維持しつつ、18%の楕円ブレンドで四隅のS字波打ちを抑える
    rx_out = float(np.interp(0.0, thetas, data["r_out_lut"]))
    rz_out = 0.5 * (float(np.interp(0.5 * math.pi, thetas, data["r_out_lut"])) + float(np.interp(1.5 * math.pi, thetas, data["r_out_lut"])))
    r_ell = 1.0 / np.sqrt((np.cos(ang_grid) / rx_out) ** 2 + (np.sin(ang_grid) / rz_out) ** 2)
    r_out_smooth = 0.82 * r_out_orig + 0.18 * r_ell

    frame_scale = 0.835
    thickness_slim = 0.56
    r_out = r_out_smooth * frame_scale
    w_frame = (r_out_orig - r_in_orig) * frame_scale * thickness_slim
    r_in = r_out - w_frame
    zc = data["face_center_Z"] + 0.022
    return r_in, r_out, zc


def create_face_screen_mesh(surf_model, data, n_ang=160, n_rad=28, flat_mode=False):
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


def create_face_frame_mesh(surf_model, data, n_ang=180, n_prof=28, flat_mode=False):
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

        if flat_mode:
            # 非立体フラット青枠版: ボディ前面曲面とピタッと同一面(h_off=+0.0007m)のフラッシュ曲面
            h_off = 0.0007
        else:
            # 立体青枠版: TVモニターベゼルとして立体的に盛り上げる
            arch = math.sin(math.pi * s) ** 0.44
            h_off = -0.005 + 0.043 * arch

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


def create_eye_mesh(surf_model, name, cx_eye, cz_eye=1.265, radius=0.073):
    """
    Rev.10: 顔全体を段差・出っ張り・落ち影のない完全フラット(コンフォーマル曲面シェル h_off=+0.0014m)として生成
    """
    n_ang = 56
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
        r = radius * frac
        xs = cx_eye + r * np.cos(ang_grid)
        zs = cz_eye + r * np.sin(ang_grid)
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
    Rev.10最終調整: 口も両端の丸みを維持したまま、立体的な出っ張り・落ち影のない完全フラット(h_off=+0.0014m)仕様で生成
    """
    z_arc_center = 1.325
    r_arc = 0.355
    r_tube = 0.027
    max_ang = math.radians(37.5)

    n_spine = 64
    n_cap = 24
    n_prof = 24

    spine_pts_x, spine_pts_z, spine_tx, spine_tz, spine_r_scale = [], [], [], [], []

    for ic in range(n_cap):
        u = ic / n_cap
        alpha = 0.5 * math.pi * u
        th = -max_ang
        tx, tz = math.cos(th), math.sin(th)
        ext = math.cos(alpha) * (r_tube * 1.15)
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
        ext = math.cos(alpha) * (r_tube * 1.15)
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


def create_arm_meshes(data, surf_model):
    """
    正面図(05_front.png)のぷっくり丸いハの字パドルシルエットと
    側面図(03_side.png)のティアドロップ輪郭(Z=0.28..0.76, 幅0.362m)を100%同時に満たす3Dラバーアームを生成
    Rev.8: スリム化したボディ曲面(surf_model)の横幅に合わせてアーム位置と張り出し量を完全同期
    """
    arm_z_lut = data["arm_z_lut"]
    arm_half_d_lut = data["arm_half_d"]
    arm_mid_y_lut = data["arm_mid_y"]

    # スリム化したボディ側面表面 X_body(Y=0, Z) の厳密な逆引きテーブルを構築
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
        x_body_surf = np.interp(Z, zs_test, xs_test)
        x_body_rim = x_body_surf - 0.010 * (half_y / 0.181) ** 2

        # ① 正面図(05_front.png)の下端パドル丸み & ② 側面図の上半部(Z=0.55..0.76)の張り出しを同時に満たす凸曲線 x_outer(Z)
        x_tip_top = float(np.interp(z_max, zs_test, xs_test)) + 0.003
        x_tip_bot = x_tip_top - 0.005
        x_peak = x_tip_top + 0.072
        t_bot = np.clip((Z - z_min) / (0.368 - z_min), 0.0, 1.0)
        u_up = np.clip((Z - 0.368) / (z_max - 0.368), 0.0, 1.0)
        x_outer = np.where(
            Z <= 0.368,
            x_tip_bot + (x_peak - x_tip_bot) * np.sqrt(t_bot * (2.0 - t_bot)),
            x_tip_top + (x_peak - x_tip_top) * (1.0 - (u_up ** 1.32)) ** 1.82,
        )

        # 内側輪郭 x_inner(Z): 下端(Z=0.280)の x_tip_bot から脇下(Z=0.352)を通って胴体内部へぷっくり丸く収束
        s_in = np.clip((Z - z_min) / (0.355 - z_min), 0.0, 1.0)
        x_inner_paddle = x_tip_bot - 0.200 * (s_in ** 0.68)
        u_top_in = np.clip((Z - 0.680) / (z_max - 0.680), 0.0, 1.0)
        env_top_in = np.sqrt(np.maximum(1.0 - u_top_in * u_top_in, 0.0))
        x_inner_body = x_tip_top * (1.0 - env_top_in) + (x_body_surf - 0.060) * env_top_in
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

        # アーム下端極付近(Z < 0.308)の法線特異点を滑らかに緩和
        for _ in range(3):
            tip_updates = {}
            for v in verts:
                if v.co.z < 0.308:
                    nb = [e.other_vert(v) for e in v.link_edges]
                    if nb:
                        tip_updates[v] = 0.55 * v.co + 0.45 * (sum((n.co for n in nb), Vector((0.0, 0.0, 0.0))) / len(nb))
            for v, co in tip_updates.items():
                v.co = co

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

    globe_y = 1.190
    globe_z = 2.3725
    globe_radius = 0.180

    # 1) 根元: お尻内部(Y=0.35m, Z=0.49m)からお尻表面を貫通する密な制御点
    root_z = np.linspace(0.490, float(raw_z[0]) - 0.008, 22)
    root_y = np.linspace(0.350, float(raw_y[0]) - 0.015, 22)

    # 2) 下部膨らみ: お尻表面から背中下部の最大後方突出点 (Z=1.060m, Y=1.101m, dY/dZ=0) まで
    low_mask = raw_z <= 1.060
    low_z = raw_z[low_mask]
    low_y = raw_y[low_mask]
    z_peak = float(low_z[-1])
    y_peak = float(low_y[-1])

    # 3) 中間インフレクション: 最大突出点(Z=1.06m, dY/dZ=0) ➔ 背中上部の谷部(Z=1.64m, Y=0.975m, dY/dZ=0) へ滑らかな余弦補間
    z_valley = 1.640
    y_valley = 0.975
    u_mid = np.linspace(0.02, 1.0, 40)
    mid_z = z_peak + (z_valley - z_peak) * u_mid
    mid_y = y_peak - (y_peak - y_valley) * 0.5 * (1.0 - np.cos(math.pi * u_mid))

    # 4) 上部カーブ: 谷部(Z=1.64m, dY/dZ=0) ➔ 地球儀真下の直前(Z=2.155m, Y=globe_y, dY/dZ=0) へ滑らかな余弦補間
    u_arc = np.linspace(0.02, 1.0, 42)
    arc_z = z_valley + (2.155 - z_valley) * u_arc
    arc_y = y_valley + (globe_y - y_valley) * 0.5 * (1.0 - np.cos(math.pi * u_arc))

    # 5) 地球儀の真下(南極 Z=2.1925m)へ下から垂直(+Z方向)に刺さる直線部
    vert_z = np.linspace(2.160, 2.255, 16)
    vert_y = np.full_like(vert_z, globe_y)

    ctrl_z = np.concatenate([root_z, low_z, mid_z, arc_z, vert_z])
    ctrl_y = np.concatenate([root_y, low_y, mid_y, arc_y, vert_y])

    n_pts = 160
    t_raw = np.linspace(0.0, 1.0, len(ctrl_z))
    t_fine = np.linspace(0.0, 1.0, n_pts)
    z_fine = np.interp(t_fine, t_raw, ctrl_z)
    y_fine = np.interp(t_fine, t_raw, ctrl_y)

    k_sm = np.exp(-0.5 * (np.arange(-8, 9) / 3.5) ** 2)
    k_sm /= k_sm.sum()
    z_fine = np.convolve(np.pad(z_fine, 8, mode='edge'), k_sm, mode='valid')
    y_fine = np.convolve(np.pad(y_fine, 8, mode='edge'), k_sm, mode='valid')
    z_fine[0], y_fine[0] = 0.490, 0.350
    y_fine[-6:] = globe_y
    z_fine[-6:] = np.linspace(float(z_fine[-7]), 2.255, 6)

    r_pipe = 15.5 / 400.0
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
    arm_data = bpy.data.armatures.new("IINet_Armature_Data")
    arm_obj = bpy.data.objects.new("IINet_Armature", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    eb = arm_data.edit_bones

    b_root = eb.new("Root")
    b_root.head = (0.0, 0.0, -0.105)
    b_root.tail = (0.0, 0.0, 0.18)

    b_body = eb.new("Body")
    b_body.head = (0.0, 0.0, 0.18)
    b_body.tail = (0.0, 0.0, 1.90)
    b_body.parent = b_root

    b_leg_l = eb.new("Leg.L")
    b_leg_l.head = (0.245, 0.0, 0.18)
    b_leg_l.tail = (0.230, 0.0, -0.105)
    b_leg_l.parent = b_body

    b_leg_r = eb.new("Leg.R")
    b_leg_r.head = (-0.245, 0.0, 0.18)
    b_leg_r.tail = (-0.230, 0.0, -0.105)
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
                if z < 0.20:
                    w_leg = float(np.clip((0.20 - z) / 0.16, 0.0, 1.0))
                    if x >= 0:
                        vg_leg_l.add([v.index], w_leg, 'REPLACE')
                    else:
                        vg_leg_r.add([v.index], w_leg, 'REPLACE')
                    vg_body.add([v.index], 1.0 - w_leg, 'REPLACE')
                else:
                    vg_body.add([v.index], 1.0, 'REPLACE')
        elif name in ("Face_Screen", "Face_Frame", "Eye.L", "Eye.R", "Mouth", "Logo_LILI_net"):
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
                elif z < 1.65:
                    vg2.add([v.index], 1.0, 'REPLACE')
                else:
                    vg3.add([v.index], 1.0, 'REPLACE')

    return arm_obj


# ==========================================
# 5. マテリアル設定（アニメ調廃止 ➔ 本格3Dマット質感・自然陰影）
# ==========================================
def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb255_to_linear_rgba(r, g, b, a=1.0):
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), a)


def set_bsdf_matte_params(bsdf, rgba):
    """
    Rev.3: フラットな自己発光(Emission)を完全ゼロにし、
    テカリを抑えたしっとりした3Dマット質感(Roughness=0.94, Specular=0.08)で自然な立体陰影を表現
    """
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = 0.94
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = 0.0
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.08
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.0
        bsdf.inputs["Coat Roughness"].default_value = 1.0
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.0
    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = 0.04
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = 0.0


def create_matte_material(name, rgb255, emission=0.0):
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
    scene.view_settings.exposure = 0.05

    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    bg_node = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    bg_node.inputs[0].default_value = (0.98, 0.98, 1.00, 1.0)
    bg_node.inputs[1].default_value = 0.44

    STUDIO_RIG_LIGHTS.clear()
    rig_defs = [
        ("Key_Cam", 215.0, 3.4, (1.00, 0.99, 0.98), True),
        ("Fill_Cam", 105.0, 4.4, (0.97, 0.99, 1.00), False),
        ("Rim_Cam", 95.0, 3.8, (0.98, 0.99, 1.00), False),
        ("Bounce_Cam", 70.0, 4.5, (1.00, 0.99, 1.00), False),
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
        "Key_Cam": target - 4.7 * forward - 2.6 * right + 2.5 * up,
        "Fill_Cam": target - 4.8 * forward + 3.1 * right + 0.6 * up,
        "Rim_Cam": target + 3.4 * forward + 0.8 * right + 3.6 * up,
        "Bounce_Cam": target - 3.6 * forward - 3.4 * up,
    }
    for name, lpos in placements.items():
        if name in STUDIO_RIG_LIGHTS:
            lobj = STUDIO_RIG_LIGHTS[name]
            lobj.location = lpos
            direction = (target - lpos).normalized()
            lobj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def set_camera_pose(cam_obj, pos, forward, up_hint, ortho=False, ortho_scale=3.02, lens=85.0):
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
    """Rev.3: アニメ調の黒い輪郭線(Freestyle)を完全OFFにし、純粋な3Dマット陰影で表現"""
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
        shadow_rx = w * 0.25
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


def build_and_render_variant(data, surf_model, flat_mode, blend_path, glb_path, hero_path, front_path, board_path, sheet_path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    configure_cycles_gpu(scene)

    # 2. 全3Dパーツ生成 (Rev.10最終調整: 画面枠サイズに合わせて目の間隔・サイズも原画バランスに最適化)
    body_obj = create_body_mesh(surf_model, res=136)
    logo_obj = create_logo_3d_mesh(surf_model)
    screen_obj = create_face_screen_mesh(surf_model, data, flat_mode=flat_mode)
    frame_obj = create_face_frame_mesh(surf_model, data, flat_mode=flat_mode)
    eye_l_obj = create_eye_mesh(surf_model, "Eye.L", cx_eye=+0.218, cz_eye=1.262, radius=0.072)
    eye_r_obj = create_eye_mesh(surf_model, "Eye.R", cx_eye=-0.218, cz_eye=1.262, radius=0.072)
    mouth_obj = create_mouth_mesh(surf_model)
    arm_l_obj, arm_r_obj = create_arm_meshes(data, surf_model)
    ant_obj, globe_obj = create_antenna_and_globe(data)

    all_meshes = [
        body_obj, logo_obj, screen_obj, frame_obj,
        eye_l_obj, eye_r_obj, mouth_obj,
        arm_l_obj, arm_r_obj,
        ant_obj, globe_obj,
    ]

    # 3. マテリアル作成（本格3Dマット質感・自然陰影）＆割り当て
    mat_body_pink = create_matte_material("Mat_Body_Pink", (245, 82, 164))
    mat_arm_pink = create_matte_material("Mat_Arm_Pink", (236, 66, 154))
    mat_frame_blue = create_matte_material("Mat_Frame_Blue", (58, 90, 174))
    mat_feature_blue = create_matte_material("Mat_Feature_Blue", (46, 76, 168))
    mat_stem_blue = create_matte_material("Mat_Stem_Blue", (58, 92, 172))
    mat_screen_cream = create_matte_material("Mat_Screen_Cream", (250, 228, 156))
    mat_logo_yellow = create_matte_material("Mat_Logo_Yellow", (255, 242, 15))
    mat_logo_side = create_matte_material("Mat_Logo_Side", (185, 125, 0))
    mat_globe = create_globe_material()

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

    # 4. アーマチュア構築＆スキニング
    create_armature_and_bind(all_meshes)

    # 5. ライティング・Freestyle OFF・カメラ設定
    setup_lighting_and_world()
    disable_freestyle_outline()

    cam_data = bpy.data.cameras.new("RenderCam")
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)

    hero_target = Vector((0.02, 0.12, 1.18))
    hero_pos = Vector((3.55, -6.10, 1.78))
    set_camera_pose(cam_obj, hero_pos, hero_target - hero_pos, (0, 0, 1), ortho=False, lens=72.0)
    scene.camera = cam_obj

    # 6. .blend 保存 & .glb エクスポート
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB')

    # 7. 各ビューのレンダリングと高解像度シート生成
    tmp_render = os.path.join(DRAFTS_DIR, "_tmp_render.png")

    # (A) ヒーローカット (1400 x 1680)
    hero_raw = render_view_to_array(cam_obj, 1400, 1680, tmp_render, transparent=True)
    hero_card = composite_on_card(hero_raw, has_floor_shadow=True)
    save_rgba_uint8_as_png(hero_card, hero_path)

    # (B) 5面図＋斜めビューの個別レンダリング (各 800 x 960)
    pw, ph = 800, 960
    set_camera_pose(cam_obj, (0.0, -6.0, 1.20), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), ortho=True, ortho_scale=3.02)
    img_front = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True), has_floor_shadow=True)
    save_rgba_uint8_as_png(img_front, front_path)

    set_camera_pose(cam_obj, (6.0, 0.25, 1.20), (-1.0, 0.0, 0.0), (0.0, 0.0, 1.0), ortho=True, ortho_scale=3.02)
    img_side = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True), has_floor_shadow=True)

    set_camera_pose(cam_obj, (0.0, 6.0, 1.20), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0), ortho=True, ortho_scale=3.02)
    img_back = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True), has_floor_shadow=True)

    set_camera_pose(cam_obj, (0.0, 0.25, 6.0), (0.0, 0.0, -1.0), (-1.0, 0.0, 0.0), ortho=True, ortho_scale=3.02)
    img_top = composite_on_card(render_view_to_array(cam_obj, pw, ph, tmp_render, transparent=True), has_floor_shadow=False)

    set_camera_pose(cam_obj, (0.0, 0.25, -6.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), ortho=True, ortho_scale=3.02)
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
    save_rgba_uint8_as_png(board, board_path)

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
    save_rgba_uint8_as_png(sheet, sheet_path)


def main():
    import shutil
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # 1. 参照5面図からプロファイル＆テクスチャ抽出
    data = extract_textures_and_profiles()
    surf_model = IINetSurfaceModel(data)

    # Rev.10: 顔全体（枠・画面・目・口）を完全平面（非立体フラット曲面）仕様でビルド＆レンダリング
    build_and_render_variant(
        data, surf_model,
        flat_mode=True,
        blend_path=BLEND_OUT_PATH,
        glb_path=GLB_OUT_PATH,
        hero_path=HERO_IMG_PATH,
        front_path=FRONT_IMG_PATH,
        board_path=BOARD_IMG_PATH,
        sheet_path=SHEET_IMG_PATH,
    )

    # flat_frame パスへも同一の完全平面顔モデル・レンダリング成果物を同期保存
    for src_p, dst_p in [
        (BLEND_OUT_PATH, FLAT_BLEND_OUT_PATH),
        (GLB_OUT_PATH, FLAT_GLB_OUT_PATH),
        (HERO_IMG_PATH, FLAT_HERO_IMG_PATH),
        (FRONT_IMG_PATH, FLAT_FRONT_IMG_PATH),
        (BOARD_IMG_PATH, FLAT_BOARD_IMG_PATH),
        (SHEET_IMG_PATH, FLAT_SHEET_IMG_PATH),
    ]:
        shutil.copy2(src_p, dst_p)

    print("ALL RENDERS AND EXPORTS (FLAT FACE & SMALLER FRAME REV.10) COMPLETED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
