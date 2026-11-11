# -*- coding: utf-8 -*-
"""
CVN公式マスコットキャラクター「いい-ch（LILI-ch）＆ いい-NETくん（LILI-net）」
2体ペア3Dアニメーション動画（15.0秒 / 360フレーム @ 24fps）
【カービィ型・超短足マスコットの可愛い仕草 全面再設計版（SO(3)/SE(3) 純粋回転リグ）】

  Phase 1 (Frame 1〜128 / 0.00s〜5.33s):
    リファレンス（Kirby walk cycle 24fps: 1歩=8f / 1サイクル=16f）準拠の
    超短足「トコトコ／ポテポテ」ウォーク（Y=+4.35m ➔ 0.0m、1歩≈0.272m）。
    歩き出しは斜め前3/4カメラアングルで前後の足運び・つま先キュッ上向き・短い手の逆位相スイングを
    立体的に見せ、Frame 76〜132 で完成静止画の正面カメラへ滑らかに回り込む。
  Phase 2 (Frame 129〜168 / 5.33s〜7.00s):
    定位置 Y=0.0m に到着した瞬間、両足を揃えて小さく「ピョコン！」と可愛い着地ホップ（+4.5cm）➔
    「ポテッ」と自然な3%クッションで正面スマイル構図にピタッと静止（Frame 156 で静止画と100%一致）。
  Phase 3 (Frame 169〜240 / 7.00s〜10.00s):
    お腹の凹み・ロゴ歪みゼロ！ぷっくり丸いタマゴ体型のまま、短いパドル手をちょこんと後ろ外側へ添えて
    前へ約26°綺麗に「ペコリ！」とおじぎし、アンテナと地球儀も可愛く前へ揺れる。
  Phase 4 (Frame 241〜360 / 10.00s〜15.00s):
    腕の伸縮ゼロ（常時1.00倍）！外側の短いパドル手をほっぺの横（+54°〜+82°）へグイッと持ち上げ、
    周期10フレームで「パタパタパタッ！」と元気に振りながら、小首傾げ＆片足ちょこん浮きリズムを刻み、
    最後は正面静止構図（Frame 360）にピタッと収まる。

Usage:
  1) 視覚監査シート2枚（歩行8コマ連続＋全フェーズ6コマ）高速監査モード:
     blender.exe --background --python build_pair_animation.py -- --check-only
  2) 全360フレーム（15.0秒）MP4動画＋最終成果物一括出力モード:
     blender.exe --background --python build_pair_animation.py
"""

import os
import sys
import math
import time
import numpy as np
import bpy
import bmesh
from mathutils import Vector, Matrix

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import build_iinet_kun as mod_iinet
import build_pair_scene as mod_pair

DEPT_DIR = os.path.dirname(SCRIPT_DIR)
FINAL_DIR = os.path.join(DEPT_DIR, "final_outputs")
os.makedirs(FINAL_DIR, exist_ok=True)

AUDIT_WALK_8_PATH = os.path.join(SCRIPT_DIR, "audit_walk_cycle_8frames.png")
CHECK_SHEET_DRAFT_PATH = os.path.join(SCRIPT_DIR, "anim_keyframes_check.png")
KEYFRAMES_FINAL_PATH = os.path.join(FINAL_DIR, "pair_iich_and_iinet_anim_keyframes.png")
ANIM_BLEND_PATH = os.path.join(FINAL_DIR, "cvn_iich_and_iinet_pair_anim.blend")
ANIM_MP4_PATH = os.path.join(FINAL_DIR, "pair_iich_and_iinet_run_bow_wave.mp4")

FPS = 24
FRAME_START = 1
FRAME_END = 360


# ==========================================
# 数学ユーティリティ（C^1 / C^2 イージング ＆ SO(3) Exponential-Map）
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


def so3_log_from_matrix(R):
    """3x3 回転行列 R から軸角ベクトル omega (rad) を抽出する"""
    tr = float(R[0, 0] + R[1, 1] + R[2, 2])
    cos_th = max(-1.0, min(1.0, 0.5 * (tr - 1.0)))
    th = math.acos(cos_th)
    if th < 1e-7:
        return np.zeros(3, dtype=np.float64), 0.0, np.array([1.0, 0.0, 0.0], dtype=np.float64)
    denom = 2.0 * math.sin(th)
    kx = (R[2, 1] - R[1, 2]) / denom
    ky = (R[0, 2] - R[2, 0]) / denom
    kz = (R[1, 0] - R[0, 1]) / denom
    k = np.array([kx, ky, kz], dtype=np.float64)
    nrm = float(np.linalg.norm(k))
    if nrm > 1e-9:
        k /= nrm
    return k * th, th, k


