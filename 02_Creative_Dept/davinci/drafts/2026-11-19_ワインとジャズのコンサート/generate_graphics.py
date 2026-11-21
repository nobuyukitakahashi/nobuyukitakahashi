# -*- coding: utf-8 -*-
"""
Generate all 4K (3840x2160) graphics assets for:
  2026-11-19 ワインとジャズのコンサート (HONKA music SALON / DALUMA x 田中 良明)
Uses official leaflet 450dpi vector logos + bg1.png background + high-craft Japanese typography.
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops

DRAFT_DIR = r"G:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-19_ワインとジャズのコンサート"
TITLE_ASSETS = os.path.join(DRAFT_DIR, "title_assets")
OUT_DIR = os.path.join(DRAFT_DIR, "graphics")
PREVIEW_DIR = os.path.join(OUT_DIR, "previews")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(PREVIEW_DIR, exist_ok=True)

BG1_PATH = r"C:\Users\nobuy\OneDrive\My Documents\クライアント別\飯田ケーブルテレビ_ICTV_cvn\2026-11-19_ボジョレー・ヌーボー解禁日_ワインとジャズのコンサート_HONKA_presents\leaflet\bg1.png"
VEC_PATH = os.path.join(TITLE_ASSETS, "leaflet_vectors_450dpi.png")
DALUMA_RAW = os.path.join(TITLE_ASSETS, "daluma_logo_raw.png")
SALON_RAW = os.path.join(TITLE_ASSETS, "salon_logo_raw.png")

W, H = 3840, 2160

# Fonts
FONT_MINCHO_B = r"C:\Windows\Fonts\yumindb.ttf"
FONT_MINCHO_R = r"C:\Windows\Fonts\yumin.ttf"
FONT_SANS_VF  = r"C:\Windows\Fonts\NotoSansJP-VF.ttf"
FONT_SERIF_VF = r"C:\Windows\Fonts\NotoSerifJP-VF.ttf"
FONT_GEORGIA  = r"C:\Windows\Fonts\georgia.ttf"
FONT_GEORGIA_I = r"C:\Windows\Fonts\georgiai.ttf"
FONT_GEORGIA_B = r"C:\Windows\Fonts\georgiab.ttf"

def load_font(path, size, variation=None):
    f = ImageFont.truetype(path, size)
    if variation:
        try:
            f.set_variation_by_axes(variation)
        except Exception:
            pass
    return f

def add_drop_shadow(rgba_img, offset=(0, 8), radius=14, shadow_alpha=210, color=(0, 0, 0)):
    """Return a slightly padded RGBA image with a soft drop shadow behind non-transparent pixels."""
    pad = radius * 2 + max(abs(offset[0]), abs(offset[1])) + 4
    nw, nh = rgba_img.width + pad * 2, rgba_img.height + pad * 2
    base = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
    alpha = rgba_img.split()[3]
    shadow_a = alpha.point(lambda a: int(a * shadow_alpha / 255))
    shadow = Image.new("RGBA", rgba_img.size, color + (0,))
    shadow.putalpha(shadow_a)
    shadow_layer = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
    shadow_layer.paste(shadow, (pad + offset[0], pad + offset[1]))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius))
    base = Image.alpha_composite(base, shadow_layer)
    base.paste(rgba_img, (pad, pad), rgba_img)
    return base, pad

def crop_alpha_tight(img, pad=2):
    arr = np.array(img)
    ys, xs = np.where(arr[:, :, 3] > 10)
    if len(xs) == 0:
        return img
    x0 = max(0, int(xs.min()) - pad)
    y0 = max(0, int(ys.min()) - pad)
    x1 = min(img.width, int(xs.max()) + pad + 1)
    y1 = min(img.height, int(ys.max()) + pad + 1)
    return img.crop((x0, y0, x1, y1))

def resize_to_height(img, target_h):
    ratio = target_h / img.height
    return img.resize((max(1, int(round(img.width * ratio))), target_h), Image.Resampling.LANCZOS)

def resize_to_width(img, target_w):
    ratio = target_w / img.width
    return img.resize((target_w, max(1, int(round(img.height * ratio)))), Image.Resampling.LANCZOS)

def recolor_dark_ink_logo(raw_path, bbox, rgb_color=(248, 234, 198)):
    """Extract black/dark-ink vector logo from white/transparent PDF rasterization into clean colored RGBA."""
    im = Image.open(raw_path).convert("RGBA").crop(bbox)
    arr = np.array(im, dtype=np.float32)
    # Ink strength: where pixels are opaque and dark (or alpha > 0 and luminance low)
    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    # If background is transparent (alpha=0), keep alpha; if white background, invert lum
    alpha_in = arr[:, :, 3] / 255.0
    ink = np.clip((255.0 - lum) / 235.0, 0.0, 1.0) * alpha_in
    out = np.zeros_like(arr, dtype=np.uint8)
    out[:, :, 0] = rgb_color[0]
    out[:, :, 1] = rgb_color[1]
    out[:, :, 2] = rgb_color[2]
    out[:, :, 3] = np.clip(ink * 255.0, 0, 255).astype(np.uint8)
    return crop_alpha_tight(Image.fromarray(out, "RGBA"), pad=4)

def make_widescreen_bg(mode="opening"):
    """Compose a seamless 3840x2160 widescreen wine-and-jazz salon background from official bg1.png."""
    bg1 = Image.open(BG1_PATH).convert("RGB")
    bw, bh = bg1.size  # 2110 x 2982

    # Base deep warm wine-black canvas
    canvas = Image.new("RGBA", (W, H), (8, 4, 4, 255))

    # 1. Lower salon bokeh + candle table (from bottom 48% of bg1.png)
    bot_crop = bg1.crop((0, int(bh * 0.54), bw, bh))
    bot_scaled = resize_to_width(bot_crop, W)
    # Place aligned to bottom of 4K canvas
    y_bot = H - bot_scaled.height
    # Smooth vertical fade-in mask on top of bot_scaled
    mask_arr = np.ones((bot_scaled.height, W), dtype=np.float32)
    fade_h = min(650, int(bot_scaled.height * 0.45))
    ramp = np.linspace(0.0, 1.0, fade_h) ** 1.6
    mask_arr[:fade_h, :] = ramp[:, None]
    if mode != "opening":
        # Darken & soften for intermission/bridge/ending cards
        bot_scaled = ImageEnhance.Brightness(bot_scaled).enhance(0.42)
        bot_scaled = bot_scaled.filter(ImageFilter.GaussianBlur(10))
    else:
        bot_scaled = ImageEnhance.Brightness(bot_scaled).enhance(0.68)
    bot_rgba = bot_scaled.convert("RGBA")
    bot_rgba.putalpha(Image.fromarray((mask_arr * 255).astype(np.uint8)))
    canvas.alpha_composite(bot_rgba, (0, max(0, y_bot)))

    if mode == "opening":
        # 2. Upper pouring wine glass + golden music staff from top 39% of bg1.png
        top_crop = bg1.crop((0, 0, bw, int(bh * 0.39)))
        # Scale proportionally to width 3400 (slightly zoomed in so wine glass & staff look majestic)
        top_scaled = resize_to_width(top_crop, 3550)
        # Blend with screen/alpha fade at bottom and left edges
        tw, th = top_scaled.size
        t_arr = np.array(top_scaled, dtype=np.float32)
        # Soft vertical fade at bottom 32% of top_scaled
        v_mask = np.ones((th, tw), dtype=np.float32)
        vf = int(th * 0.36)
        v_mask[th - vf:, :] = np.linspace(1.0, 0.0, vf)[:, None] ** 1.4
        # Soft horizontal fade on left 10%
        hf = int(tw * 0.08)
        v_mask[:, :hf] *= np.linspace(0.25, 1.0, hf)[None, :]
        # Use luminance-assisted alpha so black pixels blend invisibly into dark canvas
        lum = (0.299 * t_arr[:, :, 0] + 0.587 * t_arr[:, :, 1] + 0.114 * t_arr[:, :, 2]) / 255.0
        a_mask = np.clip(lum * 2.2, 0.0, 1.0) * v_mask
        top_rgba = top_scaled.convert("RGBA")
        top_rgba.putalpha(Image.fromarray((a_mask * 255).astype(np.uint8)))
        # Position aligned to top-right so pouring wine bottle enters from top-right edge!
        canvas.alpha_composite(top_rgba, (W - tw, 0))

        # 3. Subtle dark radial scrim behind title & lower cast lines so gold/ivory text pops cleanly
        yy, xx = np.mgrid[0:H, 0:W]
        dist = ((xx - 1550.0) / 1550.0) ** 2 + ((yy - 950.0) / 800.0) ** 2
        scrim_a = np.clip(1.0 - dist, 0.0, 1.0) ** 1.4 * 0.52
        # Extra soft horizontal dark band behind cast & date lines (y=1240..1760)
        band = np.exp(-((yy - 1510.0) / 260.0) ** 2) * 0.58
        scrim_a = np.clip(scrim_a + band, 0.0, 0.78)
        scrim = np.zeros((H, W, 4), dtype=np.uint8)
        scrim[:, :, 0] = 8
        scrim[:, :, 1] = 3
        scrim[:, :, 2] = 4
        scrim[:, :, 3] = (scrim_a * 255).astype(np.uint8)
        canvas = Image.alpha_composite(canvas, Image.fromarray(scrim, "RGBA"))
    else:
        # Subtle golden bokeh / ambient top wine vignette for secondary cards
        yy, xx = np.mgrid[0:H, 0:W]
        # Warm burgundy center glow
        dist = ((xx - W * 0.5) / (W * 0.55)) ** 2 + ((yy - H * 0.45) / (H * 0.55)) ** 2
        glow = np.clip(1.0 - dist, 0.0, 1.0) ** 1.8
        overlay = np.zeros((H, W, 4), dtype=np.uint8)
        overlay[:, :, 0] = 74
        overlay[:, :, 1] = 14
        overlay[:, :, 2] = 24
        overlay[:, :, 3] = (glow * 72).astype(np.uint8)
        canvas = Image.alpha_composite(canvas, Image.fromarray(overlay, "RGBA"))

    # Subtle outer vignette
    yy, xx = np.mgrid[0:H, 0:W]
    vdist = np.sqrt(((xx - W / 2) / (W * 0.58)) ** 2 + ((yy - H / 2) / (H * 0.58)) ** 2)
    vig = np.clip((vdist - 0.65) / 0.55, 0.0, 1.0) ** 1.6 * 0.55
    vig_img = np.zeros((H, W, 4), dtype=np.uint8)
    vig_img[:, :, 3] = (vig * 255).astype(np.uint8)
    canvas = Image.alpha_composite(canvas, Image.fromarray(vig_img, "RGBA"))
    return canvas

def paste_centered_with_shadow(canvas, img, cx, cy, offset=(0, 8), radius=14, shadow_alpha=215):
    sh, pad = add_drop_shadow(img, offset=offset, radius=radius, shadow_alpha=shadow_alpha)
    x = int(round(cx - sh.width / 2))
    y = int(round(cy - sh.height / 2))
    canvas.alpha_composite(sh, (x, y))

def draw_text_centered(draw, cx, y, text, font, fill, shadow=True, shadow_offset=(0, 4)):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = int(round(cx - tw / 2)) - bbox[0]
    y_draw = int(round(y)) - bbox[1]
    if shadow:
        draw.text((x + shadow_offset[0], y_draw + shadow_offset[1]), text, font=font, fill=(0, 0, 0, 195))
    draw.text((x, y_draw), text, font=font, fill=fill)
    return tw, th

def build_full_cards():
    print("Loading 450dpi official leaflet vectors...")
    vec = Image.open(VEC_PATH).convert("RGBA")

    # Crop official vector elements tightly from 450dpi leaflet (verified zero cross-bleed!)
    v_beaujolais = crop_alpha_tight(vec.crop((780, 695, 2585, 1052)))
    v_honka      = crop_alpha_tight(vec.crop((2775, 685, 3795, 960)))
    # Mask out any tiny residual Sip & Swing pixels on top-left of main title crop
    mt_raw = vec.crop((530, 1025, 3320, 1890)).copy()
    mt_arr = np.array(mt_raw)
    mt_arr[:35, :1660, :] = 0
    v_maintitle  = crop_alpha_tight(Image.fromarray(mt_arr, "RGBA"))
    v_hsalon     = crop_alpha_tight(vec.crop((580, 2190, 3980, 2285)))
    v_ensemble   = crop_alpha_tight(vec.crop((580, 2310, 3980, 2550)))
    # Footer elements (wine bar + SALON De TATSUH + BBA + cvn)
    v_footer_all = crop_alpha_tight(vec.crop((310, 5465, 4245, 5940)))
    # Extract SALON De TATSUH + sponsor credits without the burgundy box (only light pixels inside footer)
    f_arr = np.array(v_footer_all)
    # Inside burgundy box (#5E141C -> R~94, G~20, B~28), text/logo is ivory/gold (G > 90 or R > 150)
    is_fg = ((f_arr[:, :, 0].astype(int) + f_arr[:, :, 1].astype(int) + f_arr[:, :, 2].astype(int)) > 260) & (f_arr[:, :, 3] > 20)
    f_clean = np.zeros_like(f_arr)
    f_clean[is_fg] = f_arr[is_fg]
    v_footer_logos = crop_alpha_tight(Image.fromarray(f_clean, "RGBA"), pad=6)

    # Also clean DALUMA & SALON standalone logos from their individual PDFs
    daluma_white = recolor_dark_ink_logo(DALUMA_RAW, (940, 1290, 3545, 1885), rgb_color=(255, 252, 244))
    salon_gold   = recolor_dark_ink_logo(SALON_RAW,  (30, 1900, 3270, 2305), rgb_color=(244, 224, 178))

    # =========================================================
    # 1. OPENING TITLE (00_opening_title.png)
    # =========================================================
    op = make_widescreen_bg("opening")

    # Top header row: Beaujolais Nouveau (left-center) + HONKA official badge (top-left or top-center-right before wine glass)
    # Wait: the pouring wine glass is around x=2750..3500, y=150..850.
    # So placing Beaujolais + HONKA cleanly across x=220..2550 at y=160..390 keeps zero overlap with the wine glass!
    beau_s = resize_to_height(v_beaujolais, 175)
    honka_s = resize_to_height(v_honka, 130)
    paste_centered_with_shadow(op, beau_s, 1140, 275, offset=(0, 6), radius=12, shadow_alpha=220)
    paste_centered_with_shadow(op, honka_s, 2110, 255, offset=(0, 6), radius=12, shadow_alpha=220)

    # Main calligraphic gold title "ワインとジャズのコンサート"
    title_s = resize_to_width(v_maintitle, 2280)
    paste_centered_with_shadow(op, title_s, 1460, 745, offset=(0, 12), radius=22, shadow_alpha=245)

    # HONKA music SALON golden flourish divider (centered across full 4K frame)
    hsalon_s = resize_to_width(v_hsalon, 2860)
    paste_centered_with_shadow(op, hsalon_s, W // 2, 1190, offset=(0, 5), radius=10, shadow_alpha=210)

    # Ensemble line: "サックスカルテット DALUMA × ドラム 田中良明"
    ens_s = resize_to_width(v_ensemble, 2720)
    paste_centered_with_shadow(op, ens_s, W // 2, 1355, offset=(0, 8), radius=16, shadow_alpha=240)

    # Performer names & instruments + Date & Venue
    draw = ImageDraw.Draw(op)
    f_cast = load_font(FONT_MINCHO_B, 46)
    f_date = load_font(FONT_GEORGIA, 46)
    f_venue = load_font(FONT_MINCHO_R, 42)
    cast_line = "西浦 颯 (S.Sax / A.Sax)   ・   鈴木 真明地 (A.Sax)   ・   渡邊 丈留 (T.Sax)   ・   高橋 幹太 (B.Sax)   ・   田中 良明 (Drums)"
    draw_text_centered(draw, W // 2, 1510, cast_line, f_cast, (244, 232, 206, 255), shadow=True, shadow_offset=(0, 4))

    date_line = "2026.11.19 (Thu)    |    SALON De TATSUH  （飯田市銀座・サロンド タツ）"
    draw_text_centered(draw, W // 2, 1625, date_line, f_venue, (226, 195, 130, 245), shadow=True, shadow_offset=(0, 4))

    # Official wine-red bottom ribbon bar matching leaflet footer
    ribbon_y0, ribbon_y1 = 1815, 2075
    ribbon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(ribbon)
    rdraw.rectangle([0, ribbon_y0, W, ribbon_y1], fill=(82, 16, 24, 230))
    # Subtle gold top & bottom hairline on ribbon
    rdraw.rectangle([0, ribbon_y0, W, ribbon_y0 + 3], fill=(214, 178, 102, 210))
    rdraw.rectangle([0, ribbon_y1 - 3, W, ribbon_y1], fill=(214, 178, 102, 210))
    op = Image.alpha_composite(op, ribbon)

    # Place official SALON De TATSUH + BBA + cvn vector footer centered inside the ribbon
    f_logos_s = resize_to_height(v_footer_logos, 195)
    paste_centered_with_shadow(op, f_logos_s, W // 2, (ribbon_y0 + ribbon_y1) // 2 + 2, offset=(0, 4), radius=8, shadow_alpha=170)

    op.convert("RGB").save(os.path.join(OUT_DIR, "00_opening_title.png"), quality=95)
    print("Saved 00_opening_title.png")

    # =========================================================
    # 2. PART 2 INTERMISSION CARD (01_part2_card.png)
    # =========================================================
    p2 = make_widescreen_bg("card")
    draw = ImageDraw.Draw(p2)
    # Fine gold double frame
    draw.rectangle([160, 140, W - 160, H - 140], outline=(206, 172, 100, 110), width=3)
    draw.rectangle([182, 162, W - 182, H - 162], outline=(206, 172, 100, 60), width=2)

    hsalon_p2 = resize_to_width(v_hsalon, 2100)
    paste_centered_with_shadow(p2, hsalon_p2, W // 2, 560, offset=(0, 4), radius=8, shadow_alpha=180)

    draw = ImageDraw.Draw(p2)
    draw_text_centered(draw, W // 2, 740, "S E C O N D   S T A G E", load_font(FONT_GEORGIA, 58), (228, 196, 126, 255))
    draw_text_centered(draw, W // 2, 875, "—  第 2 部  —", load_font(FONT_MINCHO_B, 152), (255, 250, 240, 255), shadow_offset=(0, 8))

    # Decorative gold rule
    draw.line([(W // 2 - 420, 1135), (W // 2 + 420, 1135)], fill=(214, 178, 102, 180), width=3)

    draw_text_centered(draw, W // 2, 1210, "ワインとジャズのコンサート", load_font(FONT_MINCHO_R, 64), (242, 224, 184, 240))
    ens_p2 = resize_to_width(v_ensemble, 1900)
    paste_centered_with_shadow(p2, ens_p2, W // 2, 1390, offset=(0, 5), radius=10, shadow_alpha=190)

    salon_p2 = resize_to_height(salon_gold, 86)
    paste_centered_with_shadow(p2, salon_p2, W // 2, 1825, offset=(0, 3), radius=6, shadow_alpha=150)
    p2.convert("RGB").save(os.path.join(OUT_DIR, "01_part2_card.png"), quality=95)
    print("Saved 01_part2_card.png")

    # =========================================================
    # 3. RECORDING-GAP BRIDGE CARD (02_gap_bridge_card.png)
    # =========================================================
    gb = make_widescreen_bg("card")
    draw = ImageDraw.Draw(gb)
    draw.rectangle([200, 180, W - 200, H - 180], outline=(206, 172, 100, 95), width=2)
    draw.rectangle([218, 198, W - 218, H - 198], outline=(206, 172, 100, 50), width=1)

    draw_text_centered(draw, W // 2, 650, "SEIKO MATSUDA MEDLEY   —   04 / 04", load_font(FONT_GEORGIA, 48), (226, 194, 124, 245))
    draw_text_centered(draw, W // 2, 780, "青い珊瑚礁", load_font(FONT_MINCHO_B, 128), (255, 250, 240, 255), shadow_offset=(0, 6))
    draw_text_centered(draw, W // 2, 950, "（ 演奏途中より再開 ）", load_font(FONT_MINCHO_R, 54), (234, 212, 168, 240))

    draw.line([(W // 2 - 520, 1095), (W // 2 + 520, 1095)], fill=(214, 178, 102, 160), width=2)

    draw_text_centered(draw, W // 2, 1185, "※ 収録機材の再起動に伴い、楽曲の途中から映像・音声が再開いたします。", load_font(FONT_MINCHO_R, 48), (235, 228, 218, 230))
    draw_text_centered(draw, W // 2, 1275, "あらかじめご了承のうえ、引き続きコンサートをお楽しみください。", load_font(FONT_MINCHO_R, 44), (210, 200, 188, 215))

    salon_gb = resize_to_height(salon_gold, 72)
    paste_centered_with_shadow(gb, salon_gb, W // 2, 1810, offset=(0, 3), radius=6, shadow_alpha=140)
    gb.convert("RGB").save(os.path.join(OUT_DIR, "02_gap_bridge_card.png"), quality=95)
    print("Saved 02_gap_bridge_card.png")

    # =========================================================
    # 4. ENDING CREDITS CARD (99_ending_credits.png)
    # =========================================================
    ec = make_widescreen_bg("card")
    draw = ImageDraw.Draw(ec)
    draw.rectangle([150, 130, W - 150, H - 130], outline=(206, 172, 100, 110), width=3)

    draw_text_centered(draw, W // 2, 225, "Thank you for watching", load_font(FONT_GEORGIA_I, 66), (230, 198, 128, 255))
    title_ec = resize_to_width(v_maintitle, 1220)
    paste_centered_with_shadow(ec, title_ec, W // 2, 510, offset=(0, 8), radius=14, shadow_alpha=220)

    draw = ImageDraw.Draw(ec)
    draw.line([(420, 745), (W - 420, 745)], fill=(214, 178, 102, 140), width=2)

    # Left column: PERFORMERS (x=540..1850)
    lx = 560
    draw.text((lx, 800), "PERFORMERS", font=load_font(FONT_GEORGIA, 42), fill=(228, 196, 126, 255))
    daluma_ec = resize_to_height(daluma_white, 74)
    sh_d, pad_d = add_drop_shadow(daluma_ec, offset=(0, 4), radius=8, shadow_alpha=180)
    ec.alpha_composite(sh_d, (lx - pad_d, 875 - pad_d))
    draw = ImageDraw.Draw(ec)

    f_role = load_font(FONT_MINCHO_R, 42)
    f_name = load_font(FONT_MINCHO_B, 52)
    members_ec = [
        ("ソプラノ＆アルトサックス", "西浦 颯"),
        ("アルトサックス", "鈴木 真明地"),
        ("テナーサックス", "渡邊 丈留"),
        ("バリトンサックス", "高橋 幹太"),
        ("ドラム", "田中 良明"),
    ]
    cy = 995
    for role, name in members_ec:
        draw.text((lx, cy + 6), role, font=f_role, fill=(218, 202, 172, 235))
        draw.text((lx + 540, cy), name, font=f_name, fill=(255, 252, 245, 255))
        cy += 98

    # Vertical gold divider between columns
    draw.line([(W // 2 + 40, 805), (W // 2 + 40, 1495)], fill=(214, 178, 102, 100), width=2)

    # Right column: EVENT & CREDITS (x=2080..3350)
    rx = 2110
    draw.text((rx, 800), "CONCERT INFORMATION", font=load_font(FONT_GEORGIA, 42), fill=(228, 196, 126, 255))
    info_lines = [
        ("開催日", "2026年11月19日（木）"),
        ("会場", "サロン ド タツ（SALON De TATSUH）"),
        ("所在地", "長野県飯田市銀座3-1-1 トップヒルズ第2D棟"),
        ("主催", "プロモーター BBA"),
        ("後援", "株式会社 cvn"),
        ("企画", "HONKA music SALON"),
    ]
    cy = 905
    for k, v in info_lines:
        draw.text((rx, cy), k, font=load_font(FONT_MINCHO_R, 38), fill=(226, 194, 124, 230))
        draw.text((rx + 195, cy - 2), v, font=load_font(FONT_MINCHO_R, 42), fill=(248, 242, 232, 250))
        cy += 92

    # Bottom logos row: HONKA + SALON De TATSUH + BBA/cvn
    draw.line([(420, 1580), (W - 420, 1580)], fill=(214, 178, 102, 140), width=2)
    honka_ec = resize_to_height(v_honka, 92)
    footer_ec = resize_to_height(v_footer_logos, 145)
    paste_centered_with_shadow(ec, honka_ec, 1180, 1775, offset=(0, 4), radius=8, shadow_alpha=170)
    paste_centered_with_shadow(ec, footer_ec, 2450, 1775, offset=(0, 4), radius=8, shadow_alpha=170)

    ec.convert("RGB").save(os.path.join(OUT_DIR, "99_ending_credits.png"), quality=95)
    print("Saved 99_ending_credits.png")


# =========================================================
# 5. LOWER-THIRD TELOPS (Transparent 4K RGBA, Bottom-Right)
# =========================================================
def draw_rounded_card_shadow(w, h, radius=14):
    pad = 36
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad + 8, pad + w, pad + h + 8], radius=radius, fill=(0, 0, 0, 175))
    im = im.filter(ImageFilter.GaussianBlur(16))
    return im, pad

def make_song_telop(filename, header_label, title_jp, subtitle="", is_medley=False, is_encore=False):
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    f_hdr = load_font(FONT_MINCHO_B if any(ord(c) > 127 for c in header_label) else FONT_GEORGIA_B, 32)
    f_title = load_font(FONT_MINCHO_B, 62)
    f_sub = load_font(FONT_GEORGIA_I if (subtitle and all(ord(c) < 128 for c in subtitle)) else FONT_MINCHO_R, 34)

    # Measure text widths accurately
    tmp = ImageDraw.Draw(canvas)
    w_hdr = tmp.textbbox((0, 0), header_label, font=f_hdr)[2]
    w_title = tmp.textbbox((0, 0), title_jp, font=f_title)[2]
    w_sub = tmp.textbbox((0, 0), subtitle, font=f_sub)[2] if subtitle else 0

    content_w = max(w_hdr, w_title, w_sub)
    card_w = max(760, min(1760, content_w + 150))
    card_h = 238 if subtitle else 188

    # Anchor bottom-right inside broadcast title-safe zone (130px right, 115px bottom)
    x1 = W - 130
    y1 = H - 115
    x0 = x1 - card_w
    y0 = y1 - card_h

    # Soft shadow behind card
    sh, pad = draw_rounded_card_shadow(card_w, card_h, radius=12)
    canvas.alpha_composite(sh, (x0 - pad, y0 - pad))

    # Gradient translucent deep wine-burgundy card body
    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    arr = np.zeros((card_h, card_w, 4), dtype=np.uint8)
    # Subtle left-to-right wine gradient
    t = np.linspace(0.0, 1.0, card_w)[None, :]
    if is_encore:
        # Deeper royal burgundy-gold tint for Encore
        r = (66 * (1 - t) + 34 * t)
        g = (14 * (1 - t) + 10 * t)
        b = (22 * (1 - t) + 16 * t)
    elif is_medley:
        r = (52 * (1 - t) + 24 * t)
        g = (11 * (1 - t) + 8 * t)
        b = (22 * (1 - t) + 16 * t)
    else:
        r = (44 * (1 - t) + 20 * t)
        g = (10 * (1 - t) + 8 * t)
        b = (18 * (1 - t) + 14 * t)
    arr[:, :, 0] = r.astype(np.uint8)
    arr[:, :, 1] = g.astype(np.uint8)
    arr[:, :, 2] = b.astype(np.uint8)
    arr[:, :, 3] = 218

    # Rounded mask
    rmask = Image.new("L", (card_w, card_h), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=12, fill=255)
    card = Image.fromarray(arr, "RGBA")
    card.putalpha(ImageChops.multiply(card.split()[3], rmask))

    cdraw = ImageDraw.Draw(card)
    # Crisp champagne-gold border & thick left accent bar
    gold_main = (242, 206, 126, 255) if (is_medley or is_encore) else (222, 188, 118, 255)
    gold_line = (220, 186, 114, 150)
    cdraw.rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=12, outline=gold_line, width=2)
    cdraw.rectangle([0, 12, 12, card_h - 12], fill=gold_main)
    # Subtle golden inner hairline below header
    cdraw.line([(54, 72), (card_w - 50, 72)], fill=(224, 190, 118, 95), width=2)

    # Text placement inside card
    tx = 56
    # Header label
    cdraw.text((tx, 26), header_label, font=f_hdr, fill=gold_main)
    # Main title
    cdraw.text((tx + 2, 92 + 3), title_jp, font=f_title, fill=(0, 0, 0, 180))
    cdraw.text((tx, 92), title_jp, font=f_title, fill=(255, 253, 247, 255))
    # Subtitle
    if subtitle:
        cdraw.text((tx, 174), subtitle, font=f_sub, fill=(224, 210, 184, 240))

    canvas.alpha_composite(card, (x0, y0))
    out_path = os.path.join(OUT_DIR, filename)
    canvas.save(out_path)
    return out_path

def make_member_telop(filename, role_jp, role_en, name_jp, name_en, group_label="MEMBER INTRODUCTION  |  DALUMA"):
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    f_grp = load_font(FONT_GEORGIA_B, 28)
    f_role = load_font(FONT_MINCHO_B, 38)
    f_name = load_font(FONT_MINCHO_B, 78)
    f_en = load_font(FONT_GEORGIA_I, 38)

    role_line = f"{role_jp}   /   {role_en}"
    tmp = ImageDraw.Draw(canvas)
    w_grp = tmp.textbbox((0, 0), group_label, font=f_grp)[2]
    w_role = tmp.textbbox((0, 0), role_line, font=f_role)[2]
    w_name = tmp.textbbox((0, 0), name_jp, font=f_name)[2]
    w_en = tmp.textbbox((0, 0), name_en, font=f_en)[2]

    name_row_w = w_name + 48 + w_en
    card_w = max(1060, max(w_grp, w_role, name_row_w) + 160)
    card_h = 266

    x1 = W - 130
    y1 = H - 115
    x0 = x1 - card_w
    y0 = y1 - card_h

    sh, pad = draw_rounded_card_shadow(card_w, card_h, radius=14)
    canvas.alpha_composite(sh, (x0 - pad, y0 - pad))

    # Deep midnight-burgundy card with double champagne-gold left accent
    arr = np.zeros((card_h, card_w, 4), dtype=np.uint8)
    t = np.linspace(0.0, 1.0, card_w)[None, :]
    arr[:, :, 0] = (34 * (1 - t) + 16 * t).astype(np.uint8)
    arr[:, :, 1] = (12 * (1 - t) + 9 * t).astype(np.uint8)
    arr[:, :, 2] = (22 * (1 - t) + 18 * t).astype(np.uint8)
    arr[:, :, 3] = 224

    rmask = Image.new("L", (card_w, card_h), 0)
    ImageDraw.Draw(rmask).rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=14, fill=255)
    card = Image.fromarray(arr, "RGBA")
    card.putalpha(ImageChops.multiply(card.split()[3], rmask))

    cdraw = ImageDraw.Draw(card)
    gold_bright = (244, 212, 138, 255)
    cdraw.rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=14, outline=(232, 198, 126, 175), width=2)
    # Double left accent bar
    cdraw.rectangle([0, 14, 14, card_h - 14], fill=gold_bright)
    cdraw.rectangle([22, 24, 26, card_h - 24], fill=(232, 198, 126, 190))

    tx = 66
    # Group micro-header
    cdraw.text((tx, 26), group_label, font=f_grp, fill=(216, 184, 118, 235))
    # Instrument role
    cdraw.text((tx, 70), role_line, font=f_role, fill=gold_bright)
    # Delicate gold hairline
    cdraw.line([(tx, 126), (card_w - 56, 126)], fill=(232, 198, 126, 115), width=2)
    # Performer name (JP) + (EN)
    cdraw.text((tx + 2, 148 + 3), name_jp, font=f_name, fill=(0, 0, 0, 190))
    cdraw.text((tx, 148), name_jp, font=f_name, fill=(255, 255, 255, 255))
    cdraw.text((tx + w_name + 44, 182), name_en, font=f_en, fill=(224, 206, 174, 240))

    canvas.alpha_composite(card, (x0, y0))
    out_path = os.path.join(OUT_DIR, filename)
    canvas.save(out_path)
    return out_path

def build_all_telops():
    # 5 Member Introductions
    members = [
        ("member_01_suzuki.png",    "アルトサックス",           "Alto Sax",           "鈴木 真明地", "Machi Suzuki",    "MEMBER INTRODUCTION  |  DALUMA"),
        ("member_02_watanabe.png",  "テナーサックス",           "Tenor Sax",          "渡邊 丈留",   "Takeru Watanabe", "MEMBER INTRODUCTION  |  DALUMA"),
        ("member_03_takahashi.png", "バリトンサックス",         "Baritone Sax",       "高橋 幹太",   "Kanta Takahashi", "MEMBER INTRODUCTION  |  DALUMA"),
        ("member_04_tanaka.png",    "ドラム",                   "Drums",              "田中 良明",   "Yoshiaki Tanaka", "MEMBER INTRODUCTION  |  DRUMS"),
        ("member_05_nishiura.png",  "ソプラノ＆アルトサックス", "Soprano & Alto Sax", "西浦 颯",     "Hayate Nishiura", "MEMBER INTRODUCTION  |  DALUMA"),
    ]
    for args in members:
        make_member_telop(*args)
    print(f"Saved {len(members)} member intro telops.")

    # 22 Song & Medley Telops
    songs = [
        # Part 1
        ("song_01_jounetsu.png",     "NOW PLAYING", "情熱大陸", "葉加瀬 太郎", False, False),
        ("song_02_takefive.png",     "NOW PLAYING", "Take Five（テイク・ファイブ）", "Paul Desmond", False, False),
        ("song_03_champs.png",       "NOW PLAYING", "オー・シャンゼリゼ", "Les Champs-Élysées  /  Mike Wilsh & Mike Deighan", False, False),
        ("song_04_atrain.png",       "NOW PLAYING", "A列車で行こう", 'Take the "A" Train  /  Billy Strayhorn', False, False),
        ("song_05_singsing.png",     "NOW PLAYING", "Sing, Sing, Sing", "Louis Prima", False, False),
        # Part 2: Seiko Matsuda Medley
        ("song_06_seiko_01.png",     "松田聖子メドレー   01 / 04", "SWEET MEMORIES", "Seiko Matsuda Medley", True, False),
        ("song_07_seiko_02.png",     "松田聖子メドレー   02 / 04", "赤いスイートピー", "Seiko Matsuda Medley", True, False),
        ("song_08_seiko_03.png",     "松田聖子メドレー   03 / 04", "瑠璃色の地球", "Seiko Matsuda Medley", True, False),
        ("song_09_seiko_04.png",     "松田聖子メドレー   04 / 04", "青い珊瑚礁", "Seiko Matsuda Medley", True, False),
        # Cherbourg
        ("song_10_cherbourg.png",    "NOW PLAYING  |  SAX QUARTET", "シェルブールの雨傘", "Les Parapluies de Cherbourg  /  Michel Legrand", False, False),
        # Stevie Wonder Medley
        ("song_11_stevie_01.png",    "STEVIE WONDER MEDLEY   01 / 04", "Sir Duke（愛するデューク）", "Stevie Wonder", True, False),
        ("song_12_stevie_02.png",    "STEVIE WONDER MEDLEY   02 / 04", "Superstition（迷信）", "Stevie Wonder", True, False),
        ("song_13_stevie_03.png",    "STEVIE WONDER MEDLEY   03 / 04", "I Wish（回想）", "Stevie Wonder", True, False),
        ("song_14_stevie_04.png",    "STEVIE WONDER MEDLEY   04 / 04", "Isn't She Lovely（可愛いアイシャ）", "Stevie Wonder", True, False),
        # Beat It / Beauty and the Beast / Matsuken Samba
        ("song_15_beatit.png",       "NOW PLAYING", "Beat It（今夜はビート・イット）", "Michael Jackson  /  Arr. 高橋 幹太", False, False),
        ("song_16_beauty.png",       "NOW PLAYING", "美女と野獣", "Beauty and the Beast  /  Alan Menken", False, False),
        ("song_17_matsuken.png",     "NOW PLAYING", "マツケンサンバ II", "宮川 彬良", False, False),
        # Checkers Medley
        ("song_18_checkers_01.png",  "チェッカーズ・メドレー   01 / 04", "ギザギザハートの子守唄", "The Checkers Medley", True, False),
        ("song_19_checkers_02.png",  "チェッカーズ・メドレー   02 / 04", "星屑のステージ", "The Checkers Medley", True, False),
        ("song_20_checkers_03.png",  "チェッカーズ・メドレー   03 / 04", "涙のリクエスト", "The Checkers Medley", True, False),
        ("song_21_checkers_04.png",  "チェッカーズ・メドレー   04 / 04", "ジュリアに傷心", "The Checkers Medley", True, False),
        # Miagete Goran / Encore September
        ("song_22_miagete.png",      "NOW PLAYING  |  SAX QUARTET", "見上げてごらん夜の星を", "いずみたく", False, False),
        ("song_23_september.png",    "★ ENCORE", "September（セプテンバー）", "Earth, Wind & Fire", False, True),
    ]
    for args in songs:
        make_song_telop(*args)
    print(f"Saved {len(songs)} song/medley telops.")

def build_composite_previews():
    """Composite sample telops over real 4K concert frames to visually audit scale, contrast, and safe margins."""
    f1 = Image.open(os.path.join(DRAFT_DIR, "precision_probes", "frame_c01_play.jpg")).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
    f4 = Image.open(os.path.join(DRAFT_DIR, "precision_probes", "frame_c04_start.jpg")).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)

    samples = [
        (f1, "member_05_nishiura.png", "preview_member_on_video.jpg"),
        (f1, "song_01_jounetsu.png",   "preview_song_single_on_video.jpg"),
        (f4, "song_11_stevie_01.png",  "preview_song_medley_on_video.jpg"),
        (f4, "song_23_september.png",  "preview_encore_on_video.jpg"),
    ]
    for bg, overlay_name, out_name in samples:
        ov = Image.open(os.path.join(OUT_DIR, overlay_name)).convert("RGBA")
        comp = Image.alpha_composite(bg, ov).convert("RGB")
        # Save half-res 1920x1080 JPG for crisp fast inspection
        comp.resize((1920, 1080), Image.Resampling.LANCZOS).save(os.path.join(PREVIEW_DIR, out_name), quality=92)
    print("Saved composite previews in", PREVIEW_DIR)

if __name__ == "__main__":
    build_full_cards()
    build_all_telops()
    build_composite_previews()
    print("ALL GRAPHICS GENERATED SUCCESSFULLY!")
