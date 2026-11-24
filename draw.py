#!/usr/bin/env python3
"""Draw the NEWS-23 b164 heroes-scene front page (1024x1024)."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (17, 17, 17)
NAVY = (14, 42, 71)
NAVY2 = (22, 58, 92)
GOLD = (201, 162, 39)
GOLD_L = (232, 196, 90)
RED = (179, 38, 30)
RED_BG = (246, 226, 224)
TEAL = (14, 107, 107)
GREY = (102, 102, 102)
LIGHT = (230, 224, 210)
BLUE = (46, 110, 180)
ORANGE = (232, 110, 30)

FD = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FDB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FDS = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(d, s, f):
    return d.textlength(s, font=f)


def fit(d, s, path, size, max_w, min_size=8):
    """Shrink font until text fits max_w; return font."""
    while size > min_size and text_w(d, s, font(path, size)) > max_w:
        size -= 1
    return font(path, size)


def wrap(d, s, f, max_w):
    """Greedy wrap into lines fitting max_w."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(d, t, f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def chip(d, x, y, label, kind):
    """Small pill; returns width used."""
    bg = (34, 120, 60) if kind == "REPORTED" else (179, 38, 30)
    f = font(FDB, 10)
    w = int(text_w(d, label, f)) + 12
    d.rounded_rectangle([x, y, x + w, y + 15], radius=7, fill=bg)
    d.text((x + 6, y + 2), label, font=f, fill=(255, 255, 255))
    return w


