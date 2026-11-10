# -*- coding: utf-8 -*-
"""
CVN公式マスコットキャラクター「いい-ch（LILI-ch）＆ いい-NETくん（LILI-net）」
2体ペア3Dアニメーション動画（15.0秒 / 360フレーム @ 24fps）
【全身3Dラバー（ゴム弾性）変形エンジン搭載版】
  Phase 1 (Frame 1〜132 / 0.0s〜5.5s):
    間（ま）をおいて「ムニュッ（ゴム足着地タメ）➔ ぴょこっ！（ゴム足ストレッチ＆ホップ）」と
    2体仲良く左右に体を傾けながら（±12°）歩いてくる愛らしいラバーウォーク
  Phase 2 (Frame 133〜168 / 5.5s〜7.0s):
    到着してゴム弾性スクワッシュ＆ポヨン復帰で正面静止構図にピタッと収まる
  Phase 3 (Frame 169〜240 / 7.0s〜10.0s):
    顔から下がゴムのようにクニュッと内側にへこんで折れ曲がる深いおじぎ
  Phase 4 (Frame 241〜360 / 10.0s〜15.0s):
    腕が丸みを保ったままゴムのようにビヨーンと伸びて、大きく元気よくブンブン手を振る

Usage:
  1) キーフレーム6枚コンタクトシート高速監査モード:
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
from mathutils import Vector, Matrix, Euler

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import build_iinet_kun as mod_iinet
import build_pair_scene as mod_pair

DEPT_DIR = os.path.dirname(SCRIPT_DIR)
FINAL_DIR = os.path.join(DEPT_DIR, "final_outputs")
os.makedirs(FINAL_DIR, exist_ok=True)

CHECK_SHEET_DRAFT_PATH = os.path.join(SCRIPT_DIR, "anim_keyframes_check.png")
KEYFRAMES_FINAL_PATH = os.path.join(FINAL_DIR, "pair_iich_and_iinet_anim_keyframes.png")
ANIM_BLEND_PATH = os.path.join(FINAL_DIR, "cvn_iich_and_iinet_pair_anim.blend")
ANIM_MP4_PATH = os.path.join(FINAL_DIR, "pair_iich_and_iinet_run_bow_wave.mp4")

FPS = 24
FRAME_START = 1
FRAME_END = 360


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


def capture_character_rest_state(arm_obj, meshes, is_iich=True):
    """
    各キャラクターの全メッシュの初期頂点座標（Rest Coords）と、
    直交Frenet座標系によるゴム腕伸縮・ゴム足スクワッシュ＆ストレッチ・腹部クニュ折り変形に必要な
    頂点メタデータを事前計算してキャッシュする。
    """
    body_obj = next(m for m in meshes if m.name.endswith("_Body"))
    n_body = len(body_obj.data.vertices)
    body_co = np.empty(n_body * 3, dtype=np.float64)
    body_obj.data.vertices.foreach_get("co", body_co)
    body_co = body_co.reshape(-1, 3)

    if is_iich:
        sx, sy, sz = 0.8473, 0.8350, 0.8262
        z_arm_min = 0.245 * sz
        z_armpit = 0.315 * sz
        z_arm_peak = 0.320 * sz
        z_arm_max = 0.555 * sz
        x_peak = 1.048 * sx
        z_leg_top = 0.205
        x_sh = 0.575
        z_sh = 0.355
        phi_rest = math.radians(-24.0)
        l_arm_max = 0.325
    else:
        z_arm_min = 0.2820
        z_armpit = 0.3460
        z_arm_peak = 0.3727
        z_arm_max = 0.6680
        x_peak = 0.9823
        z_leg_top = 0.255
        x_sh = 0.665
        z_sh = 0.485
        phi_rest = math.radians(-28.0)
        l_arm_max = 0.345

    # 腕を除いた胴体本来の外周プロファイル x_body(z) を背面・前面の中央断面(|y| > 0.16m)から正確に推定
    z_grid = np.linspace(0.0, 2.2, 220)
    x_body_grid = np.zeros_like(z_grid)
    for idx, zg in enumerate(z_grid):
        mask = (np.abs(body_co[:, 2] - zg) < 0.035) & (np.abs(body_co[:, 1]) > 0.165)
        if np.any(mask):
            x_body_grid[idx] = np.max(np.abs(body_co[mask, 0]))
        else:
            mask2 = np.abs(body_co[:, 2] - zg) < 0.045
            x_body_grid[idx] = np.max(np.abs(body_co[mask2, 0])) if np.any(mask2) else 0.60
    k_sm = np.array([0.15, 0.25, 0.20, 0.25, 0.15])
    x_body_grid = np.convolve(np.pad(x_body_grid, 2, mode='edge'), k_sm, mode='valid')

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
            xb = np.interp(vz, z_grid, x_body_grid)

            # 腕付け根からの突出量 d_out と滑らかな接合ブレンド重み w_arm_blend
            # パドル全体(上縁・先端・下縁)が丸みを保って一体で伸びるよう、胴体表面内側(-0.042m)から0.032m幅で1.0へ立ち上げる
            d_out = ax - (xb - 0.042)
            wz_low = smoothstep_np((vz - (z_arm_min - 0.020)) / 0.025)
            wz_high = 1.0 - smoothstep_np((vz - (z_arm_max + 0.005)) / 0.030)
            wy_arm = 1.0 - smoothstep_np((np.abs(vy - 0.035) - 0.155) / 0.045)
            w_arm_blend = smoothstep_np(d_out / 0.032) * wz_low * wz_high * wy_arm

            # 脚・足元ラバー領域マスク: 足底(Z=0)〜脚付け根(z_leg_top)
            u_leg_z = smoothstep_np((z_leg_top - vz) / (z_leg_top - 0.005))
            u_leg_x = smoothstep_np((ax - 0.040) / 0.095) * (1.0 - smoothstep_np((ax - 0.46) / 0.10))
            w_leg = u_leg_z * u_leg_x
        else:
            w_arm_blend = None
            w_leg = None
            xb = None

        mesh_entries.append({
            "obj": obj,
            "rest_co": co,
            "is_body": is_body,
            "is_ant_or_globe": is_ant_or_globe,
            "w_arm_blend": w_arm_blend,
            "w_leg": w_leg,
            "xb": xb,
        })

    return {
        "arm_obj": arm_obj,
        "is_iich": is_iich,
        "meshes": mesh_entries,
        "z_arm_min": z_arm_min,
        "z_armpit": z_armpit,
        "z_arm_peak": z_arm_peak,
        "z_arm_max": z_arm_max,
        "x_sh": x_sh,
        "z_sh": z_sh,
        "phi_rest": phi_rest,
        "l_arm_max": l_arm_max,
        "z_leg_top": z_leg_top,
    }


def deform_rubber_legs_and_feet(
    x, y, z, w_leg, z_leg_top, is_iich,
    leg_l_rx, leg_r_rx,
    leg_l_stretch, leg_r_stretch,
    leg_l_lift_z, leg_r_lift_z,
):
    """
    左右の足元（Leg.L: x>=0, Leg.R: x<0）に対して、ゴム弾性の柔軟な伸縮・スクワッシュ・スイング変形を適用する。
    """
    mask = w_leg > 1e-4
    if not np.any(mask):
        return x, y, z

    xm = x[mask]
    ym = y[mask]
    zm = z[mask]
    wm = w_leg[mask]

    is_left = xm >= 0.0
    x_foot_center = np.where(is_left, +(0.222 if is_iich else 0.238), -(0.222 if is_iich else 0.238))

    stretch_val = np.where(is_left, leg_l_stretch, leg_r_stretch) * wm
    lift_z_val = np.where(is_left, leg_l_lift_z, leg_r_lift_z) * wm
    ang_rx = np.where(is_left, leg_l_rx, leg_r_rx) * wm

    kz = np.clip(1.0 + stretch_val, 0.65, 1.45)
    kxy = 1.0 / np.sqrt(kz)

    z_stretched = z_leg_top - (z_leg_top - zm) * kz + lift_z_val
    x_bulged = x_foot_center + (xm - x_foot_center) * kxy
    y_bulged = ym * kxy

    u_tip = np.clip((z_leg_top - zm) / z_leg_top, 0.0, 1.0)
    ang_eff = ang_rx * (0.65 * u_tip + 0.35 * (u_tip ** 1.8))
    ca, sa = np.cos(ang_eff), np.sin(ang_eff)
    dy_l = y_bulged
    dz_l = z_stretched - z_leg_top
    y_new = dy_l * ca - dz_l * sa
    z_new = z_leg_top + dy_l * sa + dz_l * ca

    x_out = x.copy()
    y_out = y.copy()
    z_out = z.copy()
    x_out[mask] = x_bulged
    y_out[mask] = y_new
    z_out[mask] = z_new
    return x_out, y_out, z_out


def deform_rubber_arm_frenet(
    x, y, z, w_arm_blend, char_state,
    side_sign, delta_angle_deg, stretch_ratio, whip_deg, forward_bias=0.0
):
    """
    直交Frenet座標系 (ell, tau) に基づくゴム腕の伸縮・大振り・しなり変形。
      - 腕パドルの断面直交座標 (ell: 腕軸方向距離, tau: 腕軸に垂直な厚み座標) で伸縮と曲線曲げを行うため、
        腕を1.8倍〜2.0倍にビヨーンと伸ばして大きく上下に振っても、先端の丸いパドル形状が一切尖らず
        ぷっくり可愛い丸みを100%保ったままゴムのようにしなやかに伸びて振れる！
    """
    mask = (w_arm_blend > 1e-4) & ((x * side_sign) > 0.0)
    if not np.any(mask):
        return x, y, z

    xm = x[mask]
    ym = y[mask]
    zm = z[mask]
    wb = w_arm_blend[mask]

    ax = np.abs(xm)
    x_sh = char_state["x_sh"]
    z_sh = char_state["z_sh"]
    phi0 = char_state["phi_rest"]  # 約 -25° (斜め下向き初期軸)
    l_max = char_state["l_arm_max"]

    c0, s0 = math.cos(phi0), math.sin(phi0)
    dx = ax - x_sh
    dz = zm - z_sh

    # Rest状態の腕軸に沿う距離 ell と、腕軸に直交する厚みオフセット tau
    ell = np.maximum(dx * c0 + dz * s0, 0.0)
    tau = -dx * s0 + dz * c0
    u_axial = np.clip(ell / l_max, 0.0, 1.0)

    # 1) ゴム腕の軸方向ストレッチ:
    #    中間シャフト(u_axial <= 0.72)をゴムのようにビヨーンと伸ばし、先端キャップ(u_axial > 0.72)は等長並進＋ぷっくり膨張させることで、
    #    伸ばしたときも先端が絶対に尖らず、ぷっくり丸い可愛いゴムの手先を100%維持する！
    s_shaft = smoothstep_np(np.clip(u_axial / 0.72, 0.0, 1.0))
    extra_len = (stretch_ratio - 1.0) * (0.22 if char_state["is_iich"] else 0.23) * s_shaft
    ell_stretched = ell + extra_len
    tau_puffed = tau * (1.0 + 0.24 * max(stretch_ratio - 1.0, 0.0) * smoothstep_np(np.clip(u_axial / 0.65, 0.0, 1.0)))

    # 2) 腕軸の回転角 phi_new(u):
    #    初期角度 phi0 (-25°) から delta_angle_deg だけ上方向へ持ち上げ、先端にしなり whip_deg を付与
    d_phi = math.radians(delta_angle_deg) * smoothstep_np(np.clip(u_axial / 0.38, 0.0, 1.0)) + math.radians(whip_deg) * (u_axial ** 1.4)
    phi_new = phi0 + d_phi

    cn = np.cos(phi_new)
    sn = np.sin(phi_new)

    # 3) 上向きに持ち上げた際、脇下が折れずに外側・上側へふっくら張り出すクリアランス補正
    lift_pos = max(0.0, delta_angle_deg / 65.0)
    dx_clear = (0.035 if char_state["is_iich"] else 0.040) * lift_pos * s_shaft
    dz_clear = (0.045 if char_state["is_iich"] else 0.055) * lift_pos * s_shaft

    ax_target = x_sh + ell_stretched * cn - tau_puffed * sn + dx_clear
    z_target = z_sh + ell_stretched * sn + tau_puffed * cn + dz_clear

    x_new = xm + side_sign * (ax_target - ax) * wb
    z_new = zm + (z_target - zm) * wb
    y_new = ym + forward_bias * s_shaft * wb

    x_out = x.copy()
    y_out = y.copy()
    z_out = z.copy()
    x_out[mask] = x_new
    y_out[mask] = y_new
    z_out[mask] = z_new
    return x_out, y_out, z_out


def evaluate_paused_pyoko_walk(f, is_iich=True):
    """
    【オーナー指示対応】
    細かすぎる小走りではなく、もう少し「間（ま）」をおいて、
    「ムニュッ（着地してゴムの足が潰れるタメ）➔ ぴょこっ！（ゴムの足がビヨッと伸びて左右へ体を傾けながらホップ）」と
    2体が仲良く揃ったリズムで左右に傾きながら歩いてくるラバーウォーク波形を生成する。
      - 1歩 = 14.0フレーム（左右1サイクル = 28.0フレーム、5.5秒間で約9.4歩）
      - 2体がぶつからないよう同位相（ほんの2フレーム差）で左右へ仲良く傾く
    """
    step_frames = 14.0
    # 2体が互いにぶつからないよう同じ方向へ仲良く傾きつつ、1.8フレームだけ自然なタイミング差をつける
    f_eff = f - (0.0 if is_iich else 1.8)
    s_total = max(0.0, f_eff - 1.0) / step_frames

    step_idx = int(math.floor(s_total))
    u = s_total - step_idx  # 0.0 .. 1.0 within current single step
    stance_sign = 1.0 if (step_idx % 2 == 0) else -1.0

    # 1) 上下ホップ (dz_hop) と 胴体スクワッシュ (squash_z):
    #    u in [0.00..0.38]: 着地してゴムの足と胴体がムニュッと沈み込む「間（タメ）」
    #    u in [0.38..1.00]: ゴムの反発で「ぴょこっ！」と上へ跳ねて次の足へ移る
    if u < 0.38:
        ut = u / 0.38
        pause_curve = math.sin(math.pi * ut)
        dz_hop = -0.020 * pause_curve
        squash_z = -0.070 * pause_curve
        hop_arc = 0.0
    else:
        uh = (u - 0.38) / 0.62
        hop_arc = math.sin(math.pi * uh) ** 0.85
        dz_hop = (0.092 if is_iich else 0.088) * hop_arc
        squash_z = +0.062 * math.sin(math.pi * uh)

    # 2) 左右の大きな傾き（ロール角 ±11.5°）と横スウェイ:
    #    着地している足側へグイッと体を傾け、「間」を置いてから反対側へぴょこっと移る
    raw_cycle_sin = math.sin(math.pi * s_total)
    paused_tilt = math.copysign(abs(raw_cycle_sin) ** 0.65, raw_cycle_sin)
    torso_roll_deg = (11.8 if is_iich else 11.2) * paused_tilt
    dx_sway = 0.055 * paused_tilt
    torso_yaw_deg = 5.5 * math.cos(math.pi * s_total)
    torso_pitch_deg = 4.0 - 3.0 * hop_arc

    # 3) ゴム弾性の柔軟な足元の動き（スタンス足の着地スクワッシュ➔キックストレッチ ＆ スイング足の前方リフト）
    if u < 0.38:
        u_sq = math.sin(math.pi * (u / 0.38))
        stance_stretch = -0.24 * u_sq
        stance_lift_z = 0.0
        stance_rx = math.radians(-10.0 * (1.0 - u / 0.38))

        swing_stretch = +0.12 * u_sq
        swing_lift_z = 0.028 * u_sq
        swing_rx = math.radians(+16.0 * (1.0 - 2.0 * (u / 0.38)))
    else:
        uh = (u - 0.38) / 0.62
        kick_env = math.sin(math.pi * uh)
        stance_stretch = +0.28 * kick_env
        stance_lift_z = 0.015 * kick_env
        stance_rx = math.radians(+26.0 * kick_env)

        swing_stretch = +0.22 * kick_env
        swing_lift_z = 0.055 * kick_env
        swing_rx = math.radians(-26.0 * math.sin(0.5 * math.pi * uh))

    if stance_sign > 0.0:
        leg_l_stretch, leg_l_lift_z, leg_l_rx = stance_stretch, stance_lift_z, stance_rx
        leg_r_stretch, leg_r_lift_z, leg_r_rx = swing_stretch, swing_lift_z, swing_rx
    else:
        leg_r_stretch, leg_r_lift_z, leg_r_rx = stance_stretch, stance_lift_z, stance_rx
        leg_l_stretch, leg_l_lift_z, leg_l_rx = swing_stretch, swing_lift_z, swing_rx

    return (
        dz_hop, dx_sway, squash_z,
        torso_pitch_deg, torso_roll_deg, torso_yaw_deg,
        leg_l_rx, leg_r_rx,
        leg_l_stretch, leg_r_stretch,
        leg_l_lift_z, leg_r_lift_z,
        paused_tilt, hop_arc,
    )


def apply_character_rubber_deformation_at_frame(char_state, frame_idx):
    """
    指定フレーム f (1..360) におけるキャラクター全体の3Dラバー（ゴム弾性）変形を計算し、
    全メッシュの頂点座標と法線をリアルタイム更新する。
    """
    f = float(frame_idx)
    is_iich = char_state["is_iich"]
    arm_obj = char_state["arm_obj"]

    base_loc = Vector((-0.946, -0.025, 0.0036)) if is_iich else Vector((+0.881, +0.025, 0.0000))

    # --- 初期化 ---
    dy_run = 0.0
    dz_hop = 0.0
    dx_sway = 0.0

    torso_pitch_deg = 0.0
    torso_roll_deg = 0.0
    torso_yaw_deg = 0.0
    squash_z = 0.0

    leg_l_rx, leg_r_rx = 0.0, 0.0
    leg_l_stretch, leg_r_stretch = 0.0, 0.0
    leg_l_lift_z, leg_r_lift_z = 0.0, 0.0

    arm_l_angle, arm_l_stretch, arm_l_whip, arm_l_fwd = 0.0, 1.0, 0.0, 0.0
    arm_r_angle, arm_r_stretch, arm_r_whip, arm_r_fwd = 0.0, 1.0, 0.0, 0.0

    bow_amount = 0.0
    bow_whip = 0.0

    ant_pitch_extra_deg = 0.0
    ant_roll_extra_deg = 0.0

    # =========================================================================
    # Phase 1 (Frame 1〜132 / 0.0s〜5.5s):
    # 間（ま）をおいて、ぴょこぴょこ左右に体を傾けながら歩く＋ゴム弾性の柔軟な足元の動き
    # =========================================================================
    if f <= 132.0:
        u_run = (f - 1.0) / 131.0
        step_s = (f - 1.0) / 14.0
        step_pause_mod = -0.012 * math.sin(2.0 * math.pi * step_s) * (1.0 - u_run)
        ease_pos = np.clip(1.0 - ((1.0 - u_run) ** 1.55) + step_pause_mod, 0.0, 1.0)
        dy_run = 11.50 * (1.0 - ease_pos)

        amp_walk = 1.0 if f <= 114.0 else (1.0 - 0.55 * smoothstep_scalar((f - 114.0) / 18.0))

        (
            w_dz_hop, w_dx_sway, w_squash_z,
            w_pitch, w_roll, w_yaw,
            w_leg_l_rx, w_leg_r_rx,
            w_leg_l_str, w_leg_r_str,
            w_leg_l_lz, w_leg_r_lz,
            paused_tilt, hop_arc,
        ) = evaluate_paused_pyoko_walk(f, is_iich=is_iich)

        dz_hop = w_dz_hop * amp_walk
        dx_sway = w_dx_sway * amp_walk
        squash_z = w_squash_z * amp_walk
        torso_pitch_deg = w_pitch * amp_walk
        torso_roll_deg = w_roll * amp_walk
        torso_yaw_deg = w_yaw * amp_walk

        leg_l_rx = w_leg_l_rx * amp_walk
        leg_r_rx = w_leg_r_rx * amp_walk
        leg_l_stretch = w_leg_l_str * amp_walk
        leg_r_stretch = w_leg_r_str * amp_walk
        leg_l_lift_z = w_leg_l_lz * amp_walk
        leg_r_lift_z = w_leg_r_lz * amp_walk

        # ぴょこぴょこ歩きに合わせてゴムの手も少し伸びて可愛くバランスをとる（外側の手は大きく、内側の手はぶつからない範囲で）
        outer_walk_ang = (22.0 + 18.0 * hop_arc) * amp_walk
        inner_walk_ang = (12.0 + 10.0 * hop_arc) * amp_walk
        if is_iich:
            arm_r_angle, arm_r_stretch, arm_r_whip = outer_walk_ang, 1.0 + 0.30 * amp_walk, -10.0 * hop_arc * amp_walk
            arm_l_angle, arm_l_stretch, arm_l_whip = inner_walk_ang, 1.0 + 0.15 * amp_walk, -6.0 * hop_arc * amp_walk
        else:
            arm_l_angle, arm_l_stretch, arm_l_whip = outer_walk_ang, 1.0 + 0.30 * amp_walk, -10.0 * hop_arc * amp_walk
            arm_r_angle, arm_r_stretch, arm_r_whip = inner_walk_ang, 1.0 + 0.15 * amp_walk, -6.0 * hop_arc * amp_walk

        ant_pitch_extra_deg = (-6.0 + 12.0 * hop_arc) * amp_walk
        ant_roll_extra_deg = -14.0 * paused_tilt * amp_walk

    # =========================================================================
    # Phase 2 (Frame 133〜168 / 5.5s〜7.0s):
    # Y=0.0mに到着し、「ぴょこん ➔ ムニュッ（ゴム足着地スクワッシュ）➔ ポヨン（弾性復帰）」で正面構図に静止
    # =========================================================================
    elif f <= 168.0:
        dy_run = 0.0
        u_stop = (f - 132.0) / 36.0
        if f <= 154.0:
            us = (f - 132.0) / 22.0
            damp = 1.0 - smoothstep_scalar(us)
            bounce_wave = math.sin(2.0 * math.pi * us) * damp
            dz_hop = -0.018 * bounce_wave
            squash_z = -0.065 * bounce_wave
            torso_roll_deg = 5.0 * math.cos(1.5 * math.pi * us) * (damp ** 1.3)
            leg_l_stretch = -0.18 * max(bounce_wave, 0.0) + 0.12 * max(-bounce_wave, 0.0)
            leg_r_stretch = -0.18 * max(bounce_wave, 0.0) + 0.12 * max(-bounce_wave, 0.0)
            arm_l_angle = 14.0 * damp
            arm_r_angle = 14.0 * damp
            arm_l_stretch = 1.0 + 0.14 * damp
            arm_r_stretch = 1.0 + 0.14 * damp

        damp_osc = math.exp(-3.0 * u_stop) * math.sin(2.6 * math.pi * u_stop)
        ant_pitch_extra_deg = 12.0 * damp_osc
        ant_roll_extra_deg = 7.0 * damp_osc * (1.0 if is_iich else -1.0)

    # =========================================================================
    # Phase 3 (Frame 169〜240 / 7.0s〜10.0s):
    # 【オーナー指示】顔から下がゴムのようにクニュッとへこんで内側に折れ曲がる深いおじぎ
    # =========================================================================
    elif f <= 240.0:
        dy_run = 0.0
        if f < 175.0:
            u_pre = smoothstep_scalar((f - 169.0) / 6.0)
            bow_amount = 0.0
            squash_z = 0.055 * math.sin(math.pi * u_pre)
            dz_hop = 0.010 * math.sin(math.pi * u_pre)
        elif f < 195.0:
            u_down = (f - 175.0) / 20.0
            bow_amount = smootherstep_scalar(u_down)
        elif f <= 214.0:
            u_hold = (f - 195.0) / 19.0
            bow_amount = 1.0 + 0.035 * math.sin(math.pi * u_hold)
        elif f <= 234.0:
            u_up = (f - 214.0) / 20.0
            bow_amount = 1.0 - smootherstep_scalar(u_up)
        else:
            u_settle = (f - 234.0) / 6.0
            bow_amount = 0.0
            squash_z = 0.040 * math.sin(math.pi * u_settle) * (1.0 - u_settle)

        f_lag = max(169.0, f - 3.8)
        if f_lag < 175.0:
            bow_lag = 0.0
        elif f_lag < 195.0:
            bow_lag = smootherstep_scalar((f_lag - 175.0) / 20.0)
        elif f_lag <= 214.0:
            bow_lag = 1.0
        elif f_lag <= 234.0:
            bow_lag = 1.0 - smootherstep_scalar((f_lag - 214.0) / 20.0)
        else:
            bow_lag = 0.0
        bow_whip = bow_amount - bow_lag

        # おじぎ中に足元もゴムらしくムニュッと踏ん張る
        leg_l_stretch = -0.12 * bow_amount
        leg_r_stretch = -0.12 * bow_amount

        arm_l_angle = 14.0 * bow_amount
        arm_r_angle = 14.0 * bow_amount
        arm_l_stretch = 1.0 + 0.25 * bow_amount
        arm_r_stretch = 1.0 + 0.25 * bow_amount
        arm_l_fwd = -0.06 * bow_amount
        arm_r_fwd = -0.06 * bow_amount

    # =========================================================================
    # Phase 4 (Frame 241〜360 / 10.0s〜15.0s):
    # 【オーナー指示】ゴムのように腕がビヨーンと伸びて、大きく元気よくブンブン手を振る
    # =========================================================================
    else:
        dy_run = 0.0
        env_in = smoothstep_scalar(min((f - 241.0) / 13.0, 1.0))
        env_out = 1.0 - smoothstep_scalar(np.clip((f - 336.0) / 20.0, 0.0, 1.0))
        w_wave = env_in * env_out

        # Frame 276 で sin(theta_w) = +1.0 (斜め上へ高く振り上げ)、Frame 300 で sin(theta_w) = -1.0 (横下へ大きく振り下ろし)
        theta_w = 2.0 * math.pi * ((f - 272.0) / 16.0)
        sw = math.sin(theta_w)
        cw = math.cos(theta_w)

        dz_hop = 0.038 * abs(sw) * w_wave
        squash_z = 0.065 * sw * w_wave
        torso_roll_deg = 5.5 * sw * w_wave
        torso_yaw_deg = 3.5 * cw * w_wave
        dx_sway = 0.025 * sw * w_wave

        leg_l_stretch = 0.15 * sw * w_wave
        leg_r_stretch = -0.15 * sw * w_wave
        leg_l_rx = math.radians(12.0 * sw * w_wave)
        leg_r_rx = math.radians(-12.0 * sw * w_wave)

        # 【直交Frenetゴム腕による「丸みを保ったままビヨーンと伸びて大きく振る」パラメータ】
        # 画面左右端(±2.17m)から見切れず、かつ先端がぷっくり丸いゴムの手として大きく上下スイングする設定:
        #   sw = +1 (Frame 276): delta = +64° -> 斜め上外側へ高くビヨーンと伸びてバンザイ手振り！
        #   sw = -1 (Frame 300): delta = +10° -> 斜め横外側へワイドにビヨーンと振り下ろし！
        outer_delta = (37.0 + 27.0 * sw) * w_wave
        outer_stretch = 1.0 + (0.72 + 0.12 * abs(sw)) * w_wave
        outer_whip = -14.0 * cw * w_wave
        outer_fwd = -0.08 * w_wave

        # 内側の腕も中央で重ならない角度・伸縮率で斜め前・上下に元気に振る
        inner_delta = (28.0 - 18.0 * sw) * w_wave
        inner_stretch = 1.0 + (0.38 + 0.08 * abs(cw)) * w_wave
        inner_whip = +10.0 * cw * w_wave
        inner_fwd = -0.14 * w_wave

        if is_iich:
            arm_r_angle, arm_r_stretch, arm_r_whip, arm_r_fwd = outer_delta, outer_stretch, outer_whip, outer_fwd
            arm_l_angle, arm_l_stretch, arm_l_whip, arm_l_fwd = inner_delta, inner_stretch, inner_whip, inner_fwd
        else:
            arm_l_angle, arm_l_stretch, arm_l_whip, arm_l_fwd = outer_delta, outer_stretch, outer_whip, outer_fwd
            arm_r_angle, arm_r_stretch, arm_r_whip, arm_r_fwd = inner_delta, inner_stretch, inner_whip, inner_fwd

        ant_pitch_extra_deg = 6.0 * abs(sw) * w_wave
        ant_roll_extra_deg = -10.0 * sw * w_wave

    arm_obj.location = Vector((
        base_loc.x + dx_sway,
        base_loc.y + dy_run,
        base_loc.z + dz_hop,
    ))

    # =========================================================================
    # 各メッシュへの3Dラバー空間ワープ適用
    # =========================================================================
    z_foot_lock = 0.145 if is_iich else 0.185
    z_fold_center = 0.315 if is_iich else 0.395
    sigma_fold = 0.105 if is_iich else 0.125
    z_bend_top = 0.480 if is_iich else 0.580

    for entry in char_state["meshes"]:
        obj = entry["obj"]
        rest_co = entry["rest_co"]
        x = rest_co[:, 0].copy()
        y = rest_co[:, 1].copy()
        z = rest_co[:, 2].copy()

        # ---------------------------------------------------------------------
        # Step 1: Bodyメッシュのゴム足スクワッシュ＆ストレッチ ＋ 直交Frenetゴム腕ストレッチ＆大振り変形
        # ---------------------------------------------------------------------
        if entry["is_body"]:
            if (
                abs(leg_l_rx) > 1e-4
                or abs(leg_r_rx) > 1e-4
                or abs(leg_l_stretch) > 1e-4
                or abs(leg_r_stretch) > 1e-4
                or abs(leg_l_lift_z) > 1e-4
                or abs(leg_r_lift_z) > 1e-4
            ):
                x, y, z = deform_rubber_legs_and_feet(
                    x, y, z, entry["w_leg"], char_state["z_leg_top"], is_iich,
                    leg_l_rx, leg_r_rx,
                    leg_l_stretch, leg_r_stretch,
                    leg_l_lift_z, leg_r_lift_z,
                )

            wb = entry["w_arm_blend"]
            if abs(arm_l_angle) > 1e-3 or abs(arm_l_stretch - 1.0) > 1e-3:
                x, y, z = deform_rubber_arm_frenet(
                    x, y, z, wb, char_state,
                    side_sign=+1.0,
                    delta_angle_deg=arm_l_angle,
                    stretch_ratio=arm_l_stretch,
                    whip_deg=arm_l_whip,
                    forward_bias=arm_l_fwd,
                )
            if abs(arm_r_angle) > 1e-3 or abs(arm_r_stretch - 1.0) > 1e-3:
                x, y, z = deform_rubber_arm_frenet(
                    x, y, z, wb, char_state,
                    side_sign=-1.0,
                    delta_angle_deg=arm_r_angle,
                    stretch_ratio=arm_r_stretch,
                    whip_deg=arm_r_whip,
                    forward_bias=arm_r_fwd,
                )

        # ---------------------------------------------------------------------
        # Step 2: ゴム胴体の伸縮 (Squash & Stretch: 体積保存でZが潰れるとX,Yがぷっくり広がる)
        # ---------------------------------------------------------------------
        if abs(squash_z) > 1e-5:
            u_sq = smoothstep_np((z - z_foot_lock) / 0.25)
            kz = 1.0 + squash_z * u_sq
            kxy = 1.0 / np.sqrt(np.maximum(kz, 0.70))
            x = x * kxy
            y = y * kxy
            z = np.where(z > z_foot_lock, z_foot_lock + (z - z_foot_lock) * kz, z)

        # ---------------------------------------------------------------------
        # Step 3: 【Phase 3 コア実装】
        # 「顔から下がゴムのようにクニュッとへこんで内側に折れ曲がる深いおじぎ」
        #   - 顔枠の下端が胸ロゴに食い込まず、かつ地球儀も画面上端から絶対に見切れないよう、
        #     ボディ中心ヒンジ(y_hinge=0.05m)＋腹部アコーディオン収縮＋左右26%クニュ折りくびれ＋アンテナ前傾を組み合わせる！
        # ---------------------------------------------------------------------
        if bow_amount > 1e-5:
            b = bow_amount
            u_above_foot = smoothstep_np((z - z_foot_lock) / 0.065)

            z_crease_curve = z_fold_center + 0.045 * (x * x)
            w_fold = u_above_foot * np.exp(-0.5 * ((z - z_crease_curve) / sigma_fold) ** 2)

            # (A) 顔から下の折れ曲がり帯の左右輪郭(|X|)を内側へ26%クニュッと深く引き込み、
            #     その上下（足元付け根＆頬の下）を少しぷっくり膨らませて「ゴムが内側に折れ曲がったくびれ」を明確化
            w_hip_bulge = u_above_foot * np.exp(-0.5 * ((z - (z_foot_lock + 0.040)) / 0.050) ** 2)
            w_cheek_bulge = np.exp(-0.5 * ((z - (z_bend_top + 0.060)) / 0.075) ** 2)
            x_fold_scale = 1.0 - 0.26 * b * w_fold + 0.08 * b * w_hip_bulge + 0.04 * b * w_cheek_bulge
            x = x * x_fold_scale

            # (B) 前面のお腹（顔の下〜胸ロゴ領域）がゴム人形のお腹を押したように内側(+Y奥方向)へクニュッとへこむ
            w_front_belly = smoothstep_np((0.15 - y) / 0.65)
            y = y + (0.20 if is_iich else 0.23) * b * w_fold * w_front_belly

            # (C) 折れ曲がりヒンジ(y_hinge=-0.28m, z_hinge)を中心に、顔・頭部全体が手前下方向へ 37°/35° 深く前傾しておじぎする
            #     y_hinge=-0.28m かつ遷移幅を広く取ることで dz_rot/dz > 0 (単調増加) を厳密保証し、
            #     胸ロゴ(LILI-ch / LILI-net)が顔枠の下端に隠れずゴム腹部の斜面上で綺麗に読めるようにする！
            y_hinge = -0.28
            z_hinge = 0.42 if is_iich else 0.50
            z_pitch_top = 0.58 if is_iich else 0.68

            u_pitch = smootherstep_np((z - (z_foot_lock + 0.02)) / (z_pitch_top - (z_foot_lock + 0.02)))
            max_bow_deg = 37.0 if is_iich else 35.0
            pitch_rad = math.radians(max_bow_deg * b) * u_pitch

            cp = np.cos(pitch_rad)
            sp = np.sin(pitch_rad)
            dy_p = y - y_hinge
            dz_p = z - z_hinge
            y_rot = y_hinge + dy_p * cp - dz_p * sp
            z_rot = z_hinge + dy_p * sp + dz_p * cp - (0.045 if is_iich else 0.055) * b * u_pitch
            y, z = y_rot, z_rot

            # (D) アンテナと地球儀が画面上端から見切れないよう、頭頂接続部からさらに前下方向へゴムしなり前傾させる
            if entry["is_ant_or_globe"]:
                u_ant = smoothstep_np((rest_co[:, 2] - 0.85) / 1.10)
                extra_ant_deg = (22.0 * b - 16.0 * bow_whip)
                a_rad = math.radians(extra_ant_deg) * u_ant
                ca_a, sa_a = np.cos(a_rad), np.sin(a_rad)
                y_ap = 0.35 if is_iich else 0.55
                z_ap = 1.15 if is_iich else 1.35
                dy_a = y - y_ap
                dz_a = z - z_ap
                y = y_ap + dy_a * ca_a - dz_a * sa_a
                z = z_ap + dy_a * sa_a + dz_a * ca_a - (0.12 if is_iich else 0.22) * b * u_ant

        # ---------------------------------------------------------------------
        # Step 4: 歩行・手振り時の全身の前傾・左右の大きなロール傾き(±12°)・ツイスト＆アンテナ揺れ
        # ---------------------------------------------------------------------
        if (
            abs(torso_pitch_deg) > 1e-4
            or abs(torso_roll_deg) > 1e-4
            or abs(torso_yaw_deg) > 1e-4
            or abs(ant_pitch_extra_deg) > 1e-4
            or abs(ant_roll_extra_deg) > 1e-4
        ):
            u_body_move = smoothstep_np((rest_co[:, 2] - 0.08) / 0.18)
            u_rubber_arc = 0.82 + 0.28 * np.clip(rest_co[:, 2] / 1.5, 0.0, 1.0)
            p_rad = math.radians(torso_pitch_deg) * u_body_move
            r_rad = math.radians(torso_roll_deg) * u_body_move * u_rubber_arc
            yw_rad = math.radians(torso_yaw_deg) * u_body_move

            if entry["is_ant_or_globe"]:
                u_ant = smoothstep_np((rest_co[:, 2] - 0.75) / 1.25)
                p_rad = p_rad + math.radians(ant_pitch_extra_deg) * u_ant
                r_rad = r_rad + math.radians(ant_roll_extra_deg) * u_ant

            z_piv = 0.20 if is_iich else 0.24

            cp, sp = np.cos(p_rad), np.sin(p_rad)
            dz_p = z - z_piv
            y_p = y * cp - dz_p * sp
            z_p = z_piv + y * sp + dz_p * cp
            y, z = y_p, z_p

            cr, sr = np.cos(r_rad), np.sin(r_rad)
            dz_r = z - z_piv
            x_r = x * cr + dz_r * sr
            z_r = z_piv - x * sr + dz_r * cr
            x, z = x_r, z_r

            cy, sy_rot = np.cos(yw_rad), np.sin(yw_rad)
            x_y = x * cy - y * sy_rot
            y_y = x * sy_rot + y * cy
            x, y = x_y, y_y

        new_co = np.column_stack([x, y, z]).astype(np.float32)
        obj.data.vertices.foreach_set("co", new_co.ravel())
        obj.data.update()


def create_studio_floor_and_backdrop():
    mesh = bpy.data.meshes.new("Studio_Cyclorama_Mesh")
    obj = bpy.data.objects.new("Studio_Cyclorama", mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    n_x = 18
    xs = np.linspace(-11.5, 11.5, n_x)

    profile_yz = []
    for y in np.linspace(-4.0, 14.5, 20):
        profile_yz.append((float(y), 0.0))
    for i in range(1, 12):
        ang = (0.5 * math.pi) * (i / 12.0)
        R_cyc = 3.5
        y_c = 14.5 + R_cyc * math.sin(ang)
        z_c = R_cyc * (1.0 - math.cos(ang))
        profile_yz.append((float(y_c), float(z_c)))
    for z in np.linspace(3.5, 10.5, 8)[1:]:
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
    cam_data.clip_end = 50.0

    ldata = bpy.data.lights.new(name="Runway_Fill", type='AREA')
    ldata.energy = 380.0
    ldata.color = (1.0, 0.99, 0.99)
    ldata.size = 9.5
    if hasattr(ldata, "use_shadow"):
        ldata.use_shadow = True
    lobj = bpy.data.objects.new(name="Runway_Fill", object_data=ldata)
    bpy.context.collection.objects.link(lobj)
    lobj.location = Vector((0.0, 6.0, 6.2))
    direction = (Vector((0.0, 5.5, 1.0)) - lobj.location).normalized()
    lobj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    return cam_obj


def render_keyframes_contact_sheet(cam_obj, char_states, out_paths, width=640, height=480):
    """
    15秒（360フレーム）各フェーズの代表6フレーム（Frame 25, 89, 156, 202, 276, 300）をレンダリングし、
    3列×2行のコンタクトシートPNGとして指定パス群へ出力する。
    """
    scene = bpy.context.scene
    check_frames = [25, 89, 156, 202, 276, 300]
    tmp_path = os.path.join(SCRIPT_DIR, "_tmp_anim_kf.png")

    panels = []
    for f in check_frames:
        scene.frame_set(f)
        for cs in char_states:
            apply_character_rubber_deformation_at_frame(cs, f)
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
    cols, rows = 3, 2
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
        print(f"Saved keyframes contact sheet to: {out_path}")


def bake_keyframe_shapekeys_for_blend_file(char_states):
    scene = bpy.context.scene
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.render.fps = FPS

    for f in range(FRAME_START, FRAME_END + 1):
        for cs in char_states:
            apply_character_rubber_deformation_at_frame(cs, f)
            cs["arm_obj"].keyframe_insert(data_path="location", frame=f)

    for cs in char_states:
        apply_character_rubber_deformation_at_frame(cs, 156)


def render_full_mp4_animation(scene, cam_obj, char_states, mp4_path, width=1280, height=960):
    def on_frame_change(scn, depsgraph=None):
        f_cur = scn.frame_current
        for cs in char_states:
            apply_character_rubber_deformation_at_frame(cs, f_cur)

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

    render_keyframes_contact_sheet(
        cam_obj,
        char_states,
        [CHECK_SHEET_DRAFT_PATH, KEYFRAMES_FINAL_PATH],
        width=640,
        height=480,
    )

    bake_keyframe_shapekeys_for_blend_file(char_states)
    scene.frame_set(156)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=ANIM_BLEND_PATH)

    if not check_only:
        render_full_mp4_animation(scene, cam_obj, char_states, ANIM_MP4_PATH, width=1280, height=960)

    print("ALL PAIR ANIMATION TASKS COMPLETED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