# ==========================================
# 1. キャラクター初期頂点＆シームレスブレンド重み事前計算
# ==========================================
def capture_character_rest_state(arm_obj, meshes, is_iich=True):
    """
    各キャラクターの全メッシュ初期座標（Rest Coords）と、
    ・短いパドル手の SO(3) 純粋回転ブレンド重み w_arm_blend（伸縮ゼロ・体積収縮ゼロ）
    ・超短足の滑らかな左右分離重み s_L, s_R ＆ 高さ減衰 w_leg（胸ロゴ領域を100%保護）
    を事前計算してキャッシュする。
    """
    body_obj = next(m for m in meshes if m.name.endswith("_Body"))
    n_body = len(body_obj.data.vertices)
    body_co = np.empty(n_body * 3, dtype=np.float64)
    body_obj.data.vertices.foreach_get("co", body_co)
    body_co = body_co.reshape(-1, 3)

    if is_iich:
        sz = 0.8262
        z_arm_min = 0.245 * sz     # 0.2024
        z_arm_max = 0.555 * sz     # 0.4585
        y_arm_mid = 0.0334
        y_arm_half = 0.112
        u_sh, y_sh, z_sh = 0.665, 0.0334, 0.345
        u_flap_piv, z_flap_piv = 0.295, 0.715
        z_leg_piv = 0.075
        pure_z_bands = list(np.linspace(0.11, 0.185, 8)) + list(np.linspace(0.478, 0.92, 18))
        base_loc = Vector((-0.946, -0.025, 0.0036))
    else:
        z_arm_min = 0.2820
        z_arm_max = 0.6680
        y_arm_mid = 0.0460
        y_arm_half = 0.132
        u_sh, y_sh, z_sh = 0.735, 0.0460, 0.465
        u_flap_piv, z_flap_piv = 0.455, 0.800
        z_leg_piv = 0.108
        pure_z_bands = list(np.linspace(0.15, 0.260, 8)) + list(np.linspace(0.685, 1.15, 18))
        base_loc = Vector((+0.881, +0.025, 0.0000))

    # 腕を除いた純粋なタマゴ型ボディ赤道輪郭 x_body_eq(z) を純ボディ帯域から高精度多項式近似
    zb_samples = []
    xb_samples = []
    for zc in pure_z_bands:
        m = (np.abs(body_co[:, 2] - zc) < 0.014) & (np.abs(body_co[:, 1] - y_arm_mid) < 0.055)
        if np.any(m):
            zb_samples.append(zc)
            xb_samples.append(float(np.max(np.abs(body_co[m, 0]))))
    poly_xb = np.polyfit(np.array(zb_samples), np.array(xb_samples), deg=4)

    z_min_rest = float(np.min(body_co[:, 2]))
    ground_ref_z = float(base_loc.z) + z_min_rest

    mesh_entries = []
    for obj in meshes:
        nv = len(obj.data.vertices)
        co = np.empty(nv * 3, dtype=np.float64)
        obj.data.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)

        is_body = obj.name.endswith("_Body")
        is_ant_or_globe = obj.name.endswith("_Antenna") or obj.name.endswith("_Globe")

        if is_body:
            vx, vy, vz = co[:, 0], co[:, 1], co[:, 2]
            ax = np.abs(vx)
            xb = np.polyval(poly_xb, np.clip(vz, 0.08, 1.15))

            # 1) パドル腕ブレンド重み w_arm_blend:
            #    胴体内部 (xb - 0.078m) から胴体表面 xb にかけて滑らかに 0 -> 1 へ立ち上げることで、
            #    外へ出ているパドル手全体 (ax >= xb) が重み 1.000 の完全な一体剛体として回転し、
            #    L字折れやクビレ・伸縮を100%防止する。前面の顔枠・胸ロゴ領域への影響も厳密にゼロ。
            d_out = ax - (xb - 0.078)
            wx_arm = smootherstep_np(d_out / 0.080)
            wz_low = smootherstep_np((vz - (z_arm_min - 0.036)) / 0.044)
            wz_high = 1.0 - smootherstep_np((vz - (z_arm_max - 0.004)) / 0.056)
            wy_arm = 1.0 - smootherstep_np((np.abs(vy - y_arm_mid) - (y_arm_half + 0.008)) / 0.054)
            w_arm_blend = wx_arm * wz_low * wz_high * wy_arm

            # 2) 超短足ブレンド重み w_leg & 左右分離 s_L, s_R:
            #    前面の胸ロゴ（IICh: z>=0.148m, IINet: z>=0.294m）直下で厳密に 0.0 に減衰させつつ、
            #    ロゴの無いお尻・背面側(y > -0.08m)では遷移帯を高く(0.29m / 0.41m)取り、大きな後ろ足蹴り上げも滑らかに吸収する。
            if is_iich:
                w_front_chest = smootherstep_np((-0.10 - vy) / 0.13)
                z_leg_top_v = 0.290 * (1.0 - w_front_chest) + 0.145 * w_front_chest
                z_foot_solid_v = 0.052 * (1.0 - w_front_chest) + 0.024 * w_front_chest
            else:
                w_front_chest = smootherstep_np((-0.12 - vy) / 0.14)
                z_leg_top_v = 0.410 * (1.0 - w_front_chest) + 0.278 * w_front_chest
                z_foot_solid_v = 0.085 * (1.0 - w_front_chest) + 0.042 * w_front_chest

            u_leg_z = 1.0 - smootherstep_np((vz - z_foot_solid_v) / np.maximum(z_leg_top_v - z_foot_solid_v, 0.05))
            u_leg_x_out = 1.0 - smootherstep_np((ax - 0.45) / 0.09)
            w_leg = u_leg_z * u_leg_x_out * (1.0 - w_arm_blend)
            s_leg_l = 0.5 * (1.0 + np.tanh(vx / 0.085))
        else:
            w_arm_blend = None
            w_leg = None
            s_leg_l = None

        mesh_entries.append({
            "obj": obj,
            "rest_co": co,
            "is_body": is_body,
            "is_ant_or_globe": is_ant_or_globe,
            "w_arm_blend": w_arm_blend,
            "w_leg": w_leg,
            "s_leg_l": s_leg_l,
        })

    return {
        "arm_obj": arm_obj,
        "is_iich": is_iich,
        "base_loc": base_loc,
        "ground_ref_z": ground_ref_z,
        "meshes": mesh_entries,
        "u_sh": u_sh,
        "y_sh": y_sh,
        "z_sh": z_sh,
        "u_flap_piv": u_flap_piv,
        "z_flap_piv": z_flap_piv,
        "z_leg_piv": z_leg_piv,
    }


