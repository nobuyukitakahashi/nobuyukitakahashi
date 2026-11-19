# -*- coding: utf-8 -*-
"""
CVN公式マスコットキャラクター「いい-ch（LILI-ch）＆ いい-NETくん（LILI-net）」
2体ペア3Dアニメーション動画（15.0秒 / 450フレーム @ 30fps / Full HD 1920x1080 16:9 / 48kHz ステレオ効果音SE統合）
【v10: しなやか尻尾物理エンジン（2次バネ減衰＋S字波動カンチレバー＋地球儀完全真球0.000mm追従）
  ＋ 目の瞬きを若干ゆっくり柔和に調整（v9の腕隙間ゼロ＆いい-ch女の子仕様を完全継承）】

  Phase 1 (Frame 1〜160 / 0.00s〜5.33s @ 30fps):
    リファレンス（Kirby walk cycle: 1歩=10f / 1サイクル=20f @ 30fps）準拠の
    超短足「トコトコ／ポテポテ」ウォーク（Y=+4.35m ➔ 0.0m、1歩≈0.272m）。
    歩き出しは斜め前3/4カメラアングルで前後の足運び・足の心地よい弾性伸縮・短い手の逆位相スイングを
    立体的に見せ、Frame 95〜165 で完成静止画の正面カメラ（16:9 ワイド構図）へ滑らかに回り込む。
  Phase 2 (Frame 161〜210 / 5.33s〜7.00s @ 30fps):
    定位置 Y=0.0m に到着した瞬間、両足を揃えて小さく「ピョコン！」と可愛い着地ホップ（+4.6cm）➔
    「ポテッ」と自然なクッションで正面スマイル構図にピタッと静止（Frame 195 で静止画と完全一致）。
  Phase 3 (Frame 211〜300 / 7.00s〜10.00s @ 30fps):
    お腹の凹み・ロゴ歪みゼロ！ぷっくり丸いタマゴ体型のまま、短いパドル手をちょこんと後ろ外側へ添えて
    前へ約21°綺麗に「ペコリ！」とおじぎし、アンテナと地球儀も可愛く前へ揺れる。
  Phase 4 (Frame 301〜450 / 10.00s〜15.00s @ 30fps):
    腕の伸縮ゼロ・ひれゼロ・切れ目ゼロ！外側の短いパドル手をほっぺの横へグイッと持ち上げ、
    元気に「パタパタパタッ！」と振りながら、小首傾げ＆片足ちょこん浮きリズムを刻み、
    最後は正面静止構図（Frame 450）にピタッと収まる。

Usage:
  1) 視覚監査シート3枚（腕根元400%拡大シート＋歩行8コマ連続＋全フェーズ6コマ）高速監査モード:
     blender.exe --background --python build_pair_animation.py -- --check-only
  2) 全450フレーム（15.0秒 @ 30fps, 1920x1080）MP4動画＋最終成果物一括出力モード:
     blender.exe --background --python build_pair_animation.py
"""

import os
import sys
import math
import time
import wave
import subprocess
import numpy as np
import bpy
import bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import build_iich_kun as mod_iich
import build_iinet_kun as mod_iinet
import build_pair_scene as mod_pair

DEPT_DIR = os.path.dirname(SCRIPT_DIR)
FINAL_DIR = os.path.join(DEPT_DIR, "final_outputs")
os.makedirs(FINAL_DIR, exist_ok=True)

AUDIT_ARM_SEAM_CLOSEUP_PATH = os.path.join(SCRIPT_DIR, "audit_arm_seam_closeup.png")
AUDIT_EYE_EXPR_PATH = os.path.join(SCRIPT_DIR, "audit_eye_expressions.png")
AUDIT_TAIL_SUPPLE_PATH = os.path.join(SCRIPT_DIR, "audit_tail_supple_motion.png")
AUDIT_WALK_8_PATH = os.path.join(SCRIPT_DIR, "audit_walk_cycle_8frames.png")
CHECK_SHEET_DRAFT_PATH = os.path.join(SCRIPT_DIR, "anim_keyframes_check.png")
KEYFRAMES_FINAL_PATH = os.path.join(FINAL_DIR, "pair_iich_and_iinet_anim_keyframes.png")
ANIM_BLEND_PATH = os.path.join(FINAL_DIR, "cvn_iich_and_iinet_pair_anim.blend")
ANIM_MP4_PATH = os.path.join(FINAL_DIR, "pair_iich_and_iinet_run_bow_wave.mp4")
ANIM_SFX_WAV_PATH = os.path.join(FINAL_DIR, "pair_iich_and_iinet_sfx.wav")

FPS = 30
FRAME_START = 1
FRAME_END = 450

# 16:9 Full HD (1920x1080) において 4:3 (lens=70.0mm) と上下画角（頭上・足元余白）を100%一致させる焦点距離
LENS_16_9 = 52.5


# ==========================================
# 数学・平滑化ユーティリティ（C^1 / C^2 イージング ＆ ガウシアンフィルタ）
# ==========================================
def smoothstep_scalar(t):
    t = float(np.clip(t, 0.0, 1.0))
    return t * t * (3.0 - 2.0 * t)


