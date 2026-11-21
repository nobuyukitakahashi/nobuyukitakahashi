# -*- coding: utf-8 -*-
"""
Generate perspective-matched 4K RGBA piano-cloth logo overlays for:
  - Part 1 & Clip 03 (piano_logo_part1.png)
  - Part 2 Clip 04 & 05A (piano_logo_part2.png — shifted to post-restart camera framing + gentle DoF match)

Uses official 450dpi leaflet vector logos:
  - ワインとジャズのコンサート (gold calligraphy)
  - SALON De TATSUH (champagne-ivory brush logo)
  - Subtle champagne-gold hairline accents (zero clunky opaque box — lets the real dark piano cloth shine through!)
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

DRAFT_DIR   = r"G:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-19_ワインとジャズのコンサート"
TITLE_DIR   = os.path.join(DRAFT_DIR, "title_assets")
WORK_DIR    = os.path.join(DRAFT_DIR, "piano_logo_work")
STILLS_DIR  = os.path.join(DRAFT_DIR, "audit_stills_v2")
GFX_DIR     = os.path.join(DRAFT_DIR, "graphics")
os.makedirs(WORK_DIR, exist_ok=True)

VEC_PATH    = os.path.join(TITLE_DIR, "leaflet_vectors_450dpi.png")
SALON_RAW   = os.path.join(TITLE_DIR, "salon_logo_raw.png")
FONT_GEO    = r"C:\Windows\Fonts\georgia.ttf"
FONT_GEO_I  = r"C:\Windows\Fonts\georgiai.ttf"
FONT_MINCHO = r"C:\Windows\Fonts\yumin.ttf"

W, H = 3840, 2160

def crop_alpha_tight(img, pad=4):
    arr = np.array(img)
    ys, xs = np.where(arr[:, :, 3] > 10)
    if len(xs) == 0:
        return img
    return img.crop((
        max(0, int(xs.min()) - pad),
        max(0, int(ys.min()) - pad),
        min(img.width, int(xs.max()) + pad + 1),
        min(img.height, int(ys.max()) + pad + 1),
    ))

def resize_to_width(img, tw):
    r = tw / img.width
    return img.resize((tw, max(1, int(round(img.height * r)))), Image.Resampling.LANCZOS)

def recolor_dark_ink(raw_path, bbox, rgb=(244, 228, 192)):
    im = Image.open(raw_path).convert("RGBA").crop(bbox)
    arr = np.array(im, dtype=np.float32)
    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    ink = np.clip((255.0 - lum) / 235.0, 0.0, 1.0) * (arr[:, :, 3] / 255.0)
    out = np.zeros_like(arr, dtype=np.uint8)
    out[:, :, 0] = rgb[0]
    out[:, :, 1] = rgb[1]
    out[:, :, 2] = rgb[2]
    out[:, :, 3] = np.clip(ink * 255.0, 0, 255).astype(np.uint8)
    return crop_alpha_tight(Image.fromarray(out, "RGBA"), pad=4)

def find_perspective_coeffs(src_pts, dst_pts):
    """Return 8 perspective transform coeffs mapping dst(x,y) -> src(x,y) for PIL Image.transform."""
    matrix = []
    for p_dst, p_src in zip(dst_pts, src_pts):
        matrix.append([p_dst[0], p_dst[1], 1, 0, 0, 0, -p_src[0] * p_dst[0], -p_src[0] * p_dst[1]])
        matrix.append([0, 0, 0, p_dst[0], p_dst[1], 1, -p_src[1] * p_dst[0], -p_src[1] * p_dst[1]])
    A = np.array(matrix, dtype=np.float64)
    B = np.array([c for pt in src_pts for c in pt], dtype=np.float64)
    res = np.linalg.solve(A, B)
    return res.tolist()

def build_flat_emblem():
    """Build a crisp high-res flat RGBA emblem (1200 x 1460) designed for the piano cloth:
       1. Official HONKA badge + official HONKA music SALON gold flourish
       2. Official ワインとジャズのコンサート gold calligraphic logo
       3. Official SALON De TATSUH brush logo + date
    """
    EW, EH = 1200, 1460
    emb = Image.new("RGBA", (EW, EH), (0, 0, 0, 0))

    vec = Image.open(VEC_PATH).convert("RGBA")
    # Official HONKA badge (450dpi vector)
    v_honka = crop_alpha_tight(vec.crop((2775, 685, 3795, 960)))
    # Gently warm/refine HONKA badge yellow slightly so it harmonizes with champagne-gold under tungsten salon lighting
    hk_arr = np.array(v_honka, dtype=np.float32)
    # Keep dark black letters crisp, warm up bright yellow slightly to luxury brass-gold
    is_yellow = (hk_arr[:, :, 0] > 160) & (hk_arr[:, :, 1] > 140)
    hk_arr[is_yellow, 0] = np.clip(hk_arr[is_yellow, 0] * 0.94, 0, 255)
    hk_arr[is_yellow, 1] = np.clip(hk_arr[is_yellow, 1] * 0.87, 0, 255)
    hk_arr[is_yellow, 2] = np.clip(hk_arr[is_yellow, 2] * 0.95 + 24, 0, 255)
    v_honka_refined = Image.fromarray(hk_arr.astype(np.uint8), "RGBA")

    # Official "HONKA music SALON" with curved gold flourish (zero DALUMA bleed)
    v_hsalon = crop_alpha_tight(vec.crop((580, 2190, 3980, 2285)))

    # Clean main title "ワインとジャズのコンサート" (zero Sip & Swing bleed)
    mt_raw = vec.crop((530, 1025, 3320, 1890)).copy()
    mt_arr = np.array(mt_raw)
    mt_arr[:35, :1660, :] = 0
    v_maintitle = crop_alpha_tight(Image.fromarray(mt_arr, "RGBA"))

    # Slightly refine main title gold to warm luxury champagne-gold
    mt_rgba = v_maintitle.copy()
    a_mt = np.array(mt_rgba, dtype=np.float32)
    r, g, b = a_mt[:, :, 0], a_mt[:, :, 1], a_mt[:, :, 2]
    a_mt[:, :, 0] = np.clip(r * 0.96 + 8, 0, 255)
    a_mt[:, :, 1] = np.clip(g * 0.89 + 12, 0, 255)
    a_mt[:, :, 2] = np.clip(b * 0.95 + 32, 0, 255)
    v_maintitle_refined = Image.fromarray(a_mt.astype(np.uint8), "RGBA")

    # Official SALON De TATSUH brush logo in luminous champagne-ivory
    salon_logo = recolor_dark_ink(SALON_RAW, (30, 1900, 3270, 2305), rgb=(246, 232, 200))

    def paste_with_shadow(base_img, fg, x, y, sh_a=0.72, blur=9):
        sa = fg.split()[3].point(lambda a: int(a * sh_a))
        sh = Image.new("RGBA", fg.size, (0, 0, 0, 0))
        sh.putalpha(sa)
        sl = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
        sl.paste(sh, (x + 4, y + 9))
        sl = sl.filter(ImageFilter.GaussianBlur(blur))
        base_img = Image.alpha_composite(base_img, sl)
        base_img.alpha_composite(fg, (x, y))
        return base_img

    cx = EW // 2
    gold_line = (224, 192, 128, 195)

    # 1. Top: Official HONKA badge (sleek, smart size) + HONKA music SALON official text & flourish
    honka_s = resize_to_width(v_honka_refined, 430)
    emb = paste_with_shadow(emb, honka_s, cx - honka_s.width // 2, 72, sh_a=0.65, blur=8)

    # Crisp "HONKA music SALON" text + flanking gold hairlines (more legible at distance than tiny PDF flourish alone)
    draw = ImageDraw.Draw(emb)
    hs_y = 72 + honka_s.height + 34
    f_hs = ImageFont.truetype(FONT_GEO, 52)
    hs_txt = "HONKA music SALON"
    hsb = draw.textbbox((0, 0), hs_txt, font=f_hs)
    hs_w = hsb[2] - hsb[0]
    draw.text((cx - hs_w // 2 + 2, hs_y + 4), hs_txt, font=f_hs, fill=(0, 0, 0, 175))
    draw.text((cx - hs_w // 2, hs_y), hs_txt, font=f_hs, fill=(244, 218, 158, 250))

    # Official curved gold flourish accent right underneath HONKA music SALON
    hsalon_s = resize_to_width(v_hsalon, 1080)
    # Keep only the outer golden curved wings (mask out the tiny duplicate center text so our crisp 52px text shines!)
    hs_arr = np.array(hsalon_s)
    hs_arr[:, int(hs_arr.shape[1] * 0.34):int(hs_arr.shape[1] * 0.66), 3] = 0
    # Draw sleek connecting gold rule with center diamond
    rule_y = hs_y + 72
    draw.line([(120, rule_y), (cx - 38, rule_y)], fill=gold_line, width=3)
    draw.line([(cx + 38, rule_y), (EW - 120, rule_y)], fill=gold_line, width=3)
    draw.polygon([(cx, rule_y - 12), (cx + 12, rule_y), (cx, rule_y + 12), (cx - 12, rule_y)], fill=(238, 208, 146, 235))

    # 2. Hero Logo 1: ワインとジャズのコンサート
    title_s = resize_to_width(v_maintitle_refined, 1070)
    ty = rule_y + 46
    emb = paste_with_shadow(emb, title_s, cx - title_s.width // 2, ty, sh_a=0.75, blur=10)

    # Elegant thin divider between main title and venue logo
    draw = ImageDraw.Draw(emb)
    div_y = ty + title_s.height + 70
    draw.line([(175, div_y), (cx - 130, div_y)], fill=gold_line, width=3)
    draw.line([(cx + 130, div_y), (EW - 175, div_y)], fill=gold_line, width=3)
    f_mid = ImageFont.truetype(FONT_GEO_I, 42)
    mid_txt = "at"
    mb = draw.textbbox((0, 0), mid_txt, font=f_mid)
    draw.text((cx - (mb[2] - mb[0]) // 2, div_y - 26), mid_txt, font=f_mid, fill=(236, 208, 154, 240))

    # 3. Hero Logo 2: SALON De TATSUH
    salon_s = resize_to_width(salon_logo, 1050)
    sy = div_y + 62
    emb = paste_with_shadow(emb, salon_s, cx - salon_s.width // 2, sy, sh_a=0.75, blur=9)

    # Subtle concert date & bottom gold accent rule
    draw = ImageDraw.Draw(emb)
    sub_y = sy + salon_s.height + 52
    f_sub = ImageFont.truetype(FONT_GEO, 40)
    sub_txt = "2026.11.19   |   IIDA"
    sb = draw.textbbox((0, 0), sub_txt, font=f_sub)
    draw.text((cx - (sb[2] - sb[0]) // 2, sub_y), sub_txt, font=f_sub, fill=(234, 210, 164, 230))

    bot_y = sub_y + 82
    draw.line([(140, bot_y), (EW - 140, bot_y)], fill=gold_line, width=3)

    # Apply subtle natural ambient lighting falloff
    arr = np.array(emb, dtype=np.float32)
    yy, xx = np.mgrid[0:EH, 0:EW]
    light = 0.88 + 0.14 * (xx / EW) - 0.10 * (yy / EH)
    arr[:, :, :3] = np.clip(arr[:, :, :3] * light[:, :, None], 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")

def warp_onto_4k(emblem, dst_quad, opacity=0.84, blur_radius=0.0):
    """Perspective-warp flat emblem onto 3840x2160 RGBA canvas at exact piano cloth quad."""
    EW, EH = emblem.size
    src_quad = [(0, 0), (EW, 0), (EW, EH), (0, EH)]
    coeffs = find_perspective_coeffs(src_quad, dst_quad)
    warped = emblem.transform((W, H), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC)
    if blur_radius > 0:
        warped = warped.filter(ImageFilter.GaussianBlur(blur_radius))
    if opacity < 1.0:
        arr = np.array(warped, dtype=np.float32)
        arr[:, :, 3] = np.clip(arr[:, :, 3] * opacity, 0, 255)
        warped = Image.fromarray(arr.astype(np.uint8), "RGBA")
    return warped

def main():
    emblem = build_flat_emblem()
    emblem.save(os.path.join(WORK_DIR, "emblem_flat.png"))

    # Exact piano-cloth plane quads (TL, TR, BR, BL) measured from piano_grid_4states.jpg:
    # Part 1 & Clip 03: piano top edge (0,710)->(520,745), right fold (520,745)->(660,1680)
    # Place emblem smartly inside the clean flat cloth with generous margin on all 4 sides:
    quad_p1 = [
        (36,  850),   # Top-Left
        (492, 886),   # Top-Right (follows 3.8 deg perspective slope of piano top!)
        (572, 1530),  # Bottom-Right (follows outward drape slope of piano cloth!)
        (68,  1560),  # Bottom-Left (subtle bottom perspective convergence!)
    ]
    # Part 2 Clip 04 & 05A: camera shifted ~155px right & ~35px up after restart
    quad_p2 = [
        (180, 800),   # Top-Left
        (652, 834),   # Top-Right
        (736, 1480),  # Bottom-Right
        (212, 1510),  # Bottom-Left
    ]

    ov_p1 = warp_onto_4k(emblem, quad_p1, opacity=0.88, blur_radius=0.35)
    ov_p2 = warp_onto_4k(emblem, quad_p2, opacity=0.84, blur_radius=1.75)

    p1_path = os.path.join(GFX_DIR, "piano_logo_part1.png")
    p2_path = os.path.join(GFX_DIR, "piano_logo_part2.png")
    ov_p1.save(p1_path)
    ov_p2.save(p2_path)
    print("Saved 4K piano overlays:", p1_path, p2_path)

    # Build 2x2 full-frame visual audit preview over real stabilized stills (including bottom-right telops!)
    samples = [
        ("02_Song01_Jounetsu.png",  ov_p1, "Part 1: Sitting Play (Jounetsu Tairiku)"),
        ("03_Member_Suzuki.png",    ov_p1, "Part 1: Standing MC (Member Intro)"),
        ("08_Seiko04_Resume.png",   ov_p2, "Part 2: Clip 04 Sitting (Soft-Focus Match)"),
        ("11_Encore_September.png", ov_p2, "Part 2: Clip 05A Encore Standing"),
    ]
    tw, th, ch = 960, 540, 38
    board = Image.new("RGB", (tw * 2, (th + ch) * 2), (16, 10, 12))
    draw = ImageDraw.Draw(board)
    f_cap = ImageFont.truetype(r"C:\Windows\Fonts\yumindb.ttf", 22)

    for idx, (fn, ov, cap) in enumerate(samples):
        bg = Image.open(os.path.join(STILLS_DIR, fn)).convert("RGBA")
        comp = Image.alpha_composite(bg, ov).convert("RGB")
        # Save full-res preview for c01_sit too
        if idx == 0:
            comp.resize((1920, 1080), Image.Resampling.LANCZOS).save(
                os.path.join(WORK_DIR, "preview_full_part1.jpg"), quality=93
            )
        r, c = divmod(idx, 2)
        x, y = c * tw, r * (th + ch)
        board.paste(comp.resize((tw, th), Image.Resampling.LANCZOS), (x, y))
        draw.rectangle([x, y + th, x + tw, y + th + ch], fill=(32, 12, 16))
        draw.text((x + 14, y + th + 7), cap, font=f_cap, fill=(244, 224, 180))

    bpath = os.path.join(WORK_DIR, "piano_logo_preview_board.jpg")
    board.save(bpath, quality=93)
    print("Saved preview board:", bpath)

if __name__ == "__main__":
    main()