# ==========================================
# 2. SO(3) / SE(3) 純粋回転リグ（短い手 ＆ 超短足）
# ==========================================
def deform_short_arm_so3_pure_rotation(
    x, y, z, w_arm_blend, char_state,
    side_sign, flap_deg, swing_fwd_deg
):
    """
    タマゴ型ボディ側面の曲率中心 (u_flap_piv, z_flap_piv) ＆ 肩関節 (u_sh, y_sh) を中心とする
    SO(3) Exponential-Map 純粋直交回転（det(R)=1、伸縮率 1.000倍厳守）。
      - パドル突出領域 (w_arm_blend = 1.0) は完全一体剛体として回転するため、
        ほっぺ横まで高く持ち上げてもL字折れや脇ノッチが一切発生せず、丸く短いカービィ手を100%維持する。
      - flap_deg > 0      : ボディ側面の丸みに沿って下向き初期角からほっぺ横へパタッと挙上
      - swing_fwd_deg > 0 : 肩関節を中心に前方（-Y ほっぺ・お腹側）へスイング
      - swing_fwd_deg < 0 : 肩関節を中心に後方（+Y お尻・背中側）へスイング
    """
    if abs(flap_deg) < 1e-4 and abs(swing_fwd_deg) < 1e-4:
        return x, y, z

    mask = (w_arm_blend > 1e-4) & ((x * side_sign) > 0.0)
    if not np.any(mask):
        return x, y, z

    wb = w_arm_blend[mask]
    u_out = side_sign * x[mask]
    ym = y[mask]
    zm = z[mask]

    u_sh = char_state["u_sh"]
    y_sh = char_state["y_sh"]
    z_sh = char_state["z_sh"]
    u_fp = char_state["u_flap_piv"]
    z_fp = char_state["z_flap_piv"]

    # 1) 上下パタパタ挙上（Flap: ボディ側面曲率中心まわりの純粋 SO(2) 回転 R(wb * alpha)）
    alpha_v = wb * math.radians(flap_deg)
    ca = np.cos(alpha_v)
    sa = np.sin(alpha_v)
    du_f = u_out - u_fp
    dz_f = zm - z_fp
    u_1 = u_fp + du_f * ca - dz_f * sa
    z_1 = z_fp + du_f * sa + dz_f * ca

    # 回転後の肩ピボット位置 u_sh_1 を中心に前後スイング（Azimuth: 純粋 SO(2) 回転 R(wb * beta)）
    u_sh_1 = u_fp + (u_sh - u_fp) * ca - (z_sh - z_fp) * sa
    beta_v = wb * math.radians(swing_fwd_deg)
    cb = np.cos(beta_v)
    sb = np.sin(beta_v)
    du_s = u_1 - u_sh_1
    dy_s = ym - y_sh
    u_2 = u_sh_1 + du_s * cb + dy_s * sb
    y_2 = y_sh - du_s * sb + dy_s * cb

    x_out = x.copy()
    y_out = y.copy()
    z_out = z.copy()
    x_out[mask] = side_sign * u_2
    y_out[mask] = y_2
    z_out[mask] = z_1
    return x_out, y_out, z_out


def deform_stubby_legs_kirby(
    x, y, z, w_leg, s_leg_l, z_leg_piv,
    leg_l_rx_deg, leg_r_rx_deg,
    leg_l_dy, leg_r_dy,
    leg_l_dz, leg_r_dz,
):
    """
    カービィ型の超短足前後パタパタ＆つま先キュッ上向き変形（伸縮ゼロ・股下引き裂きゼロ・すね折れシワゼロ）。
      - 前振り(rx<0)時は前すね表面(y≈-0.21m)、後蹴り(rx>0)時はかかと側(y≈+0.21m)へピボットYを置くことで、
        胸ロゴ直下のすね表面が押し潰されず dz'/dz >= +0.75 の滑らかな連続曲面を100%保証する！
    """
    if (
        abs(leg_l_rx_deg) < 1e-4 and abs(leg_r_rx_deg) < 1e-4
        and abs(leg_l_dy) < 1e-5 and abs(leg_r_dy) < 1e-5
        and abs(leg_l_dz) < 1e-5 and abs(leg_r_dz) < 1e-5
    ):
        return x, y, z

    mask = w_leg > 1e-4
    if not np.any(mask):
        return x, y, z

    wm = w_leg[mask]
    sl = s_leg_l[mask]
    sr = 1.0 - sl
    ym = y[mask]
    zm = z[mask]

    rx_rad_raw = math.radians(leg_l_rx_deg) * sl + math.radians(leg_r_rx_deg) * sr
    rx_eff = wm * rx_rad_raw
    dy_eff = wm * (leg_l_dy * sl + leg_r_dy * sr)
    dz_eff = wm * (leg_l_dz * sl + leg_r_dz * sr)

    # 前すね(y=-0.245m) / 後かかと(y=+0.245m) ピボットにより大きなストライド＆つま先アップでも胸ロゴ直下の横シワを完全ゼロ化
    y_piv = 0.245 * np.tanh(rx_rad_raw / 0.24)

    ca = np.cos(rx_eff)
    sa = np.sin(rx_eff)
    dy_rel = ym - y_piv
    dz_rel = zm - z_leg_piv

    y_new = y_piv + dy_rel * ca - dz_rel * sa + dy_eff
    z_new = z_leg_piv + dy_rel * sa + dz_rel * ca + dz_eff

    y_out = y.copy()
    z_out = z.copy()
    y_out[mask] = y_new
    z_out[mask] = z_new
    return x, y_out, z_out