def smootherstep_scalar(t):
    t = float(np.clip(t, 0.0, 1.0))
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def smoothstep_np(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def smootherstep_np(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def frame30_to_f24(frame_idx):
    """
    30fps のフレーム番号 (1..450, 15.0秒) を、
    24fps 基準の連続フレーム時刻 f_24 (1.0..360.2) に正確に変換する。
    これにより実時間（秒単位のテンポ・1歩=10f=1/3秒・1サイクル=20f=2/3秒）が100%維持される。
    """
    return 1.0 + (float(frame_idx) - 1.0) * (24.0 / 30.0)


def make_gaussian_kernel_1d(sigma, radius=None):
    if sigma <= 1e-5:
        return np.array([1.0], dtype=np.float64)
    if radius is None:
        radius = max(1, int(math.ceil(3.0 * sigma)))
    x = np.arange(-radius, radius + 1, dtype=np.float64)
    k = np.exp(-0.5 * (x / sigma) ** 2)
    return k / np.sum(k)


def gaussian_smooth_periodic_1d(arr, sigma, axis=-1):
    """周期境界（角度 θ 方向）に沿った1Dガウシアン平滑化"""
    if sigma <= 1e-5:
        return arr.copy()
    k = make_gaussian_kernel_1d(sigma)
    rad = (len(k) - 1) // 2
    pad_width = [(0, 0)] * arr.ndim
    pad_width[axis] = (rad, rad)
    padded = np.pad(arr, pad_width, mode='wrap')
    return np.apply_along_axis(lambda m: np.convolve(m, k, mode='valid'), axis, padded)


def gaussian_smooth_edge_1d(arr, sigma, axis=0):
    """端値保持境界（半径 u / 座標 y, z 方向）に沿った1Dガウシアン平滑化"""
    if sigma <= 1e-5:
        return arr.copy()
    k = make_gaussian_kernel_1d(sigma)
    rad = (len(k) - 1) // 2
    pad_width = [(0, 0)] * arr.ndim
    pad_width[axis] = (rad, rad)
    padded = np.pad(arr, pad_width, mode='edge')
    return np.apply_along_axis(lambda m: np.convolve(m, k, mode='valid'), axis, padded)


# ==========================================
# 1. ボディ円筒放射曲面 S_body(φ, z) 高精度ルックアップ＆スライディング吸盤フィレット構築
# ==========================================
def build_body_lateral_surface_grid(body_obj, is_iich=True):
    """
    Body メッシュの実ポリゴンと頂点法線から BVHTree を構築し、
    背骨中心軸 (x=0, y=0, z) まわりの円筒方位角 φ = atan2(y, |x|) ∈ [-0.48π, +0.48π] と
    高さ z の2Dグリッド上で、正確な円筒表面半径 R_surf(φ, z) = sqrt(X^2 + Y^2) と
    重心補間された滑らかな3D単位法線 N_surf(φ, z) を事前計算する。
    ※ 卵型胴体は中心軸に対して100%星状凸であるため、全レイが表面とほぼ直角に交差し、
       前面胸部や背面へスカートが回り込んでもグレージング段差（棚状アーティファクト）が一切発生しない。
    """
    body_obj.data.update()
    verts = [v.co.copy() for v in body_obj.data.vertices]
    vnorms = [v.normal.copy() for v in body_obj.data.vertices]
    tris = []
    for p in body_obj.data.polygons:
        vs = p.vertices[:]
        tris.append((vs[0], vs[1], vs[2]))
        if len(vs) == 4:
            tris.append((vs[0], vs[2], vs[3]))
    bvh = BVHTree.FromPolygons(verts, tris)

    nphi, nz = 180, 240
    phi_min, phi_max = -0.48 * math.pi, 0.48 * math.pi
    z_min, z_max = (0.12, 1.38) if is_iich else (0.16, 1.68)
    phis = np.linspace(phi_min, phi_max, nphi)
    zs = np.linspace(z_min, z_max, nz)

    R_grid = np.zeros((nphi, nz), dtype=np.float64)
    N_grid = np.zeros((nphi, nz, 3), dtype=np.float64)
    valid_mask = np.zeros((nphi, nz), dtype=bool)

    for iz, zv in enumerate(zs):
        for ip, phiv in enumerate(phis):
            cp, sp = math.cos(float(phiv)), math.sin(float(phiv))
            ray_orig = Vector((2.2 * cp, 2.2 * sp, float(zv)))
            ray_dir = Vector((-cp, -sp, 0.0))
            loc, norm, tidx, dist = bvh.ray_cast(ray_orig, ray_dir)
            if loc is not None and loc.x > 0.005:
                R_grid[ip, iz] = math.hypot(float(loc.x), float(loc.y))
                i0, i1, i2 = tris[tidx]
                n_interp = barycentric_transform(
                    loc, verts[i0], verts[i1], verts[i2], vnorms[i0], vnorms[i1], vnorms[i2]
                ).normalized()
                N_grid[ip, iz] = (float(n_interp.x), float(n_interp.y), float(n_interp.z))
                valid_mask[ip, iz] = True

        val_idx = np.where(valid_mask[:, iz])[0]
        if len(val_idx) > 0:
            first_i, last_i = int(val_idx[0]), int(val_idx[-1])
            if first_i > 0:
                R_grid[:first_i, iz] = R_grid[first_i, iz]
                N_grid[:first_i, iz] = N_grid[first_i, iz]
            if last_i < nphi - 1:
                R_grid[last_i + 1:, iz] = R_grid[last_i, iz]
                N_grid[last_i + 1:, iz] = N_grid[last_i, iz]

    # ポリゴン分割の微細ファセット量子化を除去する微小ガウシアンフィルタ
    R_grid = gaussian_smooth_edge_1d(gaussian_smooth_edge_1d(R_grid, 0.85, axis=0), 0.85, axis=1)
    N_grid = gaussian_smooth_edge_1d(gaussian_smooth_edge_1d(N_grid, 1.05, axis=0), 1.05, axis=1)
    n_len = np.linalg.norm(N_grid, axis=-1, keepdims=True)
    N_grid = N_grid / np.maximum(n_len, 1e-8)

    return {
        "phis": phis,
        "zs": zs,
        "phi0": phi_min,
        "z0": z_min,
        "dphi": (phi_max - phi_min) / (nphi - 1),
        "dz": (z_max - z_min) / (nz - 1),
        "nphi": nphi,
        "nz": nz,
        "R_grid": R_grid,
        "N_grid": N_grid,
        "R_ref": 0.62,
    }


def eval_body_cyl_surface(surf_grid, phi_arr, z_arr, side_sign=+1.0):
    """
    任意の円筒方位角・高さ配列 (phi_arr, z_arr) に対して Body の円筒半径 R_surf (>0) と
    3D単位法線ベクトル (side_sign * Nx, Ny, Nz) を高速双線形補間で返す。
    """
    nphi = surf_grid["nphi"]
    nz = surf_grid["nz"]
    up = np.clip((phi_arr - surf_grid["phi0"]) / surf_grid["dphi"], 0.0, nphi - 1.0001)
    uz = np.clip((z_arr - surf_grid["z0"]) / surf_grid["dz"], 0.0, nz - 1.0001)
    ip0 = up.astype(np.int32)
    iz0 = uz.astype(np.int32)
    fp = up - ip0
    fz = uz - iz0

    w00 = (1.0 - fp) * (1.0 - fz)
    w10 = fp * (1.0 - fz)
    w01 = (1.0 - fp) * fz
    w11 = fp * fz

    Rg = surf_grid["R_grid"]
    Ng = surf_grid["N_grid"]

    r_val = (
        w00 * Rg[ip0, iz0]
        + w10 * Rg[ip0 + 1, iz0]
        + w01 * Rg[ip0, iz0 + 1]
        + w11 * Rg[ip0 + 1, iz0 + 1]
    )
    n_val = (
        w00[..., None] * Ng[ip0, iz0]
        + w10[..., None] * Ng[ip0 + 1, iz0]
        + w01[..., None] * Ng[ip0, iz0 + 1]
        + w11[..., None] * Ng[ip0 + 1, iz0 + 1]
    )
    n_val = n_val.copy()
    n_val[..., 0] *= side_sign
    n_len = np.linalg.norm(n_val, axis=-1, keepdims=True)
    n_val = n_val / np.maximum(n_len, 1e-8)
    return r_val, n_val


def rotate_rigid_arm_so3(x, y, z, char_state, side_sign, flap_deg, swing_fwd_deg, sh_lift_factor=0.0):
    """
    【v8 改修】パドル手（Arm.L / Arm.R）に対する肩ボールジョイント中心の純粋剛体 SO(3) 直交回転（det(R)=1、伸縮・せん断歪み厳密ゼロ）。
      1) 腕付け根断面中心（肩ソケットボールジョイント中心 u_piv, y_piv, z_piv）を共通ピボットとすることで、
         前後スイングや上下挙上時に付け根が胴体から外へ抜け出たり（コブ化）、深くめり込んだりする現象を根絶。
      2) 手振り・挙上時に肩ソケット位置自体をタマゴ胴体側面の表面等高線 R_surf(z) に沿って正確かつ滑らかに
         上・ほっぺ横へスライド（dz_lift, du_lift）させながら純粋剛体 SO(3) 回転させる。
    """
    if abs(flap_deg) < 1e-5 and abs(swing_fwd_deg) < 1e-5 and abs(sh_lift_factor) < 1e-5:
        return x.copy(), y.copy(), z.copy()

    u_out = side_sign * x
    u_piv = char_state["u_sh"]
    y_piv = char_state["y_sh"]
    z_piv = char_state["z_sh"]

    # 肩ソケットのタマゴ表面等高線追従リフト (dz_lift, du_lift)
    u_lift = max(float(sh_lift_factor), smootherstep_scalar(max(0.0, flap_deg) / 38.0))
    dz_lift = char_state["sh_lift_z"] * u_lift
    if dz_lift > 1e-5:
        sg = char_state["surf_grid"]
        phi_sh = math.atan2(y_piv, u_piv)
        r0, _ = eval_body_cyl_surface(sg, np.array([phi_sh]), np.array([z_piv]), side_sign=1.0)
        r1, _ = eval_body_cyl_surface(sg, np.array([phi_sh]), np.array([z_piv + dz_lift]), side_sign=1.0)
        du_surf = float(r1[0] - r0[0])
        du_lift = du_surf + char_state["sh_lift_u_in"] * u_lift
    else:
        du_lift = 0.0

    # 1) 肩ボールジョイント中心 (u_piv, y_piv, z_piv) からの相対ベクトル
    du_0 = u_out - u_piv
    dy_0 = y - y_piv
    dz_0 = z - z_piv

    # 2) 前後スイング（Azimuth: 純粋剛体 SO(2) 回転）
    beta = math.radians(swing_fwd_deg)
    cb = math.cos(beta)
    sb = math.sin(beta)
    du_1 = du_0 * cb + dy_0 * sb
    dy_1 = -du_0 * sb + dy_0 * cb

    # 3) 上下パタパタ挙上（Flap: 純粋剛体 SO(2) 回転）＋ 胴体表面等高線スライド
    alpha = math.radians(flap_deg)
    ca = math.cos(alpha)
    sa = math.sin(alpha)
    du_2 = du_1 * ca - dz_0 * sa
    dz_2 = du_1 * sa + dz_0 * ca

    u_final = (u_piv + du_lift) + du_2
    y_final = y_piv + dy_1
    z_final = (z_piv + dz_lift) + dz_2

    x_out = side_sign * u_final
    return x_out, y_final, z_final


def find_first_crossing_continuous(arr_2d, thresh_1d, m_min=45, m_max=182):
    """
    外側パドル (m = m_max, 常に h > thresh) から内側 (m -> m_min) へ向かって探索し、
    外側から見て最初に h < thresh となる交差位置 m_cross[k] を連続線形補間で求める。
    これにより内側極キャップ (m < m_min) が大角度回転時に反対側へ動いても100%無視される。
    """
    n_u, n_theta = arr_2d.shape
    m_hi_lim = min(int(m_max), n_u - 1)
    m_lo_lim = max(int(m_min), 1)
    sub = arr_2d[m_lo_lim:m_hi_lim + 1, :] - thresh_1d[None, :]
    below = sub < 0.0
    rev_idx = np.argmax(below[::-1, :], axis=0)
    has_below = np.any(below, axis=0)
    idx_lo_sub = np.where(has_below, (sub.shape[0] - 1) - rev_idx, 0)
    idx_lo = np.clip(m_lo_lim + idx_lo_sub, m_lo_lim, m_hi_lim - 1)
    idx_hi = idx_lo + 1

    k_idx = np.arange(n_theta)
    v_lo = arr_2d[idx_lo, k_idx] - thresh_1d
    v_hi = arr_2d[idx_hi, k_idx] - thresh_1d
    denom = np.maximum(v_hi - v_lo, 1e-8)
    frac = np.clip(-v_lo / denom, 0.0, 1.0)
    return idx_lo.astype(np.float64) + frac


def interp_along_u_table(table_3d, m_float_2d):
    """
    table_3d[n_u, n_theta, 3] に対して、任意の連続行インデックス配列 m_float_2d[..., n_theta] で
    各列 k ごとに線形補間した 3D 座標配列 [..., n_theta, 3] を返す。
    """
    n_u, n_theta, _ = table_3d.shape
    m_clamped = np.clip(m_float_2d, 0.0, n_u - 1.0001)
    m0 = m_clamped.astype(np.int32)
    fm = (m_clamped - m0)[..., None]
    k_idx = np.arange(n_theta)
    return (1.0 - fm) * table_3d[m0, k_idx] + fm * table_3d[m0 + 1, k_idx]


def evaluate_arm_fillet_skirt_pose(skirt_meta, char_state, side_sign, flap_deg, swing_fwd_deg, sh_lift_factor=0.0):
    """
    【v8 コアアルゴリズム：dR_from_c クランプ撤廃 ＋ m_lock=0.55 先端剛体保護 ＋ 単一C^2調和フィレット曲面化】
    1) パドル曲面テーブル C_rest_uyz[n_u, n_theta, 3] を rotate_rigid_arm_so3 で純粋剛体 SO(3) 回転させる。
    2) 腕の先端側半分以上 (u = 0.55..1.0, m >= m_lock) を100%純粋剛体として保護し、パドル中間部がラプラシアンで痩せる現象を根絶。
    3) 前に振った腕や高く上げた腕の途中にひょうたん型のくびれ・潰れを作っていた dR_from_c クランプを完全撤廃し、
       リム j=0 からロック端 j=n_fillet までを自然な母線補間＋調和ラプラシアン緩和で滑らかに繋ぐ。
    """
    surf_grid = char_state["surf_grid"]
    R_ref = surf_grid["R_ref"]
    is_iich = char_state["is_iich"]
    C_rest_uyz = skirt_meta["C_rest_uyz"]
    pole_rest_uyz = skirt_meta["pole_rest_uyz"]
    thetas = skirt_meta["thetas"]
    n_u = skirt_meta["n_u"]
    n_theta = skirt_meta["n_theta"]
    n_skirt = skirt_meta["n_skirt"]
    n_collar = skirt_meta["n_collar"]
    n_tip = skirt_meta["n_tip"]
    m_lock = skirt_meta["m_lock"]
    n_fillet = n_skirt + n_collar

    # Step A: パドル曲面テーブル全体を肩ボールジョイントピボットで純粋剛体 SO(3) 回転
    X_rest = side_sign * C_rest_uyz[:, :, 0]
    Y_rest = C_rest_uyz[:, :, 1]
    Z_rest = C_rest_uyz[:, :, 2]
    X_rot, Y_rot, Z_rot = rotate_rigid_arm_so3(
        X_rest.ravel(), Y_rest.ravel(), Z_rest.ravel(),
        char_state, side_sign, flap_deg, swing_fwd_deg, sh_lift_factor=sh_lift_factor,
    )
    X_rot = X_rot.reshape(n_u, n_theta)
    Y_rot = Y_rot.reshape(n_u, n_theta)
    Z_rot = Z_rot.reshape(n_u, n_theta)
    U_rot = np.maximum(side_sign * X_rot, 1e-5)

    px_r, py_r, pz_r = rotate_rigid_arm_so3(
        np.array([side_sign * pole_rest_uyz[0]]),
        np.array([pole_rest_uyz[1]]),
        np.array([pole_rest_uyz[2]]),
        char_state, side_sign, flap_deg, swing_fwd_deg, sh_lift_factor=sh_lift_factor,
    )
    pole_rot = np.array([float(px_r[0]), float(py_r[0]), float(pz_r[0])], dtype=np.float64)

    # Step B: 円筒座標 (R_rot, Phi_rot, Z_rot) と Body 表面からの放射高さ h_rot = R_rot - R_surf
    R_rot = np.hypot(U_rot, Y_rot)
    Phi_rot = np.arctan2(Y_rot, U_rot)
    S_rot = R_ref * Phi_rot
    R_surf_rot, _ = eval_body_cyl_surface(surf_grid, Phi_rot, Z_rot, side_sign=side_sign)
    h_rot = R_rot - R_surf_rot

    # Step C: 方位角 θ に応じたコンパクトかつカメラ前面側で胴体輪郭と確実に接線接続する吸盤フィレット幅 W_k(θ)
    # θ = 0: 肩上端(+Z), θ = π/2: 背面(+Y), θ = π: 脇下(-Z), θ = 3π/2: 前面(-Y)
    w_front = (np.maximum(0.0, -np.sin(thetas))) ** 1.35
    w_back = (np.maximum(0.0, np.sin(thetas))) ** 1.5
    w_pit_raw = (np.maximum(0.0, -np.cos(thetas))) ** 2.0
    # 前面下側（脇下〜前腹境界 θ=210°〜265°）でフィレット幅が急減して胴体裏へ隠れるのを完全に防ぐ
    w_pit = w_pit_raw * (1.0 - 0.82 * w_front)

    if is_iich:
        W_top = 0.024
        W_front = 0.040
        W_back = 0.028
        W_pit = 0.016
    else:
        W_top = 0.026
        W_front = 0.050
        W_back = 0.030
        W_pit = 0.020

    W_fb_mix = (1.0 - w_front - w_back) * W_top + w_front * W_front + w_back * W_back
    W_k = (1.0 - w_pit) * W_fb_mix + w_pit * W_pit

    # Step D: 交差インデックス m_zero (h=0) の連続特定＆周期平滑化、および動的ロック端 m_lock_k の算出
    # 【v9 改修】高い手振り (f=345) 等で肩上端の m_lock が胴体内部へ潜って j=26->27 で折れ返る現象 (min_cos_bend=-0.916) を
    # 根絶するため、方位角ごとに m_lock_k >= m_zero + 18.0 を動的に保証する。
    m_zero = find_first_crossing_continuous(h_rot, np.zeros(n_theta, dtype=np.float64), m_min=18, m_max=int(n_u - 36))
    m_zero = gaussian_smooth_periodic_1d(m_zero, sigma=4.5, axis=0)
    m_zero = np.clip(m_zero, 18.0, float(n_u - 42))

    m_lock_k = np.maximum(float(m_lock), m_zero + 18.0)
    m_lock_k = gaussian_smooth_periodic_1d(m_lock_k, sigma=3.5, axis=0)
    m_lock_k = np.clip(m_lock_k, m_zero + 14.0, float(n_u - 22))

    # Step E: (h, S_phi, Z) 空間における交差ループ P_x と、交差ループ外向き単位法線 (vs, vz)
    table_hsz = np.stack([h_rot, S_rot, Z_rot], axis=-1)
    P_zero_hsz = interp_along_u_table(table_hsz, m_zero)

    S_x = gaussian_smooth_periodic_1d(P_zero_hsz[:, 1], sigma=3.5, axis=0)
    Z_x = gaussian_smooth_periodic_1d(P_zero_hsz[:, 2], sigma=3.5, axis=0)

    Sc = float(np.mean(S_x))
    Zc = float(np.mean(Z_x))
    rs = S_x - Sc
    rz = Z_x - Zc
    r_len = np.hypot(rs, rz)
    rs_u = rs / np.maximum(r_len, 1e-6)
    rz_u = rz / np.maximum(r_len, 1e-6)

    dS_dth = np.roll(S_x, -1) - np.roll(S_x, 1)
    dZ_dth = np.roll(Z_x, -1) - np.roll(Z_x, 1)
    ns_c = dZ_dth
    nz_c = -dS_dth
    dot_rc = ns_c * rs_u + nz_c * rz_u
    flip_sign = np.where(dot_rc >= 0.0, 1.0, -1.0)
    ns_c *= flip_sign
    nz_c *= flip_sign
    c_len = np.hypot(ns_c, nz_c)
    ns_u = ns_c / np.maximum(c_len, 1e-6)
    nz_u = nz_c / np.maximum(c_len, 1e-6)

    vs = gaussian_smooth_periodic_1d(0.65 * rs_u + 0.35 * ns_u, sigma=4.2, axis=0)
    vz = gaussian_smooth_periodic_1d(0.65 * rz_u + 0.35 * nz_u, sigma=4.2, axis=0)
    v_len = np.hypot(vs, vz)
    vs /= np.maximum(v_len, 1e-6)
    vz /= np.maximum(v_len, 1e-6)

    W_eff = gaussian_smooth_periodic_1d(W_k, sigma=4.0, axis=0)
    S_0 = gaussian_smooth_periodic_1d(S_x + W_eff * vs, sigma=3.5, axis=0)
    Z_0 = gaussian_smooth_periodic_1d(Z_x + W_eff * vz, sigma=3.5, axis=0)

    # Step F: リム (j=0) から動的ロック端 (j=n_fillet, m=m_lock_k) までの単一C^2母線補間
    # 【v9 改修】リム端 j=0 を胴体内部へ -0.45mm 確実に噛み込ませ（delta_rim=-0.00045）、
    # j=1 付近で法線差 0.00° のまま胴体表面を滑らかに通過させることで、いい-NETくん側の微小浮き隙間を100%ゼロ化！
    t_fillet = np.linspace(0.0, 1.0, n_fillet + 1)[:, None]
    m_fillet = m_zero[None, :] + (t_fillet ** 1.08) * (m_lock_k[None, :] - m_zero[None, :])
    P_rigid_hsz = interp_along_u_table(table_hsz, m_fillet)

    delta_rim = -0.00035
    delta_safe = 0.00018
    w_h_rigid = (t_fillet ** 2) * (3.0 - 2.0 * t_fillet)
    h_base_lift = delta_rim + (0.0040 * t_fillet * ((1.0 - t_fillet) ** 2)) + 0.0006 * smootherstep_np(t_fillet / 0.16)
    H_sc = (1.0 - w_h_rigid) * h_base_lift + w_h_rigid * np.maximum(P_rigid_hsz[:, :, 0], delta_safe + 0.0025 * t_fillet)

    w_sz_rim = (1.0 - smootherstep_np(np.clip(t_fillet / 0.78, 0.0, 1.0))) ** 1.45
    S_sc = P_rigid_hsz[:, :, 1] + w_sz_rim * (S_0[None, :] - P_rigid_hsz[0:1, :, 1])
    Z_sc = P_rigid_hsz[:, :, 2] + w_sz_rim * (Z_0[None, :] - P_rigid_hsz[0:1, :, 2])

    # Step G: (h, S_phi, Z) 空間での境界固定2D調和ラプラシアン緩和（リム j=0 と外側ロック端 j>=n_fillet-1 を完全固定）
    H_sc[0, :] = delta_rim
    S_sc[0, :] = S_0
    Z_sc[0, :] = Z_0
    for _ in range(12):
        H_avg = 0.50 * (H_sc[:-2, :] + H_sc[2:, :]) + 0.25 * (np.roll(H_sc[1:-1, :], 1, axis=1) + np.roll(H_sc[1:-1, :], -1, axis=1)) - 0.50 * H_sc[1:-1, :]
        S_avg = 0.50 * (S_sc[:-2, :] + S_sc[2:, :]) + 0.25 * (np.roll(S_sc[1:-1, :], 1, axis=1) + np.roll(S_sc[1:-1, :], -1, axis=1)) - 0.50 * S_sc[1:-1, :]
        Z_avg = 0.50 * (Z_sc[:-2, :] + Z_sc[2:, :]) + 0.25 * (np.roll(Z_sc[1:-1, :], 1, axis=1) + np.roll(Z_sc[1:-1, :], -1, axis=1)) - 0.50 * Z_sc[1:-1, :]
        H_sc[1:-1, :] = 0.45 * H_sc[1:-1, :] + 0.55 * H_avg
        S_sc[1:-1, :] = 0.45 * S_sc[1:-1, :] + 0.55 * S_avg
        Z_sc[1:-1, :] = 0.45 * Z_sc[1:-1, :] + 0.55 * Z_avg
        H_sc[0, :] = delta_rim
        S_sc[0, :] = S_0
        Z_sc[0, :] = Z_0

    Phi_sc = S_sc / R_ref
    R_surf_sc, N_body_sc = eval_body_cyl_surface(surf_grid, Phi_sc, Z_sc, side_sign=side_sign)
    R_tot_sc = R_surf_sc + H_sc
    X_sc = side_sign * R_tot_sc * np.cos(Phi_sc)
    Y_sc = R_tot_sc * np.sin(Phi_sc)
    P_sc_xyz = np.stack([X_sc, Y_sc, Z_sc], axis=-1)

    # Step H: 外側純粋剛体パドル先端 (j > n_fillet, m > m_lock_k) と結合し、フィレット接合部のみ軽く3D調和緩和
    t_tip = np.linspace(0.0, 1.0, n_tip + 1)[1:-1, None]
    m_tip = m_lock_k[None, :] + t_tip * ((n_u - 1.0) - m_lock_k[None, :])
    table_xyz = np.stack([X_rot, Y_rot, Z_rot], axis=-1)
    P_tip_xyz = interp_along_u_table(table_xyz, m_tip)

    all_rings_3d = np.vstack([P_sc_xyz, P_tip_xyz])
    n_tot_rings = all_rings_3d.shape[0]
    j_all = np.arange(n_tot_rings, dtype=np.float64)
    # j=0..1 (リム) と j >= n_fillet+4 (パドル先端半分以上) は 0.0 で100%剛体ロック
    w_3d_j = smootherstep_np((j_all - 1.0) / 3.0) * (1.0 - smootherstep_np((j_all - (n_fillet - 2.0)) / 5.0))
    w_3d_j[:2] = 0.0
    w_3d = w_3d_j[:, None, None]

    for _ in range(6):
        avg_3d = (
            0.45 * (all_rings_3d[:-2] + all_rings_3d[2:])
            + 0.30 * (np.roll(all_rings_3d[1:-1], 1, axis=1) + np.roll(all_rings_3d[1:-1], -1, axis=1))
            - 0.50 * all_rings_3d[1:-1]
        )
        all_rings_3d[1:-1] = (1.0 - 0.45 * w_3d[1:-1]) * all_rings_3d[1:-1] + (0.45 * w_3d[1:-1]) * avg_3d
        U_chk = np.maximum(side_sign * all_rings_3d[2:n_fillet + 3, :, 0], 1e-5)
        Y_chk = all_rings_3d[2:n_fillet + 3, :, 1]
        Z_chk = all_rings_3d[2:n_fillet + 3, :, 2]
        R_chk = np.hypot(U_chk, Y_chk)
        Phi_chk = np.arctan2(Y_chk, U_chk)
        Rs_chk, _ = eval_body_cyl_surface(surf_grid, Phi_chk, Z_chk, side_sign=side_sign)
        R_safe = np.maximum(R_chk, Rs_chk + delta_safe)
        all_rings_3d[2:n_fillet + 3, :, 0] = side_sign * R_safe * np.cos(Phi_chk)
        all_rings_3d[2:n_fillet + 3, :, 1] = R_safe * np.sin(Phi_chk)

    Phi_all = np.arctan2(all_rings_3d[:, :, 1], np.maximum(side_sign * all_rings_3d[:, :, 0], 1e-5))
    _, N_body_rings = eval_body_cyl_surface(surf_grid, Phi_all, all_rings_3d[:, :, 2], side_sign=side_sign)

    phi_pole = math.atan2(float(pole_rot[1]), max(float(side_sign * pole_rot[0]), 1e-5))
    _, N_body_pole = eval_body_cyl_surface(
        surf_grid, np.array([phi_pole]), np.array([pole_rot[2]]), side_sign=side_sign
    )

    all_rings_xyz = all_rings_3d.reshape(-1, 3)
    all_verts_xyz = np.vstack([all_rings_xyz, pole_rot[None, :]])

    all_rings_nbody = N_body_rings.reshape(-1, 3)
    all_verts_nbody = np.vstack([all_rings_nbody, N_body_pole.reshape(1, 3)])

    return (
        all_verts_xyz[:, 0].copy(),
        all_verts_xyz[:, 1].copy(),
        all_verts_xyz[:, 2].copy(),
        all_verts_nbody,
    )


def rebuild_arm_as_polar_skirt_mesh(arm_part_obj, char_state, side_sign=+1.0):
    """
    build_pair_scene.py が生成した滑らかなパドル腕メッシュ（ラプラシアン平滑化済み 8,216 頂点）を
    単位球面 S^2 上の BVHTree 重心補間でサンプリングし、
    ・外側パドル先端 (u >= m_lock): 100% 純粋剛体回転
    ・根元スカートリム (j = 0, s = 0): Body 表面に 0.18mm オフセット＆法線角度差 0.00° で密着する開境界ループ
    を持つ極座標構造化メッシュ（6,273 頂点）に再構築する。
    """
    surf_grid = char_state["surf_grid"]
    is_iich = char_state["is_iich"]

    # 1) 元の平滑化済み Cube-Sphere 頂点と S^2 単位球座標の対応構築
    orig_mesh = arm_part_obj.data
    p3d_verts = [Vector((side_sign * v.co.x, v.co.y, v.co.z)) for v in orig_mesh.vertices]

    bm_ref = bmesh.new()
    bmesh.ops.create_cube(bm_ref, size=2.0)
    bmesh.ops.subdivide_edges(bm_ref, edges=bm_ref.edges[:], cuts=36, use_grid_fill=True)
    bm_ref.verts.ensure_lookup_table()
    bm_ref.faces.ensure_lookup_table()
    coords_c = np.array([v.co[:] for v in bm_ref.verts], dtype=np.float64)
    tan_c = np.tan(coords_c * (math.pi / 4.0))
    unit_p = tan_c / np.linalg.norm(tan_c, axis=1, keepdims=True)

    tris_s2 = []
    for f in bm_ref.faces:
        vs = [v.index for v in f.verts]
        tris_s2.append((vs[0], vs[1], vs[2]))
        if len(vs) == 4:
            tris_s2.append((vs[0], vs[2], vs[3]))
    bm_ref.free()

    s2_verts = [Vector(u) for u in unit_p]
    bvh_s2 = BVHTree.FromPolygons(s2_verts, tris_s2)

    # 2) 内側肩根元極 p_in から外側パドル頂点 p_out へ向かう極座標グリッド (psi, theta) サンプリング
    alpha0 = 0.24
    p_in = np.array([-math.cos(alpha0), 0.0, math.sin(alpha0)], dtype=np.float64)
    e1 = np.array([math.sin(alpha0), 0.0, math.cos(alpha0)], dtype=np.float64)
    e2 = np.array([0.0, 1.0, 0.0], dtype=np.float64)

    n_u = 240
    n_theta = 112
    psis = np.linspace(0.0, math.pi, n_u)
    thetas = np.linspace(0.0, 2.0 * math.pi, n_theta, endpoint=False)

    C_raw = np.zeros((n_u, n_theta, 3), dtype=np.float64)
    for m, psi in enumerate(psis):
        cp, sp = math.cos(psi), math.sin(psi)
        # 内側極キャップ (psi < 0.24*pi) のみ Body 内部へ深く引き込み、大角度スイング時の根元抜けを完全防止
        deep_pull = 0.055 * (math.cos(0.5 * math.pi * min(psi / (0.24 * math.pi), 1.0)) ** 2)
        for k, th in enumerate(thetas):
            u_vec = cp * p_in + sp * (math.cos(th) * e1 + math.sin(th) * e2)
            loc, _, tidx, _ = bvh_s2.find_nearest(Vector(u_vec))
            i0, i1, i2 = tris_s2[tidx]
            p_int = barycentric_transform(
                loc, s2_verts[i0], s2_verts[i1], s2_verts[i2],
                p3d_verts[i0], p3d_verts[i1], p3d_verts[i2],
            )
            C_raw[m, k, 0] = float(p_int.x) - deep_pull
            C_raw[m, k, 1] = float(p_int.y)
            C_raw[m, k, 2] = float(p_int.z)

    # 微小平滑化でポリゴン補間ファセットを除去
    C_raw[:-4] = gaussian_smooth_edge_1d(C_raw[:-4], sigma=0.85, axis=0)
    C_raw[:-1] = gaussian_smooth_periodic_1d(C_raw[:-1], sigma=0.85, axis=1)
    pole_rest_uyz = np.mean(C_raw[-1, :, :], axis=0)

    # 3) 静止状態での交差位置を u=0.35, ネック位置を u=0.45 に揃える正規化ワープ
    R_raw_0 = np.hypot(np.maximum(C_raw[:, :, 0], 1e-5), C_raw[:, :, 1])
    Phi_raw_0 = np.arctan2(C_raw[:, :, 1], np.maximum(C_raw[:, :, 0], 1e-5))
    R_surf_0, _ = eval_body_cyl_surface(surf_grid, Phi_raw_0, C_raw[:, :, 2], side_sign=+1.0)
    h_0 = R_raw_0 - R_surf_0
    w_pit = (np.maximum(0.0, -np.cos(thetas))) ** 2.2
    H_rest = (1.0 - w_pit) * (0.024 if is_iich else 0.026) + w_pit * (0.0085 if is_iich else 0.0095)

    m_zero_0 = gaussian_smooth_periodic_1d(
        find_first_crossing_continuous(h_0, np.zeros(n_theta), m_min=5, m_max=210), sigma=3.0, axis=0
    )
    m_neck_0 = gaussian_smooth_periodic_1d(
        find_first_crossing_continuous(h_0, H_rest, m_min=8, m_max=215), sigma=3.0, axis=0
    )
    m_neck_0 = np.maximum(m_neck_0, m_zero_0 + 3.5)

    u_norm = np.linspace(0.0, 1.0, n_u)
    C_rest_uyz = np.zeros_like(C_raw)
    idx_src = np.arange(n_u, dtype=np.float64)
    for k in range(n_theta):
        m_warp = np.interp(
            u_norm,
            [0.0, 0.35, 0.45, 1.0],
            [0.0, float(m_zero_0[k]), float(m_neck_0[k]), float(n_u - 1)],
        )
        for c in range(3):
            C_rest_uyz[:, k, c] = np.interp(m_warp, idx_src, C_raw[:, k, c])

    # 【v8 改修】m_lock = 0.55 * (n_u - 1) に引き締め、パドル手の先端側半分以上 (u = 0.55..1.0) を
    # 100%純粋剛体回転として保護（中間部がラプラシアンで細く痩せる現象を根絶）。
    # n_skirt=14, n_collar=12, n_tip=30 -> n_rings = 15 + 12 + 29 = 56 rings + 1 pole = 6,273 verts（トポロジ100%同一）
    n_skirt = 14
    n_collar = 12
    n_tip = 30
    n_rings = (n_skirt + 1) + n_collar + (n_tip - 1)  # 56 rings + 1 pole = 6,273 verts
    m_lock = 0.55 * (n_u - 1)

    # 法線ブレンド重み w_norm_blend(j, k):
    # リム端 (j=0, s=0) では w=1.000 で Body のシェーディング法線と100.0%一致（角度差 0.00°）させ、
    # フィレット遷移帯で実幾何法線 n_geom へ広い C^2 smootherstep で滑らかに遷移させる。
    ring_s = (np.arange(n_rings, dtype=np.float64) / float(n_skirt))[:, None]
    sin2_th = (np.sin(thetas) ** 2)[None, :]
    s_max_theta = 0.88 + 0.36 * sin2_th
    w_norm_2d = 1.0 - smootherstep_np(np.maximum(ring_s - (1.0 / float(n_skirt)), 0.0) / s_max_theta)
    w_norm_2d[0, :] = 1.0
    w_norm_2d[1, :] = 1.0
    vert_w_norm = np.append(w_norm_2d.ravel(), 0.0)
    vert_ring_s = np.append(np.repeat(ring_s[:, 0], n_theta), 3.0)

    skirt_meta = {
        "C_rest_uyz": C_rest_uyz,
        "pole_rest_uyz": pole_rest_uyz,
        "thetas": thetas,
        "n_u": n_u,
        "n_theta": n_theta,
        "n_skirt": n_skirt,
        "n_collar": n_collar,
        "n_tip": n_tip,
        "n_rings": n_rings,
        "m_lock": m_lock,
        "vert_w_norm": vert_w_norm,
        "vert_ring_s": vert_ring_s,
    }

    # 4) 静止ポーズ座標を計算して BMesh トポロジを構築
    vx, vy, vz, _ = evaluate_arm_fillet_skirt_pose(
        skirt_meta, char_state, side_sign=side_sign, flap_deg=0.0, swing_fwd_deg=0.0
    )

    bm_new = bmesh.new()
    bm_verts = [bm_new.verts.new((float(vx[i]), float(vy[i]), float(vz[i]))) for i in range(len(vx))]
    bm_new.verts.ensure_lookup_table()

    for j in range(n_rings - 1):
        row0 = j * n_theta
        row1 = (j + 1) * n_theta
        for k in range(n_theta):
            k_next = (k + 1) % n_theta
            v00 = bm_verts[row0 + k]
            v01 = bm_verts[row0 + k_next]
            v11 = bm_verts[row1 + k_next]
            v10 = bm_verts[row1 + k]
            if side_sign > 0.0:
                f = bm_new.faces.new((v00, v10, v11, v01))
            else:
                f = bm_new.faces.new((v00, v01, v11, v10))
            f.smooth = True

    # 外側パドル頂点キャップ
    last_row = (n_rings - 1) * n_theta
    v_pole = bm_verts[n_rings * n_theta]
    for k in range(n_theta):
        k_next = (k + 1) % n_theta
        v0 = bm_verts[last_row + k]
        v1 = bm_verts[last_row + k_next]
        if side_sign > 0.0:
            f = bm_new.faces.new((v0, v_pole, v1))
        else:
            f = bm_new.faces.new((v0, v1, v_pole))
        f.smooth = True

    bmesh.ops.recalc_face_normals(bm_new, faces=bm_new.faces[:])
    # 外側極の法線が正しく外側 (side_sign * +X) を向いていることを保証
    if v_pole.normal.x * side_sign < 0.0:
        bmesh.ops.reverse_faces(bm_new, faces=bm_new.faces[:])
        bmesh.ops.recalc_face_normals(bm_new, faces=bm_new.faces[:])

    bm_new.to_mesh(orig_mesh)
    bm_new.free()
    for poly in orig_mesh.polygons:
        poly.use_smooth = True
    orig_mesh.update()

    # 頂点グループ再登録
    short_name = "Arm.L" if side_sign > 0.0 else "Arm.R"
    vg = arm_part_obj.vertex_groups.get(short_name)
    if vg is None:
        vg = arm_part_obj.vertex_groups.new(name=short_name)
    vg.add(list(range(len(orig_mesh.vertices))), 1.0, 'REPLACE')

    return skirt_meta


# ==========================================
# 1B. 目の表情（まばたき・おじぎ閉じ目 ︶ ︶・手振り笑顔目 ◠ ◠）コンフォーマル曲面投影＆生成（v9：案A 王道マスコット系）
# ==========================================
def build_face_screen_projector(screen_obj):
    """
    Face_Screen メッシュのポリゴンと頂点法線から BVHTree を構築し、
    任意の前面 (x, z) 配列を画面曲面へ完全密着投影 (y, nx, ny, nz) するプロジェクタを返す。
    """
    screen_obj.data.update()
    verts = [v.co.copy() for v in screen_obj.data.vertices]
    vnorms = [v.normal.copy() for v in screen_obj.data.vertices]
    tris = []
    for p in screen_obj.data.polygons:
        vs = p.vertices[:]
        tris.append((vs[0], vs[1], vs[2]))
        if len(vs) == 4:
            tris.append((vs[0], vs[2], vs[3]))
    bvh = BVHTree.FromPolygons(verts, tris)

    def project_xz(xs, zs, h_off=0.00075):
        xs_a = np.asarray(xs, dtype=np.float64)
        zs_a = np.asarray(zs, dtype=np.float64)
        out_x = np.empty_like(xs_a)
        out_y = np.empty_like(xs_a)
        out_z = np.empty_like(xs_a)
        for i in range(len(xs_a)):
            xv = float(xs_a[i])
            zv = float(zs_a[i])
            loc, norm, tidx, _ = bvh.ray_cast(Vector((xv, -2.2, zv)), Vector((0.0, 1.0, 0.0)))
            if loc is None:
                loc, norm, tidx, _ = bvh.find_nearest(Vector((xv, -0.5, zv)))
            i0, i1, i2 = tris[tidx]
            n_int = barycentric_transform(
                loc, verts[i0], verts[i1], verts[i2], vnorms[i0], vnorms[i1], vnorms[i2]
            ).normalized()
            if n_int.y > 0.0:
                n_int = -n_int
            out_x[i] = float(loc.x + h_off * n_int.x)
            out_y[i] = float(loc.y + h_off * n_int.y)
            out_z[i] = float(loc.z + h_off * n_int.z)
        return out_x, out_y, out_z

    return project_xz


def _add_conformal_ribbon_to_bmesh(bm, proj_fn, sp_x, sp_z, sp_tx, sp_tz, sp_r, r_tube, h_off=0.00090, n_prof=14):
    """スパイン列 (sp_x, sp_z, sp_tx, sp_tz, sp_r) から滑らかなコンフォーマル曲面リボンを既存 BMesh へ追加する"""
    s_vals = np.linspace(-1.0, 1.0, n_prof)
    n_rows = len(sp_x)
    all_xs = np.empty(n_rows * n_prof, dtype=np.float64)
    all_zs = np.empty(n_rows * n_prof, dtype=np.float64)
    for i in range(n_rows):
        nx_2d, nz_2d = -sp_tz[i], sp_tx[i]
        rad = r_tube * sp_r[i]
        all_xs[i * n_prof:(i + 1) * n_prof] = sp_x[i] + nx_2d * rad * s_vals
        all_zs[i * n_prof:(i + 1) * n_prof] = sp_z[i] + nz_2d * rad * s_vals

    px, py, pz = proj_fn(all_xs, all_zs, h_off=h_off)
    rings = []
    for i in range(n_rows):
        row_v = []
        base_idx = i * n_prof
        for ip in range(n_prof):
            row_v.append(bm.verts.new((float(px[base_idx + ip]), float(py[base_idx + ip]), float(pz[base_idx + ip]))))
        rings.append(row_v)

    for i in range(n_rows - 1):
        for ip in range(n_prof - 1):
            f = bm.faces.new((rings[i][ip], rings[i + 1][ip], rings[i + 1][ip + 1], rings[i][ip + 1]))
            f.smooth = True


def create_conformal_eye_arc_mesh(
    proj_fn, name, cx_eye, cz_eye, half_w, max_ang_deg, r_tube, mat, coll, arm_obj,
    curve_up=True, h_off=0.00090, lashes=None, side_x=+1.0
):
    """
    真円弧（一定曲率）＋ 一定太さ（r_tube 均一）＋ 真円半円キャップの滑らかなコンフォーマル曲面リボンとして、
    ・curve_up=False: 大きく太く可愛いおじぎ＆まばたき閉じ目「︶」
    ・curve_up=True : 大きく太く可愛い手振りにっこり笑顔目「◠」
    を生成し、必要に応じて女の子キャラ（いい-ch）用の可愛い曲線まつげ（lashes）も同一メッシュへ統合する。
    """
    n_spine = 56
    n_cap = 16
    n_prof = 16

    max_ang = math.radians(max_ang_deg)
    r_arc = half_w / max(math.sin(max_ang), 1e-4)
    sag = r_arc * (1.0 - math.cos(max_ang))
    # 弧の視覚的重心が cz_eye に自然に収まるよう円弧中心高さを調整
    if curve_up:
        # 上向きアーチ「◠」: 円中心は下側
        z_center = cz_eye + 0.55 * sag - r_arc
    else:
        # 下向きアーチ「︶」: 円中心は上側
        z_center = cz_eye - 0.55 * sag + r_arc

    def eval_arc(th):
        if curve_up:
            x_s = cx_eye + r_arc * math.sin(th)
            z_s = z_center + r_arc * math.cos(th)
            tx = math.cos(th)
            tz = -math.sin(th)
        else:
            x_s = cx_eye + r_arc * math.sin(th)
            z_s = z_center - r_arc * math.cos(th)
            tx = math.cos(th)
            tz = math.sin(th)
        return x_s, z_s, tx, tz

    sp_x, sp_z, sp_tx, sp_tz, sp_r = [], [], [], [], []
    # 左端の真円半円キャップ
    x0, z0, tx0, tz0 = eval_arc(-max_ang)
    for ic in range(n_cap):
        alpha = 0.5 * math.pi * (ic / float(n_cap))
        ext = math.cos(alpha) * r_tube
        sp_x.append(x0 - tx0 * ext)
        sp_z.append(z0 - tz0 * ext)
        sp_tx.append(tx0)
        sp_tz.append(tz0)
        sp_r.append(math.sin(max(alpha, 0.02)))
    # 中央真円弧スパイン（太さ 1.000 完全一定）
    for iseg in range(n_spine):
        th = -max_ang + 2.0 * max_ang * (iseg / float(n_spine - 1))
        xs, zs, tx, tz = eval_arc(th)
        sp_x.append(xs)
        sp_z.append(zs)
        sp_tx.append(tx)
        sp_tz.append(tz)
        sp_r.append(1.0)
    # 右端の真円半円キャップ
    x1, z1, tx1, tz1 = eval_arc(+max_ang)
    for ic in range(1, n_cap + 1):
        alpha = 0.5 * math.pi * (1.0 - ic / float(n_cap))
        ext = math.cos(alpha) * r_tube
        sp_x.append(x1 + tx1 * ext)
        sp_z.append(z1 + tz1 * ext)
        sp_tx.append(tx1)
        sp_tz.append(tz1)
        sp_r.append(math.sin(max(alpha, 0.02)))

    bm = bmesh.new()
    _add_conformal_ribbon_to_bmesh(bm, proj_fn, sp_x, sp_z, sp_tx, sp_tz, sp_r, r_tube, h_off=h_off, n_prof=n_prof)

    # 女の子キャラクター用（いい-ch）の可愛い曲線まつげを追加（目尻側から外向きへ自然にスッと伸びる2本）
    if lashes:
        for th_deg, ang_start_deg, ang_end_deg, lash_len, r_lash in lashes:
            th_rad = side_x * math.radians(th_deg)
            bx, bz, _, _ = eval_arc(th_rad)
            # 2次ベジェ的に根元角度から先端角度へ滑らかにカーブするまつげスパイン
            n_l = 18
            n_lcap = 8
            lx, lz, ltx, ltz, lr = [], [], [], [], []
            a0 = math.radians(ang_start_deg)
            a1 = math.radians(ang_end_deg)
            cx_cur, cz_cur = bx, bz
            ds = lash_len / float(n_l - 1)
            pts_l = [(cx_cur, cz_cur)]
            tangs_l = [(side_x * math.cos(a0), math.sin(a0))]
            for il in range(1, n_l):
                u = il / float(n_l - 1)
                ang_u = a0 + (a1 - a0) * u
                dx_u = side_x * math.cos(ang_u)
                dz_u = math.sin(ang_u)
                cx_cur += dx_u * ds
                cz_cur += dz_u * ds
                pts_l.append((cx_cur, cz_cur))
                tangs_l.append((dx_u, dz_u))

            for il in range(n_l):
                u = il / float(n_l - 1)
                lx.append(pts_l[il][0])
                lz.append(pts_l[il][1])
                ltx.append(tangs_l[il][0])
                ltz.append(tangs_l[il][1])
                # 根元は弧と馴染み、先端に向かってごく控えめに可愛い丸先へ
                lr.append(1.0 - 0.18 * u)
            # 先端の丸キャップ
            ex, ez = pts_l[-1]
            etx, etz = tangs_l[-1]
            r_end = 0.82
            for ic in range(1, n_lcap + 1):
                alpha = 0.5 * math.pi * (1.0 - ic / float(n_lcap))
                ext = math.cos(alpha) * (r_lash * r_end)
                lx.append(ex + etx * ext)
                lz.append(ez + etz * ext)
                ltx.append(etx)
                ltz.append(etz)
                lr.append(r_end * math.sin(max(alpha, 0.02)))

            _add_conformal_ribbon_to_bmesh(
                bm, proj_fn, lx, lz, ltx, ltz, lr, r_lash, h_off=h_off + 0.00004, n_prof=10
            )

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    obj.parent = arm_obj
    for poly in mesh.polygons:
        poly.use_smooth = True
    if hasattr(obj, "visible_shadow"):
        obj.visible_shadow = False
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def create_conformal_cheek_blush_mesh(proj_fn, name, cx_chk, cz_chk, rx_chk, rz_chk, mat, coll, arm_obj, h_off=0.00050):
    """女の子キャラクター（いい-ch）用のほんのり可愛いパステルピンクほっぺチークをコンフォーマル曲面投影で生成"""
    n_ang = 48
    n_rad = 10
    ang_grid = np.linspace(0.0, 2.0 * math.pi, n_ang, endpoint=False)
    bm = bmesh.new()

    cx0, cy0, cz0 = proj_fn(np.array([cx_chk]), np.array([cz_chk]), h_off=h_off)
    v_center = bm.verts.new((float(cx0[0]), float(cy0[0]), float(cz0[0])))

    rings = []
    for ir in range(1, n_rad + 1):
        frac = ir / float(n_rad)
        xs = cx_chk + (rx_chk * frac) * np.cos(ang_grid)
        zs = cz_chk + (rz_chk * frac) * np.sin(ang_grid)
        px, py, pz = proj_fn(xs, zs, h_off=h_off)
        rings.append([bm.verts.new((float(px[ia]), float(py[ia]), float(pz[ia]))) for ia in range(n_ang)])

    for ia in range(n_ang):
        ia_next = (ia + 1) % n_ang
        f = bm.faces.new((v_center, rings[0][ia], rings[0][ia_next]))
        f.smooth = True
    for ir in range(n_rad - 1):
        for ia in range(n_ang):
            ia_next = (ia + 1) % n_ang
            f = bm.faces.new((rings[ir][ia], rings[ir + 1][ia], rings[ir + 1][ia_next], rings[ir][ia_next]))
            f.smooth = True

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    obj.parent = arm_obj
    for poly in mesh.polygons:
        poly.use_smooth = True
    if hasattr(obj, "visible_shadow"):
        obj.visible_shadow = False
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def evaluate_eye_expression_at_frame(f_24, is_iich=True):
    """
    【v10：案A（王道マスコット系）目の表情タイムライン — 瞬きを若干ゆっくり・やわらかい動作へ最適化】
    戻り値: (mode, blink_val, happy_lift)
      - mode: "normal"（通常目＋まばたき） / "closed"（おじぎ閉じ目 ︶ ︶） / "happy"（手振り笑顔目 ◠ ◠）
      - blink_val ∈ [0.0, 1.0]: 通常目のまばたき閉じ具合
      - happy_lift: 笑顔目のごく控えめなリズムバウンス (m)
    """
    def single_blink_pulse(f_now, f_center, half_close=3.0, hold_shut=1.1, half_open=4.2):
        # 閉じる(3.0 f_24) ➔ 閉眼ホールド(1.1 f_24) ➔ やわらかく開く(4.2 f_24) ≒ 約0.35秒のゆったり可愛い瞬き
        dt = f_now - f_center
        h_h = 0.5 * hold_shut
        if dt < -(half_close + h_h) or dt > (half_open + h_h):
            return 0.0
        if abs(dt) <= h_h:
            return 1.0
        if dt < -h_h:
            return smootherstep_scalar(1.0 + (dt + h_h) / half_close)
        else:
            return 1.0 - smootherstep_scalar((dt - h_h) / half_open)

    # Phase 1: 歩いてくる（2体ずらしのゆったり自然なまばたき2回：閉眼頂点では均一太さの大弧閉じ目︶︶を使用）
    if f_24 <= 128.0:
        centers = (36.0, 96.0) if is_iich else (48.0, 108.0)
        b_val = max(single_blink_pulse(f_24, c) for c in centers)
        if b_val >= 0.68:
            return "closed", 1.0, 0.0
        return "normal", b_val, 0.0

    # Phase 2: 着地ホップ（ホップ頂点付近でやわらかく1回まばたき ➔ Frame 195 正面静止は通常目100%一致）
    if f_24 <= 168.0:
        c_hop = 136.0 if is_iich else 137.5
        b_val = single_blink_pulse(f_24, c_hop, half_close=2.6, hold_shut=1.0, half_open=3.8)
        if b_val >= 0.68:
            return "closed", 1.0, 0.0
        return "normal", b_val, 0.0

    # Phase 3: おじぎ（頭を下げる瞬間にゆったりまばたき連動で「︶ ︶」閉じ目へ切替 ➔ 起き上がりでやさしく開眼）
    if f_24 <= 240.0:
        if f_24 < 172.0:
            return "normal", 0.0, 0.0
        elif f_24 < 176.2:
            return "normal", smootherstep_scalar((f_24 - 172.0) / 4.2), 0.0
        elif f_24 <= 223.5:
            return "closed", 1.0, 0.0
        elif f_24 <= 228.9:
            return "normal", 1.0 - smootherstep_scalar((f_24 - 223.5) / 5.4), 0.0
        else:
            return "normal", 0.0, 0.0

    # Phase 4: 手を振る（ゆったりまばたき連動で「◠ ◠」にっこり笑顔目へ切替 ➔ 最後は公式の通常目に戻ってフィニッシュ）
    if f_24 < 242.8:
        return "normal", 0.0, 0.0
    elif f_24 < 247.0:
        return "normal", smootherstep_scalar((f_24 - 242.8) / 4.2), 0.0
    elif f_24 <= 336.5:
        theta_10 = 2.0 * math.pi * ((f_24 - 273.5) / 10.0)
        happy_lift = 0.0045 * max(0.0, math.sin(theta_10))
        return "happy", 0.0, happy_lift
    elif f_24 <= 341.9:
        return "normal", 1.0 - smootherstep_scalar((f_24 - 336.5) / 5.4), 0.0
    else:
        return "normal", 0.0, 0.0


# ==========================================
# 1C. しなやか尻尾物理エンジン（2次バネ減衰＋S字波動カンチレバー＋地球儀完全真球0.000mm追従：v10）
# ==========================================
def precompute_supple_tail_physics(is_iich=True):
    """
    全450フレーム（@30fps, 15.0秒）にわたるしっぽ（青いケーブル茎＋地球儀）の
    2モード弾性バネ減衰シミュレーション（1次カンチレバーたわみ q1 ＋ 2次S字波動遅れ q2）を
    サブステップ積分（300Hz, dt=1/300s）で事前計算し、フレーム毎の (q1_x, q1_y, q2_x, q2_y) テーブルを返す。
    ・根元 (s=0) は C^1 完全固定（背中からの浮き・抜けゼロ）
    ・中間 (0<s<1) は遅れ波動 q2 によりしなやかなS字カーブを描く
    ・着地ホップ後・おじぎ後・手振り中に自然な慣性オーバーシュート＆減衰余韻（ポヨン・ユラッ）を生む
    ・Frame 195 正面静止および Frame 450 終了時には正確に 0.000 へ収束する
    """
    substeps = 10
    dt = 1.0 / float(FPS * substeps)
    n_frames = FRAME_END

    # キャラ個性に応じた固有振動数＆減衰比（いい-ch: 軽快でしなやか、いい-NETくん: ゆったり優雅な弾性）
    if is_iich:
        w1, z1 = 9.6, 0.23
        w2, z2 = 17.2, 0.28
        amp_scale = 1.00
    else:
        w1, z1 = 8.2, 0.21
        w2, z2 = 14.8, 0.26
        amp_scale = 1.12

    def eval_tail_drive_at_f24(f):
        """各フェーズにおける胴体運動由来の目標たわみ・慣性駆動力 (tx, ty, s2x_bias, s2y_bias) を返す"""
        tx, ty = 0.0, 0.0
        s2x_b, s2y_b = 0.0, 0.0

        # Phase 1: トコトコ歩行（歩調に連動した軽快な8の字S字スイング）
        if f <= 128.0:
            amp_w = 1.0 if f <= 114.0 else (1.0 - smootherstep_scalar((f - 114.0) / 14.0))
            ph_off = 0.0 if is_iich else 3.0
            ph = 2.0 * math.pi * ((f - 1.0 - ph_off) / 16.0)
            # 胴体ロールと逆位相でしっぽが左右へ大きくスイング、2倍周波で前後にポヨンとしなる
            tx = -0.175 * math.sin(ph) * amp_w * amp_scale
            ty = (0.045 + 0.095 * math.sin(2.0 * ph - 0.35 * math.pi)) * amp_w * amp_scale
            # 進行遅れによるS字うねり駆動
            s2x_b = +0.055 * math.cos(ph) * amp_w * amp_scale
            s2y_b = -0.036 * math.cos(2.0 * ph - 0.35 * math.pi) * amp_w * amp_scale

        # Phase 2: 着地ホップ（飛び上がりで後ろへ引き、着地の衝撃で前へグッと沈んでポヨン・ユラッと余韻）
        elif f <= 168.0:
            f_hop = f - (0.0 if is_iich else 1.0)
            if 129.0 <= f_hop <= 143.0:
                uh = (f_hop - 129.0) / 14.0
                arc = math.sin(math.pi * uh)
                ty = +0.165 * arc * amp_scale
                tx = (-0.045 if is_iich else +0.045) * arc * amp_scale
                s2y_b = -0.055 * math.cos(math.pi * uh) * amp_scale
            elif 143.0 < f_hop <= 152.0:
                uc = (f_hop - 143.0) / 9.0
                cush = math.sin(math.pi * uc) * (1.0 - 0.35 * uc)
                ty = -0.220 * cush * amp_scale
                s2y_b = +0.068 * cush * amp_scale

        # Phase 3: 可愛いおじぎ（下げ始めで後ろへS字遅れ ➔ 最下点で前へしなやかにビヨ〜ン ➔ 起き上がりで柔らかく戻る）
        elif f <= 240.0:
            def eval_bow_u(tf):
                if tf < 176.0:
                    u_pre = smoothstep_scalar((tf - 169.0) / 7.0)
                    return -0.14 * math.sin(math.pi * u_pre)
                elif tf < 195.0:
                    return smootherstep_scalar((tf - 176.0) / 19.0)
                elif tf <= 214.0:
                    u_h = (tf - 195.0) / 19.0
                    return 1.0 + 0.02 * math.sin(math.pi * u_h)
                elif tf <= 234.0:
                    return 1.0 - smootherstep_scalar((tf - 214.0) / 20.0)
                else:
                    return 0.0

            b0 = eval_bow_u(f)
            b_prev = eval_bow_u(max(169.0, f - 1.5))
            b_vel = (b0 - b_prev) / 1.5
            # 前屈時は重力でしっぽ先端も前へしなやかに垂れ、角速度に比例した慣性遅れでS字を描く
            ty = (-0.240 * b0 + 2.85 * b_vel) * amp_scale
            tx = ((-0.045 if is_iich else +0.045) * b0) * amp_scale
            s2y_b = (-1.15 * b_vel - 0.025 * b0) * amp_scale

        # Phase 4: 元気な手振り（リズムに合わせてご機嫌に大きくしなやかな8の字S字スイング）
        else:
            env_in = smootherstep_scalar(np.clip((f - 241.0) / 14.0, 0.0, 1.0))
            env_out = 1.0 - smootherstep_scalar(np.clip((f - 332.0) / 18.0, 0.0, 1.0))
            w_w = env_in * env_out
            th10 = 2.0 * math.pi * ((f - 273.5) / 10.0)
            th_step = 2.0 * math.pi * ((f - 276.0) / 30.0) + 0.5 * math.pi
            mirror_s = -1.0 if is_iich else +1.0
            c_step = mirror_s * math.sin(th_step)
            # 大きなご機嫌左右スイング＋手振りパタパタ連動の軽快な前後リプル
            tx = (0.195 * c_step + 0.068 * mirror_s * math.sin(th10)) * w_w * amp_scale
            ty = (-0.065 * abs(math.sin(th10)) + 0.045 * math.cos(th10)) * w_w * amp_scale
            s2x_b = (-0.055 * mirror_s * math.cos(th10) - 0.032 * mirror_s * math.cos(th_step)) * w_w * amp_scale
            s2y_b = (+0.028 * math.sin(th10)) * w_w * amp_scale

        return tx, ty, s2x_b, s2y_b

    # 歩行開始時 (Frame 1) から自然にしなっているよう、事前ウォームアップを0.6秒実行
    q1x = q1y = v1x = v1y = 0.0
    q2x = q2y = v2x = v2y = 0.0
    for k in range(-int(0.6 * FPS * substeps), 0):
        f_cur = frame30_to_f24(1.0 + k / float(substeps))
        tx, ty, s2x_b, s2y_b = eval_tail_drive_at_f24(f_cur)
        a1x = (w1 * w1) * (tx - q1x) - 2.0 * z1 * w1 * v1x
        a1y = (w1 * w1) * (ty - q1y) - 2.0 * z1 * w1 * v1y
        v1x += a1x * dt
        v1y += a1y * dt
        q1x += v1x * dt
        q1y += v1y * dt
        # Mode 2 (S字しなり): Mode 1 の速度に逆らう慣性遅れ＋位相バイアスで駆動
        t2x = -0.022 * v1x + s2x_b
        t2y = -0.022 * v1y + s2y_b
        a2x = (w2 * w2) * (t2x - q2x) - 2.0 * z2 * w2 * v2x
        a2y = (w2 * w2) * (t2y - q2y) - 2.0 * z2 * w2 * v2y
        v2x += a2x * dt
        v2y += a2y * dt
        q2x += v2x * dt
        q2y += v2y * dt

    table = np.zeros((n_frames + 1, 4), dtype=np.float64)
    for frame_idx in range(1, n_frames + 1):
        for s_i in range(substeps):
            f_sub = frame30_to_f24(float(frame_idx) - 1.0 + (s_i + 1) / float(substeps))
            tx, ty, s2x_b, s2y_b = eval_tail_drive_at_f24(f_sub)
            a1x = (w1 * w1) * (tx - q1x) - 2.0 * z1 * w1 * v1x
            a1y = (w1 * w1) * (ty - q1y) - 2.0 * z1 * w1 * v1y
            v1x += a1x * dt
            v1y += a1y * dt
            q1x += v1x * dt
            q1y += v1y * dt

            t2x = -0.024 * v1x + s2x_b
            t2y = -0.024 * v1y + s2y_b
            a2x = (w2 * w2) * (t2x - q2x) - 2.0 * z2 * w2 * v2x
            a2y = (w2 * w2) * (t2y - q2y) - 2.0 * z2 * w2 * v2y
            v2x += a2x * dt
            v2y += a2y * dt
            q2x += v2x * dt
            q2y += v2y * dt

        # 公式静止ポーズ (Frame 195 前後 ＆ Frame 450 終端) に向かって滑らかに 0.000 収束させる保護マスク
        f24_now = frame30_to_f24(frame_idx)
        env_hold = 1.0
        if 152.0 <= f24_now <= 168.0:
            # Frame 190..210: ホップ余韻の後に Frame 195 でピタッと静まる
            env_hold = 1.0 - smootherstep_scalar((f24_now - 152.0) / 4.2)
        elif f24_now >= 346.0:
            env_hold = 1.0 - smootherstep_scalar((f24_now - 346.0) / 10.0)

        # 極端な振れ幅で背中ボディにめり込まない安全ソフトリミッタ
        q1x_c = float(np.clip(q1x * env_hold, -0.32, 0.32))
        q1y_c = float(np.clip(q1y * env_hold, -0.34, 0.28))
        q2x_c = float(np.clip(q2x * env_hold, -0.10, 0.10))
        q2y_c = float(np.clip(q2y * env_hold, -0.10, 0.10))
        table[frame_idx] = (q1x_c, q1y_c, q2x_c, q2y_c)

    return table


def apply_supple_tail_and_globe_deform(x, y, z, char_state, frame_idx, is_globe=False):
    """
    【v10 しなやか尻尾変形】
    1) 青いケーブル茎 (is_globe=False):
       背中根元 z <= z_root は完全固定 (C^1 連続) とし、s = clip((z - z_root)/L_z, 0, 1) に沿って
       ・1次カンチレバーたわみ φ1(s) = s^2 * (1.35 - 0.35*s)
       ・2次S字波動しなり φ2(s) = sin(π*s) * s^1.15
       ・厳密弧長保存の Z 沈み込み Δz(s) = -0.5 * ∫[(dx/dz)^2 + (dy/dz)^2] dz
       を適用して本物の弾性ケーブルのようにしなやかに曲げる。
    2) 先端の地球儀 (is_globe=True):
       球体を一切歪ませない純粋剛体 SO(3) 回転（先端接線角 θ_roll, θ_pitch）＋
       茎先端の厳密変位 (Δx_tip, Δy_tip, Δz_tip) 平行移動を適用し、
       全フレームで「完全真球」かつ「茎先端と地球儀3D球心の0.000mm完全一致」を保証する。
    """
    f_clamped = int(np.clip(frame_idx, 1, FRAME_END))
    q1x, q1y, q2x, q2y = char_state["tail_table"][f_clamped]
    if abs(q1x) < 1e-6 and abs(q1y) < 1e-6 and abs(q2x) < 1e-6 and abs(q2y) < 1e-6:
        return x, y, z

    z_root = char_state["tail_z_root"]
    gx0, gy0, gz0 = char_state["globe_center_rest"]
    L_z = max(gz0 - z_root, 0.5)

    # 101点の高精度グリッド上で弧長保存 Δz(s) を数値積分
    s_grid = np.linspace(0.0, 1.0, 101)
    ds = s_grid[1] - s_grid[0]
    dphi1 = s_grid * (2.70 - 1.05 * s_grid)
    dphi2 = math.pi * np.cos(math.pi * s_grid) * (s_grid ** 1.15) + 1.15 * np.sin(math.pi * s_grid) * np.where(s_grid > 1e-6, s_grid ** 0.15, 0.0)
    dxdz_g = (q1x * dphi1 + q2x * dphi2) / L_z
    dydz_g = (q1y * dphi1 + q2y * dphi2) / L_z
    # 弧長保存: dz_drop(s) = -0.5 * ∫_0^s (dx/dz^2 + dy/dz^2) * L_z du
    integrand = 0.5 * (dxdz_g * dxdz_g + dydz_g * dydz_g) * L_z
    dz_grid = np.zeros_like(s_grid)
    dz_grid[1:] = -np.cumsum(0.5 * (integrand[:-1] + integrand[1:]) * ds)
    dz_tip = float(dz_grid[-1])

    if not is_globe:
        s_v = np.clip((z - z_root) / L_z, 0.0, 1.0)
        phi1 = (s_v * s_v) * (1.35 - 0.35 * s_v)
        phi2 = np.sin(math.pi * s_v) * (s_v ** 1.15)
        dx = q1x * phi1 + q2x * phi2
        dy = q1y * phi1 + q2y * phi2
        dz = np.interp(s_v, s_grid, dz_grid)
        return x + dx, y + dy, z + dz
    else:
        # 先端 s=1 の厳密接線角で地球儀を純粋剛体 SO(3) 回転し、茎先端位置へ厳密平行移動
        slope_x = float(dxdz_g[-1])
        slope_y = float(dydz_g[-1])
        # +X 方向への傾き -> Y軸まわりのロール (+ang_y), +Y 方向への傾き -> X軸まわりのピッチ (-ang_x)
        ang_y = math.atan(slope_x) * 0.85
        ang_x = -math.atan(slope_y) * 0.85

        rx = x - gx0
        ry = y - gy0
        rz = z - gz0

        # X軸ピッチ回転 (Y-Z平面)
        cx, sx = math.cos(ang_x), math.sin(ang_x)
        ry1 = ry * cx - rz * sx
        rz1 = ry * sx + rz * cx
        # Y軸ロール回転 (X-Z平面)
        cy, sy = math.cos(ang_y), math.sin(ang_y)
        rx2 = rx * cy + rz1 * sy
        rz2 = -rx * sy + rz1 * cy

        return (gx0 + q1x) + rx2, (gy0 + q1y) + ry1, (gz0 + dz_tip) + rz2


# ==========================================
# 2. キャラクター初期頂点＆変形パラメータ事前計算
# ==========================================
def capture_character_rest_state(arm_obj, meshes, is_iich=True):
    """
    各キャラクターの全メッシュ初期座標（Rest Coords）と、
    ・Body 側面曲面の高精度2Dグリッド (X_surf, N_surf)
    ・パドル手（Arm.L / Arm.R）の極座標スライディング吸盤フィレットスカート構造
    ・超短足のねじれゼロ股関節振り子回転＆心地よい弾性伸縮用パラメータ
    ・目の表情メッシュ（まばたき・おじぎ閉じ目 ︶ ︶・手振り笑顔目 ◠ ◠）
    を事前計算してキャッシュする。
    """
    body_obj = next(m for m in meshes if m.name.endswith("_Body"))
    screen_obj = next(m for m in meshes if m.name.endswith("_Face_Screen"))
    n_body = len(body_obj.data.vertices)
    body_co = np.empty(n_body * 3, dtype=np.float64)
    body_obj.data.vertices.foreach_get("co", body_co)
    body_co = body_co.reshape(-1, 3)

    if is_iich:
        # 肩ソケット（腕付け根断面中心）ボールジョイントピボット ＋ 手振り時のタマゴ表面等高線追従スライド
        u_sh, y_sh, z_sh = 0.688, 0.026, 0.345
        sh_lift_z, sh_lift_u_in = 0.068, -0.006
        # 【v8 改修】足変形の上端 z_leg_top (= z_hip_piv) を実際の足突起ドーム高さに引き下げ、
        # 股間の谷より上の「1つに繋がった丸いお腹」を左右逆にねじらないようにする
        z_leg_solid = 0.022
        z_leg_top = 0.112
        z_hip_piv = 0.112
        x_foot_center = 0.255
        base_loc = Vector((-0.946, -0.025, 0.0036))
    else:
        # 【v9 改修】y_sh を 0.046 -> 0.026 へ適正化し、おじぎ・手振り時に腕の根元が胴体輪郭裏へ回り込んで
        # 黒い隙間スジを生む現象を根絶する
        u_sh, y_sh, z_sh = 0.758, 0.026, 0.475
        sh_lift_z, sh_lift_u_in = 0.084, -0.006
        z_leg_solid = 0.030
        z_leg_top = 0.175
        z_hip_piv = 0.175
        x_foot_center = 0.265
        base_loc = Vector((+0.881, +0.025, 0.0000))

    z_min_rest = float(np.min(body_co[:, 2]))
    ground_ref_z = float(base_loc.z) + z_min_rest

    surf_grid = build_body_lateral_surface_grid(body_obj, is_iich=is_iich)
    face_proj = build_face_screen_projector(screen_obj)

    # 目の表情メッシュ（おじぎ閉じ目 ︶ ︶、手振り笑顔目 ◠ ◠）＆ 女の子用（いい-ch）まつげ・チーク・笑顔口を生成
    prefix = "IICh" if is_iich else "IINet"
    coll_char = body_obj.users_collection[0] if body_obj.users_collection else bpy.context.scene.collection
    extra_eye_objs = []
    if is_iich:
        mat_eye_expr = bpy.data.materials.get("IICh_Mat_Eye_Inner_Navy") or bpy.data.materials.get("IICh_Mat_Feature_Blue")
        mat_mouth_iich = bpy.data.materials.get("IICh_Mat_Feature_Blue") or mat_eye_expr
        eye_specs = [
            ("R", -0.2750, 0.8593, 0.0850, 0.1140, -1.0),
            ("L", +0.3075, 0.8593, 0.0850, 0.1140, +1.0),
        ]
        # いい-ch（女の子設定）：いい-NETくんより繊細で細い均一ライン (0.0205m) ＋ 目尻の可愛い曲線まつげ2本
        closed_half_w, closed_ang, closed_rtube = 0.136, 52.0, 0.0205
        happy_half_w, happy_ang, happy_rtube = 0.122, 76.0, 0.0205
        cz_closed_off, cz_happy_off = -0.008, +0.044
        # まつげ定義: (th_deg, ang_start_deg, ang_end_deg, lash_len, r_lash)
        lashes_closed = [
            (46.0, -14.0, +4.0, 0.056, 0.0135),
            (28.0, -34.0, -16.0, 0.048, 0.0125),
        ]
        lashes_happy = [
            (66.0, +12.0, +28.0, 0.056, 0.0135),
            (44.0, +32.0, +48.0, 0.048, 0.0125),
        ]

        # 女の子らしいパステルピンクのほっぺチーク（おじぎ・手振り笑顔時に表示）
        mat_cheek = mod_pair.create_micro_grain_material(
            "IICh_Mat_Cheek_Pink", (255, 168, 194),
            bump_dist=0.0018, bump_strength=0.18, rough_min=0.62, rough_max=0.82,
            spec_ior=0.18, sheen_weight=0.08, coat_weight=0.0, fine_scale=85.0, mid_scale=24.0
        )
        chk_r = create_conformal_cheek_blush_mesh(
            face_proj, "IICh_Cheek.R", -0.348, 0.675, 0.092, 0.048, mat_cheek, coll_char, arm_obj, h_off=0.00055
        )
        chk_l = create_conformal_cheek_blush_mesh(
            face_proj, "IICh_Cheek.L", +0.378, 0.675, 0.092, 0.048, mat_cheek, coll_char, arm_obj, h_off=0.00055
        )
        # 手振り笑顔時用の少し広くにっこりした可愛い笑顔口 (IICh_MouthHappy)
        mouth_happy = create_conformal_eye_arc_mesh(
            face_proj, "IICh_MouthHappy",
            +0.0184, 0.562, 0.168, 34.0, 0.0235,
            mat_mouth_iich, coll_char, arm_obj, curve_up=False, h_off=0.00090,
        )
        extra_eye_objs.extend([chk_r, chk_l, mouth_happy])
    else:
        mat_eye_expr = bpy.data.materials.get("IINet_Mat_Feature_Blue")
        eye_specs = [
            ("R", -0.2677, 1.2934, 0.0742, 0.0742, -1.0),
            ("L", +0.3075, 1.2934, 0.0742, 0.0742, +1.0),
        ]
        # いい-NETくん：しっかりした均一ライン (0.0300m)、おじぎ閉じ目は緩やかでやさしい弧 (46°) へ調整
        closed_half_w, closed_ang, closed_rtube = 0.146, 46.0, 0.0300
        happy_half_w, happy_ang, happy_rtube = 0.140, 68.0, 0.0300
        cz_closed_off, cz_happy_off = -0.006, +0.022
        lashes_closed = None
        lashes_happy = None

    eye_spec_map = {}
    for side_tag, cx_e, cz_e, rx_e, rz_e, side_x in eye_specs:
        eye_spec_map[f"{prefix}_Eye.{side_tag}"] = (cx_e, cz_e, rx_e, rz_e)
        obj_closed = create_conformal_eye_arc_mesh(
            face_proj, f"{prefix}_EyeClosed.{side_tag}",
            cx_e, cz_e + cz_closed_off, closed_half_w, closed_ang, closed_rtube,
            mat_eye_expr, coll_char, arm_obj, curve_up=False, h_off=0.00090,
            lashes=lashes_closed, side_x=side_x,
        )
        obj_happy = create_conformal_eye_arc_mesh(
            face_proj, f"{prefix}_EyeHappy.{side_tag}",
            cx_e, cz_e + cz_happy_off, happy_half_w, happy_ang, happy_rtube,
            mat_eye_expr, coll_char, arm_obj, curve_up=True, h_off=0.00090,
            lashes=lashes_happy, side_x=side_x,
        )
        extra_eye_objs.extend([obj_closed, obj_happy])

    all_char_meshes = list(meshes) + extra_eye_objs

    # しっぽ物理エンジン（v10）用の事前シミュレーション＆地球儀球心・背中根元高さ取得
    globe_obj = next(m for m in meshes if m.name.endswith("_Globe"))
    g_co = np.empty(len(globe_obj.data.vertices) * 3, dtype=np.float64)
    globe_obj.data.vertices.foreach_get("co", g_co)
    g_co = g_co.reshape(-1, 3)
    globe_center_rest = (float(np.mean(g_co[:, 0])), float(np.mean(g_co[:, 1])), float(np.mean(g_co[:, 2])))
    tail_z_root = 0.438 if is_iich else 0.520
    tail_table = precompute_supple_tail_physics(is_iich=is_iich)

    char_state = {
        "arm_obj": arm_obj,
        "is_iich": is_iich,
        "base_loc": base_loc,
        "ground_ref_z": ground_ref_z,
        "surf_grid": surf_grid,
        "face_proj": face_proj,
        "tail_table": tail_table,
        "tail_z_root": tail_z_root,
        "globe_center_rest": globe_center_rest,
        "meshes": [],
        "u_sh": u_sh,
        "y_sh": y_sh,
        "z_sh": z_sh,
        "sh_lift_z": sh_lift_z,
        "sh_lift_u_in": sh_lift_u_in,
        "z_hip_piv": z_hip_piv,
        "z_leg_solid": z_leg_solid,
        "z_leg_top": z_leg_top,
        "x_foot_center": x_foot_center,
    }

    mesh_entries = []
    for obj in all_char_meshes:
        # Armature モディファイアが有効だと Cycles Depsgraph 評価時にカスタム分割法線
        # (normals_split_custom_set_from_vertices) が上書き再計算されるため、完全に除去する
        obj.modifiers.clear()
        is_body = obj.name.endswith("_Body")
        is_arm_l = obj.name.endswith("_Arm.L")
        is_arm_r = obj.name.endswith("_Arm.R")
        is_logo = "_Logo_" in obj.name
        is_antenna = obj.name.endswith("_Antenna")
        is_globe = obj.name.endswith("_Globe")
        is_ant_or_globe = is_antenna or is_globe
        is_eye_normal = obj.name in eye_spec_map
        is_eye_closed = "_EyeClosed." in obj.name
        is_eye_happy = "_EyeHappy." in obj.name
        is_cheek = "_Cheek." in obj.name
        is_mouth_normal = obj.name == "IICh_Mouth"
        is_mouth_happy = obj.name == "IICh_MouthHappy"

        skirt_meta = None
        if is_arm_l:
            skirt_meta = rebuild_arm_as_polar_skirt_mesh(obj, char_state, side_sign=+1.0)
        elif is_arm_r:
            skirt_meta = rebuild_arm_as_polar_skirt_mesh(obj, char_state, side_sign=-1.0)

        nv = len(obj.data.vertices)
        co = np.empty(nv * 3, dtype=np.float64)
        obj.data.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)

        eye_meta = None
        if is_eye_normal:
            cx_e, cz_e, rx_e, rz_e = eye_spec_map[obj.name]
            # まばたき全閉 (blink=1.0) 時のコンフォーマル投影座標も大きく太く可愛い弧に整える
            dx_n = np.clip((co[:, 0] - cx_e) / max(rx_e, 1e-4), -1.2, 1.2)
            x_scale_shut = 1.42 if is_iich else 1.54
            z_scale_shut = 0.25 if is_iich else 0.34
            x_shut = cx_e + (co[:, 0] - cx_e) * x_scale_shut
            z_shut = (cz_e - 0.012) + (co[:, 2] - cz_e) * z_scale_shut - 0.034 * (dx_n ** 2)
            # いい-ch の二重オーバル目の内側/外側オフセット差を保ったまま曲面へ投影
            h_shut = 0.00095 if is_iich else 0.00080
            bx, by, bz = face_proj(x_shut, z_shut, h_off=h_shut)
            eye_meta = {
                "cx": cx_e, "cz": cz_e,
                "shut_co": np.column_stack([bx, by, bz]),
            }

        if is_body:
            vx, vy, vz = co[:, 0], co[:, 1], co[:, 2]
            abs_x = np.abs(vx)
            # 【v8 改修】足突起ドームのみを動かし、股間アーチ中央 (|x| < 0.065m) と
            # 前面のお腹〜胸ロゴ下 (y < -0.14m, z > z_belly_guard) を保護して3/4斜めアングルでのお腹下のくびれ・段差を100%根絶
            w_z_leg = 1.0 - smootherstep_np((vz - z_leg_solid) / (z_leg_top - z_leg_solid))
            u_arch_x = smootherstep_np((abs_x - 0.028) / 0.115)
            u_arch_z = smootherstep_np((vz - (0.062 if is_iich else 0.115)) / 0.045)
            w_crotch_arch = 1.0 - 0.78 * (1.0 - u_arch_x) * u_arch_z

            z_belly_0 = 0.070 if is_iich else 0.118
            u_belly_z = smootherstep_np((vz - z_belly_0) / (z_leg_top - z_belly_0))
            u_belly_y = smootherstep_np((-vy - 0.135) / 0.110)
            w_belly_protect = 1.0 - 0.65 * u_belly_z * u_belly_y

            w_leg = w_z_leg * w_crotch_arch * w_belly_protect
            s_leg_l = 0.5 * (1.0 + np.tanh(vx / 0.105))

            # 【v7/v8 コア】変位ベクトル場 Δp = p - p_rest に対する高速ベクトル化ラプラシアン平滑化グラフの事前構築
            z_lap_max = 0.144 if is_iich else 0.255
            u_lap_bot = smootherstep_np((vz - 0.016) / 0.022)
            u_lap_top = 1.0 - smootherstep_np((vz - (z_lap_max - 0.040)) / 0.040)
            logo_guard = np.where((vy < -0.18) & (vz >= (0.142 if is_iich else 0.250)), 0.0, 1.0)
            w_lap_full = u_lap_bot * u_lap_top * logo_guard

            act_indices = np.where(w_lap_full > 1e-4)[0]
            adj_list = [[] for _ in range(nv)]
            for e in obj.data.edges:
                v0, v1 = e.vertices[0], e.vertices[1]
                adj_list[v0].append(v1)
                adj_list[v1].append(v0)
            nb_mat = np.zeros((len(act_indices), 4), dtype=np.int32)
            for ii, v_idx in enumerate(act_indices):
                nbs = adj_list[v_idx]
                if len(nbs) >= 4:
                    nb_mat[ii] = nbs[:4]
                elif len(nbs) == 3:
                    nb_mat[ii] = [nbs[0], nbs[1], nbs[2], nbs[0]]
                elif len(nbs) == 2:
                    nb_mat[ii] = [nbs[0], nbs[1], nbs[0], nbs[1]]
                else:
                    nb_mat[ii] = [v_idx, v_idx, v_idx, v_idx]

            body_lap_meta = {
                "act_indices": act_indices,
                "nb_mat": nb_mat,
                "w_act": (0.62 * w_lap_full[act_indices])[:, None],
            }
        else:
            w_leg = None
            s_leg_l = None
            body_lap_meta = None

        mesh_entries.append({
            "obj": obj,
            "rest_co": co,
            "is_body": is_body,
            "is_arm_l": is_arm_l,
            "is_arm_r": is_arm_r,
            "is_logo": is_logo,
            "is_antenna": is_antenna,
            "is_globe": is_globe,
            "is_ant_or_globe": is_ant_or_globe,
            "is_eye_normal": is_eye_normal,
            "is_eye_closed": is_eye_closed,
            "is_eye_happy": is_eye_happy,
            "is_cheek": is_cheek,
            "is_mouth_normal": is_mouth_normal,
            "is_mouth_happy": is_mouth_happy,
            "eye_meta": eye_meta,
            "w_leg": w_leg,
            "s_leg_l": s_leg_l,
            "body_lap_meta": body_lap_meta,
            "skirt_meta": skirt_meta,
        })

    char_state["meshes"] = mesh_entries
    return char_state


# ==========================================
# 3. 超短足の振り子回転＋弾性伸縮 ＆ カービィお手本準拠ウォーク関数
# ==========================================
def smooth_body_displacement_laplacian(x, y, z, rest_co, body_lap_meta, n_iters=14):
    """
    【v7 コア】頂点座標 p 自体ではなく「初期メッシュからの変位ベクトル場 Δp = p - p_rest」に対して
    Body メッシュの隣接グラフ上で境界固定ラプラシアン調和緩和を適用する。
    ・静止時 (Δp = 0) は元メッシュと 0.0000mm 完全一致し、タマゴや足の丸みが一切痩せない。
    ・足スイング時や片足リフト時、おじぎ時には、下腹部遷移帯や股間アーチの局所的なせん断・折れ・ひきつれだけが
      滑らかなポアソン調和変位場へと緩和され、しわ・たるみ・段差が100%消滅する。
    """
    if body_lap_meta is None:
        return x, y, z
    act_idx = body_lap_meta["act_indices"]
    nb_mat = body_lap_meta["nb_mat"]
    w_act = body_lap_meta["w_act"]

    disp = np.column_stack([x - rest_co[:, 0], y - rest_co[:, 1], z - rest_co[:, 2]])
    if np.max(np.abs(disp[act_idx])) < 1e-6:
        return x, y, z

    for _ in range(n_iters):
        avg_nb = 0.25 * (
            disp[nb_mat[:, 0]] + disp[nb_mat[:, 1]] + disp[nb_mat[:, 2]] + disp[nb_mat[:, 3]]
        )
        disp[act_idx] = (1.0 - w_act) * disp[act_idx] + w_act * avg_nb

    return (
        rest_co[:, 0] + disp[:, 0],
        rest_co[:, 1] + disp[:, 1],
        rest_co[:, 2] + disp[:, 2],
    )


def deform_stubby_legs_pendulum_stretch(
    x, y, z, w_leg, s_leg_l, char_state,
    leg_l_rx_deg, leg_r_rx_deg,
    leg_l_dy, leg_r_dy,
    leg_l_stretch, leg_r_stretch,
    leg_l_lift_z, leg_r_lift_z,
):
    """
    【v7 改修】超短足のしわ・たるみ・下腹部段差・股間ひきつれを完全ゼロにする股関節振り子回転：
      1) ピボット高さ z_hip を遷移帯上端 z_leg_top に一致させ、z < z_leg_top 全域で dz_rel = z - z_leg_top <= 0 を単調維持
         （符号逆転による胸ロゴ直下のS字波打ち・二重あご段差を根絶）。
      2) w_leg(z) が z = z_leg_top で 0 になるため、変位量 w_leg(z) * (z_leg_top - z) は値も1階・2階微係数もすべて 0（高次 C^2 連続）。
      3) タマゴ下部曲面勾配に調和した 3D 振り子回転と控えめなリフトにより、アコーディオン潰れジワを根絶。
    """
    if (
        abs(leg_l_rx_deg) < 1e-4 and abs(leg_r_rx_deg) < 1e-4
        and abs(leg_l_dy) < 1e-5 and abs(leg_r_dy) < 1e-5
        and abs(leg_l_stretch) < 1e-5 and abs(leg_r_stretch) < 1e-5
        and abs(leg_l_lift_z) < 1e-5 and abs(leg_r_lift_z) < 1e-5
    ):
        return x, y, z

    mask = w_leg > 1e-4
    if not np.any(mask):
        return x, y, z

    wm = w_leg[mask]
    sl = s_leg_l[mask]
    sr = 1.0 - sl
    xm = x[mask]
    ym = y[mask]
    zm = z[mask]

    z_hip = char_state["z_hip_piv"]

    # アコーディオン潰れしわを防ぐため、負の圧縮 stretch を抑えて自然な弾性のみを付与
    st_l = max(-0.015, leg_l_stretch)
    st_r = max(-0.015, leg_r_stretch)
    st_eff = wm * (st_l * sl + st_r * sr)
    kz_leg = 1.0 + 0.30 * st_eff

    dz_from_hip = zm - z_hip  # 常に <= 0
    zm_st = z_hip + dz_from_hip * kz_leg
    xm_st = xm
    ym_st = ym

    rx_rad = wm * (math.radians(leg_l_rx_deg) * sl + math.radians(leg_r_rx_deg) * sr)
    dy_glide = wm * (leg_l_dy * sl + leg_r_dy * sr)
    ca = np.cos(rx_rad)
    sa = np.sin(rx_rad)
    dy_rel = ym_st
    dz_rel = zm_st - z_hip  # 常に <= 0

    # タマゴ下部曲面の接線勾配に調和するソフトなZ回転成分（z_hip に向かって C^2 で減衰し、お腹下のひさし段差を防止）
    w_rot_z = (1.0 - smootherstep_np((zm - 0.010) / (z_hip - 0.010))) ** 1.4
    dy_rot_arm = np.clip(dy_rel, -0.095, 0.095) * w_rot_z

    y_rot = dy_rel + (-dz_rel * sa + dy_glide)
    z_rot = z_hip + dy_rot_arm * sa + dz_rel * ca

    # 過剰な局所Z押し潰しを防ぎ、滑らかな足持ち上げを実現
    dz_lift = 0.28 * wm * (leg_l_lift_z * sl + leg_r_lift_z * sr)
    z_final = z_rot + dz_lift

    x_out = x.copy()
    y_out = y.copy()
    z_out = z.copy()
    x_out[mask] = xm_st
    y_out[mask] = y_rot
    z_out[mask] = z_final
    return x_out, y_out, z_out


def evaluate_kirby_walk_cycle(f_24, is_iich=True):
    """
    リファレンス動画（Kirby walk cycle）準拠：
      - 30fps にて 1歩 = 10.0フレーム（1/3秒）、左右1サイクル = 20.0フレーム（2/3秒）
      - 2体は自然な位相差で仲良くトコトコ歩く
      - 股関節振り子回転＋足の心地よい弾性伸縮＋パドル手の逆位相スイング
    """
    phase_offset = 0.0 if is_iich else 3.0
    phase = 2.0 * math.pi * ((f_24 - 1.0 - phase_offset) / 16.0)

    s = math.sin(phase)

    step_bounce = math.sin(2.0 * phase - 0.35 * math.pi)
    z_air_hop = (0.042 if is_iich else 0.040) * (max(0.0, step_bounce) ** 1.35)
    squash_z = 0.015 * step_bounce

    torso_pitch_deg = 3.0 - 1.5 * max(0.0, step_bounce)
    torso_yaw_deg = 8.2 * s
    torso_roll_deg = 4.0 * s
    dx_sway = 0.025 * s

    # 【v8 改修】股間より上のお腹にくびれ・段差が一切出ないよう、足突起ドームの局所スイング角を 10.5°/11.5° に整え、
    # 胴体のヨーひねり (8.2°) とバウンスを活かして立体的にトコトコ歩く
    max_swing_deg = 10.5 if is_iich else 11.5
    stride_glide = 0.005 if is_iich else 0.006

    def single_leg_motion(u_ph):
        su = math.sin(u_ph)
        cu = math.cos(u_ph)
        rx_deg = -max_swing_deg * su - 0.6 * cu
        dy_l = -stride_glide * su

        ext_swing = (su * su)
        kick_push = max(0.0, -su)
        stance_comp = max(0.0, -cu) * (1.0 - su * su)
        stretch = +0.038 * ext_swing + 0.010 * kick_push - 0.012 * stance_comp

        swing_lift = max(0.0, math.sin(u_ph + 0.35 * math.pi)) ** 1.6
        lift_z = (0.018 if is_iich else 0.022) * swing_lift
        return rx_deg, dy_l, stretch, lift_z

    leg_l_rx, leg_l_dy, leg_l_stretch, leg_l_lift = single_leg_motion(phase)
    leg_r_rx, leg_r_dy, leg_r_stretch, leg_r_lift = single_leg_motion(phase + math.pi)

    # 【v8/v9 改修】超短いパドル手が後ろ振り時に胴体正面輪郭の裏へ隠れて黒い隙間スジを出さないよう、
    # 自然な前後スイング幅 (21.0°/19.5°) ＋ わずかな前寄りバイアス (+2.0°) で立体的に振る
    swing_amp = 21.0 if is_iich else 19.5
    arm_r_swing = 2.0 + swing_amp * s
    arm_l_swing = 2.0 - swing_amp * s

    outer_base_flap = 10.0 if is_iich else 11.0
    inner_base_flap = 6.0 if is_iich else 7.0
    if is_iich:
        arm_r_flap = outer_base_flap + 8.5 * max(0.0, s) + 2.0 * abs(s)
        arm_l_flap = inner_base_flap + 6.5 * max(0.0, -s) + 1.5 * abs(s)
    else:
        arm_l_flap = outer_base_flap + 9.0 * max(0.0, -s) + 2.5 * abs(s)
        arm_r_flap = inner_base_flap + 7.0 * max(0.0, s) + 1.5 * abs(s)

    phase_lag = 2.0 * math.pi * ((f_24 - 4.0 - phase_offset) / 16.0)
    ant_pitch_extra = -3.5 + 7.5 * math.sin(2.0 * phase_lag - 0.35 * math.pi)
    ant_roll_extra = -6.5 * math.sin(phase_lag)

    return {
        "z_air_hop": z_air_hop,
        "dx_sway": dx_sway,
        "squash_z": squash_z,
        "torso_pitch_deg": torso_pitch_deg,
        "torso_roll_deg": torso_roll_deg,
        "torso_yaw_deg": torso_yaw_deg,
        "leg_l_rx": leg_l_rx, "leg_l_dy": leg_l_dy, "leg_l_stretch": leg_l_stretch, "leg_l_lift": leg_l_lift,
        "leg_r_rx": leg_r_rx, "leg_r_dy": leg_r_dy, "leg_r_stretch": leg_r_stretch, "leg_r_lift": leg_r_lift,
        "arm_l_flap": arm_l_flap, "arm_l_swing": arm_l_swing,
        "arm_r_flap": arm_r_flap, "arm_r_swing": arm_r_swing,
        "ant_pitch_extra": ant_pitch_extra,
        "ant_roll_extra": ant_roll_extra,
    }


# ==========================================
# 4. 全フェーズ統合（Phase 1〜4）フレーム評価＆メッシュ・法線更新
# ==========================================
def get_walk_forward_y(f_24):
    if f_24 >= 128.0:
        return 0.0
    u = np.clip((f_24 - 1.0) / 127.0, 0.0, 1.0)
    if u <= 0.86:
        prog = u / (0.86 + 0.14 * 0.5)
    else:
        ut = (u - 0.86) / 0.14
        prog = (0.86 + 0.14 * (ut - 0.5 * ut * ut)) / (0.86 + 0.14 * 0.5)
    return 4.35 * max(0.0, 1.0 - prog)


def update_camera_for_frame(cam_obj, frame_idx):
    """
    16:9 Full HD (1920x1080) にて lens = 52.5mm を使用し、
    頭上（地球儀上端）と足元の縦方向余白バランスを従来の完成構図と100%一致させつつ、
    左右に開放的な16:9スタジオ空間を広げる。
    """
    f_24 = frame30_to_f24(frame_idx)
    final_pos = Vector((0.0, -8.45, 1.22))
    final_fwd = Vector((0.0, 1.0, 0.0))

    if f_24 >= 132.0:
        mod_pair.set_pair_camera_pose(
            cam_obj,
            pos=final_pos,
            forward=final_fwd,
            up_hint=(0.0, 0.0, 1.0),
            ortho=False,
            lens=LENS_16_9,
        )
        return

    y_pair = get_walk_forward_y(f_24)
    u_walk_cam = smoothstep_scalar(min(max(f_24 - 1.0, 0.0) / 72.0, 1.0))
    if f_24 <= 72.0:
        w_to_front = 0.0
    else:
        w_to_front = smootherstep_scalar((f_24 - 72.0) / (132.0 - 72.0))

    azim_deg = (36.0 - 3.5 * u_walk_cam) * (1.0 - w_to_front)
    azim_rad = math.radians(azim_deg)
    cam_dist = (9.45 - 0.25 * u_walk_cam) * (1.0 - w_to_front) + 8.45 * w_to_front

    tgt_x = -0.05 * (1.0 - w_to_front)
    tgt_y = y_pair * (1.0 - w_to_front)
    tgt_z = 1.08 * (1.0 - w_to_front) + 1.22 * w_to_front
    cam_z = 1.36 * (1.0 - w_to_front) + 1.22 * w_to_front

    cam_pos = Vector((
        tgt_x - cam_dist * math.sin(azim_rad),
        tgt_y - cam_dist * math.cos(azim_rad),
        cam_z,
    ))
    cam_fwd = (Vector((tgt_x, tgt_y, tgt_z)) - cam_pos).normalized()

    mod_pair.set_pair_camera_pose(
        cam_obj,
        pos=cam_pos,
        forward=cam_fwd,
        up_hint=(0.0, 0.0, 1.0),
        ortho=False,
        lens=LENS_16_9,
    )
    light_y = (1.0 - w_to_front) * (y_pair * 0.75) + 0.10
    right = cam_fwd.cross(Vector((0.0, 0.0, 1.0))).normalized()
    up = right.cross(cam_fwd).normalized()
    target_l = Vector((0.0, light_y, 1.05))
    placements = {
        "Key_Cam": target_l - 4.2 * cam_fwd - 4.0 * right + 4.0 * up,
        "Fill_Cam": target_l - 4.6 * cam_fwd + 4.8 * right + 0.4 * up,
        "Rim_Cam": target_l + 4.2 * cam_fwd + 2.2 * right + 4.2 * up,
        "Bounce_Cam": target_l - 4.0 * cam_fwd - 4.4 * up,
    }
    for name, lpos in placements.items():
        if name in mod_pair.PAIR_LIGHTS:
            lobj = mod_pair.PAIR_LIGHTS[name]
            lobj.location = lpos
            lobj.rotation_euler = (target_l - lpos).normalized().to_track_quat('-Z', 'Y').to_euler()


def transform_body_normal_steps_2_to_4(n_arr, squash_z, bow_deg, torso_pitch_deg, torso_roll_deg, torso_yaw_deg):
    """
    Step 1B 時点の Body 表面法線ベクトル配列 n_arr[N, 3] に対して、
    Step 2 (squash_z)・Step 3 (bow_deg)・Step 4 (torso_pitch/roll/yaw) と
    100%同一の法線変換を適用し、最終フレーム空間での正確な Body 単位法線を返す。
    """
    nx = n_arr[:, 0].copy()
    ny = n_arr[:, 1].copy()
    nz = n_arr[:, 2].copy()

    if abs(squash_z) > 1e-5:
        kz = 1.0 + squash_z
        kxy = 1.0 / math.sqrt(max(kz, 0.85))
        nx = nx / kxy
        ny = ny / kxy
        nz = nz / kz

    if abs(bow_deg) > 1e-4:
        p_bow = math.radians(bow_deg)
        cb, sb = math.cos(p_bow), math.sin(p_bow)
        ny, nz = (ny * cb - nz * sb), (ny * sb + nz * cb)

    if (
        abs(torso_pitch_deg) > 1e-4
        or abs(torso_roll_deg) > 1e-4
        or abs(torso_yaw_deg) > 1e-4
    ):
        p_rad = math.radians(torso_pitch_deg)
        r_rad = math.radians(torso_roll_deg)
        yw_rad = math.radians(torso_yaw_deg)

        cp, sp = math.cos(p_rad), math.sin(p_rad)
        ny, nz = (ny * cp - nz * sp), (ny * sp + nz * cp)

        cr, sr = math.cos(r_rad), math.sin(r_rad)
        nx, nz = (nx * cr + nz * sr), (-nx * sr + nz * cr)

        cy, sy_r = math.cos(yw_rad), math.sin(yw_rad)
        nx, ny = (nx * cy - ny * sy_r), (nx * sy_r + ny * cy)

    out = np.column_stack([nx, ny, nz])
    n_len = np.linalg.norm(out, axis=-1, keepdims=True)
    return out / np.maximum(n_len, 1e-8)


def apply_character_kirby_motion_at_frame(char_state, frame_idx):
    """
    指定フレーム frame_idx (1..450 @ 30fps) における仕草を計算し、
    全メッシュの頂点座標更新・腕スカートの法線完全一致ブレンド・足底厳密接地ロックを適用する。
    """
    f = frame30_to_f24(frame_idx)
    is_iich = char_state["is_iich"]
    arm_obj = char_state["arm_obj"]
    base_loc = char_state["base_loc"]

    dy_walk = 0.0
    dx_lane = 0.0
    dx_sway = 0.0
    z_air_hop = 0.0

    squash_z = 0.0
    torso_pitch_deg = 0.0
    torso_roll_deg = 0.0
    torso_yaw_deg = 0.0

    leg_l_rx, leg_l_dy, leg_l_stretch, leg_l_lift = 0.0, 0.0, 0.0, 0.0
    leg_r_rx, leg_r_dy, leg_r_stretch, leg_r_lift = 0.0, 0.0, 0.0, 0.0

    arm_l_flap, arm_l_swing, arm_l_lift_fac = 0.0, 0.0, 0.0
    arm_r_flap, arm_r_swing, arm_r_lift_fac = 0.0, 0.0, 0.0

    bow_deg = 0.0
    bow_whip = 0.0

    ant_pitch_extra = 0.0
    ant_roll_extra = 0.0

    # =========================================================================
    # Phase 1 (f_24 <= 128.0 / Frame 1〜160 @ 30fps): 超短足トコトコウォーク
    # =========================================================================
    if f <= 128.0:
        w_lane = 1.0 - smootherstep_scalar(np.clip((f - 72.0) / 54.0, 0.0, 1.0))
        dx_lane = (-0.210 if is_iich else +0.210) * w_lane
        dy_stagger = (+0.360 if is_iich else -0.360) * w_lane
        dy_walk = get_walk_forward_y(f) + dy_stagger

        amp_walk = 1.0 if f <= 114.0 else (1.0 - smootherstep_scalar((f - 114.0) / 14.0))
        w = evaluate_kirby_walk_cycle(f, is_iich=is_iich)

        z_air_hop = w["z_air_hop"] * amp_walk
        dx_sway = w["dx_sway"] * amp_walk
        squash_z = w["squash_z"] * amp_walk
        torso_pitch_deg = w["torso_pitch_deg"] * amp_walk
        torso_roll_deg = w["torso_roll_deg"] * amp_walk
        torso_yaw_deg = w["torso_yaw_deg"] * amp_walk

        leg_l_rx = w["leg_l_rx"] * amp_walk
        leg_l_dy = w["leg_l_dy"] * amp_walk
        leg_l_stretch = w["leg_l_stretch"] * amp_walk
        leg_l_lift = w["leg_l_lift"] * amp_walk
        leg_r_rx = w["leg_r_rx"] * amp_walk
        leg_r_dy = w["leg_r_dy"] * amp_walk
        leg_r_stretch = w["leg_r_stretch"] * amp_walk
        leg_r_lift = w["leg_r_lift"] * amp_walk

        arm_l_flap = w["arm_l_flap"] * amp_walk
        arm_l_swing = w["arm_l_swing"] * amp_walk
        arm_r_flap = w["arm_r_flap"] * amp_walk
        arm_r_swing = w["arm_r_swing"] * amp_walk

        ant_pitch_extra = w["ant_pitch_extra"] * amp_walk
        ant_roll_extra = w["ant_roll_extra"] * amp_walk

    # =========================================================================
    # Phase 2 (128.0 < f_24 <= 168.0 / Frame 161〜210 @ 30fps): 着地ホップ＆正面静止
    # =========================================================================
    elif f <= 168.0:
        dy_walk = 0.0
        f_hop = f - (0.0 if is_iich else 1.0)
        if 129.0 <= f_hop <= 143.0:
            uh = (f_hop - 129.0) / 14.0
            hop_arc = math.sin(math.pi * uh)
            z_air_hop = 0.046 * hop_arc
            squash_z = +0.015 * hop_arc
            leg_l_rx = +6.0 * hop_arc
            leg_r_rx = +6.0 * hop_arc
            leg_l_stretch = +0.065 * hop_arc
            leg_r_stretch = +0.065 * hop_arc
            outer_flap = 13.5 * hop_arc
            inner_flap = 6.0 * hop_arc
            if is_iich:
                arm_r_flap, arm_l_flap = outer_flap, inner_flap
            else:
                arm_l_flap, arm_r_flap = outer_flap, inner_flap
            arm_l_swing = 10.0 * hop_arc
            arm_r_swing = 10.0 * hop_arc
            ant_pitch_extra = -7.0 * hop_arc
        elif 143.0 < f_hop <= 153.0:
            uc = (f_hop - 143.0) / 10.0
            cush = math.sin(math.pi * uc) * (1.0 - 0.4 * uc)
            z_air_hop = 0.0
            squash_z = -0.018 * cush
            leg_l_stretch = -0.045 * cush
            leg_r_stretch = -0.045 * cush
            outer_flap = 4.0 * cush
            if is_iich:
                arm_r_flap = outer_flap
            else:
                arm_l_flap = outer_flap
            ant_pitch_extra = 8.5 * cush
        elif 153.0 < f_hop < 156.0:
            us = (f_hop - 153.0) / 3.0
            ant_pitch_extra = -2.0 * math.sin(math.pi * us) * (1.0 - us)

    # =========================================================================
    # Phase 3 (168.0 < f_24 <= 240.0 / Frame 211〜300 @ 30fps): 可愛いおじぎ
    # =========================================================================
    elif f <= 240.0:
        dy_walk = 0.0
        max_bow = 20.5 if is_iich else 21.5

        def eval_bow_unit(t_frame):
            if t_frame < 176.0:
                u_pre = smoothstep_scalar((t_frame - 169.0) / 7.0)
                return -0.14 * math.sin(math.pi * u_pre)
            elif t_frame < 195.0:
                return smootherstep_scalar((t_frame - 176.0) / 19.0)
            elif t_frame <= 214.0:
                u_h = (t_frame - 195.0) / 19.0
                return 1.0 + 0.02 * math.sin(math.pi * u_h)
            elif t_frame <= 234.0:
                return 1.0 - smootherstep_scalar((t_frame - 214.0) / 20.0)
            else:
                return 0.0

        b_unit = eval_bow_unit(f)
        b_lag = eval_bow_unit(max(169.0, f - 3.2))
        bow_deg = max_bow * b_unit
        bow_whip = b_unit - b_lag

        if f < 176.0:
            u_pre = math.sin(math.pi * smoothstep_scalar((f - 169.0) / 7.0))
            squash_z = +0.012 * u_pre
            outer_pre = 10.0 * u_pre
            inner_pre = 5.0 * u_pre
            if is_iich:
                arm_r_flap, arm_l_flap = outer_pre, inner_pre
            else:
                arm_l_flap, arm_r_flap = outer_pre, inner_pre
            arm_l_swing = +10.0 * u_pre
            arm_r_swing = +10.0 * u_pre
        elif f > 234.0:
            u_set = (f - 234.0) / 6.0
            squash_z = +0.012 * math.sin(math.pi * u_set) * (1.0 - u_set)
            ant_pitch_extra = -4.0 * math.sin(math.pi * u_set) * (1.0 - u_set)
        else:
            b_pos = max(0.0, b_unit)
            outer_bow_flap = 16.0 * b_pos
            inner_bow_flap = 9.0 * b_pos
            if is_iich:
                arm_r_flap, arm_l_flap = outer_bow_flap, inner_bow_flap
            else:
                arm_l_flap, arm_r_flap = outer_bow_flap, inner_bow_flap
            # 【v9 改修】後ろ振り角を -22° -> -10° へ適正化し、おじぎ時に腕付け根が胴体輪郭裏へ潜って
            # 黒い隙間・切れ目スジを生む現象を完全根絶しつつ可愛いペコリ姿勢を保つ
            arm_l_swing = -10.0 * b_pos
            arm_r_swing = -10.0 * b_pos

    # =========================================================================
    # Phase 4 (f_24 > 240.0 / Frame 301〜450 @ 30fps): 元気なほっぺ横手振り
    # =========================================================================
    else:
        dy_walk = 0.0
        env_in = smootherstep_scalar(np.clip((f - 241.0) / 14.0, 0.0, 1.0))
        env_out = 1.0 - smootherstep_scalar(np.clip((f - 334.0) / 18.0, 0.0, 1.0))
        w_wave = env_in * env_out

        theta_10 = 2.0 * math.pi * ((f - 273.5) / 10.0)
        sw10 = math.sin(theta_10)
        cw10 = math.cos(theta_10)

        theta_step = 2.0 * math.pi * ((f - 276.0) / 30.0) + 0.5 * math.pi
        sw_step = math.sin(theta_step)
        mirror_sign = -1.0 if is_iich else +1.0
        char_step = mirror_sign * sw_step

        # 【v8 改修】手を振るときは肩ソケット自体をタマゴ側面の表面等高線に沿ってほっぺ横へスライド (arm_lift_fac = w_wave) させつつ、
        # パドル自体の挙上角を (25.5 + 11.5 * sw10) に抑えることで、肩上端の暗い影スジ・ひょうたんくびれを100%ゼロにする！
        if is_iich:
            outer_flap = (25.0 + 11.0 * sw10) * w_wave
            outer_swing = (8.0 + 4.5 * cw10) * w_wave
        else:
            outer_flap = (23.5 + 10.5 * sw10) * w_wave
            outer_swing = (12.0 + 4.5 * cw10) * w_wave

        inner_flap = (6.0 - 2.5 * sw10) * w_wave
        inner_swing = (14.0 - 4.0 * sw_step) * w_wave

        if is_iich:
            arm_r_flap, arm_r_swing, arm_r_lift_fac = outer_flap, outer_swing, w_wave
            arm_l_flap, arm_l_swing, arm_l_lift_fac = inner_flap, inner_swing, 0.0
        else:
            arm_l_flap, arm_l_swing, arm_l_lift_fac = outer_flap, outer_swing, w_wave
            arm_r_flap, arm_r_swing, arm_r_lift_fac = inner_flap, inner_swing, 0.0

        torso_roll_deg = (-3.8 * char_step) * w_wave
        torso_yaw_deg = (3.2 * char_step) * w_wave
        dx_sway = ((-0.026 if is_iich else +0.026) - 0.014 * char_step) * w_wave
        squash_z = 0.012 * abs(sw10) * w_wave - 0.004 * w_wave
        z_air_hop = 0.012 * max(0.0, abs(sw10) - 0.20) * w_wave

        # 【v8 改修】手振り中 (Phase 4) は左右非対称な足の局所変形をすべて 0.0 にロックし、
        # 両足とも100%綺麗な丸い対称シルエットを維持したまま、身体全体の小首傾げロール・スウェイ・リズムホップで可愛く表現！
        leg_l_rx, leg_l_dy, leg_l_stretch, leg_l_lift = 0.0, 0.0, 0.0, 0.0
        leg_r_rx, leg_r_dy, leg_r_stretch, leg_r_lift = 0.0, 0.0, 0.0, 0.0

        ant_pitch_extra = 4.8 * abs(sw10) * w_wave
        ant_roll_extra = 6.8 * char_step * w_wave

        if 351.0 < f < 358.0:
            uf = (f - 351.0) / 7.0
            squash_z += 0.010 * math.sin(math.pi * uf) * (1.0 - uf)

    # =========================================================================
    # 各メッシュへの変形適用（Body / Arm.L / Arm.R / Face / Logo / Antenna / Globe）
    # =========================================================================
    z_foot_cush = 0.140 if is_iich else 0.190
    z_bow_z0 = 0.025 if is_iich else 0.035
    span_bow = 0.115 if is_iich else 0.195
    z_bow_piv = 0.145 if is_iich else 0.215
    y_bow_piv = -0.080 if is_iich else -0.080

    z_min_body_current = None
    eye_mode, eye_blink, eye_happy_lift = evaluate_eye_expression_at_frame(f, is_iich=is_iich)

    for entry in char_state["meshes"]:
        obj = entry["obj"]
        rest_co = entry["rest_co"]
        nbody_rest = None
        is_hidden_eye = False

        # Step 1A / 1B / 1C: Body の超短足変形 / 腕の剛体回転＋吸盤フィレットスカート / 目の表情切替＆まばたき
        if entry["is_body"]:
            x = rest_co[:, 0].copy()
            y = rest_co[:, 1].copy()
            z = rest_co[:, 2].copy()
            x, y, z = deform_stubby_legs_pendulum_stretch(
                x, y, z,
                entry["w_leg"], entry["s_leg_l"], char_state,
                leg_l_rx, leg_r_rx,
                leg_l_dy, leg_r_dy,
                leg_l_stretch, leg_r_stretch,
                leg_l_lift, leg_r_lift,
            )
        elif entry["is_arm_l"]:
            x, y, z, nbody_rest = evaluate_arm_fillet_skirt_pose(
                entry["skirt_meta"], char_state,
                side_sign=+1.0, flap_deg=arm_l_flap, swing_fwd_deg=arm_l_swing, sh_lift_factor=arm_l_lift_fac,
            )
        elif entry["is_arm_r"]:
            x, y, z, nbody_rest = evaluate_arm_fillet_skirt_pose(
                entry["skirt_meta"], char_state,
                side_sign=-1.0, flap_deg=arm_r_flap, swing_fwd_deg=arm_r_swing, sh_lift_factor=arm_r_lift_fac,
            )
        elif entry["is_eye_normal"]:
            if eye_mode == "normal":
                if eye_blink > 1e-4:
                    shut_co = entry["eye_meta"]["shut_co"]
                    x = (1.0 - eye_blink) * rest_co[:, 0] + eye_blink * shut_co[:, 0]
                    y = (1.0 - eye_blink) * rest_co[:, 1] + eye_blink * shut_co[:, 1]
                    z = (1.0 - eye_blink) * rest_co[:, 2] + eye_blink * shut_co[:, 2]
                else:
                    x = rest_co[:, 0].copy()
                    y = rest_co[:, 1].copy()
                    z = rest_co[:, 2].copy()
            else:
                is_hidden_eye = True
        elif entry["is_eye_closed"]:
            if eye_mode == "closed":
                x = rest_co[:, 0].copy()
                y = rest_co[:, 1].copy()
                z = rest_co[:, 2].copy()
            else:
                is_hidden_eye = True
        elif entry["is_eye_happy"]:
            if eye_mode == "happy":
                x = rest_co[:, 0].copy()
                y = rest_co[:, 1].copy()
                z = rest_co[:, 2].copy() + eye_happy_lift
            else:
                is_hidden_eye = True
        elif entry["is_cheek"]:
            # いい-chのほっぺチークはおじぎ閉じ目・手振り笑顔時に可愛く表示（静止画・歩行時は公式そのまま）
            if eye_mode == "happy" or (eye_mode == "closed" and f > 168.0):
                x = rest_co[:, 0].copy()
                y = rest_co[:, 1].copy()
                z = rest_co[:, 2].copy() + (0.5 * eye_happy_lift if eye_mode == "happy" else 0.0)
            else:
                is_hidden_eye = True
        elif entry["is_mouth_normal"]:
            if eye_mode == "happy":
                is_hidden_eye = True
            else:
                x = rest_co[:, 0].copy()
                y = rest_co[:, 1].copy()
                z = rest_co[:, 2].copy()
        elif entry["is_mouth_happy"]:
            if eye_mode == "happy":
                x = rest_co[:, 0].copy()
                y = rest_co[:, 1].copy()
                z = rest_co[:, 2].copy()
            else:
                is_hidden_eye = True
        elif entry["is_antenna"]:
            x = rest_co[:, 0].copy()
            y = rest_co[:, 1].copy()
            z = rest_co[:, 2].copy()
            x, y, z = apply_supple_tail_and_globe_deform(x, y, z, char_state, frame_idx, is_globe=False)
        elif entry["is_globe"]:
            x = rest_co[:, 0].copy()
            y = rest_co[:, 1].copy()
            z = rest_co[:, 2].copy()
            x, y, z = apply_supple_tail_and_globe_deform(x, y, z, char_state, frame_idx, is_globe=True)
        else:
            x = rest_co[:, 0].copy()
            y = rest_co[:, 1].copy()
            z = rest_co[:, 2].copy()

        if is_hidden_eye:
            # 非表示の表情メッシュはボディ内部中心へ退避（Cycles の Depsgraph キャッシュ影響ゼロで確実に非表示）
            nv_h = len(rest_co)
            z_hide = 0.72 if is_iich else 1.05
            hide_co = np.empty((nv_h, 3), dtype=np.float32)
            hide_co[:, 0] = 0.0
            hide_co[:, 1] = 0.20
            hide_co[:, 2] = z_hide
            obj.data.vertices.foreach_set("co", hide_co.ravel())
            obj.data.update()
            continue

        # Step 2: 着地クッション等のごく控えめな体積保存バウンス（±1.5%以内）
        # Step 1B 後の z 座標を共通参照することで、スカートリム (s=0) と Body 表面の 0.000mm 一致を完全維持
        if abs(squash_z) > 1e-5:
            z_ref_sq = z if (entry["is_arm_l"] or entry["is_arm_r"] or entry["is_body"]) else rest_co[:, 2]
            u_sq = smootherstep_np((z_ref_sq - z_foot_cush) / 0.22)
            kz = 1.0 + squash_z * u_sq
            kxy = 1.0 / np.sqrt(np.maximum(kz, 0.85))
            x = x * kxy
            y = y * kxy
            z = np.where(z > z_foot_cush, z_foot_cush + (z - z_foot_cush) * kz, z)

        # Step 3: Phase 3 おじぎ（上部ボディ・胸ロゴ・両腕・しっぽは u_bow=1.0 の純粋剛体回転、y_bow_piv=-0.08m で前腹部圧縮しわ防止）
        # ※ v10 ではしっぽ＆地球儀のしなやかな追従しなり・バネ余韻は Step 1D (apply_supple_tail_and_globe_deform) で物理計算済み
        if abs(bow_deg) > 1e-4:
            if entry["is_body"]:
                u_bow = 0.15 + 0.85 * smootherstep_np((rest_co[:, 2] - z_bow_z0) / span_bow)
            else:
                u_bow = 1.0
            p_bow = math.radians(bow_deg) * u_bow
            cb, sb = np.cos(p_bow), np.sin(p_bow)
            dy_b = y - y_bow_piv
            dz_b = z - z_bow_piv
            y = y_bow_piv + dy_b * cb - dz_b * sb
            z = z_bow_piv + dy_b * sb + dz_b * cb

        # Step 3B: Body 下部遷移帯・股間アーチの変位ベクトル場 Δp ラプラシアン調和緩和（しわ・段差・ひきつれ完全ゼロ化）
        if entry["is_body"]:
            x, y, z = smooth_body_displacement_laplacian(
                x, y, z, rest_co, entry["body_lap_meta"], n_iters=18
            )

        # Step 4: 身体の可愛い最小限の傾き・ツイスト（しっぽ＆地球儀は u_orient=1.0 で胴体へ剛体追従しつつ Step 1D の弾性S字しなりを保持）
        if (
            abs(torso_pitch_deg) > 1e-4
            or abs(torso_roll_deg) > 1e-4
            or abs(torso_yaw_deg) > 1e-4
        ):
            if entry["is_arm_l"] or entry["is_arm_r"] or entry["is_ant_or_globe"]:
                u_orient = 1.0
            else:
                u_orient = 0.72 + 0.28 * smootherstep_np((rest_co[:, 2] - 0.02) / 0.16)
            p_rad = math.radians(torso_pitch_deg) * u_orient
            r_rad = math.radians(torso_roll_deg) * u_orient
            yw_rad = math.radians(torso_yaw_deg) * u_orient

            z_piv = 0.18 if is_iich else 0.24

            cp, sp = np.cos(p_rad), np.sin(p_rad)
            dz_p = z - z_piv
            y, z = (y * cp - dz_p * sp), (z_piv + y * sp + dz_p * cp)

            cr, sr = np.cos(r_rad), np.sin(r_rad)
            dz_r = z - z_piv
            x, z = (x * cr + dz_r * sr), (z_piv - x * sr + dz_r * cr)

            cy, sy_r = np.cos(yw_rad), np.sin(yw_rad)
            x, y = (x * cy - y * sy_r), (x * sy_r + y * cy)

        if entry["is_body"]:
            z_min_body_current = float(np.min(z))

        new_co = np.column_stack([x, y, z]).astype(np.float32)
        if "custom_normal" in obj.data.attributes:
            obj.data.attributes.remove(obj.data.attributes["custom_normal"])
        obj.data.vertices.foreach_set("co", new_co.ravel())
        obj.data.update()

        # Step 4B: 腕スカートのカスタム分割法線ブレンド（非微分な np.maximum を撤廃し、純粋な C^2 smootherstep 遷移へ！）
        if (entry["is_arm_l"] or entry["is_arm_r"]) and nbody_rest is not None:
            nv_arm = len(obj.data.vertices)
            n_geom = np.empty(nv_arm * 3, dtype=np.float32)
            obj.data.vertices.foreach_get("normal", n_geom)
            n_geom = n_geom.reshape(-1, 3).astype(np.float64)

            n_body_final = transform_body_normal_steps_2_to_4(
                nbody_rest, squash_z, bow_deg, torso_pitch_deg, torso_roll_deg, torso_yaw_deg
            )
            # リム端 (j=0) で n_body_final と 100.0% 一致（角度差 0.00°）、
            # そこから純粋な C^2 重み w_nb で実幾何法線 n_geom へ滑らかに遷移させる（陰影リングスジ完全消滅）
            w_nb = entry["skirt_meta"]["vert_w_norm"][:, None]
            n_blend = w_nb * n_body_final + (1.0 - w_nb) * n_geom
            n_len = np.linalg.norm(n_blend, axis=-1, keepdims=True)
            n_blend = n_blend / np.maximum(n_len, 1e-8)

            # 極座標グリッド (n_rings, n_theta) 上で法線ベクトル場を2Dガウシアン平滑化し、
            # リム端 (j=0) は Body 法線と角度差 0.00° に厳密ロックする
            n_rings_m = entry["skirt_meta"]["n_rings"]
            n_theta_m = entry["skirt_meta"]["n_theta"]
            n_grid_2d = n_blend[:-1].reshape(n_rings_m, n_theta_m, 3)
            n_body_2d = n_body_final[:-1].reshape(n_rings_m, n_theta_m, 3)
            n_grid_sm = gaussian_smooth_periodic_1d(
                gaussian_smooth_edge_1d(n_grid_2d, sigma=1.8, axis=0), sigma=1.8, axis=1
            )
            # j=0（ボディ内部噛み込み端）と j=1（表面通過直後）の両方を Body 法線に 0.00° ロック
            n_grid_sm[0] = n_body_2d[0]
            n_grid_sm[1] = n_body_2d[1]
            n_blend[:-1] = n_grid_sm.reshape(-1, 3)
            n_len2 = np.linalg.norm(n_blend, axis=-1, keepdims=True)
            n_custom = (n_blend / np.maximum(n_len2, 1e-8)).astype(np.float32)
            obj.data.normals_split_custom_set_from_vertices(n_custom)

    # Step 5: 足底最下点 min(z) の厳密接地ロック（床めり込みゼロ・浮きゼロ・静止時完全一致）
    loc_z = char_state["ground_ref_z"] - z_min_body_current + z_air_hop
    arm_obj.location = Vector((
        base_loc.x + dx_lane + dx_sway,
        base_loc.y + dy_walk,
        loc_z,
    ))


# ==========================================
# 5. スタジオ背景（16:9 ワイド＆3/4アングル対応ホリゾント）・照明・カメラ
# ==========================================
def create_studio_floor_and_backdrop():
    mesh = bpy.data.meshes.new("Studio_Cyclorama_Mesh")
    obj = bpy.data.objects.new("Studio_Cyclorama", mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    n_x = 48
    xs = np.linspace(-52.0, 52.0, n_x)

    profile_yz = []
    for y in np.linspace(-10.0, 16.5, 26):
        profile_yz.append((float(y), 0.0))
    for i in range(1, 12):
        ang = (0.5 * math.pi) * (i / 12.0)
        R_cyc = 4.0
        y_c = 16.5 + R_cyc * math.sin(ang)
        z_c = R_cyc * (1.0 - math.cos(ang))
        profile_yz.append((float(y_c), float(z_c)))
    for z in np.linspace(4.0, 16.0, 10)[1:]:
        profile_yz.append((20.5, float(z)))

    grid_verts = []
    for y_val, z_val in profile_yz:
        row_v = [bm.verts.new((float(x_val), y_val, z_val)) for x_val in xs]
        grid_verts.append(row_v)

    for r in range(len(grid_verts) - 1):
        for c in range(n_x - 1):
            f = bm.faces.new((grid_verts[r][c], grid_verts[r][c + 1], grid_verts[r + 1][c + 1], grid_verts[r + 1][c]))
            f.smooth = True

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()

    mat = bpy.data.materials.new("Mat_Studio_Cyclorama")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    sep_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
    map_r = nodes.new(type='ShaderNodeMapRange')
    map_r.inputs["From Min"].default_value = 0.0
    map_r.inputs["From Max"].default_value = 7.5
    map_r.inputs["To Min"].default_value = 0.0
    map_r.inputs["To Max"].default_value = 1.0

    mix_c = nodes.new(type='ShaderNodeMix')
    mix_c.data_type = 'RGBA'
    col_floor = mod_iinet.rgb255_to_linear_rgba(232, 238, 248)
    col_wall = mod_iinet.rgb255_to_linear_rgba(246, 249, 254)
    mix_c.inputs["A"].default_value = col_floor
    mix_c.inputs["B"].default_value = col_wall

    links.new(tex_coord.outputs["Object"], sep_xyz.inputs["Vector"])
    links.new(sep_xyz.outputs["Z"], map_r.inputs["Value"])
    links.new(map_r.outputs["Result"], mix_c.inputs["Factor"])
    links.new(mix_c.outputs["Result"], bsdf.inputs["Base Color"])

    bsdf.inputs["Roughness"].default_value = 0.92
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.08
    if "Emission Strength" in bsdf.inputs:
        links.new(mix_c.outputs["Result"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 0.38

    obj.data.materials.append(mat)
    return obj


def setup_animation_lighting_and_camera(scene):
    mod_pair.setup_pair_lighting_and_world()
    mod_iinet.disable_freestyle_outline()

    cam_data = bpy.data.cameras.new("PairAnimCam")
    cam_obj = bpy.data.objects.new("PairAnimCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    mod_pair.set_pair_camera_pose(
        cam_obj,
        pos=(0.0, -8.45, 1.22),
        forward=(0.0, 1.0, 0.0),
        up_hint=(0.0, 0.0, 1.0),
        ortho=False,
        lens=LENS_16_9,
    )
    cam_data.clip_start = 0.1
    cam_data.clip_end = 60.0

    ldata = bpy.data.lights.new(name="Runway_Fill", type='AREA')
    ldata.energy = 320.0
    ldata.color = (1.0, 0.99, 0.99)
    ldata.size = 10.0
    if hasattr(ldata, "use_shadow"):
        ldata.use_shadow = True
    lobj = bpy.data.objects.new(name="Runway_Fill", object_data=ldata)
    bpy.context.collection.objects.link(lobj)
    lobj.location = Vector((0.0, 4.2, 6.2))
    direction = (Vector((0.0, 3.2, 1.0)) - lobj.location).normalized()
    lobj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    return cam_obj


# ==========================================
# 6. 視覚監査コンタクトシート（400%拡大クローズアップ＋歩行8コマ＋全フェーズ6コマ）＆ MP4出力
# ==========================================
def render_arm_seam_closeup_sheet(
    cam_obj, char_states, frame_list, cols, rows, out_path, panel_w=840, panel_h=360
):
    """
    【v6 必須監査】腕の付け根（吸盤フィレットスカート境界）を 400% ズーム（lens=105mm 望遠・横長サブパネル）で
    左半分＝いい-ch（緑）の両肩・両腕根元、右半分＝いい-NETくん（ピンク）の両肩・両腕根元として並べた
    6ポーズ拡大視覚監査シート（audit_arm_seam_closeup.png）を出力する。
    """
    scene = bpy.context.scene
    tmp_path = os.path.join(SCRIPT_DIR, "_tmp_closeup_kf.png")
    half_w = panel_w // 2

    panels = []
    for f in frame_list:
        scene.frame_set(f)
        update_camera_for_frame(cam_obj, f)
        for cs in char_states:
            apply_character_kirby_motion_at_frame(cs, f)
        bpy.context.view_layer.update()

        cam_fwd = (cam_obj.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()

        sub_imgs = []
        for cs in char_states:
            loc = cs["arm_obj"].location
            is_iich = cs["is_iich"]
            # 各キャラクターの両肩・両腕根元〜脇下ゾーン全体が横長サブパネル(420x360)いっぱいに収まるようズーム撮影
            z_tgt = (0.40 if is_iich else 0.52) + (0.12 if f >= 330 else 0.0)
            tgt = Vector((loc.x, loc.y, loc.z + z_tgt))
            c_pos = tgt - 5.20 * cam_fwd
            lens_zoom = 86.0 if f >= 330 else 102.0
            mod_pair.set_pair_camera_pose(
                cam_obj, pos=c_pos, forward=cam_fwd, up_hint=(0.0, 0.0, 1.0), ortho=False, lens=lens_zoom
            )
            arr = mod_iinet.render_view_to_array(cam_obj, half_w, panel_h, tmp_path, transparent=False)
            sub_imgs.append(arr)

        panel = np.concatenate(sub_imgs, axis=1)
        border_col = (205, 215, 232)
        panel[:2, :, :3] = border_col
        panel[-2:, :, :3] = border_col
        panel[:, :2, :3] = border_col
        panel[:, -2:, :3] = border_col
        panel[:, half_w - 1:half_w + 1, :3] = (220, 226, 238)
        panels.append(panel)

    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    pad = 16
    sheet_w = cols * panel_w + (cols + 1) * pad
    sheet_h = rows * panel_h + (rows + 1) * pad
    sheet = np.full((sheet_h, sheet_w, 4), 240, dtype=np.uint8)
    sheet[:, :, 3] = 255

    for idx, panel in enumerate(panels):
        r = idx // cols
        c = idx % cols
        y0 = pad + r * (panel_h + pad)
        x0 = pad + c * (panel_w + pad)
        sheet[y0:y0 + panel_h, x0:x0 + panel_w] = panel

    mod_iinet.save_rgba_uint8_as_png(sheet, out_path)
    print(f"Saved 400% arm-seam closeup audit sheet (frames={frame_list}) to: {out_path}")


def render_eye_expression_audit_sheet(
    cam_obj, char_states, frame_list, cols, rows, out_path, panel_w=840, panel_h=380
):
    """
    【v9 必須監査】2キャラクターの目の表情（まばたき・公式通常目・おじぎ閉じ目 ︶︶・手振り笑顔目 ◠◠）を
    顔アップ（左半分＝いい-ch、右半分＝いい-NETくん）で6フレーム並べて監査するシートを出力する。
    """
    scene = bpy.context.scene
    tmp_path = os.path.join(SCRIPT_DIR, "_tmp_eye_kf.png")
    half_w = panel_w // 2

    panels = []
    for f in frame_list:
        scene.frame_set(f)
        update_camera_for_frame(cam_obj, f)
        for cs in char_states:
            apply_character_kirby_motion_at_frame(cs, f)
        bpy.context.view_layer.update()

        cam_fwd = (cam_obj.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
        sub_imgs = []
        for cs in char_states:
            loc = cs["arm_obj"].location
            is_iich = cs["is_iich"]
            z_tgt = 0.84 if is_iich else 1.20
            tgt = Vector((loc.x, loc.y, loc.z + z_tgt))
            c_pos = tgt - 4.40 * cam_fwd
            mod_pair.set_pair_camera_pose(
                cam_obj, pos=c_pos, forward=cam_fwd, up_hint=(0.0, 0.0, 1.0), ortho=False, lens=92.0
            )
            arr = mod_iinet.render_view_to_array(cam_obj, half_w, panel_h, tmp_path, transparent=False)
            sub_imgs.append(arr)

        panel = np.concatenate(sub_imgs, axis=1)
        border_col = (205, 215, 232)
        panel[:2, :, :3] = border_col
        panel[-2:, :, :3] = border_col
        panel[:, :2, :3] = border_col
        panel[:, -2:, :3] = border_col
        panel[:, half_w - 1:half_w + 1, :3] = (220, 226, 238)
        panels.append(panel)

    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    pad = 16
    sheet_w = cols * panel_w + (cols + 1) * pad
    sheet_h = rows * panel_h + (rows + 1) * pad
    sheet = np.full((sheet_h, sheet_w, 4), 240, dtype=np.uint8)
    sheet[:, :, 3] = 255

    for idx, panel in enumerate(panels):
        r = idx // cols
        c = idx % cols
        y0 = pad + r * (panel_h + pad)
        x0 = pad + c * (panel_w + pad)
        sheet[y0:y0 + panel_h, x0:x0 + panel_w] = panel

    mod_iinet.save_rgba_uint8_as_png(sheet, out_path)
    print(f"Saved eye-expression closeup audit sheet (frames={frame_list}) to: {out_path}")


def render_contact_sheet_for_frames(
    cam_obj, char_states, frame_list, cols, rows, out_paths, width=640, height=360
):
    scene = bpy.context.scene
    tmp_path = os.path.join(SCRIPT_DIR, "_tmp_anim_kf.png")

    panels = []
    for f in frame_list:
        scene.frame_set(f)
        update_camera_for_frame(cam_obj, f)
        for cs in char_states:
            apply_character_kirby_motion_at_frame(cs, f)
        bpy.context.view_layer.update()
        arr = mod_iinet.render_view_to_array(cam_obj, width, height, tmp_path, transparent=False)
        border_col = (205, 215, 232)
        arr[:2, :, :3] = border_col
        arr[-2:, :, :3] = border_col
        arr[:, :2, :3] = border_col
        arr[:, -2:, :3] = border_col
        panels.append(arr)

    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    pad = 16
    sheet_w = cols * width + (cols + 1) * pad
    sheet_h = rows * height + (rows + 1) * pad
    sheet = np.full((sheet_h, sheet_w, 4), 240, dtype=np.uint8)
    sheet[:, :, 3] = 255

    for idx, panel in enumerate(panels):
        r = idx // cols
        c = idx % cols
        y0 = pad + r * (height + pad)
        x0 = pad + c * (width + pad)
        sheet[y0:y0 + height, x0:x0 + width] = panel

    for out_path in out_paths:
        mod_iinet.save_rgba_uint8_as_png(sheet, out_path)
        print(f"Saved contact sheet ({cols}x{rows}, frames={frame_list}) to: {out_path}")


def generate_synchronized_mascot_sfx_wav(wav_path, sr=48000, duration_sec=15.0):
    """
    【v8 新規】アニメーションの全450フレーム（15.0秒 @ 30fps）の動きと1ミリ秒のズレもなく完全同期した
    48,000Hz / 16-bit ステレオ効果音トラック（pair_iich_and_iinet_sfx.wav）をプロシージャル合成する。
      - Phase 1 (Frame 1〜160 / 0.00s〜5.33s): 歩く音「ポテッ、トコッ、ポテッ、トコッ♪」（左右位相差・距離クレッシェンド完全同期）
      - Phase 2 (Frame 161〜210 / 5.33s〜7.00s): 着地ホップ音「ピョコン♪ ➔ ポテッ！」
      - Phase 3 (Frame 211〜300 / 7.00s〜10.00s): おじぎ音「ペコリ♪（下降2音マリンバチャイム＋ソフトスウィッシュ）➔ フワッ♪」
      - Phase 4 (Frame 301〜450 / 10.00s〜15.00s): 手を振る音「パタパタパタッ♪（フリフリッ♪）」
    """
    n_samples = int(sr * duration_sec)
    audio = np.zeros((n_samples, 2), dtype=np.float64)
    rng = np.random.default_rng(20261118)

    def f24_to_sec(f_24_val):
        f30 = 1.0 + (float(f_24_val) - 1.0) * (30.0 / 24.0)
        return max(0.0, (f30 - 1.0) / float(FPS))

    def add_stereo_clip(t_start_sec, sig_mono, gain_l, gain_r):
        i0 = int(round(t_start_sec * sr))
        if i0 >= n_samples or len(sig_mono) == 0:
            return
        if i0 < 0:
            sig_mono = sig_mono[-i0:]
            i0 = 0
        i1 = min(n_samples, i0 + len(sig_mono))
        seg = sig_mono[:i1 - i0]
        audio[i0:i1, 0] += seg * gain_l
        audio[i0:i1, 1] += seg * gain_r

    def smooth_band_noise(n_len, win_lp=32, win_hp=180):
        raw = rng.standard_normal(n_len + win_hp * 2)
        k_lp = np.ones(win_lp, dtype=np.float64) / float(win_lp)
        lp = np.convolve(raw, k_lp, mode='same')
        k_hp = np.ones(win_hp, dtype=np.float64) / float(win_hp)
        bp = lp - np.convolve(lp, k_hp, mode='same')
        return bp[win_hp:win_hp + n_len]

    # -------------------------------------------------------------------------
    # 1. Phase 1: 歩く音（ポテポテ・トコトコ足音）
    #    phase = 2π * ((f_24 - 1.0 - phase_offset) / 16.0)
    #    1歩 = 8.0 f_24 (= 10.0f @ 30fps = 0.3333s) ごとに左足・右足が交互着地
    # -------------------------------------------------------------------------
    def synth_cute_footstep(is_iich_char, is_left_foot, vol_scale):
        dur = 0.068 if is_iich_char else 0.075
        n_s = int(sr * dur)
        t = np.linspace(0.0, dur, n_s, endpoint=False)
        p_alt = 1.00 if is_left_foot else 0.95

        # (a) ぷっくり柔らかいソフビ足底クッションのピッチドロップ基音
        f0 = (265.0 if is_iich_char else 222.0) * p_alt
        f1 = (124.0 if is_iich_char else 104.0) * p_alt
        freq_t = f1 + (f0 - f1) * np.exp(-t / 0.018)
        phase_t = 2.0 * math.pi * np.cumsum(freq_t) / float(sr)
        env_thump = (1.0 - np.exp(-t / 0.0025)) * np.exp(-t / 0.021)
        sig_thump = np.sin(phase_t) * env_thump

        # (b) 木琴/マレット風の温かく可愛い「ポコッ／トコッ」ポップ倍音
        fp0 = (530.0 if is_iich_char else 455.0) * p_alt
        fp1 = (695.0 if is_iich_char else 590.0) * p_alt
        freq_pop = fp0 + (fp1 - fp0) * np.clip(t / 0.024, 0.0, 1.0)
        phase_pop = 2.0 * math.pi * np.cumsum(freq_pop) / float(sr)
        env_pop = np.sin(math.pi * np.clip(t / 0.028, 0.0, 1.0)) ** 1.4 * np.exp(-t / 0.016)
        sig_pop = 0.44 * np.sin(phase_pop) * env_pop

        # (c) ごく微かなソフト接地タップスウィッシュ
        nz = smooth_band_noise(n_s, win_lp=24, win_hp=140)
        env_nz = np.sin(math.pi * np.clip(t / 0.022, 0.0, 1.0)) ** 2 * np.exp(-t / 0.012)
        sig_nz = 0.08 * nz * env_nz

        return (sig_thump + sig_pop + sig_nz) * (0.34 * vol_scale)

    for is_iich_c, ph_off, gl, gr in [
        (True, 0.0, 0.82, 0.48),
        (False, 3.0, 0.48, 0.82),
    ]:
        for step_k in range(16):
            f24_step = 2.5 + ph_off + 8.0 * step_k
            if f24_step > 125.5:
                break
            amp_w = 1.0 if f24_step <= 114.0 else (1.0 - smootherstep_scalar((f24_step - 114.0) / 14.0))
            dist_cresc = 0.46 + 0.54 * smoothstep_scalar(min(max(f24_step - 1.0, 0.0) / 96.0, 1.0))
            vol = amp_w * dist_cresc
            if vol > 0.05:
                clip = synth_cute_footstep(is_iich_c, (step_k % 2 == 0), vol)
                add_stereo_clip(f24_to_sec(f24_step), clip, gl, gr)

    # -------------------------------------------------------------------------
    # 2. Phase 2: 着地ホップ音「ピョコン♪ ➔ ポテッ！」
    # -------------------------------------------------------------------------
    def synth_hop_boing(pitch_mul=1.0):
        dur = 0.145
        n_s = int(sr * dur)
        t = np.linspace(0.0, dur, n_s, endpoint=False)
        u = t / dur
        freq = (350.0 + 440.0 * (u ** 0.72) + 35.0 * np.sin(2.0 * math.pi * 18.0 * t)) * pitch_mul
        ph = 2.0 * math.pi * np.cumsum(freq) / float(sr)
        env = (1.0 - np.exp(-t / 0.004)) * np.exp(-t / 0.052) * np.sin(math.pi * u) ** 0.4
        return (0.78 * np.sin(ph) + 0.22 * np.sin(2.0 * ph)) * env * 0.30

    for is_iich_c, f_off, p_m, gl, gr in [
        (True, 0.0, 1.04, 0.80, 0.50),
        (False, 1.0, 0.96, 0.50, 0.80),
    ]:
        add_stereo_clip(f24_to_sec(129.0 + f_off), synth_hop_boing(p_m), gl, gr)
        land_clip = synth_cute_footstep(is_iich_c, True, 1.15)
        add_stereo_clip(f24_to_sec(143.0 + f_off), land_clip, gl, gr)

    # -------------------------------------------------------------------------
    # 3. Phase 3: おじぎ音「ペコリ♪（下降2音マリンバチャイム＋ソフトスウィッシュ）➔ フワッ♪」
    # -------------------------------------------------------------------------
    def synth_marimba_note(freq_hz, dur=0.16):
        n_s = int(sr * dur)
        t = np.linspace(0.0, dur, n_s, endpoint=False)
        ph = 2.0 * math.pi * freq_hz * t
        env = (1.0 - np.exp(-t / 0.003)) * np.exp(-t / 0.045)
        env_harm = (1.0 - np.exp(-t / 0.002)) * np.exp(-t / 0.018)
        return (0.82 * np.sin(ph) * env + 0.18 * np.sin(2.0 * ph) * env_harm) * 0.26

    def synth_soft_whoosh(dur=0.22, f_start=380.0, f_end=260.0):
        n_s = int(sr * dur)
        t = np.linspace(0.0, dur, n_s, endpoint=False)
        u = t / dur
        nz = smooth_band_noise(n_s, win_lp=38, win_hp=210)
        freq = f_start + (f_end - f_start) * u
        ph = 2.0 * math.pi * np.cumsum(freq) / float(sr)
        env = (np.sin(math.pi * u) ** 1.6)
        return (0.45 * nz + 0.55 * np.sin(ph)) * env * 0.16

    # おじぎ開始 (f_24 = 177.0 / Frame 222): E5 (659.25Hz) -> C5 (523.25Hz)
    t_bow_in = f24_to_sec(177.0)
    add_stereo_clip(t_bow_in, synth_soft_whoosh(0.24, 420.0, 250.0), 0.70, 0.70)
    add_stereo_clip(t_bow_in + 0.01, synth_marimba_note(659.25, 0.15), 0.75, 0.60)
    add_stereo_clip(t_bow_in + 0.085, synth_marimba_note(523.25, 0.18), 0.60, 0.75)

    # おじぎ起き上がり (f_24 = 216.0 / Frame 271): C5 (523.25Hz) -> E5 (659.25Hz)
    t_bow_up = f24_to_sec(216.0)
    add_stereo_clip(t_bow_up, synth_soft_whoosh(0.20, 260.0, 440.0), 0.70, 0.70)
    add_stereo_clip(t_bow_up + 0.01, synth_marimba_note(523.25, 0.14), 0.62, 0.74)
    add_stereo_clip(t_bow_up + 0.075, synth_marimba_note(659.25, 0.17), 0.74, 0.62)

    # -------------------------------------------------------------------------
    # 4. Phase 4: 手を振る音「パタパタパタッ♪（フリフリッ♪）」
    #    theta_10 = 2π * ((f_24 - 273.5) / 10.0)
    #    上振り速度ピーク (f_24 = 243.5 + 10*k) と 下振り速度ピーク (f_24 = 248.5 + 10*k)
    # -------------------------------------------------------------------------
    def synth_wave_patapata(is_up_stroke, env_w):
        dur = 0.086
        n_s = int(sr * dur)
        t = np.linspace(0.0, dur, n_s, endpoint=False)
        u = t / dur
        win = np.sin(math.pi * u) ** 1.5

        # (a) シルクのように滑らかなパドル風切りスウィッシュ
        nz = smooth_band_noise(n_s, win_lp=20, win_hp=150)
        sig_swish = 0.42 * nz * win

        # (b) キュートな軽快マスコットポップトーン（上振り=上昇スイープ、下振り=下降スイープ）
        if is_up_stroke:
            f0, f1 = 560.0, 760.0
        else:
            f0, f1 = 690.0, 515.0
        freq = f0 + (f1 - f0) * smoothstep_np(u)
        ph = 2.0 * math.pi * np.cumsum(freq) / float(sr)
        env_tone = (1.0 - np.exp(-t / 0.003)) * np.exp(-t / 0.028) * win
        sig_tone = (0.75 * np.sin(ph) + 0.25 * np.sin(2.0 * ph)) * env_tone

        return (sig_swish + sig_tone) * (0.25 * env_w)

    f24_wave = 243.5
    stroke_idx = 0
    while f24_wave <= 349.0:
        env_in = smootherstep_scalar(np.clip((f24_wave - 241.0) / 14.0, 0.0, 1.0))
        env_out = 1.0 - smootherstep_scalar(np.clip((f24_wave - 334.0) / 18.0, 0.0, 1.0))
        w_w = env_in * env_out
        if w_w > 0.12:
            is_up = (stroke_idx % 2 == 0)
            clip_w = synth_wave_patapata(is_up, w_w)
            t_w = f24_to_sec(f24_wave) - 0.035
            # 左右のキャラクターが一緒にパタパタ振る豊かなステレオ感
            add_stereo_clip(t_w, clip_w, 0.78, 0.56)
            add_stereo_clip(t_w + 0.012, clip_w * 0.94, 0.56, 0.78)
        f24_wave += 5.0
        stroke_idx += 1

    # ソフトリミッタ＆正規化（ピーク -1.5dBFS = 0.84）
    peak = float(np.max(np.abs(audio)))
    if peak > 1e-6:
        audio = np.tanh(audio / max(peak, 0.65) * 1.15) * 0.82

    pcm16 = np.clip(audio * 32767.0, -32767, 32767).astype(np.int16)
    with wave.open(wav_path, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm16.tobytes())

    print(f"Generated synchronized mascot SFX stereo WAV ({duration_sec:.1f}s @ {sr}Hz) -> {wav_path}")
    return wav_path


def attach_sfx_to_scene_vse(scene, wav_path):
    """生成した効果音 WAV を Blender Video Sequence Editor (VSE) の Frame 1 に配置する"""
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    seq_ed = scene.sequence_editor
    strips = getattr(seq_ed, "strips", None) or getattr(seq_ed, "sequences", None)
    if strips is not None:
        for s in list(strips):
            if s.name.startswith("Mascot_SFX"):
                strips.remove(s)
        snd_strip = strips.new_sound(name="Mascot_SFX", filepath=wav_path, channel=1, frame_start=1)
        if hasattr(snd_strip, "volume"):
            snd_strip.volume = 1.0


def bake_keyframes_for_blend_file(cam_obj, char_states, wav_path=None):
    scene = bpy.context.scene
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.render.fps = FPS
    scene.render.fps_base = 1.0
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

    if wav_path and os.path.exists(wav_path):
        attach_sfx_to_scene_vse(scene, wav_path)

    cam_obj.rotation_mode = 'XYZ'
    for f in range(FRAME_START, FRAME_END + 1):
        update_camera_for_frame(cam_obj, f)
        cam_obj.keyframe_insert(data_path="location", frame=f)
        cam_obj.keyframe_insert(data_path="rotation_euler", frame=f)
        for cs in char_states:
            apply_character_kirby_motion_at_frame(cs, f)
            cs["arm_obj"].keyframe_insert(data_path="location", frame=f)

    # Frame 195 (@30fps = 6.50s) は正面静止ポーズ
    scene.frame_set(195)
    update_camera_for_frame(cam_obj, 195)
    for cs in char_states:
        apply_character_kirby_motion_at_frame(cs, 195)


def render_full_mp4_animation(scene, cam_obj, char_states, mp4_path, wav_path=None, width=1920, height=1080):
    def on_frame_change(scn, depsgraph=None):
        f_cur = scn.frame_current
        update_camera_for_frame(cam_obj, f_cur)
        for cs in char_states:
            apply_character_kirby_motion_at_frame(cs, f_cur)

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(on_frame_change)

    if hasattr(scene.render, "use_persistent_data"):
        scene.render.use_persistent_data = False

    if wav_path and os.path.exists(wav_path):
        attach_sfx_to_scene_vse(scene, wav_path)

    scene.camera = cam_obj
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.render.fps = FPS
    scene.render.fps_base = 1.0
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.filepath = mp4_path

    img_settings = scene.render.image_settings
    if hasattr(img_settings, "media_type"):
        img_settings.media_type = 'VIDEO'
    else:
        img_settings.file_format = 'FFMPEG'

    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
    scene.render.ffmpeg.gopsize = 15
    scene.render.ffmpeg.audio_codec = 'AAC'
    scene.render.ffmpeg.audio_bitrate = 192
    if hasattr(scene.render.ffmpeg, "audio_mixrate"):
        scene.render.ffmpeg.audio_mixrate = 48000
    if hasattr(scene.render.ffmpeg, "audio_channels"):
        scene.render.ffmpeg.audio_channels = 'STEREO'

    t0 = time.time()
    bpy.ops.render.render(animation=True)
    dt = time.time() - t0
    bpy.app.handlers.frame_change_pre.clear()

    # 万一 Blender の VSE と 3D Scene レンダリング仕様で音声トラックが控えめまたは未多重化の場合に備え、
    # ffmpeg が利用可能であれば生成した高音質 48kHz WAV を確実に AAC 192kbps で無劣化多重化（映像は -c:v copy）する
    if wav_path and os.path.exists(wav_path) and os.path.exists(mp4_path):
        tmp_mux = mp4_path + ".mux_tmp.mp4"
        try:
            res = subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", mp4_path,
                    "-i", wav_path,
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-ar", "48000",
                    "-ac", "2",
                    "-shortest",
                    tmp_mux,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
            )
            if res.returncode == 0 and os.path.exists(tmp_mux) and os.path.getsize(tmp_mux) > 100000:
                os.replace(tmp_mux, mp4_path)
                print(f"Verified & muxed 48kHz stereo AAC audio track into MP4 -> {mp4_path}")
            elif os.path.exists(tmp_mux):
                os.remove(tmp_mux)
        except Exception as e:
            print(f"Note: external ffmpeg mux skipped ({e}); using Blender internal AAC output.")
            if os.path.exists(tmp_mux):
                os.remove(tmp_mux)

    print(f"MP4 animation render with synchronized SFX (450 frames / 15.0s @ 30fps, 1920x1080) completed in {dt:.1f}s -> {mp4_path}")


def main():
    check_only = ("--check-only" in sys.argv)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    mod_iinet.configure_cycles_gpu(scene)

    scene.cycles.samples = 28
    scene.cycles.use_denoising = True
    if hasattr(scene.cycles, "denoiser"):
        scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    if hasattr(scene.cycles, "denoising_input_passes"):
        scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    if hasattr(scene.cycles, "denoising_prefilter"):
        scene.cycles.denoising_prefilter = 'FAST'

    coll_iich = bpy.data.collections.new("Collection_IICh")
    coll_iinet = bpy.data.collections.new("Collection_IINet")
    scene.collection.children.link(coll_iich)
    scene.collection.children.link(coll_iinet)

    if not os.path.exists(mod_iinet.GLOBE_TEX_PATH):
        mod_iinet.extract_textures_and_profiles()
    mat_globe = mod_pair.create_micro_grain_globe_material()
    im_ref = mod_iinet.load_image_rgba_uint8(mod_pair.REF_PAIR_PATH)

    # fuse_arms=False により、胴体（純粋なタマゴ型メッシュ）と両腕（独立した滑らかなパドルメッシュ）を分離構築し、
    # capture_character_rest_state 内で腕を極座標スライディング吸盤フィレットスカート構造へ再構築する。
    arm_iich, meshes_iich = mod_pair.build_iich_character(coll_iich, mat_globe, im_ref, fuse_arms=False)
    arm_iinet, meshes_iinet = mod_pair.build_iinet_character(coll_iinet, mat_globe, im_ref, fuse_arms=False)

    state_iich = capture_character_rest_state(arm_iich, meshes_iich, is_iich=True)
    state_iinet = capture_character_rest_state(arm_iinet, meshes_iinet, is_iich=False)
    char_states = [state_iich, state_iinet]

    create_studio_floor_and_backdrop()
    cam_obj = setup_animation_lighting_and_camera(scene)

    # 監査シート0（v6〜v9最優先）：腕根元の400%拡大クローズアップ6ポーズ監査シート
    # [195: 正面静止, 26: 歩行前振り, 36: 歩行後ろ振り, 252: おじぎ, 345: 高い手振りUp, 351: 手振りDown]
    render_arm_seam_closeup_sheet(
        cam_obj,
        char_states,
        frame_list=[195, 26, 36, 252, 345, 351],
        cols=3,
        rows=2,
        out_path=AUDIT_ARM_SEAM_CLOSEUP_PATH,
        panel_w=840,
        panel_h=360,
    )

    # 監査シート0B（v9新規）：2キャラクター目の表情クローズアップ6ポーズ監査シート
    # [45: 歩行まばたき(いい-ch), 60: 歩行まばたき(いい-NET), 171: ホップまばたき, 195: 公式通常目, 252: おじぎ閉じ目(︶︶), 345: 手振り笑顔目(◠◠)]
    render_eye_expression_audit_sheet(
        cam_obj,
        char_states,
        frame_list=[45, 60, 171, 195, 252, 345],
        cols=3,
        rows=2,
        out_path=AUDIT_EYE_EXPR_PATH,
        panel_w=840,
        panel_h=380,
    )

    # 監査シート0C（v10新規）：しなやか尻尾＆地球儀の連続8ポーズ監査シート
    # [26: 歩行S字左, 36: 歩行S字右, 171: ホップ頂点, 182: 着地ポヨン沈み, 232: おじぎ下げ遅れS字, 250: おじぎ最下点しなり, 345: 手振り大きく右揺れ, 364: 手振り大きく左揺れ]
    render_contact_sheet_for_frames(
        cam_obj,
        char_states,
        frame_list=[26, 36, 171, 182, 232, 250, 345, 364],
        cols=4,
        rows=2,
        out_paths=[AUDIT_TAIL_SUPPLE_PATH],
        width=560,
        height=315,
    )

    # 監査シートA：歩行1サイクル（30fps 20フレーム周期）連続8コマ確認（16:9 パネル）
    render_contact_sheet_for_frames(
        cam_obj,
        char_states,
        frame_list=[21, 24, 26, 29, 31, 34, 36, 39],
        cols=4,
        rows=2,
        out_paths=[AUDIT_WALK_8_PATH],
        width=560,
        height=315,
    )

    # 監査シートB：全4フェーズ代表6コマ一覧（16:9 パネル）
    # [26: 歩き出し3/4, 96: 歩行中盤, 170: ピョコン着地ホップ(正面), 252: 丸ボディのままペコリおじぎ, 345: ほっぺ横手振りUp, 364: 手振りDown＆片足ちょこん浮き]
    render_contact_sheet_for_frames(
        cam_obj,
        char_states,
        frame_list=[26, 96, 170, 252, 345, 364],
        cols=3,
        rows=2,
        out_paths=[CHECK_SHEET_DRAFT_PATH, KEYFRAMES_FINAL_PATH],
        width=640,
        height=360,
    )

    sfx_wav_path = generate_synchronized_mascot_sfx_wav(ANIM_SFX_WAV_PATH, sr=48000, duration_sec=15.0)
    bake_keyframes_for_blend_file(cam_obj, char_states, wav_path=sfx_wav_path)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=ANIM_BLEND_PATH)

    if not check_only:
        render_full_mp4_animation(
            scene, cam_obj, char_states, ANIM_MP4_PATH, wav_path=sfx_wav_path, width=1920, height=1080
        )

    print("ALL PAIR ANIMATION TASKS COMPLETED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
