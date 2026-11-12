# -*- coding: utf-8 -*-
"""
CVN公式マスコットキャラクター「いい-ch（LILI-ch）＆ いい-NETくん（LILI-net）」
2体ペア3Dアニメーション動画（15.0秒 / 360フレーム @ 24fps）
【Blender 5.3 対応・腕ひれ完全ゼロ（独立パドル手 SO(3) 純粋剛体回転）＆
  超短足ねじれゼロ（股関節振り子回転＋心地よい弾性伸縮＋胸ロゴ完全同期）全面改修版】

  Phase 1 (Frame 1〜128 / 0.00s〜5.33s):
    リファレンス（Kirby walk cycle 24fps: 1歩=8f / 1サイクル=16f）準拠の
    超短足「トコトコ／ポテポテ」ウォーク（Y=+4.35m ➔ 0.0m、1歩≈0.272m）。
    歩き出しは斜め前3/4カメラアングルで前後の足運び・足の心地よい弾性伸縮・短い手の逆位相スイングを
    立体的に見せ、Frame 76〜132 で完成静止画の正面カメラへ滑らかに回り込む。
  Phase 2 (Frame 129〜168 / 5.33s〜7.00s):
    定位置 Y=0.0m に到着した瞬間、両足を揃えて小さく「ピョコン！」と可愛い着地ホップ（+4.5cm）➔
    「ポテッ」と自然な3%クッションで正面スマイル構図にピタッと静止（Frame 156 で静止画と100%一致）。
  Phase 3 (Frame 169〜240 / 7.00s〜10.00s):
    お腹の凹み・ロゴ歪みゼロ！ぷっくり丸いタマゴ体型のまま、短いパドル手をちょこんと後ろ外側へ添えて
    前へ約21°綺麗に「ペコリ！」とおじぎし、アンテナと地球儀も可愛く前へ揺れる。
  Phase 4 (Frame 241〜360 / 10.00s〜15.00s):
    腕の伸縮ゼロ（常時1.00倍・完全剛体回転）！外側の短いパドル手をほっぺの横へグイッと持ち上げ、
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
# 数学ユーティリティ（C^1 / C^2 イージング）
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


# ==========================================
# 1. キャラクター初期頂点＆変形パラメータ事前計算
# ==========================================
def capture_character_rest_state(arm_obj, meshes, is_iich=True):
    """
    各キャラクターの全メッシュ初期座標（Rest Coords）と、
    ・独立パドル手（Arm.L / Arm.R）の SO(3) 完全剛体回転用ピボット座標
    ・超短足のねじれゼロ股関節振り子回転＆心地よい弾性伸縮用パラメータ
    を事前計算してキャッシュする。
    """
    body_obj = next(m for m in meshes if m.name.endswith("_Body"))
    n_body = len(body_obj.data.vertices)
    body_co = np.empty(n_body * 3, dtype=np.float64)
    body_obj.data.vertices.foreach_get("co", body_co)
    body_co = body_co.reshape(-1, 3)

    if is_iich:
        u_sh, y_sh, z_sh = 0.655, 0.0334, 0.345
        u_flap_piv, z_flap_piv = 0.285, 0.705
        z_hip_piv = 0.145
        z_leg_solid = 0.085
        z_leg_top = 0.165
        x_foot_center = 0.255
        base_loc = Vector((-0.946, -0.025, 0.0036))
    else:
        u_sh, y_sh, z_sh = 0.725, 0.0460, 0.465
        u_flap_piv, z_flap_piv = 0.440, 0.790
        z_hip_piv = 0.215
        z_leg_solid = 0.130
        z_leg_top = 0.255
        x_foot_center = 0.265
        base_loc = Vector((+0.881, +0.025, 0.0000))

    z_min_rest = float(np.min(body_co[:, 2]))
    ground_ref_z = float(base_loc.z) + z_min_rest

    mesh_entries = []
    for obj in meshes:
        nv = len(obj.data.vertices)
        co = np.empty(nv * 3, dtype=np.float64)
        obj.data.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)

        is_body = obj.name.endswith("_Body")
        is_arm_l = obj.name.endswith("_Arm.L")
        is_arm_r = obj.name.endswith("_Arm.R")
        is_logo = "_Logo_" in obj.name
        is_ant_or_globe = obj.name.endswith("_Antenna") or obj.name.endswith("_Globe")

        # Body の超短足重み関数（3D楕円体ソケット・股関節局所フォールオフ制御）：
        # 1) ボディ本体の完全保護ゾーン（歪みゼロ保証）:
        #    胸ロゴ下端より下（IICh: z >= 0.165m, IINet: z >= 0.255m）より上のボディ本体
        #    （胸ロゴ・お腹・脇腹・タマゴ型側面輪郭・顔枠すべて）は厳密に w_leg = 0.000 にロック！
        # 2) 足先〜足首下部（IICh: z <= 0.085m, IINet: z <= 0.130m）は足の外縁まで均一に w_leg = 1.000 とし、
        #    足の付け根の関節リング帯（z_leg_solid -> z_leg_top）で smootherstep により 1.0 -> 0.0 へ滑らかに減衰させる。
        if is_body:
            vx, vz = co[:, 0], co[:, 2]
            w_leg = 1.0 - smootherstep_np((vz - z_leg_solid) / (z_leg_top - z_leg_solid))
            s_leg_l = 0.5 * (1.0 + np.tanh(vx / 0.110))
        else:
            w_leg = None
            s_leg_l = None

        mesh_entries.append({
            "obj": obj,
            "rest_co": co,
            "is_body": is_body,
            "is_arm_l": is_arm_l,
            "is_arm_r": is_arm_r,
            "is_logo": is_logo,
            "is_ant_or_globe": is_ant_or_globe,
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
        "z_hip_piv": z_hip_piv,
        "z_leg_solid": z_leg_solid,
        "z_leg_top": z_leg_top,
        "x_foot_center": x_foot_center,
    }


# ==========================================
# 2. 独立パドル腕の完全剛体 SO(3) 回転 ＆ 超短足の振り子回転＋弾性伸縮
# ==========================================
def rotate_rigid_arm_so3(x, y, z, char_state, side_sign, flap_deg, swing_fwd_deg):
    """
    独立メッシュ化されたパドル手（Arm.L / Arm.R）に対する全頂点一律 w = 1.000 の
    純粋剛体 SO(3) 直交回転（det(R)=1、メッシュ伸縮・せん断歪み厳密ゼロ）。
      - 胴体メッシュ（Body）とは分離されているため、腕を ±46° 前後スイングさせても
        +60° ほっぺ横まで持ち上げても、胴体側面に「ひれ」や「翼状の筋」が一切発生しない！
      - タマゴ型胴体側面の曲率中心 (u_flap_piv, z_flap_piv) ＆ 肩ピボット (u_sh, y_sh) の
        まわりで剛体回転するため、どの角度でも腕の根元がタマゴ胴体に深く滑らかに密着する。
    """
    if abs(flap_deg) < 1e-4 and abs(swing_fwd_deg) < 1e-4:
        return x, y, z

    u_out = side_sign * x
    u_sh = char_state["u_sh"]
    y_sh = char_state["y_sh"]
    z_sh = char_state["z_sh"]
    u_fp = char_state["u_flap_piv"]
    z_fp = char_state["z_flap_piv"]

    # 1) 上下パタパタ挙上（Flap: タマゴ側面曲率中心まわりの純粋剛体 SO(2) 回転）
    alpha = math.radians(flap_deg)
    ca = math.cos(alpha)
    sa = math.sin(alpha)
    du_f = u_out - u_fp
    dz_f = z - z_fp
    u_1 = u_fp + du_f * ca - dz_f * sa
    z_1 = z_fp + du_f * sa + dz_f * ca

    # 2) 回転後の肩ピボット u_sh_1 を中心とする前後スイング（Azimuth: 純粋剛体 SO(2) 回転）
    u_sh_1 = u_fp + (u_sh - u_fp) * ca - (z_sh - z_fp) * sa
    beta = math.radians(swing_fwd_deg)
    cb = math.cos(beta)
    sb = math.sin(beta)
    du_s = u_1 - u_sh_1
    dy_s = y - y_sh
    u_2 = u_sh_1 + du_s * cb + dy_s * sb
    y_2 = y_sh - du_s * sb + dy_s * cb

    x_out = side_sign * u_2
    return x_out, y_2, z_1


def deform_stubby_legs_pendulum_stretch(
    x, y, z, w_leg, s_leg_l, char_state,
    leg_l_rx_deg, leg_r_rx_deg,
    leg_l_dy, leg_r_dy,
    leg_l_stretch, leg_r_stretch,
    leg_l_lift_z, leg_r_lift_z,
):
    """
    超短足の可愛い丸い造形を100%保ったまま前後にトコトコ動かす「股関節振り子回転＋滑走並進＋自然な弾性伸縮」：
      1) 横幅カットオフ (u_leg_x_out) と前後非対称クリフ (w_front_chest) を全廃し、
         足先〜足首 (z <= z_leg_solid) は重み 1.0 で足の外縁まで一体として動くため、
         足のねじれやカギ鼻状の潰れが100%発生しない。
      2) 股関節高さ (z_leg_top) を胸ロゴ下端直下に設定しているため、胸ロゴ（LILI-ch / LILI-net）は
         1ミリも歪まずシャープな形状を100%維持する。
      3) 股関節ピボット (y=0, z=z_hip_piv) まわりの心地よい縦弾性伸縮（stretch: ±8%〜10%の体積保存伸縮）と
         適度な振り子回転（rx_deg: ±13°）＋前後グライド並進（dy: ±4.5cm）を組み合わせ、
         丸い足が自然にぷっくり伸び縮みしながら前後にトコトコ歩く。
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
    x_fc = char_state["x_foot_center"]

    # Step A: 足の軸方向に沿った心地よい弾性伸縮（±8〜10%程度、体積保存で丸みを維持）
    st_eff = wm * (leg_l_stretch * sl + leg_r_stretch * sr)
    kz_leg = 1.0 + st_eff
    kxy_leg = 1.0 / np.sqrt(np.maximum(kz_leg, 0.85))

    dz_from_hip = zm - z_hip
    zm_st = z_hip + dz_from_hip * kz_leg
    x_leg_axis = x_fc * (sl - sr)
    xm_st = x_leg_axis + (xm - x_leg_axis) * kxy_leg
    ym_st = ym * kxy_leg

    # Step B: 股関節ピボット (y_piv = 0.0, z_piv = z_hip) まわりの純粋振り子回転 ＋ 前後グライド
    rx_rad = wm * (math.radians(leg_l_rx_deg) * sl + math.radians(leg_r_rx_deg) * sr)
    dy_glide = wm * (leg_l_dy * sl + leg_r_dy * sr)
    ca = np.cos(rx_rad)
    sa = np.sin(rx_rad)
    dy_rel = ym_st
    dz_rel = zm_st - z_hip

    y_rot = dy_rel * ca - dz_rel * sa + dy_glide
    z_rot = z_hip + dy_rel * sa + dz_rel * ca

    # Step C: 遊脚（前へ振り出す足・片足ちょこん浮き）の自然な垂直リフト
    dz_lift = wm * (leg_l_lift_z * sl + leg_r_lift_z * sr)
    z_final = z_rot + dz_lift

    x_out = x.copy()
    y_out = y.copy()
    z_out = z.copy()
    x_out[mask] = xm_st
    y_out[mask] = y_rot
    z_out[mask] = z_final
    return x_out, y_out, z_out