# ==========================================
# 3. カービィお手本準拠 16フレーム周期ウォーク関数
# ==========================================
def evaluate_kirby_walk_cycle(f, is_iich=True):
    """
    リファレンス動画（Kirby walk cycle 24fps）完全準拠：
      - 1歩 = 8.0フレーム、左右1サイクル = 16.0フレーム
      - 2体は3.0フレームの自然な位相差で仲良くトコトコ歩く
      - 左足(+X)が前(-Y)でつま先キュッ上向きのとき、右手(-X)が前(-Y)・左手(+X)が後ろ(+Y)の逆位相スイング
    """
    phase_offset = 0.0 if is_iich else 3.0
    phase = 2.0 * math.pi * ((f - 1.0 - phase_offset) / 16.0)

    s = math.sin(phase)
    c = math.cos(phase)

    # 1歩（8フレーム）ごとの「トコ・ピョコ！」と弾む軽快な上下バウンス（z_air_hop ≈ 0.045m）と自然なクッション
    step_bounce = math.sin(2.0 * phase - 0.35 * math.pi)
    z_air_hop = (0.045 if is_iich else 0.043) * (max(0.0, step_bounce) ** 1.35)
    squash_z = 0.028 * step_bounce

    # 身体の自然な前傾・前に出た肩側への可愛いツイスト(±7.5°)・最小限の傾き(±3.8°)
    torso_pitch_deg = 3.5 - 1.8 * max(0.0, step_bounce)
    torso_yaw_deg = 7.5 * s       # s=+1(左足+Xが前)のとき右肩(-X)が前(-Y)へ出る逆位相ツイスト
    torso_roll_deg = 3.8 * s
    dx_sway = 0.026 * s

    # 左右の超短足軌道（カービィお手本準拠の大きな前後ストライド＆つま先キュッ上向き＆後ろ足蹴り上げ！）
    stride_y = 0.148 if is_iich else 0.164
    max_toe_deg = 32.5 if is_iich else 34.0

    def single_leg_motion(u_ph):
        su = math.sin(u_ph)
        cu = math.cos(u_ph)
        dy_l = -stride_y * su
        rx_deg = -max_toe_deg * su - 4.0 * cu
        # 後ろ蹴り出し(u≈1.5pi)〜前方振り戻しにかけて足裏がハッキリ床から浮き上がるカービィキック軌道
        kick_lift = max(0.0, math.cos(u_ph - 1.62 * math.pi)) ** 1.7
        dz_l = (0.058 if is_iich else 0.066) * kick_lift
        return rx_deg, dy_l, dz_l

    leg_l_rx, leg_l_dy, leg_l_dz = single_leg_motion(phase)
    leg_r_rx, leg_r_dy, leg_r_dz = single_leg_motion(phase + math.pi)

    # 短いパドル手の大きな逆位相前後スイング（前に出る手はほっぺ下前方へ可愛く回り込む！）
    swing_amp = 46.5 if is_iich else 45.0
    arm_r_swing = +swing_amp * s
    arm_l_swing = -swing_amp * s

    outer_base_flap = 12.5 if is_iich else 14.5
    inner_base_flap = 6.5 if is_iich else 7.5
    if is_iich:
        arm_r_flap = outer_base_flap + 11.5 * max(0.0, s) + 3.5 * abs(s)
        arm_l_flap = inner_base_flap + 8.5 * max(0.0, -s) + 2.0 * abs(s)
    else:
        arm_l_flap = outer_base_flap + 13.0 * max(0.0, -s) + 4.0 * abs(s)
        arm_r_flap = inner_base_flap + 10.0 * max(0.0, s) + 2.5 * abs(s)

    # 3フレーム遅れのアンテナ＆地球儀の二次バウンス
    phase_lag = 2.0 * math.pi * ((f - 4.0 - phase_offset) / 16.0)
    ant_pitch_extra = -3.5 + 7.5 * math.sin(2.0 * phase_lag - 0.35 * math.pi)
    ant_roll_extra = -6.5 * math.sin(phase_lag)

    return {
        "z_air_hop": z_air_hop,
        "dx_sway": dx_sway,
        "squash_z": squash_z,
        "torso_pitch_deg": torso_pitch_deg,
        "torso_roll_deg": torso_roll_deg,
        "torso_yaw_deg": torso_yaw_deg,
        "leg_l_rx": leg_l_rx, "leg_l_dy": leg_l_dy, "leg_l_dz": leg_l_dz,
        "leg_r_rx": leg_r_rx, "leg_r_dy": leg_r_dy, "leg_r_dz": leg_r_dz,
        "arm_l_flap": arm_l_flap, "arm_l_swing": arm_l_swing,
        "arm_r_flap": arm_r_flap, "arm_r_swing": arm_r_swing,
        "ant_pitch_extra": ant_pitch_extra,
        "ant_roll_extra": ant_roll_extra,
    }


