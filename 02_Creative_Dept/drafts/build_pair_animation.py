# -*- coding: utf-8 -*-
"""
CVN公式マスコットキャラクター「いい-ch（LILI-ch）＆ いい-NETくん（LILI-net）」
2体ペア3Dアニメーション動画（15.0秒 / 360フレーム @ 24fps）
奥からチョコチョコ走る ➔ 正面構図でピタッと静止 ➔ ぺこりとおじぎ ➔ 元気に手を振る
生成・キーフレーム監査・MP4レンダリング統合スクリプト (Blender 5.2)

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


def smoothstep(t):
    t = float(np.clip(t, 0.0, 1.0))
    return t * t * (3.0 - 2.0 * t)


def smootherstep(t):
    t = float(np.clip(t, 0.0, 1.0))
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def evaluate_character_pose_at_frame(frame_idx, is_iich=True):
    """
    指定フレーム f (1..360 / 15.0秒 @ 24fps) における各ボーンの変換パラメータを計算する。
    参考：サンリオピューロランド「けろけろけろっぴがステップを披露！」の
    超短足・丸胴体マスコット特有の「高ケイデンス小刻みパタパタ足＋ポヨンポヨン上下ホップ＋左右ヨチヨチロール」を再現。
    """
    f = float(frame_idx)
    base_loc = Vector((-0.946, -0.025, 0.0036)) if is_iich else Vector((+0.881, +0.025, 0.0000))
    phase_offset = math.radians(55.0) if is_iich else 0.0

    # 初期化
    dy_run = 0.0
    dz_hop = 0.0
    dx_sway = 0.0

    body_rx = 0.0  # X軸回転: 負(-X)でカメラ側(-Y)へ前傾おじぎ
    body_ry = 0.0  # Y軸回転: 左右ロール（ヨチヨチ傾き）
    body_rz = 0.0  # Z軸回転: 左右ツイスト

    leg_l_rx = 0.0
    leg_r_rx = 0.0

    arm_l_rx, arm_l_ry, arm_l_rz = 0.0, 0.0, 0.0
    arm_r_rx, arm_r_ry, arm_r_rz = 0.0, 0.0, 0.0

    ant1_rx, ant1_ry = 0.0, 0.0
    ant2_rx, ant2_ry = 0.0, 0.0
    ant3_rx, ant3_ry = 0.0, 0.0
    globe_rx, globe_ry, globe_rz = 0.0, 0.0, 0.0

    # =========================================================================
    # Phase 1 (Frame 1〜132 / 0.0秒〜5.5秒):
    # 奥 (Y = +11.5m) からチョコチョコ走ってきて Y = 0.0m に到着
    # =========================================================================
    if f <= 132.0:
        u_run = (f - 1.0) / 131.0
        # 終盤(f=108..132)で滑らかに減速するイーズアウト走行曲線
        ease_pos = 1.0 - ((1.0 - u_run) ** 1.65)
        dy_run = 11.50 * (1.0 - ease_pos)

        # 走行振幅エンベロープ（到着直前に減衰）
        amp_run = 1.0 if f <= 114.0 else (1.0 - 0.55 * smoothstep((f - 114.0) / 18.0))

        # 1サイクル = 7.5フレーム（24fpsで約3.2Hz = 1秒間に6.4歩の高速チョコチョコ走り）
        theta = 2.0 * math.pi * ((f - 1.0) / 7.5) + phase_offset
        s1 = math.sin(theta)
        c1 = math.cos(theta)

        # 1歩ごとにポヨンポヨンと跳ねる上下バウンス (|sin(theta)|)
        dz_hop = (0.056 if is_iich else 0.052) * abs(s1) * amp_run
        dx_sway = 0.022 * s1 * amp_run

        # 走るときの可愛い前傾姿勢 (-5.5 deg) + ホップに合わせた微小ピッチ揺れ
        body_rx = math.radians(-5.5 * amp_run + 1.8 * math.cos(2.0 * theta) * amp_run)
        # 左右にヨチヨチ傾くロール (±4.8 deg)
        body_ry = math.radians(4.8 * s1 * amp_run)
        # 胴体の微小ツイスト (±3.8 deg)
        body_rz = math.radians(3.8 * c1 * amp_run)

        # 超短足の交互パタパタ前後スイング（股のシワが出ない自然で可愛い振幅）
        leg_amp = math.radians(22.0) * amp_run
        leg_l_rx = leg_amp * s1
        leg_r_rx = -leg_amp * s1

        # 走るリズムに合わせた両腕のパタパタ揺れ（少しバンザイ気味に上げてパタパタ）
        arm_flap = math.radians(14.0) * (0.45 + 0.55 * abs(c1)) * amp_run
        arm_swing = math.radians(15.0) * s1 * amp_run
        arm_l_ry = -arm_flap
        arm_r_ry = +arm_flap
        arm_l_rx = -arm_swing
        arm_r_rx = +arm_swing

        # しっぽ・地球儀の走行セカンダリ揺れ（少し遅れた位相でぷるぷる追従）
        theta_lag = theta - 0.85
        ant1_rx = math.radians(6.5 * amp_run + 3.5 * math.sin(2.0 * theta_lag) * amp_run)
        ant2_rx = math.radians(8.0 * amp_run + 5.0 * math.sin(2.0 * theta_lag - 0.4) * amp_run)
        ant3_rx = math.radians(6.0 * amp_run + 4.5 * math.sin(2.0 * theta_lag - 0.7) * amp_run)
        ant1_ry = math.radians(-5.5 * math.sin(theta_lag) * amp_run)
        ant2_ry = math.radians(-7.5 * math.sin(theta_lag - 0.3) * amp_run)
        ant3_ry = math.radians(-6.5 * math.sin(theta_lag - 0.6) * amp_run)

    # =========================================================================
    # Phase 2 (Frame 133〜168 / 5.5秒〜7.0秒):
    # Y = 0.0m に到着し、「トントンッ」と減速足踏みして正面静止ポーズでピタッと止まる
    # =========================================================================
    elif f <= 168.0:
        dy_run = 0.0
        u_stop = (f - 132.0) / 36.0
        # 最初の20フレーム(f=132..152)でトントンと足踏み減衰し、f=152..168でピタッと静止
        u_tap = min((f - 132.0) / 20.0, 1.0)
        decay = (1.0 - smoothstep(u_tap)) ** 1.35
        theta_step = 2.0 * math.pi * ((f - 132.0) / 6.5) + phase_offset * 0.5
        s_st = math.sin(theta_step)

        dz_hop = 0.028 * abs(s_st) * decay
        body_rx = math.radians(-3.0 * decay * math.cos(theta_step))
        body_ry = math.radians(3.2 * s_st * decay)
        body_rz = math.radians(2.0 * math.cos(theta_step) * decay)

        leg_l_rx = math.radians(18.0) * s_st * decay
        leg_r_rx = -math.radians(18.0) * s_st * decay

        arm_l_ry = -math.radians(8.0) * abs(s_st) * decay
        arm_r_ry = +math.radians(8.0) * abs(s_st) * decay

        # 停止慣性で地球儀・アンテナが前にぷるんと揺れて収まるオーバーシュート
        damp_osc = math.exp(-3.2 * u_stop) * math.sin(2.8 * math.pi * u_stop)
        ant1_rx = math.radians(-7.0 * damp_osc)
        ant2_rx = math.radians(-11.0 * damp_osc)
        ant3_rx = math.radians(-9.0 * damp_osc)
        ant1_ry = math.radians(4.0 * damp_osc * (1.0 if is_iich else -1.0))
        ant2_ry = math.radians(6.0 * damp_osc * (1.0 if is_iich else -1.0))

    # =========================================================================
    # Phase 3 (Frame 169〜240 / 7.0秒〜10.0秒): 2体揃って「ぺこり」と丁寧におじぎ
    # =========================================================================
    elif f <= 240.0:
        dy_run = 0.0
        # 予備動作 (169..174: ほんの少し背筋を伸ばす) -> おじぎ下降 (174..194) -> キープ (194..212) -> 復帰 (212..234) -> 整定 (234..240)
        if f < 174.0:
            u_pre = smoothstep((f - 169.0) / 5.0)
            bow_factor = -0.08 * math.sin(math.pi * u_pre)
            dz_hop = 0.008 * math.sin(math.pi * u_pre)
        elif f < 194.0:
            bow_factor = smootherstep((f - 174.0) / 20.0)
        elif f <= 212.0:
            bow_factor = 1.0
        elif f <= 234.0:
            bow_factor = 1.0 - smootherstep((f - 212.0) / 22.0)
        else:
            bow_factor = 0.0

        # おじぎ角度: 16.0度 / 14.5度前傾 (-X回転でカメラ側 -Y へお辞儀、両キャラとも地球儀が頭頂から可愛く覗く絶妙な角度)
        max_bow_deg = 16.0 if is_iich else 14.5
        body_rx = math.radians(-max_bow_deg * bow_factor)

        # おじぎ中に重心が少し沈みつつ、足裏はRoot直下で床にピタッと接地
        dz_hop += -0.010 * max(bow_factor, 0.0)

        # おじぎのとき両手を少しだけ礼儀正しく前・内側へ添える
        arm_l_rx = math.radians(-8.0 * max(bow_factor, 0.0))
        arm_r_rx = math.radians(-8.0 * max(bow_factor, 0.0))
        arm_l_ry = math.radians(4.0 * max(bow_factor, 0.0))
        arm_r_ry = math.radians(-4.0 * max(bow_factor, 0.0))

        # しっぽ・地球儀のフォロースルー＆オーバーシュート（おじぎの時は遅れて前に傾き、起き上がると後ろへぷるんと揺れる）
        f_lag = max(169.0, f - 3.5)
        if f_lag < 174.0:
            bow_lag = 0.0
        elif f_lag < 194.0:
            bow_lag = smootherstep((f_lag - 174.0) / 20.0)
        elif f_lag <= 212.0:
            bow_lag = 1.0
        elif f_lag <= 234.0:
            bow_lag = 1.0 - smootherstep((f_lag - 212.0) / 22.0)
        else:
            bow_lag = 0.0

        whip = bow_lag - bow_factor
        rebound = 0.0
        if f > 224.0:
            u_reb = (f - 224.0) / 16.0
            rebound = math.sin(math.pi * min(u_reb, 1.0)) * 0.35

        ant1_rx = math.radians((-3.0 * bow_lag) + 10.0 * whip + 4.5 * rebound)
        ant2_rx = math.radians((-4.5 * bow_lag) + 15.0 * whip + 7.0 * rebound)
        ant3_rx = math.radians((-3.5 * bow_lag) + 12.0 * whip + 5.5 * rebound)

    # =========================================================================
    # Phase 4 (Frame 241〜360 / 10.0秒〜15.0秒):
    # カメラに向かって元気にパタパタ手を振る＆ハッピーホップし、最後1秒(336〜360)で正面構図に収まる
    # =========================================================================
    else:
        dy_run = 0.0
        # f=241..252で滑らかに手を上げ、f=252..334まで元気いっぱいに振り、f=334..356で滑らかに正面静止ポーズへ収束
        env_in = smoothstep(min((f - 241.0) / 11.0, 1.0))
        env_out = 1.0 - smoothstep(np.clip((f - 334.0) / 22.0, 0.0, 1.0))
        u_wave_env = env_in * env_out

        # 手振りの高速パタパタ周期 (1サイクル = 6.5フレーム = 約3.7Hz)
        theta_w = 2.0 * math.pi * ((f - 241.0) / 6.5) + (0.0 if is_iich else 0.45)
        sw = math.sin(theta_w)
        cw = math.cos(theta_w)

        # 嬉しそうに小刻みにポヨンと跳ねながら左右に可愛くスイング
        dz_hop = 0.028 * abs(sw) * u_wave_env
        body_ry = math.radians((3.6 if is_iich else -3.6) * math.sin(0.5 * theta_w) * u_wave_env)
        body_rz = math.radians((2.6 if is_iich else -2.6) * math.cos(0.5 * theta_w) * u_wave_env)
        body_rx = math.radians(-1.5 * abs(sw) * u_wave_env)

        # 足もリズムに合わせて可愛く小さくタッピング
        leg_l_rx = math.radians(9.0 * sw * u_wave_env)
        leg_r_rx = math.radians(-9.0 * sw * u_wave_env)

        # 【手振りモーション】
        # 脇下のソフビ曲面が折れない自然で可愛い角度範囲(-20°〜+16°)で、
        # 外側の手と内側の手を交互にパタパタ上下＆前後に振って元気いっぱいにアピール
        if is_iich:
            # いい-ch: 外側の手 = Arm.R (-X側), 内側の手 = Arm.L (+X側)
            arm_r_ry = math.radians((14.0 + 18.0 * sw) * u_wave_env)
            arm_r_rx = math.radians(-14.0 * cw * u_wave_env)
            arm_r_rz = math.radians(8.0 * sw * u_wave_env)

            arm_l_ry = math.radians((-10.0 + 14.0 * cw) * u_wave_env)
            arm_l_rx = math.radians(10.0 * sw * u_wave_env)
        else:
            # いい-NETくん: 外側の手 = Arm.L (+X側), 内側の手 = Arm.R (-X側)
            arm_l_ry = math.radians((-14.0 - 18.0 * sw) * u_wave_env)
            arm_l_rx = math.radians(-14.0 * cw * u_wave_env)
            arm_l_rz = math.radians(-8.0 * sw * u_wave_env)

            arm_r_ry = math.radians((10.0 - 14.0 * cw) * u_wave_env)
            arm_r_rx = math.radians(10.0 * sw * u_wave_env)

        # しっぽ・地球儀もハッピーに揺れる
        ant1_ry = math.radians(4.5 * math.sin(0.5 * theta_w - 0.3) * u_wave_env)
        ant2_ry = math.radians(6.5 * math.sin(0.5 * theta_w - 0.6) * u_wave_env)
        ant3_ry = math.radians(5.5 * math.sin(0.5 * theta_w - 0.9) * u_wave_env)
        ant1_rx = math.radians(3.0 * abs(sw) * u_wave_env)
        ant2_rx = math.radians(4.5 * abs(cw) * u_wave_env)

    arm_world_loc = Vector((
        base_loc.x + dx_sway,
        base_loc.y + dy_run,
        base_loc.z + dz_hop,
    ))

    bone_rotations = {
        "Root": (0.0, 0.0, 0.0),
        "Body": (body_rx, body_ry, body_rz),
        "Leg.L": (leg_l_rx, 0.0, 0.0),
        "Leg.R": (leg_r_rx, 0.0, 0.0),
        "Arm.L": (arm_l_rx, arm_l_ry, arm_l_rz),
        "Arm.R": (arm_r_rx, arm_r_ry, arm_r_rz),
        "Antenna_1": (ant1_rx, ant1_ry, 0.0),
        "Antenna_2": (ant2_rx, ant2_ry, 0.0),
        "Globe": (globe_rx, globe_ry, globe_rz),
    }
    if not is_iich:
        bone_rotations["Antenna_3"] = (ant3_rx, ant3_ry, 0.0)

    return arm_world_loc, bone_rotations


def create_studio_floor_and_backdrop():
    """
    奥(Y=+11.5m)から手前(Y=0m)まで走ってくる2体の足元に自然な接地影を落とし、
    背景の淡いブルーグレーのグラデーションを美しく見せるスタジオ床＆背景シクロラマを生成する。
    """
    mesh = bpy.data.meshes.new("Studio_Cyclorama_Mesh")
    obj = bpy.data.objects.new("Studio_Cyclorama", mesh)
    bpy.context.collection.objects.link(obj)

    import bmesh
    bm = bmesh.new()
    n_x = 18
    xs = np.linspace(-11.5, 11.5, n_x)

    # 手前(Y=-4.0, Z=0.0) -> 奥床(Y=14.5, Z=0.0) -> 緩やかなRコーナー -> 背景壁(Y=18.0, Z=10.5)
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
    """
    Y=0m到着時に完成静止画とぴったりのサイズ・構図になりつつ、
    Y=+11.5mから走ってくる奥行き感が自然に出る透視投影カメラ（lens=70mm）とスタジオライトを構築。
    """
    mod_pair.setup_pair_lighting_and_world()
    mod_iinet.disable_freestyle_outline()

    cam_data = bpy.data.cameras.new("PairAnimCam")
    cam_obj = bpy.data.objects.new("PairAnimCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # 透視投影カメラ: 焦点距離 70mm, カメラ位置 (0.0, -8.45, 1.22), 正面水平向き (0, 1, 0)
    # 36mmセンサーで距離 8.45m のとき横視野幅 = 8.45 * (36 / 70) = 4.346m となり、
    # 静止画オルソカメラ (ortho_scale = 4.35m) と Y=0m で完全一致するフレーミングを実現！
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

    # 奥(Y=+11.5m)を走っている間もキャラクターが暗くならないよう、走行レーン上部に柔らかなトップフィルライトを追加
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


def bake_animation_keyframes(arm_iich, arm_iinet):
    """全360フレーム（15.0秒 @ 24fps）のアニメーションキーフレームを両キャラクターのArmatureにベイクする"""
    scene = bpy.context.scene
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.render.fps = FPS

    for arm_obj in (arm_iich, arm_iinet):
        arm_obj.rotation_mode = 'XYZ'
        for pb in arm_obj.pose.bones:
            pb.rotation_mode = 'XYZ'

    for f in range(FRAME_START, FRAME_END + 1):
        for is_iich, arm_obj in [(True, arm_iich), (False, arm_iinet)]:
            loc, bone_rots = evaluate_character_pose_at_frame(f, is_iich=is_iich)
            arm_obj.location = loc
            arm_obj.keyframe_insert(data_path="location", frame=f)

            for b_name, (rx, ry, rz) in bone_rots.items():
                pb = arm_obj.pose.bones.get(b_name)
                if pb is not None:
                    pb.rotation_euler = Euler((rx, ry, rz), 'XYZ')
                    pb.keyframe_insert(data_path="rotation_euler", frame=f)


def render_keyframes_contact_sheet(cam_obj, out_paths, width=640, height=480):
    """
    15秒（360フレーム）各フェーズの代表6フレーム（Frame 24, 84, 156, 202, 276, 303）をレンダリングし、
    3列×2行のコンタクトシートPNGとして指定パス群へ出力する。
    """
    scene = bpy.context.scene
    check_frames = [24, 84, 156, 202, 276, 303]
    tmp_path = os.path.join(SCRIPT_DIR, "_tmp_anim_kf.png")

    panels = []
    for f in check_frames:
        scene.frame_set(f)
        bpy.context.view_layer.update()
        arr = mod_iinet.render_view_to_array(cam_obj, width, height, tmp_path, transparent=False)
        # 枠線を追加
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


def render_full_mp4_animation(scene, cam_obj, mp4_path, width=1280, height=960):
    """Blender 5.2 の VIDEO (MPEG4 / H264) 出力機能を用いて全360フレーム（15.0秒）をMP4動画へレンダリング"""
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
    print(f"MP4 animation render (360 frames / 15.0s) completed in {dt:.1f}s -> {mp4_path}")


def main():
    check_only = ("--check-only" in sys.argv)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    mod_iinet.configure_cycles_gpu(scene)

    # 微細グレイン質感と柔らかい陰影を維持しつつ全360フレームを高速完走するサンプル＆デノイザー設定
    scene.cycles.samples = 28
    scene.cycles.use_denoising = True
    if hasattr(scene.cycles, "denoiser"):
        scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    if hasattr(scene.cycles, "denoising_input_passes"):
        scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    if hasattr(scene.cycles, "denoising_prefilter"):
        scene.cycles.denoising_prefilter = 'FAST'
    if hasattr(scene.render, "use_persistent_data"):
        scene.render.use_persistent_data = True

    coll_iich = bpy.data.collections.new("Collection_IICh")
    coll_iinet = bpy.data.collections.new("Collection_IINet")
    scene.collection.children.link(coll_iich)
    scene.collection.children.link(coll_iinet)

    if not os.path.exists(mod_iinet.GLOBE_TEX_PATH):
        mod_iinet.extract_textures_and_profiles()
    mat_globe = mod_pair.create_micro_grain_globe_material()
    im_ref = mod_iinet.load_image_rgba_uint8(mod_pair.REF_PAIR_PATH)

    arm_iich, _ = mod_pair.build_iich_character(coll_iich, mat_globe, im_ref)
    arm_iinet, _ = mod_pair.build_iinet_character(coll_iinet, mat_globe, im_ref)

    create_studio_floor_and_backdrop()
    cam_obj = setup_animation_lighting_and_camera(scene)

    bake_animation_keyframes(arm_iich, arm_iinet)
    scene.frame_set(156)
    bpy.context.view_layer.update()

    # キーフレーム6枚コンタクトシート出力（1回の6枚レンダリングでdraftsとfinal_outputsの両方に保存）
    render_keyframes_contact_sheet(
        cam_obj,
        [CHECK_SHEET_DRAFT_PATH, KEYFRAMES_FINAL_PATH],
        width=640,
        height=480,
    )

    # アニメーション入り .blend ファイル保存（正面静止フレーム Frame 156 を初期表示フレームに設定）
    scene.frame_set(156)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=ANIM_BLEND_PATH)

    if not check_only:
        render_full_mp4_animation(scene, cam_obj, ANIM_MP4_PATH, width=1280, height=960)

    print("ALL PAIR ANIMATION TASKS COMPLETED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