# ==========================================
# 3. カービィお手本準拠 16フレーム周期ウォーク関数
# ==========================================
def evaluate_kirby_walk_cycle(f, is_iich=True):
    """
    リファレンス動画（Kirby walk cycle 24fps）準拠：
      - 1歩 = 8.0フレーム、左右1サイクル = 16.0フレーム
      - 2体は3.0フレームの自然な位相差で仲良くトコトコ歩く
      - 股関節振り子回転（±13°）＋前後グライド（±4.8cm）＋足の心地よい弾性伸縮（+9%伸び / -6%縮み）
      - 左足(+X)が前(-Y)のとき、右手(-X)が前(-Y)・左手(+X)が後ろ(+Y)の逆位相スイング
    """
    phase_offset = 0.0 if is_iich else 3.0
    phase = 2.0 * math.pi * ((f - 1.0 - phase_offset) / 16.0)

    s = math.sin(phase)

    # 1歩（8フレーム）ごとの「トコ・ピョコ！」と弾む軽快な上下バウンス（z_air_hop ≈ 0.042m）と控えめなクッション
    step_bounce = math.sin(2.0 * phase - 0.35 * math.pi)
    z_air_hop = (0.042 if is_iich else 0.040) * (max(0.0, step_bounce) ** 1.35)
    squash_z = 0.015 * step_bounce

    # 身体の自然な前傾・前に出た肩側への可愛いツイスト(±7.0°)・最小限の傾き(±3.5°)
    torso_pitch_deg = 3.2 - 1.6 * max(0.0, step_bounce)
    torso_yaw_deg = 7.0 * s       # s=+1(左足+Xが前)のとき右肩(-X)が前(-Y)へ出る逆位相ツイスト
    torso_roll_deg = 3.5 * s
    dx_sway = 0.024 * s

    # 左右の超短足軌道：
    # 付け根支点 z_hip_piv (0.145m / 0.215m) まわりの素直な振り子回転（±19°〜20.5°）＋ ごく微小なグライド（±1.2cm）
    max_swing_deg = 19.0 if is_iich else 20.5
    stride_glide = 0.012 if is_iich else 0.014

    def single_leg_motion(u_ph):
        su = math.sin(u_ph)
        cu = math.cos(u_ph)
        rx_deg = -max_swing_deg * su - 1.5 * cu
        dy_l = -stride_glide * su

        # 足の心地よい弾性伸縮（+8.5%伸び / -6.0%クッション縮み）：
        ext_swing = (su * su)
        kick_push = max(0.0, -su)
        stance_comp = max(0.0, -cu) * (1.0 - su * su)
        stretch = +0.075 * ext_swing + 0.020 * kick_push - 0.060 * stance_comp

        # 後ろ蹴り出し後半〜前へ振り戻す遊脚フェーズ（cu > 0）で足が床から可愛く浮く
        swing_lift = max(0.0, math.sin(u_ph + 0.35 * math.pi)) ** 1.6
        lift_z = (0.036 if is_iich else 0.042) * swing_lift
        return rx_deg, dy_l, stretch, lift_z

    leg_l_rx, leg_l_dy, leg_l_stretch, leg_l_lift = single_leg_motion(phase)
    leg_r_rx, leg_r_dy, leg_r_stretch, leg_r_lift = single_leg_motion(phase + math.pi)

    # 短い独立パドル手の逆位相前後スイング（完全剛体回転のため胴体ひれゼロ！）
    swing_amp = 38.0 if is_iich else 37.0
    arm_r_swing = +swing_amp * s
    arm_l_swing = -swing_amp * s

    outer_base_flap = 11.0 if is_iich else 12.5
    inner_base_flap = 6.0 if is_iich else 7.0
    if is_iich:
        arm_r_flap = outer_base_flap + 9.5 * max(0.0, s) + 3.0 * abs(s)
        arm_l_flap = inner_base_flap + 7.5 * max(0.0, -s) + 2.0 * abs(s)
    else:
        arm_l_flap = outer_base_flap + 10.5 * max(0.0, -s) + 3.5 * abs(s)
        arm_r_flap = inner_base_flap + 8.5 * max(0.0, s) + 2.0 * abs(s)

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
        "leg_l_rx": leg_l_rx, "leg_l_dy": leg_l_dy, "leg_l_stretch": leg_l_stretch, "leg_l_lift": leg_l_lift,
        "leg_r_rx": leg_r_rx, "leg_r_dy": leg_r_dy, "leg_r_stretch": leg_r_stretch, "leg_r_lift": leg_r_lift,
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
    if u <= 0.86:
        prog = u / (0.86 + 0.14 * 0.5)
    else:
        ut = (u - 0.86) / 0.14
        prog = (0.86 + 0.14 * (ut - 0.5 * ut * ut)) / (0.86 + 0.14 * 0.5)
    return 4.35 * max(0.0, 1.0 - prog)