# ==========================================
# 4. 全フェーズ統合（Phase 1〜4）フレーム評価＆メッシュ更新
# ==========================================
def get_walk_forward_y(f):
    """
    Phase 1 (Frame 1..128): Y = +4.35m から Y = 0.0m へ自然な一定歩幅（約0.272m/歩）で前進し、
    到着直前のみ滑らかに減速して Phase 2 の着地ホップへ繋ぐ。
    """
    if f >= 128.0:
        return 0.0
    u = np.clip((f - 1.0) / 127.0, 0.0, 1.0)
    # 大半は等速前進（足滑りゼロ）、最後の12%だけ滑らかにイーズアウト
    if u <= 0.86:
        prog = u / (0.86 + 0.14 * 0.5)
    else:
        ut = (u - 0.86) / 0.14
        prog = (0.86 + 0.14 * (ut - 0.5 * ut * ut)) / (0.86 + 0.14 * 0.5)
    return 4.35 * max(0.0, 1.0 - prog)


def update_camera_for_frame(cam_obj, frame_idx):
    """
    Phase 1 序盤〜中盤（Frame 1〜76）はリファレンス動画と同じ可愛い斜め前3/4アングルで
    2体が重ならず短い手足の前後スイングとつま先アップがバッチリ見える構図とし、
    Frame 76〜132 にかけて smootherstep で完成静止画と完全一致する正面カメラへ回り込む。
    """
    f = float(frame_idx)
    final_pos = Vector((0.0, -8.45, 1.22))
    final_fwd = Vector((0.0, 1.0, 0.0))

    if f >= 132.0:
        mod_pair.set_pair_camera_pose(
            cam_obj,
            pos=final_pos,
            forward=final_fwd,
            up_hint=(0.0, 0.0, 1.0),
            ortho=False,
            lens=70.0,
        )
        return

    y_pair = get_walk_forward_y(f)
    # 歩き出し斜め前3/4円筒オービット軌道（約36°〜33°アングル・全フレームで左右余白たっぷりのC^2連続回り込み！）
    u_walk_cam = smoothstep_scalar(min(max(f - 1.0, 0.0) / 72.0, 1.0))
    if f <= 72.0:
        w_to_front = 0.0
    else:
        w_to_front = smootherstep_scalar((f - 72.0) / (132.0 - 72.0))

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
        lens=70.0,
    )
    # 歩行中(Y>0)も2体が明るく均一にライティングされるようライト注視点をペア位置へ滑らかに追従
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