def draw():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- MASTHEAD ----------
    d.rectangle([0, 0, W, 58], fill=INK)
    d.text((16, 8), "THE WORLD TODAY", font=font(FDS, 34), fill=(255, 255, 255))
    d.text((W - 16 - text_w(d, "MONDAY 23 NOVEMBER 2026", font(FDB, 15)),
            22), "MONDAY 23 NOVEMBER 2026", font=font(FDB, 15), fill=GOLD_L)
    d.rectangle([0, 58, W, 61], fill=GOLD)

    # ---------- KICKER ----------
    d.text((16, 68), "THE WORLD IN ONE PAGE  —  31 STORIES  —  MONDAY 23 NOVEMBER 2026",
           font=font(FDB, 13), fill=NAVY)
    d.text((W - 16 - text_w(d, "NO. 327", font(FDB, 13)), 68), "NO. 327",
           font=font(FDB, 13), fill=GREY)

    # ---------- NUMBER STRIP ----------
    nums = [
        ("-3.3%", "KOSPI FALLS"), ("5.3", "POWER GAP"),
        ("11,762", "EBOLA CASES, DRC"), ("10T won", "SEOUL FUND"),
        ("2%", "BILLIONAIRE TAX"),
        ("$450M", "SKUBAL DEAL"), ("165", "MISSILES / WEEK"),
        ("12,000", "MANCHESTER CLEARED"), ("264 kg", "EXPLOSIVES, LEBANON"),
        ("$107.3B", "ANTHROPIC IPO"),
    ]
    d.rectangle([0, 88, W, 146], fill=(255, 255, 255))
    d.line([0, 88, W, 88], fill=INK, width=2)
    d.line([0, 146, W, 146], fill=INK, width=2)
    cw = W // 5
    for i, (v, lab) in enumerate(nums):
        col, row = i % 5, i // 5
        x0 = col * cw
        y0 = 90 + row * 29
        if col:
            d.line([x0, 92, x0, 142], fill=LIGHT, width=1)
        f = fit(d, v, FDB, 19, cw - 16)
        d.text((x0 + 10, y0), v, font=f, fill=NAVY)
        lf = fit(d, lab, FDB, 9, cw - 16)
        d.text((x0 + 10, y0 + 19), lab, font=lf, fill=GREY)

    # ---------- REGION BAR ----------
    d.rectangle([0, 146, W, 168], fill=NAVY)
    regions = "ASIA-PACIFIC 7    ·    AMERICAS 8    ·    MIDDLE EAST 6    ·    EUROPE 5    ·    AFRICA 3    ·    WORLD 2"
    rf = fit(d, regions, FDB, 13, W - 32)
    d.text(((W - text_w(d, regions, rf)) / 2, 152), regions, font=rf, fill=(255, 255, 255))

    # ---------- HEROES ----------
    hx0, hy0 = 16, 176
    hw = (W - 32 - 24) // 3  # 314
    gap = 12
    heroes = [
        {
            "kind": "kospi",
            "headline": "AI ROUT HITS ASIA",
            "body": "Kospi -3.3% to 4,708.54, sheds 161 pts; intraday -5.8%. Samsung -3.1%, SK Hynix -2.5%.",
            "source": "REUTERS",
        },
        {
            "kind": "guterres",
            "headline": "GUTERRES: REGULATE AI BEFORE IT'S TOO LATE",
            "body": "Bridgetown summit: 150 delegates back a risk framework - a blueprint, not a treaty.",
            "source": "AP",
        },
        {
            "kind": "power",
            "headline": "US LEAD OVER CHINA AT RECORD LOW",
            "body": "Asia Power Index 2026: US 78.9, China 73.6 - gap 5.3, narrowest since 2018. India 3rd at 40.5.",
            "source": "BLOOMBERG",
        },
    ]
    scene_h = 168
    for i, hero in enumerate(heroes):
        x0 = hx0 + i * (hw + gap)
        x1 = x0 + hw
        # scene panel
        d.rectangle([x0, hy0, x1, hy0 + scene_h], fill=NAVY)
        if hero["kind"] == "kospi":
            # lit-window skyline
            import random
            rnd = random.Random(164)
            base = hy0 + scene_h
            bx = x0 + 6
            while bx < x1 - 30:
                bw = rnd.randint(26, 44)
                bh = rnd.randint(58, 118)
                d.rectangle([bx, base - bh, bx + bw, base], fill=(8, 28, 52))
                for wy in range(base - bh + 8, base - 6, 14):
                    for wx in range(bx + 5, bx + bw - 6, 11):
                        if rnd.random() < 0.55:
                            d.rectangle([wx, wy, wx + 5, wy + 7], fill=GOLD_L)
                bx += bw + 4
            # falling chart line, kept low-right, clear of the big number
            pts = [(x0 + 150, hy0 + 118), (x0 + 185, hy0 + 126),
                   (x0 + 215, hy0 + 122), (x0 + 245, hy0 + 138),
                   (x0 + 275, hy0 + 134), (x0 + 305, hy0 + 152)]
            d.line(pts, fill=ORANGE, width=4)
            d.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4],
                      fill=ORANGE)
            # solid band behind the subtitle lines so buildings never touch text
            d.rectangle([x0, hy0 + 56, x1, hy0 + 102], fill=NAVY)
            d.text((x0 + 12, hy0 + 12), "-3.3%", font=font(FDB, 44), fill=GOLD_L)
            d.text((x0 + 12, hy0 + 62), "KOSPI 4,708.54  ·  -161 PTS",
                   font=font(FDB, 12), fill=(255, 255, 255))
            d.text((x0 + 12, hy0 + 80), "INTRADAY -5.8%",
                   font=font(FDB, 12), fill=(255, 255, 255))
            # navy band under scene for the caption
            d.rectangle([x0, hy0 + scene_h - 24, x1, hy0 + scene_h], fill=(8, 28, 52))
            d.text((x0 + 10, hy0 + scene_h - 21), "SAMSUNG -3.1%  ·  SK HYNIX -2.5%",
                   font=font(FDB, 11), fill=GOLD_L)
        elif hero["kind"] == "guterres":
            # globe, right side, clear of gold text on the left
            cx, cy, r = x0 + hw - 62, hy0 + 78, 46
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TEAL)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=2)
            for k in range(-2, 3):
                d.arc([cx - r + abs(k) * 14, cy - r, cx + r - abs(k) * 14, cy + r],
                      90, 270, fill=(180, 220, 220), width=1)
                d.arc([cx - r, cy - r + abs(k) * 14, cx + r, cy + r - abs(k) * 14],
                      0, 360, fill=(180, 220, 220), width=1)
            d.line([cx - r, cy, cx + r, cy], fill=(180, 220, 220), width=1)
            # small flags row under globe
            for j, col in enumerate([(179, 38, 30), (46, 110, 180), (34, 120, 60), (201, 162, 39)]):
                fx = x0 + hw - 118 + j * 26
                d.rectangle([fx, hy0 + scene_h - 22, fx + 20, hy0 + scene_h - 8], fill=col)
            d.text((x0 + 12, hy0 + 14), "150", font=font(FDB, 40), fill=GOLD_L)
            d.text((x0 + 12, hy0 + 56), "DELEGATES", font=font(FDB, 17), fill=(255, 255, 255))
            d.text((x0 + 12, hy0 + 78), "BACK A RISK", font=font(FDB, 17), fill=(255, 255, 255))
            d.text((x0 + 12, hy0 + 100), "FRAMEWORK", font=font(FDB, 17), fill=(255, 255, 255))
            d.text((x0 + 12, hy0 + 128), "BRIDGETOWN SUMMIT",
                   font=font(FDB, 12), fill=GOLD_L)
        else:
            # power-index bars
            d.text((x0 + 12, hy0 + 10), "ASIA POWER INDEX 2026",
                   font=font(FDB, 13), fill=GOLD_L)
            bars = [("US", 78.9, GOLD), ("CHINA", 73.6, BLUE), ("INDIA", 40.5, (150, 150, 150))]
            by = hy0 + 38
            for name, val, col in bars:
                d.text((x0 + 12, by), name, font=font(FDB, 13), fill=(255, 255, 255))
                bx0 = x0 + 78
                bw = int((val / 80.0) * (hw - 150))
                d.rectangle([bx0, by + 2, bx0 + bw, by + 16], fill=col)
                d.text((bx0 + bw + 6, by), f"{val}", font=font(FDB, 13), fill=(255, 255, 255))
                by += 26
            d.text((x0 + 12, by + 2), "GAP 5.3 - NARROWEST SINCE 2018",
                   font=font(FDB, 12), fill=GOLD_L)
            d.text((x0 + 12, by + 20), "US DIPLOMATIC INFLUENCE -6 TO 76.7",
                   font=font(FDB, 11), fill=(200, 200, 200))
        # headline (2 lines max), body, source + chip — below the scene
        ty = hy0 + scene_h + 8
        hf = fit(d, hero["headline"], FDB, 19, hw)
        lines = wrap(d, hero["headline"], hf, hw)
        lines = lines[:2]
        for ln in lines:
            d.text((x0, ty), ln, font=hf, fill=INK)
            ty += 22
        bf = font(FD, 13)
        blines = wrap(d, hero["body"], bf, hw)[:2]
        for ln in blines:
            d.text((x0, ty), ln, font=bf, fill=(40, 40, 40))
            ty += 17
        ty += 4
        sf = font(FDB, 11)
        sw = text_w(d, hero["source"], sf)
        d.text((x0, ty + 2), hero["source"], font=sf, fill=GREY)
        chip(d, x0 + sw + 8, ty, "REPORTED", "REPORTED")

    # ---------- MORE OF THE DAY ----------
    my = 176 + scene_h + 8 + 44 + 34 + 4 + 20 + 6
    d.rectangle([0, my, W, my + 26], fill=INK)
    d.text((16, my + 5), "MORE OF THE DAY", font=font(FDB, 14), fill=(255, 255, 255))
    d.text((W - 16 - text_w(d, "10 STORIES", font(FDB, 12)), my + 6), "10 STORIES",
           font=font(FDB, 12), fill=GOLD_L)

    # ---------- CARDS ----------
    cards = [
        ("Bessent demands Nvidia answers", "Treasury chief presses chipmaker on China sales.", "REPORTED"),
        ("FBI probes NCIC police-database hack", "Bureau investigates breach of law-enforcement system.", "REPORTED"),
        ("Trump: Iran strikes may resume", "President says strikes may resume in New Year.", "REPORTED"),
        ("Nasdaq futures jump 3%", "Holiday-week rally lifts US tech futures.", "REPORTED"),
        ("Skubal signs $450M Mets deal", "Two-time Cy Young winner, nine years, pitcher record.", "REPORTED"),
        ("Tom Jackson dies at 75", "NFL star turned broadcaster dies aged 75.", "REPORTED"),
        ("States sue SpaceX over AI safety", "States challenge AI safety claims in court.", "REPORTED"),
        ("Anthropic IPO $107.3B", "Raised at $83 a share; debut close $97.17.", "REPORTED"),
        ("Poland: 3 Russian missiles crossed airspace", "Warsaw says Kh-101s entered Polish skies.", "CLAIM"),
        ("Intel warns of Russian nuclear satellite", "US intelligence flags orbital nuclear threat.", "CLAIM"),
    ]
    cy0 = my + 26 + 6
    ch = 42
    colw = (W - 32 - 12) // 2
    for i, (head, body, kind) in enumerate(cards):
        col, row = i % 2, i // 2
        x0 = 16 + col * (colw + 12)
        y0 = cy0 + row * (ch + 2)
        d.rectangle([x0, y0, x0 + colw, y0 + ch], fill=(255, 255, 255))
        d.line([x0, y0 + ch, x0 + colw, y0 + ch], fill=LIGHT, width=1)
        hf = fit(d, head, FDB, 14, colw - 92)
        d.text((x0 + 6, y0 + 3), head, font=hf, fill=INK)
        chip(d, x0 + colw - 82, y0 + 3, kind, kind)
        bf = fit(d, body, FD, 12, colw - 12)
        d.text((x0 + 6, y0 + 22), body, font=bf, fill=(60, 60, 60))

    # ---------- MAP + ALSO ----------
    ay0 = cy0 + 5 * (ch + 2) + 8
    ay1 = 884
    # map panel (left)
    mx0, mx1 = 16, 500
    d.rectangle([mx0, ay0, mx1, ay1], fill=(232, 238, 240))
    d.text((mx0 + 8, ay0 + 4), "THE WORLD, 23 NOVEMBER", font=font(FDB, 12), fill=NAVY)
    # simplified continent blobs
    d.rounded_rectangle([mx0 + 30, ay0 + 34, mx0 + 150, ay0 + 96], radius=18, fill=(190, 205, 190))
    d.rounded_rectangle([mx0 + 170, ay0 + 30, mx0 + 330, ay0 + 92], radius=20, fill=(190, 205, 190))
    d.rounded_rectangle([mx0 + 350, ay0 + 40, mx0 + 452, ay0 + 100], radius=18, fill=(190, 205, 190))
    d.rounded_rectangle([mx0 + 250, ay0 + 100, mx0 + 330, ay0 + 138], radius=14, fill=(190, 205, 190))
    pins = [
        (1, "Seoul", 400, 52), (2, "Bridgetown", 96, 84),
        (3, "Washington", 70, 52), (4, "Paris", 206, 42),
        (5, "London", 192, 56), (6, "Manchester", 176, 42),
        (7, "Kyiv", 268, 44), (8, "Warsaw", 252, 38),
        (9, "Beirut", 300, 66), (10, "Gaza", 292, 78),
        (11, "Benghazi", 268, 88), (12, "Khartoum", 292, 112),
        (13, "Kinshasa", 268, 122),
    ]
    for n, name, px, py in pins:
        cx, cy = mx0 + px, ay0 + py
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED, outline=(255, 255, 255), width=1)
        nf = font(FDB, 9)
        tw = text_w(d, str(n), nf)
        d.text((cx - tw / 2, cy - 6), str(n), font=nf, fill=(255, 255, 255))
    # legend
    leg = ["1 Seoul  2 Bridgetown  3 Washington  4 Paris  5 London",
           "6 Manchester  7 Kyiv  8 Warsaw  9 Beirut  10 Gaza",
           "11 Benghazi  12 Khartoum  13 Kinshasa"]
    ly = ay1 - 44
    for ln in leg:
        lf = fit(d, ln, FD, 10, mx1 - mx0 - 16)
        d.text((mx0 + 8, ly), ln, font=lf, fill=(40, 40, 40))
        ly += 13
    # ALSO list (right)
    ax0 = 516
    d.text((ax0, ay0 + 4), "ALSO ON MONDAY", font=font(FDB, 13), fill=NAVY)
    also = [
        ("Paris: 100+ back 2% billionaire tax", False),
        ("Manchester: 12,000 cleared", False),
        ("Zelenskyy: 165 Russian missiles in a week", False),
        ("COP31: the day after Antalya pact rejected", False),
        ("Israel unity talks resume", False),
        ("Gaza: two killed in Israeli strike", False),
        ("West Bank settler attacks", False),
        ("Iran war: no deal in sight", False),
        ("Lebanon seizes 264 kg explosives", False),
        ("Bahrain: Iranian strike hits plant, 2 hurt", False),
        ("Benghazi: UN demands port probe", True),
        ("Sudan: drones downed in Khartoum", True),
        ("DRC: fighting traps Ebola teams", False),
        ("Bangladesh: Hasina jailed on return", False),
        ("Seoul minister quits over AI exam chaos", False),
        ("SK Telecom -7.3%", False),
        ("China eases margin rules to 80%", False),
        ("Seoul readies 10T-won stabilisation fund", False),
    ]
    af = font(FD, 11)
    colw2 = 236
    for i, (item, claim) in enumerate(also):
        col, row = i // 9, i % 9
        x0 = ax0 + col * (colw2 + 8)
        y0 = ay0 + 24 + row * 16
        t = item
        if claim:
            t = item + "  [CLAIM]"
        f = fit(d, t, FD, 11, colw2)
        colr = RED if claim else INK
        d.text((x0, y0), "• " + t, font=f, fill=colr)

    # ---------- DATE CHECK ----------
    dy0, dy1 = 890, 984
    d.rectangle([16, dy0, W - 16, dy1], fill=RED_BG, outline=RED, width=2)
    d.text((28, dy0 + 5), "DATE CHECK — THESE ARE NOT 23 NOVEMBER",
           font=font(FDB, 13), fill=RED)
    left_out = ["Democrats reach 258 (22 Nov)", "Sparta II fire (22 Nov)",
                "El Chapo Isidro captured (22 Nov)", "EU-Indonesia pact (21 Nov)",
                "Nigeria boat (21 Nov)", "ICJ Myanmar ruling (19 Nov)"]
    not_yet = ["Dymer search continues (14 missing)", "4 House races uncalled",
               "COP32 venue not set", "WHO evacuating trapped Ebola staff"]
    d.text((28, dy0 + 26), "LEFT OUT:", font=font(FDB, 11), fill=RED)
    for i, item in enumerate(left_out):
        col, row = i // 3, i % 3
        x0 = 28 + col * 300
        y0 = dy0 + 44 + row * 13
        d.text((x0, y0), "✕ " + item, font=font(FD, 11), fill=INK)
    d.text((640, dy0 + 26), "NOT YET:", font=font(FDB, 11), fill=RED)
    for i, item in enumerate(not_yet):
        y0 = dy0 + 44 + i * 12
        d.text((640, y0), "… " + item, font=font(FD, 11), fill=INK)

    # ---------- FOOTER ----------
    fy = 992
    d.line([16, fy, W - 16, fy], fill=INK, width=1)
    d.text((16, fy + 5), "SOURCES: REUTERS · AP · BLOOMBERG · AFP · YONHAP",
           font=font(FD, 10), fill=GREY)
    d.text((16, fy + 19), "THE WORLD TODAY · MONDAY 23 NOVEMBER 2026 · 31 STORIES · 6 REGIONS",
           font=font(FDB, 10), fill=INK)
    d.text((W - 16 - text_w(d, "REPORTED = CONFIRMED BY WIRES   ·   CLAIM = ONE SIDE'S CLAIM",
                            font(FD, 10)), fy + 19),
           "REPORTED = CONFIRMED BY WIRES   ·   CLAIM = ONE SIDE'S CLAIM",
           font=font(FD, 10), fill=GREY)

    out = os.environ.get("OUT", "entry.png")
    img.save(out)
    print("saved", out, img.size)


if __name__ == "__main__":
    draw()