def update_camera_for_frame(cam_obj, frame_idx):
    """
    Phase 1 序盤〜中盤（Frame 1〜76）は可愛い斜め前3/4アングルで
    2体が重ならず短い手足の前後スイングと足の弾性伸縮がバッチリ見える構図とし、
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

    # --- 変数のゼロ初期化（静止フレームでは完全無変形 = 原画シルエットと100%一致） ---
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
    # Phase 2 (Frame 129〜168 / 5.33s〜7.00s):
    # ちょこんと両足ジャンプ着地（「ピョコン・ピタッ！」）＆正面スマイル静止
    # =========================================================================
    elif f <= 168.0:
        dy_walk = 0.0
        f_hop = f - (0.0 if is_iich else 1.0)
        if 129.0 <= f_hop <= 143.0:
            uh = (f_hop - 129.0) / 14.0
            hop_arc = math.sin(math.pi * uh)
            z_air_hop = 0.046 * hop_arc
            squash_z = +0.015 * hop_arc
            # ジャンプ中は短い両足がちょこんと下へ伸びて揃い、短い両手を横にパタッと開く
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
            outer_bow_flap = 15.0 * b_pos
            inner_bow_flap = 8.0 * b_pos
            if is_iich:
                arm_r_flap, arm_l_flap = outer_bow_flap, inner_bow_flap
            else:
                arm_l_flap, arm_r_flap = outer_bow_flap, inner_bow_flap
            arm_l_swing = -22.0 * b_pos
            arm_r_swing = -22.0 * b_pos

    # =========================================================================
    # Phase 4 (Frame 241〜360 / 10.00s〜15.00s):
    # 独立パドル腕の完全剛体回転！ほっぺの横の高い位置で短い手を「パタパタ！」と元気に振る
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

        # 外側の独立パドル手をタマゴ側面に沿ってほっぺの横まで大きく持ち上げてパタパタ振る（ひれゼロ！）
        if is_iich:
            outer_flap = (40.0 + 16.0 * sw10) * w_wave
        else:
            outer_flap = (41.5 + 16.5 * sw10) * w_wave
        outer_swing = (6.0 + 6.0 * cw10) * w_wave

        inner_flap = (6.5 - 3.0 * sw10) * w_wave
        inner_swing = (18.0 - 5.0 * sw_step) * w_wave

        if is_iich:
            arm_r_flap, arm_r_swing = outer_flap, outer_swing
            arm_l_flap, arm_l_swing = inner_flap, inner_swing
        else:
            arm_l_flap, arm_l_swing = outer_flap, outer_swing
            arm_r_flap, arm_r_swing = inner_flap, inner_swing

        torso_roll_deg = (-3.8 * char_step) * w_wave
        torso_yaw_deg = (3.2 * char_step) * w_wave
        dx_sway = ((-0.026 if is_iich else +0.026) - 0.014 * char_step) * w_wave
        squash_z = 0.014 * abs(sw10) * w_wave - 0.005 * w_wave
        z_air_hop = 0.008 * max(0.0, abs(sw10) - 0.25) * w_wave

        # 傾いた反対側の短い足がちょこんと前に出て浮き、軸方向に+5%ぷっくり伸びる
        lift_l = max(0.0, +char_step) * w_wave
        lift_r = max(0.0, -char_step) * w_wave
        leg_l_rx = -11.0 * lift_l
        leg_l_dy = -0.010 * lift_l
        leg_l_stretch = +0.055 * lift_l - 0.030 * lift_r
        leg_l_lift = +0.038 * lift_l

        leg_r_rx = -11.0 * lift_r
        leg_r_dy = -0.010 * lift_r
        leg_r_stretch = +0.055 * lift_r - 0.030 * lift_l
        leg_r_lift = +0.038 * lift_r

        ant_pitch_extra = 4.8 * abs(sw10) * w_wave
        ant_roll_extra = 6.8 * char_step * w_wave

        if 351.0 < f < 358.0:
            uf = (f - 351.0) / 7.0
            squash_z += 0.010 * math.sin(math.pi * uf) * (1.0 - uf)

    # =========================================================================
    # 各メッシュへの変形適用（Body / Arm.L / Arm.R / Face / Logo / Antenna / Globe）
    # =========================================================================
    z_foot_cush = 0.140 if is_iich else 0.190
    z_bow_z0 = 0.045 if is_iich else 0.065
    span_bow = 0.115 if is_iich else 0.175
    z_bow_piv = 0.145 if is_iich else 0.215
    y_bow_piv = -0.345 if is_iich else -0.285

    z_min_body_current = None

    for entry in char_state["meshes"]:
        obj = entry["obj"]
        rest_co = entry["rest_co"]
        x = rest_co[:, 0].copy()
        y = rest_co[:, 1].copy()
        z = rest_co[:, 2].copy()

        # Step 1A: Body の超短足（股関節振り子回転＋滑走並進＋自然な弾性伸縮）
        if entry["is_body"]:
            x, y, z = deform_stubby_legs_pendulum_stretch(
                x, y, z,
                entry["w_leg"], entry["s_leg_l"], char_state,
                leg_l_rx, leg_r_rx,
                leg_l_dy, leg_r_dy,
                leg_l_stretch, leg_r_stretch,
                leg_l_lift, leg_r_lift,
            )

        # Step 1B: 独立パドル腕（Arm.L / Arm.R）の全頂点 w=1.000 純粋剛体 SO(3) 回転
        if entry["is_arm_l"]:
            x, y, z = rotate_rigid_arm_so3(
                x, y, z, char_state,
                side_sign=+1.0, flap_deg=arm_l_flap, swing_fwd_deg=arm_l_swing,
            )
        elif entry["is_arm_r"]:
            x, y, z = rotate_rigid_arm_so3(
                x, y, z, char_state,
                side_sign=-1.0, flap_deg=arm_r_flap, swing_fwd_deg=arm_r_swing,
            )

        # Step 2: 着地クッション等のごく控えめな体積保存バウンス（±1.5%以内）
        if abs(squash_z) > 1e-5:
            z_ref_sq = z if (entry["is_arm_l"] or entry["is_arm_r"]) else rest_co[:, 2]
            u_sq = smootherstep_np((z_ref_sq - z_foot_cush) / 0.22)
            kz = 1.0 + squash_z * u_sq
            kxy = 1.0 / np.sqrt(np.maximum(kz, 0.85))
            x = x * kxy
            y = y * kxy
            z = np.where(z > z_foot_cush, z_foot_cush + (z - z_foot_cush) * kz, z)

        # Step 3: Phase 3 短い両足でしっかり床に踏ん張り、ボディ本体と胸ロゴは100%純粋剛体回転(u_bow=1.0)で「ペコリ！」とおじぎ
        if abs(bow_deg) > 1e-4:
            if entry["is_body"]:
                u_bow = 0.08 + 0.92 * smootherstep_np((rest_co[:, 2] - z_bow_z0) / span_bow)
            else:
                u_bow = 1.0
            p_bow = math.radians(bow_deg) * u_bow
            cb, sb = np.cos(p_bow), np.sin(p_bow)
            dy_b = y - y_bow_piv
            dz_b = z - z_bow_piv
            y = y_bow_piv + dy_b * cb - dz_b * sb
            z = z_bow_piv + dy_b * sb + dz_b * cb

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
            if entry["is_arm_l"] or entry["is_arm_r"]:
                u_orient = 1.0
            else:
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

    # fuse_arms=False により、胴体（純粋なタマゴ型メッシュ）と両腕（独立した滑らかなパドルメッシュ）を分離構築
    arm_iich, meshes_iich = mod_pair.build_iich_character(coll_iich, mat_globe, im_ref, fuse_arms=False)
    arm_iinet, meshes_iinet = mod_pair.build_iinet_character(coll_iinet, mat_globe, im_ref, fuse_arms=False)

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