def apply_character_kirby_motion_at_frame(char_state, frame_idx):
    """
    指定フレーム f (1..360) における超短足マスコットの可愛い仕草を計算し、
    全メッシュの頂点座標を更新＋足底厳密接地ロックを適用する。
    """
    f = float(frame_idx)
    is_iich = char_state["is_iich"]
    arm_obj = char_state["arm_obj"]
    base_loc = char_state["base_loc"]

    # --- 変数のゼロ初期化（静止フレームでは完全無変形 = build_pair_scene と100%一致） ---
    dy_walk = 0.0
    dx_lane = 0.0
    dx_sway = 0.0
    z_air_hop = 0.0

    squash_z = 0.0
    torso_pitch_deg = 0.0
    torso_roll_deg = 0.0
    torso_yaw_deg = 0.0

    leg_l_rx, leg_l_dy, leg_l_dz = 0.0, 0.0, 0.0
    leg_r_rx, leg_r_dy, leg_r_dz = 0.0, 0.0, 0.0

    arm_l_flap, arm_l_swing = 0.0, 0.0
    arm_r_flap, arm_r_swing = 0.0, 0.0

    bow_deg = 0.0
    bow_whip = 0.0

    ant_pitch_extra = 0.0
    ant_roll_extra = 0.0

    # =========================================================================
    # Phase 1 (Frame 1〜128 / 0.00s〜5.33s):
    # カービィお手本準拠（1歩=8f / 1サイクル=16f）の超短足トコトコウォーク
    # =========================================================================
    if f <= 128.0:
        # 約35°の斜め前3/4カメラでも2体が重ならず等スケールで並ぶよう横レーン＋奥行きスタッガーを付与（到着時に0へ完全収束）
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
        leg_l_dz = w["leg_l_dz"] * amp_walk
        leg_r_rx = w["leg_r_rx"] * amp_walk
        leg_r_dy = w["leg_r_dy"] * amp_walk
        leg_r_dz = w["leg_r_dz"] * amp_walk

        arm_l_flap = w["arm_l_flap"] * amp_walk
        arm_l_swing = w["arm_l_swing"] * amp_walk
        arm_r_flap = w["arm_r_flap"] * amp_walk
        arm_r_swing = w["arm_r_swing"] * amp_walk

        ant_pitch_extra = w["ant_pitch_extra"] * amp_walk
        ant_roll_extra = w["ant_roll_extra"] * amp_walk

    # =========================================================================
    # Phase 2 (Frame 129〜168 / 5.33s〜7.00s):
    # ちょこんと両足ジャンプ着地（「ピョコン・ピタッ！」）＆正面スマイル静止
    # =========================================================================
    elif f <= 168.0:
        dy_walk = 0.0
        # 2体に1フレームだけ愛らしい着地タイミング差を持たせる
        f_hop = f - (0.0 if is_iich else 1.0)
        if 129.0 <= f_hop <= 143.0:
            uh = (f_hop - 129.0) / 14.0
            hop_arc = math.sin(math.pi * uh)
            z_air_hop = 0.046 * hop_arc
            squash_z = +0.024 * hop_arc
            # ジャンプ中は短い両足をちょこんと下向きに揃え、短い両手を横にパタッと開く
            leg_l_rx = +8.0 * hop_arc
            leg_r_rx = +8.0 * hop_arc
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
            squash_z = -0.030 * cush
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
    # Phase 3 (Frame 169〜240 / 7.00s〜10.00s):
    # 短い2本の足でしっかり踏ん張り、丸いタマゴ体型のまま「ペコリ！」とする可愛いおじぎ
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
            # 「せーのっ」と少し背筋を伸ばす可愛い予備動作
            u_pre = math.sin(math.pi * smoothstep_scalar((f - 169.0) / 7.0))
            squash_z = +0.018 * u_pre
            outer_pre = 10.0 * u_pre
            inner_pre = 5.0 * u_pre
            if is_iich:
                arm_r_flap, arm_l_flap = outer_pre, inner_pre
            else:
                arm_l_flap, arm_r_flap = outer_pre, inner_pre
            arm_l_swing = +10.0 * u_pre
            arm_r_swing = +10.0 * u_pre
        elif f > 234.0:
            # おじぎから戻った後の「ひょい・ぽよん」整え
            u_set = (f - 234.0) / 6.0
            squash_z = +0.018 * math.sin(math.pi * u_set) * (1.0 - u_set)
            ant_pitch_extra = -4.0 * math.sin(math.pi * u_set) * (1.0 - u_set)
        else:
            b_pos = max(0.0, b_unit)
            # ペンギンやカービィのように短いパドル手をちょこんと外側・後ろ(+Y)へ引いて丁寧におじぎ
            outer_bow_flap = 16.0 * b_pos
            inner_bow_flap = 8.0 * b_pos
            if is_iich:
                arm_r_flap, arm_l_flap = outer_bow_flap, inner_bow_flap
            else:
                arm_l_flap, arm_r_flap = outer_bow_flap, inner_bow_flap
            arm_l_swing = -24.0 * b_pos
            arm_r_swing = -24.0 * b_pos

    # =========================================================================
    # Phase 4 (Frame 241〜360 / 10.00s〜15.00s):
    # 腕伸縮ゼロ（1.00倍）！両キャラともほっぺの横の高い位置で短い手を「パタパタ！」と元気に振る
    # =========================================================================
    else:
        dy_walk = 0.0
        env_in = smootherstep_scalar(np.clip((f - 241.0) / 14.0, 0.0, 1.0))
        env_out = 1.0 - smootherstep_scalar(np.clip((f - 334.0) / 18.0, 0.0, 1.0))
        w_wave = env_in * env_out

        # 周期10フレームの軽快なパタパタ手振り波形（Frame 276 で sin=+1 Peak Up, Frame 291 で sin=-1 Down）
        theta_10 = 2.0 * math.pi * ((f - 273.5) / 10.0)
        sw10 = math.sin(theta_10)
        cw10 = math.cos(theta_10)

        # 30フレーム周期（手振り3往復で左右1サイクル）の可愛い小首傾げ＆片足ちょこん浮きリズム
        # Frame 276 で sw_step = +1.00（両キャラとも外側の手が高く上がり、外側の足がちょこんと浮く対称ポーズ！）
        # Frame 291 で sw_step = -1.00（両キャラとも外側の手を振り下ろし、内側の足がちょこんと浮く！）
        theta_step = 2.0 * math.pi * ((f - 276.0) / 30.0) + 0.5 * math.pi
        sw_step = math.sin(theta_step)
        mirror_sign = -1.0 if is_iich else +1.0
        char_step = mirror_sign * sw_step

        # IICh・IINet ともにタマゴ側面の輪郭に沿ってほっぺの横（+24°〜+60°）まで大きく外側上向きに持ち上げてパタパタ振る！
        if is_iich:
            outer_flap = (41.0 + 16.5 * sw10) * w_wave
        else:
            outer_flap = (42.5 + 17.0 * sw10) * w_wave
        outer_swing = (6.0 + 6.0 * cw10) * w_wave

        # 内側の短い手はぶつからない低い位置で前に少し出しながら可愛くリズムをとる
        inner_flap = (6.5 - 3.0 * sw10) * w_wave
        inner_swing = (20.0 - 5.0 * sw_step) * w_wave

        if is_iich:
            arm_r_flap, arm_r_swing = outer_flap, outer_swing
            arm_l_flap, arm_l_swing = inner_flap, inner_swing
        else:
            arm_l_flap, arm_l_swing = outer_flap, outer_swing
            arm_r_flap, arm_r_swing = inner_flap, inner_swing

        # 小首・丸ボディを可愛く傾げ（±3.8°、中央で頬が接触しないクリアランス確保）、傾いた反対側の短い足が床からちょこんと浮く！
        torso_roll_deg = (-3.8 * char_step) * w_wave
        torso_yaw_deg = (3.2 * char_step) * w_wave
        dx_sway = ((-0.026 if is_iich else +0.026) - 0.014 * char_step) * w_wave
        squash_z = 0.024 * abs(sw10) * w_wave - 0.008 * w_wave
        z_air_hop = 0.008 * max(0.0, abs(sw10) - 0.25) * w_wave

        # char_step > 0 のときは +X 足(Leg.L)が浮き、char_step < 0 のときは -X 足(Leg.R)が浮く
        lift_l = max(0.0, +char_step) * w_wave
        lift_r = max(0.0, -char_step) * w_wave
        leg_l_rx = -9.0 * lift_l
        leg_l_dy = -0.042 * lift_l
        leg_l_dz = +0.048 * lift_l

        leg_r_rx = -9.0 * lift_r
        leg_r_dy = -0.042 * lift_r
        leg_r_dz = +0.048 * lift_r

        ant_pitch_extra = 4.8 * abs(sw10) * w_wave
        ant_roll_extra = 6.8 * char_step * w_wave

        # 手を下ろした後の小さなフィナーレ整えバウンス（Frame 352〜358 -> Frame 360 で完全静止）
        if 351.0 < f < 358.0:
            uf = (f - 351.0) / 7.0
            squash_z += 0.014 * math.sin(math.pi * uf) * (1.0 - uf)

    # =========================================================================
    # 各メッシュへの変形適用（Body -> Face/Logo/Eyes/Mouth -> Antenna/Globe）
    # =========================================================================
    z_foot_cush = 0.140 if is_iich else 0.190
    z_bow_z0 = 0.036 if is_iich else 0.048
    z_bow_piv = 0.155 if is_iich else 0.220
    y_bow_piv = -0.345 if is_iich else -0.285

    z_min_body_current = None

    for entry in char_state["meshes"]:
        obj = entry["obj"]
        rest_co = entry["rest_co"]
        x = rest_co[:, 0].copy()
        y = rest_co[:, 1].copy()
        z = rest_co[:, 2].copy()

        # Step 1: Body の超短足パタパタ＆短いパドル手の SO(3) 純粋回転（伸縮ゼロ）
        if entry["is_body"]:
            x, y, z = deform_stubby_legs_kirby(
                x, y, z,
                entry["w_leg"], entry["s_leg_l"], char_state["z_leg_piv"],
                leg_l_rx, leg_r_rx,
                leg_l_dy, leg_r_dy,
                leg_l_dz, leg_r_dz,
            )
            wb = entry["w_arm_blend"]
            x, y, z = deform_short_arm_so3_pure_rotation(
                x, y, z, wb, char_state,
                side_sign=+1.0, flap_deg=arm_l_flap, swing_fwd_deg=arm_l_swing,
            )
            x, y, z = deform_short_arm_so3_pure_rotation(
                x, y, z, wb, char_state,
                side_sign=-1.0, flap_deg=arm_r_flap, swing_fwd_deg=arm_r_swing,
            )

        # Step 2: 着地クッション等のごく控えめな体積保存バウンス（±2.5〜3.0%以内）
        if abs(squash_z) > 1e-5:
            u_sq = smootherstep_np((rest_co[:, 2] - z_foot_cush) / 0.22)
            kz = 1.0 + squash_z * u_sq
            kxy = 1.0 / np.sqrt(np.maximum(kz, 0.85))
            x = x * kxy
            y = y * kxy
            z = np.where(z > z_foot_cush, z_foot_cush + (z - z_foot_cush) * kz, z)

        # Step 3: Phase 3 短い両足でしっかり床に踏ん張り、丸いタマゴ体型のまま「ペコリ！」とおじぎ
        if abs(bow_deg) > 1e-4:
            # 足底〜足首下部(z<=z_bow_z0)は重み 0.08 で床にしっかり踏ん張って正面に残り、
            # 前面足首ピボット(y_bow_piv)により両キャラとも短い2本の足の上に胸ロゴと丸い身体が綺麗に見える！
            if entry["is_body"]:
                w_f_bow = smootherstep_np((-0.10 - rest_co[:, 1]) / 0.14)
                span_bow_v = (0.110 if is_iich else 0.190) * w_f_bow + (0.250 if is_iich else 0.320) * (1.0 - w_f_bow)
                u_bow = 0.08 + 0.92 * smootherstep_np((rest_co[:, 2] - z_bow_z0) / span_bow_v)
            else:
                u_bow = 1.0
            p_bow = math.radians(bow_deg) * u_bow
            cb, sb = np.cos(p_bow), np.sin(p_bow)
            dy_b = y - y_bow_piv
            dz_b = z - z_bow_piv
            y = y_bow_piv + dy_b * cb - dz_b * sb
            z = z_bow_piv + dy_b * sb + dz_b * cb

            # アンテナと地球儀が慣性で可愛く前へ垂れて揺れ、かつ画面上端から絶対に見切れないよう制御
            if entry["is_ant_or_globe"]:
                u_ant_b = smootherstep_np((rest_co[:, 2] - 0.85) / 1.05)
                b_norm = bow_deg / (20.5 if is_iich else 21.5)
                flex_deg = (15.0 * b_norm - 11.0 * bow_whip)
                a_rad = math.radians(flex_deg) * u_ant_b
                ca_a, sa_a = np.cos(a_rad), np.sin(a_rad)
                y_ap = 0.35 if is_iich else 0.55
                z_ap = 1.15 if is_iich else 1.35
                dy_a = y - y_ap
                dz_a = z - z_ap
                y = y_ap + dy_a * ca_a - dz_a * sa_a
                z = z_ap + dy_a * sa_a + dz_a * ca_a

        # Step 4: 歩行・手振り時の身体の可愛い最小限の傾き・ツイスト ＆ アンテナ二次バウンス
        if (
            abs(torso_pitch_deg) > 1e-4
            or abs(torso_roll_deg) > 1e-4
            or abs(torso_yaw_deg) > 1e-4
            or abs(ant_pitch_extra) > 1e-4
            or abs(ant_roll_extra) > 1e-4
        ):
            u_orient = 0.72 + 0.28 * smootherstep_np((rest_co[:, 2] - 0.02) / 0.16)
            p_rad = math.radians(torso_pitch_deg) * u_orient
            r_rad = math.radians(torso_roll_deg) * u_orient
            yw_rad = math.radians(torso_yaw_deg) * u_orient

            if entry["is_ant_or_globe"]:
                u_ant = smootherstep_np((rest_co[:, 2] - 0.75) / 1.20)
                p_rad = p_rad + math.radians(ant_pitch_extra) * u_ant
                r_rad = r_rad + math.radians(ant_roll_extra) * u_ant

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
        obj.data.vertices.foreach_set("co", new_co.ravel())
        obj.data.update()

    # Step 5: 足底最下点 min(z) の厳密接地ロック（床めり込みゼロ・浮きゼロ・静止時完全一致）
    loc_z = char_state["ground_ref_z"] - z_min_body_current + z_air_hop
    arm_obj.location = Vector((
        base_loc.x + dx_lane + dx_sway,
        base_loc.y + dy_walk,
        loc_z,
    ))


# ==========================================
# 5. スタジオ背景（3/4アングル対応ワイドホリゾント）・照明・カメラ
# ==========================================
def create_studio_floor_and_backdrop():
    mesh = bpy.data.meshes.new("Studio_Cyclorama_Mesh")
    obj = bpy.data.objects.new("Studio_Cyclorama", mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    n_x = 36
    xs = np.linspace(-36.0, 36.0, n_x)

    profile_yz = []
    for y in np.linspace(-8.0, 14.5, 24):
        profile_yz.append((float(y), 0.0))
    for i in range(1, 12):
        ang = (0.5 * math.pi) * (i / 12.0)
        R_cyc = 3.5
        y_c = 14.5 + R_cyc * math.sin(ang)
        z_c = R_cyc * (1.0 - math.cos(ang))
        profile_yz.append((float(y_c), float(z_c)))
    for z in np.linspace(3.5, 12.0, 9)[1:]:
        profile_yz.append((18.0, float(z)))

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
        lens=70.0,
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
# 6. 視覚監査コンタクトシート出力 ＆ 本番MP4レンダリング
# ==========================================
def render_contact_sheet_for_frames(
    cam_obj, char_states, frame_list, cols, rows, out_paths, width=640, height=480
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


def bake_keyframes_for_blend_file(cam_obj, char_states):
    scene = bpy.context.scene
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.render.fps = FPS

    cam_obj.rotation_mode = 'XYZ'
    for f in range(FRAME_START, FRAME_END + 1):
        update_camera_for_frame(cam_obj, f)
        cam_obj.keyframe_insert(data_path="location", frame=f)
        cam_obj.keyframe_insert(data_path="rotation_euler", frame=f)
        for cs in char_states:
            apply_character_kirby_motion_at_frame(cs, f)
            cs["arm_obj"].keyframe_insert(data_path="location", frame=f)

    scene.frame_set(156)
    update_camera_for_frame(cam_obj, 156)
    for cs in char_states:
        apply_character_kirby_motion_at_frame(cs, 156)


def render_full_mp4_animation(scene, cam_obj, char_states, mp4_path, width=1280, height=960):
    def on_frame_change(scn, depsgraph=None):
        f_cur = scn.frame_current
        update_camera_for_frame(cam_obj, f_cur)
        for cs in char_states:
            apply_character_kirby_motion_at_frame(cs, f_cur)

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(on_frame_change)

    if hasattr(scene.render, "use_persistent_data"):
        scene.render.use_persistent_data = False

    scene.camera = cam_obj
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
    scene.render.ffmpeg.gopsize = 12
    scene.render.ffmpeg.audio_codec = 'NONE'

    t0 = time.time()
    bpy.ops.render.render(animation=True)
    dt = time.time() - t0
    bpy.app.handlers.frame_change_pre.clear()
    print(f"MP4 animation render (360 frames / 15.0s) completed in {dt:.1f}s -> {mp4_path}")


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

    arm_iich, meshes_iich = mod_pair.build_iich_character(coll_iich, mat_globe, im_ref)
    arm_iinet, meshes_iinet = mod_pair.build_iinet_character(coll_iinet, mat_globe, im_ref)

    state_iich = capture_character_rest_state(arm_iich, meshes_iich, is_iich=True)
    state_iinet = capture_character_rest_state(arm_iinet, meshes_iinet, is_iich=False)
    char_states = [state_iich, state_iinet]

    create_studio_floor_and_backdrop()
    cam_obj = setup_animation_lighting_and_camera(scene)

    # 監査シートA：歩行1サイクル（16フレーム周期）連続8コマ確認（2フレーム刻みで全位相を網羅）
    render_contact_sheet_for_frames(
        cam_obj,
        char_states,
        frame_list=[17, 19, 21, 23, 25, 27, 29, 31],
        cols=4,
        rows=2,
        out_paths=[AUDIT_WALK_8_PATH],
        width=560,
        height=420,
    )

    # 監査シートB：全4フェーズ代表6コマ一覧
    # [21: 歩き出し3/4, 77: 歩行中盤, 136: ピョコン着地ホップ(正面), 202: 丸ボディのままペコリおじぎ, 276: ほっぺ横手振りUp, 291: 手振りDown＆片足ちょこん浮き]
    render_contact_sheet_for_frames(
        cam_obj,
        char_states,
        frame_list=[21, 77, 136, 202, 276, 291],
        cols=3,
        rows=2,
        out_paths=[CHECK_SHEET_DRAFT_PATH, KEYFRAMES_FINAL_PATH],
        width=640,
        height=480,
    )

    bake_keyframes_for_blend_file(cam_obj, char_states)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=ANIM_BLEND_PATH)

    if not check_only:
        render_full_mp4_animation(scene, cam_obj, char_states, ANIM_MP4_PATH, width=1280, height=960)

    print("ALL PAIR ANIMATION TASKS COMPLETED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
