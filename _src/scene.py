"""Draws the cutaway house used by the home page scroll scene and the room crops.

Each room has three layers:
  base   furniture that stays put
  clean  things that only exist once the room is clean (revealed by the wipe)
  dirt   grime, clutter and mess (removed by the wipe)
The scroll script grows two mask rects per room so the squeegee reveals clean
behind it. Static crops skip the dirt layer and the masks entirely.
"""
import math
import random

OUT = "#23343a"
CREAM = "#f5f2ea"
YELLOW = "#f2c230"
SAGE = "#9cc2b5"
TEAL = "#5f8c7d"
WOOD = "#c48f5a"
BROWN = "#a8744a"
RED = "#c75b4a"
BLUE = "#4f7394"
SKY = "#cfe6ef"
GRIME = "#6b5a35"
STAIN = "#8a7444"

W, H = 1000, 880

ROOMS = {
    "bed": (114, 262, 392, 244),
    "bath": (530, 262, 356, 244),
    "living": (114, 534, 440, 252),
    "kitchen": (568, 534, 318, 252),
}


def f(n):
    return ("%.1f" % n).rstrip("0").rstrip(".")


def rect(x, y, w, h, fill, rx=0, cls="o", extra=""):
    r = f' rx="{f(rx)}"' if rx else ""
    c = f' class="{cls}"' if cls else ""
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"{r} fill="{fill}"{c}{extra}/>'


def circ(cx, cy, r, fill, cls="o", extra=""):
    c = f' class="{cls}"' if cls else ""
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}"{c}{extra}/>'


def ell(cx, cy, rx, ry, fill, cls="o", extra=""):
    c = f' class="{cls}"' if cls else ""
    return f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{fill}"{c}{extra}/>'


def path(d, fill="none", cls="o", extra=""):
    c = f' class="{cls}"' if cls else ""
    return f'<path d="{d}" fill="{fill}"{c}{extra}/>'


def line(x1, y1, x2, y2, stroke=OUT, w=3, extra=""):
    return f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round"{extra}/>'


def g(inner, extra=""):
    return f"<g{extra}>{inner}</g>"


def blob(cx, cy, rx, ry, seed, n=9, jit=0.28):
    """Irregular closed shape, smoothed through midpoints."""
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + rnd.uniform(-jit, jit)
        pts.append((cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k))
    mids = [((pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
    d = f"M{f(mids[-1][0])} {f(mids[-1][1])}"
    for i in range(n):
        d += f" Q{f(pts[i][0])} {f(pts[i][1])} {f(mids[i][0])} {f(mids[i][1])}"
    return d + "Z"


def stains(room, seed, count, color=STAIN, op=0.35, size=(10, 26)):
    x, y, w, h = room
    rnd = random.Random(seed)
    out = []
    for i in range(count):
        cx = rnd.uniform(x + 20, x + w - 20)
        cy = rnd.uniform(y + 16, y + h - 60)
        r = rnd.uniform(*size)
        out.append(path(blob(cx, cy, r, r * rnd.uniform(0.5, 0.9), seed * 31 + i), color, "", f' opacity="{op}"'))
    return "".join(out)


def cobweb(x, y, sx=1, sy=1, size=46):
    """Corner web. sx/sy flip it into the right corner."""
    s = []
    for a in (0, 22, 45, 68, 90):
        r = math.radians(a)
        s.append(f"M{f(x)} {f(y)} L{f(x + sx * size * math.cos(r))} {f(y + sy * size * math.sin(r))}")
    for k in (0.35, 0.62, 0.9):
        rr = size * k
        pts = [(x + sx * rr * math.cos(math.radians(a)), y + sy * rr * math.sin(math.radians(a))) for a in (0, 22, 45, 68, 90)]
        d = f"M{f(pts[0][0])} {f(pts[0][1])}"
        for p0, p1 in zip(pts, pts[1:]):
            mx = (p0[0] + p1[0]) / 2 - sx * rr * 0.06
            my = (p0[1] + p1[1]) / 2 - sy * rr * 0.06
            d += f" Q{f(mx)} {f(my)} {f(p1[0])} {f(p1[1])}"
        s.append(d)
    return path(" ".join(s), "none", "", ' stroke="#8d8a80" stroke-width="1.4" opacity=".9"')


def dust_bunny(cx, cy, r=7, seed=1):
    rnd = random.Random(seed)
    hairs = " ".join(
        f"M{f(cx + math.cos(a) * r * .7)} {f(cy + math.sin(a) * r * .7)} L{f(cx + math.cos(a) * r * 1.5)} {f(cy + math.sin(a) * r * 1.5)}"
        for a in [rnd.uniform(0, 6.28) for _ in range(9)]
    )
    return path(blob(cx, cy, r, r * .8, seed, 8, .3), "#9a958a", "", ' opacity=".95"') + path(hairs, "none", "", ' stroke="#8b867b" stroke-width="1.3"')


def flies(cx, cy, seed):
    rnd = random.Random(seed)
    out = []
    for i in range(3):
        x = cx + rnd.uniform(-22, 22)
        y = cy + rnd.uniform(-20, 8)
        out.append(
            f'<g class="fly" style="animation-delay:-{rnd.uniform(0, 2):.2f}s">'
            + ell(x - 2.5, y - 2.5, 3, 2, "#ffffff", "", ' opacity=".8"')
            + ell(x + 2.5, y - 2.5, 3, 2, "#ffffff", "", ' opacity=".8"')
            + circ(x, y, 2.2, OUT, "")
            + "</g>"
        )
    return "".join(out)


def planks(x, y, w, h, step=56, color="#a87446"):
    s = "".join(line(xx, y, xx, y + h, color, 1.5) for xx in range(int(x + step), int(x + w), step))
    return rect(x, y, w, h, WOOD, 0, "") + s + line(x, y, x + w, y, "#a87446", 2)


def tiles(x, y, w, h, step, fill, grout, checker=None):
    s = [rect(x, y, w, h, fill, 0, "")]
    if checker:
        for i, xx in enumerate(range(int(x), int(x + w), step)):
            for j, yy in enumerate(range(int(y), int(y + h), step)):
                if (i + j) % 2:
                    s.append(rect(xx, yy, min(step, x + w - xx), min(step, y + h - yy), checker, 0, ""))
    for xx in range(int(x + step), int(x + w), step):
        s.append(line(xx, y, xx, y + h, grout, 1.2))
    for yy in range(int(y + step), int(y + h), step):
        s.append(line(x, yy, x + w, yy, grout, 1.2))
    return "".join(s)


def window(x, y, w, h, shine=False):
    s = rect(x, y, w, h, SKY, 2)
    s += line(x + w / 2, y, x + w / 2, y + h) + line(x, y + h / 2, x + w, y + h / 2)
    s += rect(x - 6, y + h, w + 12, 8, CREAM, 2)
    return s


def window_shine(x, y, w, h):
    return (line(x + 10, y + 24, x + 24, y + 10, "#ffffff", 3)
            + line(x + 10, y + 38, x + 36, y + 12, "#ffffff", 3)
            + line(x + w / 2 + 10, y + h / 2 + 24, x + w / 2 + 24, y + h / 2 + 10, "#ffffff", 3))


def smudges(x, y, w, h, seed):
    rnd = random.Random(seed)
    s = ""
    for i in range(6):
        cx, cy = rnd.uniform(x + 8, x + w - 8), rnd.uniform(y + 8, y + h - 8)
        s += path(blob(cx, cy, rnd.uniform(6, 13), rnd.uniform(4, 9), seed + i), "#8f8a72", "", ' opacity=".45"')
    return s


def frame(x, y, w, h, art):
    return rect(x, y, w, h, CREAM, 2) + rect(x + 6, y + 6, w - 12, h - 12, art, 1, "t")


def frame_art(x, y, w, h, hill=TEAL, sun=YELLOW):
    ix, iy, iw, ih = x + 6, y + 6, w - 12, h - 12
    return (frame(x, y, w, h, SKY)
            + circ(ix + iw * .72, iy + ih * .35, min(iw, ih) * .16, sun, "")
            + path(f"M{f(ix)} {f(iy + ih)} L{f(ix + iw * .38)} {f(iy + ih * .42)} L{f(ix + iw * .7)} {f(iy + ih)}Z", hill, ""))


def plant(x, y, s=1.0):
    """Potted plant, pot top-left at x,y."""
    return (path(blob(x + 14 * s, y - 16 * s, 16 * s, 18 * s, int(x + y), 7, .25), "#6f9d6a")
            + path(blob(x + 4 * s, y - 8 * s, 9 * s, 10 * s, int(x * 3), 6, .2), "#7fb07a")
            + path(blob(x + 24 * s, y - 6 * s, 9 * s, 10 * s, int(y * 3), 6, .2), "#7fb07a")
            + path(f"M{f(x)} {f(y)} L{f(x + 28 * s)} {f(y)} L{f(x + 24 * s)} {f(y + 26 * s)} L{f(x + 4 * s)} {f(y + 26 * s)}Z", "#b8654a"))


def crumpled(cx, cy, r, seed, fill="#ffffff"):
    return path(blob(cx, cy, r, r * .9, seed, 7, .35), fill) + path(
        f"M{f(cx - r * .5)} {f(cy - r * .1)} L{f(cx)} {f(cy + r * .3)} L{f(cx + r * .4)} {f(cy - r * .3)}", "none", "t")


def bootprints(x0, y, n, seed):
    rnd = random.Random(seed)
    s = ""
    for i in range(n):
        x = x0 + i * 30
        yy = y + (6 if i % 2 else 0) + rnd.uniform(-1, 1)
        s += ell(x, yy, 9, 4, "#6e5233", "", ' opacity=".75"') + ell(x - 13, yy, 4.5, 3.5, "#6e5233", "", ' opacity=".75"')
    return s


# ---------------------------------------------------------------- bedroom
def bed_base():
    x, y, w, h = ROOMS["bed"]
    s = rect(x, y, w, h, "#dce6f0", 0, "")
    s += planks(x, 470, w, 36)
    s += rect(x, 464, w, 6, CREAM, 0, "")
    s += window(140, 298, 96, 84)
    # bed
    s += rect(268, 372, 214, 62, BLUE, 10)
    s += rect(258, 430, 234, 30, "#7a5a3c", 4)
    s += rect(264, 458, 10, 12, "#5b412b", 0, "") + rect(476, 458, 10, 12, "#5b412b", 0, "")
    s += rect(262, 418, 226, 16, "#f4f4f0", 4)
    # nightstand + lamp
    s += rect(198, 420, 50, 44, BROWN, 3) + line(198, 440, 248, 440, OUT, 2) + circ(223, 452, 2.5, OUT, "")
    s += rect(216, 404, 16, 16, TEAL, 2)
    s += path("M206 404 L242 404 L234 378 L214 378Z", CREAM)
    return s


def bed_clean():
    s = frame_art(326, 298, 76, 54)
    s += rect(276, 398, 60, 24, "#ffffff", 10) + rect(344, 398, 60, 24, "#ffffff", 10)
    s += rect(256, 414, 238, 32, YELLOW, 6)
    s += path("M262 424 Q376 432 488 424", "none", "t")
    s += rect(418, 414, 76, 32, "#e3a92a", 6)
    s += rect(262, 464, 226, 8, SAGE, 3)
    s += window_shine(140, 298, 96, 84)
    # closed hamper
    s += rect(130, 428, 46, 40, "#c9a46a", 4) + rect(126, 422, 54, 8, "#b48d55", 3)
    s += rect(212, 412, 22, 8, RED, 1, "t")
    return s


def bed_dirt():
    room = ROOMS["bed"]
    x, y, w, h = room
    s = rect(x, y, w, h, GRIME, 0, "", ' opacity=".2"')
    s += stains(room, 11, 7)
    s += cobweb(x, y) + cobweb(x + w, y, -1, 1, 38)
    s += smudges(140, 298, 96, 84, 5)
    # crooked picture
    s += g(frame_art(326, 298, 76, 54, "#7c8f84", "#c9b067"), ' transform="rotate(-9 364 325)"')
    # pillow on bed tilted, one on floor
    s += g(rect(282, 396, 60, 24, "#e8e3d6", 10), ' transform="rotate(-14 312 408)"')
    # crumpled duvet hanging off
    s += path("M252 420 Q270 404 300 414 Q330 398 360 416 Q392 400 420 418 Q452 404 482 420 Q506 430 500 452 Q496 470 474 468 Q470 450 450 452 Q420 456 400 446 Q370 452 340 444 Q300 452 268 446 Q246 440 252 420Z", "#cfc7b3")
    s += path("M300 424 Q318 436 336 426 M380 428 Q400 440 420 430", "none", "t")
    s += g(rect(430, 448, 54, 20, "#e8e3d6", 9), ' transform="rotate(12 457 458)"')
    # nightstand clutter + dust
    s += rect(200, 417, 46, 4, "#9a958a", 0, "", ' opacity=".9"')
    s += rect(224, 404, 14, 14, "#ffffff", 2) + path("M238 408 Q246 411 238 415", "none", "t")
    s += crumpled(209, 413, 6, 3)
    # overflowing laundry basket + floor pile
    s += rect(128, 430, 48, 38, "#c9a46a", 4)
    s += line(128, 442, 176, 442, "#a8844a", 1.5) + line(128, 454, 176, 454, "#a8844a", 1.5)
    s += path(blob(152, 426, 30, 14, 41, 8, .35), RED) + path(blob(140, 420, 14, 9, 42), BLUE)
    s += path(blob(206, 466, 26, 7, 43, 8, .3), BLUE) + path(blob(232, 462, 16, 8, 44, 7, .35), "#e8e1d0")
    s += path(blob(330, 469, 10, 4, 45), "#ffffff") + path(blob(350, 470, 9, 3.5, 46), RED)
    s += dust_bunny(400, 474, 6, 1) + dust_bunny(486, 476, 5, 2)
    return s


# ---------------------------------------------------------------- bathroom
def bath_base():
    x, y, w, h = ROOMS["bath"]
    s = rect(x, y, w, h, "#d7ece6", 0, "")
    s += tiles(x, 380, w, 90, 22, "#eef6f3", "#c3dbd3")
    s += tiles(x, 470, w, 36, 18, "#eef1f2", "#cfd6d9")
    s += line(x, 380, x + w, 380, "#b9d3ca", 2)
    s += rect(596, 292, 86, 70, "#bcd9e3", 10)
    # vanity
    s += rect(584, 412, 110, 58, CREAM, 3) + line(639, 412, 639, 470, OUT, 2)
    s += circ(631, 440, 2.5, OUT, "") + circ(647, 440, 2.5, OUT, "")
    s += rect(578, 402, 122, 12, "#ffffff", 3)
    s += path("M632 402 L632 388 Q632 382 640 382 L652 382 L652 388", "none")
    # toilet
    s += rect(714, 380, 34, 36, "#ffffff", 4)
    s += path("M706 418 L754 418 Q754 440 740 446 L742 470 L718 470 L720 446 Q706 440 706 418Z", "#ffffff")
    s += line(706, 418, 754, 418)
    # tub
    s += rect(760, 418, 118, 52, "#ffffff", 14)
    s += path("M872 418 L872 402 Q872 396 864 396 L856 396", "none")
    s += line(756, 290, 884, 290, OUT, 3)
    s += line(770, 332, 846, 332, OUT, 3)
    return s


def bath_clean():
    s = line(612, 304, 632, 284, "#ffffff", 4) + line(618, 322, 650, 290, "#ffffff", 4)
    s += rect(778, 332, 28, 42, YELLOW, 3) + rect(812, 332, 28, 42, SAGE, 3)
    s += path("M850 290 L880 290 L880 410 Q870 404 864 410 Q858 404 850 410Z", SAGE)
    s += line(858, 296, 858, 404, OUT, 1.5) + line(870, 296, 870, 404, OUT, 1.5)
    s += plant(588, 376, .8)
    s += rect(676, 386, 12, 16, "#ffffff", 3)
    s += rect(770, 470, 94, 7, YELLOW, 3)
    return s


def bath_dirt():
    room = ROOMS["bath"]
    x, y, w, h = room
    s = rect(x, y, w, h, GRIME, 0, "", ' opacity=".2"')
    s += stains(room, 21, 6, "#7b7a4a", .3)
    rnd = random.Random(7)
    s += "".join(circ(rnd.uniform(846, 882), rnd.uniform(266, 330), rnd.uniform(1.5, 4), "#4b5d3a", "", ' opacity=".7"') for _ in range(22))
    s += "".join(circ(rnd.uniform(536, 600), rnd.uniform(456, 468), rnd.uniform(1, 2.6), "#4b5d3a", "", ' opacity=".6"') for _ in range(12))
    s += cobweb(x, y, 1, 1, 36)
    s += smudges(596, 292, 86, 70, 9)
    s += "".join(circ(rnd.uniform(604, 676), rnd.uniform(300, 356), rnd.uniform(1.5, 3), "#ffffff", "", ' opacity=".85"') for _ in range(14))
    s += path("M768 432 Q818 438 870 432", "none", "", ' stroke="#8a6d3b" stroke-width="3.5"')
    s += path("M712 424 Q730 432 748 424", "none", "", ' stroke="#8a6d3b" stroke-width="3"')
    # fallen curtain
    s += path("M846 290 Q858 330 846 370 Q838 410 852 440 L830 444 Q818 404 828 368 Q838 328 826 296Z", "#a9b9a7")
    s += circ(838, 340, 3, "#7b7a4a", "", ' opacity=".7"') + circ(842, 392, 4, "#7b7a4a", "", ' opacity=".7"')
    # towels: one crooked, one on the floor
    s += g(rect(780, 332, 28, 42, "#d8b44a", 3), ' transform="rotate(16 794 334)"')
    s += path(blob(700, 474, 26, 8, 51, 8, .35), "#a9c7bd")
    # toilet paper trail
    s += rect(694, 396, 12, 14, "#ffffff", 3) + path("M700 410 Q690 440 700 462 Q712 478 740 476", "none", "", ' stroke="#ffffff" stroke-width="7"')
    s += path("M700 410 Q690 440 700 462 Q712 478 740 476", "none", "t", ' opacity=".4"')
    # bottles tipped on tub edge, hair on floor
    s += g(rect(790, 404, 12, 22, "#e07a5f", 3), ' transform="rotate(68 796 415)"')
    s += rect(812, 404, 10, 16, "#7fb0c9", 3)
    s += path("M600 478 q6 -6 12 0 q6 6 12 0 M640 482 q5 -5 10 0", "none", "", ' stroke="#3f3a33" stroke-width="1.6"')
    s += crumpled(668, 396, 6, 9)
    return s


# ---------------------------------------------------------------- living room
def living_base():
    x, y, w, h = ROOMS["living"]
    s = rect(x, y, w, h, "#f1e3cf", 0, "")
    s += planks(x, 750, w, 36)
    s += rect(x, 744, w, 6, CREAM, 0, "")
    s += window(136, 572, 100, 96)
    s += line(262, 600, 262, 744) + rect(248, 742, 28, 6, OUT, 2, "")
    s += path("M244 600 L280 600 L274 576 L250 576Z", CREAM)
    s += rect(296, 640, 196, 62, TEAL, 14)
    s += rect(290, 690, 208, 34, "#6f9d8d", 8)
    s += rect(278, 670, 28, 64, "#4e7a6c", 10) + rect(482, 670, 28, 64, "#4e7a6c", 10)
    s += rect(296, 732, 8, 12, OUT, 0, "") + rect(484, 732, 8, 12, OUT, 0, "")
    s += rect(286, 744, 230, 8, "#d9b27a", 3)
    s += rect(318, 714, 150, 10, BROWN, 3) + rect(330, 724, 8, 22, BROWN, 1) + rect(448, 724, 8, 22, BROWN, 1)
    return s


def living_clean():
    s = frame_art(326, 578, 58, 44) + frame_art(400, 586, 74, 36, "#4f7394")
    s += rect(312, 650, 80, 42, "#8fbcae", 12) + rect(398, 650, 80, 42, "#8fbcae", 12)
    s += g(rect(298, 664, 26, 26, YELLOW, 6), ' transform="rotate(-10 311 677)"')
    s += rect(126, 566, 14, 112, YELLOW, 3) + rect(232, 566, 14, 112, YELLOW, 3)
    s += window_shine(136, 572, 100, 96)
    s += rect(418, 698, 14, 16, SAGE, 3) + circ(421, 694, 5, RED, "t") + circ(430, 690, 5, YELLOW, "t") + circ(426, 684, 4.5, "#ffffff", "t")
    s += rect(350, 708, 40, 6, CREAM, 1, "t") + rect(354, 702, 34, 6, BLUE, 1, "t")
    s += plant(516, 718, 1)
    return s


def living_dirt():
    room = ROOMS["living"]
    x, y, w, h = room
    s = rect(x, y, w, h, GRIME, 0, "", ' opacity=".2"')
    s += stains(room, 31, 8)
    s += cobweb(x, y, 1, 1, 44) + cobweb(x + w, y, -1, 1, 34)
    s += smudges(136, 572, 100, 96, 13)
    s += g(frame_art(326, 578, 58, 44, "#7c8f84", "#c9b067"), ' transform="rotate(8 355 600)"')
    s += g(frame_art(400, 586, 74, 36, "#5d6f80", "#c9b067"), ' transform="rotate(-6 437 604)"')
    # slumped cushions, one on the floor
    s += g(rect(314, 656, 80, 42, "#7fa598", 12), ' transform="rotate(16 354 677)"')
    s += g(rect(420, 724, 70, 30, "#7fa598", 10), ' transform="rotate(-8 455 739)"')
    # pizza box, cans, chips
    s += rect(332, 704, 70, 10, "#d9b27a", 2) + path("M332 704 L344 680 L414 680 L402 704Z", "#e6c48a")
    s += circ(360, 692, 4, RED, "", ' opacity=".8"') + circ(376, 688, 3.5, RED, "", ' opacity=".8"')
    s += rect(414, 696, 10, 18, RED, 2) + rect(428, 698, 10, 16, "#5d8fbf", 2)
    s += g(rect(150, 764, 10, 18, RED, 2), ' transform="rotate(84 155 773)"')
    s += path("M444 700 L464 696 L468 714 L446 716Z", YELLOW)
    # stains on rug, mud, papers, toys, hair
    s += path(blob(330, 748, 18, 3.5, 61), "#7a5a3c", "", ' opacity=".7"') + path(blob(470, 748, 12, 3, 62), "#7a5a3c", "", ' opacity=".6"')
    s += bootprints(128, 762, 6, 3)
    s += crumpled(214, 770, 7, 21) + crumpled(520, 772, 6, 22) + crumpled(500, 762, 5, 23)
    s += rect(226, 734, 12, 12, "#5d8fbf", 1, "t") + rect(240, 736, 10, 10, YELLOW, 1, "t") + g(rect(232, 724, 11, 11, RED, 1, "t"), ' transform="rotate(14 237 729)"')
    s += dust_bunny(300, 770, 6, 4) + dust_bunny(400, 776, 7, 5) + dust_bunny(540, 760, 5, 6)
    return s


# ---------------------------------------------------------------- kitchen
def kitchen_base():
    x, y, w, h = ROOMS["kitchen"]
    s = rect(x, y, w, h, "#f7efd5", 0, "")
    s += tiles(576, 620, 240, 60, 20, "#fbfaf4", "#e6dfc6")
    s += tiles(x, 750, w, 36, 18, "#eef1f2", "#cfd6d9", "#dde3e6")
    s += rect(584, 566, 108, 50, SAGE, 3) + line(638, 566, 638, 616, OUT, 2) + circ(630, 604, 2.5, OUT, "") + circ(646, 604, 2.5, OUT, "")
    s += rect(726, 534, 16, 40, "#c7cfd2", 0) + path("M704 598 L764 598 L754 572 L714 572Z", "#c7cfd2")
    s += rect(816, 594, 62, 156, "#e6ebee", 6) + line(816, 642, 878, 642, OUT, 2)
    s += line(826, 604, 826, 630, OUT, 3) + line(826, 652, 826, 690, OUT, 3)
    s += rect(584, 690, 124, 60, SAGE, 3) + line(646, 690, 646, 750, OUT, 2) + circ(638, 712, 2.5, OUT, "") + circ(654, 712, 2.5, OUT, "")
    s += rect(708, 680, 58, 70, "#e6ebee", 3) + rect(716, 700, 42, 28, "#3d5a63", 3)
    s += circ(720, 690, 2.5, OUT, "") + circ(732, 690, 2.5, OUT, "") + circ(744, 690, 2.5, OUT, "") + circ(756, 690, 2.5, OUT, "")
    s += line(716, 736, 758, 736, OUT, 3)
    s += rect(766, 690, 46, 60, SAGE, 3) + circ(774, 712, 2.5, OUT, "")
    s += rect(578, 680, 130, 12, "#3d5a63", 3) + rect(766, 680, 50, 12, "#3d5a63", 3)
    s += rect(712, 676, 18, 4, OUT, 1, "") + rect(744, 676, 18, 4, OUT, 1, "")
    s += path("M626 680 L626 660 Q626 650 636 650 L648 650 Q656 650 656 658", "none")
    return s


def kitchen_clean():
    s = plant(650, 566, .8)
    s += path("M590 680 Q590 664 614 664 Q638 664 638 680Z", "#ffffff")
    s += circ(604, 664, 6, RED, "t") + circ(616, 660, 6, YELLOW, "t") + circ(626, 665, 5.5, "#7fb07a", "t")
    s += path("M718 676 Q716 656 734 654 Q752 656 750 676Z", RED) + path("M750 664 L760 658", "none")
    s += rect(722, 732, 16, 22, YELLOW, 2)
    s += line(736, 588, 746, 578, "#ffffff", 3) + line(830, 608, 840, 598, "#ffffff", 3)
    s += rect(778, 662, 22, 18, "#ffffff", 3) + line(778, 670, 800, 670, OUT, 1.5)
    return s


def kitchen_dirt():
    room = ROOMS["kitchen"]
    x, y, w, h = room
    s = rect(x, y, w, h, GRIME, 0, "", ' opacity=".22"')
    s += stains(room, 41, 5)
    rnd = random.Random(17)
    s += "".join(circ(rnd.uniform(580, 812), rnd.uniform(624, 676), rnd.uniform(1.5, 4.5), "#a98a4c", "", ' opacity=".75"') for _ in range(34))
    s += "".join(circ(rnd.uniform(708, 762), rnd.uniform(576, 598), rnd.uniform(1.5, 3.5), "#8a6d3b", "", ' opacity=".8"') for _ in range(12))
    s += cobweb(x + w, y, -1, 1, 40)
    # dishes piled by the sink
    for i, (px, py, rot) in enumerate([(612, 676, -6), (616, 670, 8), (610, 664, -12), (618, 658, 5), (614, 652, -4)]):
        s += g(ell(px, py, 22, 4.5, "#ffffff"), f' transform="rotate({rot} {px} {py})"')
    s += circ(608, 664, 2, "#8a6d3b", "") + circ(624, 670, 2, "#8a6d3b", "")
    s += rect(640, 662, 14, 18, "#e07a5f", 3) + path("M654 666 Q662 670 654 676", "none", "t")
    # crusted pan on the stove
    s += rect(712, 668, 40, 10, "#3d5a63", 3) + line(752, 672, 774, 668, OUT, 4)
    s += path(blob(726, 666, 9, 4, 71), "#5b412b") + path(blob(740, 665, 6, 3, 72), "#5b412b")
    # tipped cereal box, sticky notes, fridge drips
    s += g(rect(774, 664, 34, 16, YELLOW, 2), ' transform="rotate(-8 790 672)"') + "".join(circ(812 + i * 3, 678, 1.6, "#c99a52", "") for i in range(-6, 1))
    for i, (nx, ny, r) in enumerate([(838, 606, -10), (854, 612, 14), (842, 660, 6), (858, 700, -16)]):
        s += g(rect(nx, ny, 14, 14, "#f6e27a", 1, "t"), f' transform="rotate({r} {nx + 7} {ny + 7})"')
    s += path("M830 650 Q832 668 828 690", "none", "", ' stroke="#a98a4c" stroke-width="3" opacity=".7"')
    # spill + overflowing trash with flies
    s += path(blob(640, 772, 34, 7, 81, 9, .25), "#c9b27a", "", ' opacity=".85"')
    s += path("M770 776 Q764 748 774 734 Q790 722 806 734 Q816 748 810 776Z", "#4a5458")
    s += path("M780 734 L784 724 L792 732 M798 730 L804 720 L806 732", "none", "t")
    s += crumpled(760, 774, 6, 31) + g(rect(820, 768, 16, 8, RED, 2), ' transform="rotate(10 828 772)"')
    s += flies(790, 712, 3)
    s += dust_bunny(590, 780, 5, 7)
    return s


# ---------------------------------------------------------------- outside
def outside_base():
    s = rect(0, 0, W, H, SKY, 0, "", ' class="sky"')
    s += f'<g class="sun">{circ(846, 128, 44, YELLOW)}</g>'
    s += path("M120 126 Q140 96 176 112 Q196 92 224 110 Q252 108 250 130 Z", "#ffffff", "", ' opacity=".9"')
    s += rect(0, 806, W, 74, "#9cc38a", 0, "")
    s += path("M0 806 L1000 806", "none", "", ' stroke="#7ea86d" stroke-width="3"')
    s += rect(690, 108, 50, 120, "#b8654a", 0) + rect(684, 100, 62, 14, "#9e5340", 2)
    s += path("M66 264 L500 60 L934 264Z", "#3d5a63")
    for yy in (130, 175, 220):
        k = (yy - 60) / 204
        s += line(500 - 434 * k + 8, yy, 500 + 434 * k - 8, yy, "#2f4850", 2)
    s += path("M142 250 L500 98 L858 250Z", "#e8dcc6", "")
    s += circ(500, 190, 26, SKY) + line(474, 190, 526, 190, OUT, 2) + line(500, 164, 500, 216, OUT, 2)
    s += rect(100, 250, 800, 556, "#8fa6a0", 0)
    s += rect(90, 798, 820, 14, "#5e6b6d", 2)
    for cx, cy, r in ((44, 800, 26), (78, 806, 20), (930, 802, 24), (962, 806, 20)):
        s += circ(cx, cy, r, "#6f9d6a")
    return s


def outside_clean():
    rnd = random.Random(5)
    s = ""
    for _ in range(14):
        cx = rnd.choice([rnd.uniform(26, 96), rnd.uniform(910, 980)])
        s += circ(cx, rnd.uniform(784, 812), 3.2, rnd.choice([YELLOW, "#ffffff", "#e9a0a0"]), "", ' class="bloom"')
    return s


def outside_dirt():
    s = rect(0, 0, W, 806, "#b8b09c", 0, "", ' opacity=".62"')
    s += path("M40 150 Q70 110 120 128 Q150 96 200 120 Q240 112 246 146 Q250 170 220 168 L60 168 Q30 166 40 150Z", "#9d9886")
    s += path("M640 70 Q670 40 720 58 Q760 34 800 60 Q850 56 852 88 Q850 108 820 106 L660 106 Q630 102 640 70Z", "#9d9886")
    s += path("M780 160 Q806 136 846 150 Q880 140 896 166 L790 172 Q770 172 780 160Z", "#a7a291")
    rnd = random.Random(9)
    for i in range(16):
        xx = rnd.choice([rnd.uniform(102, 112), rnd.uniform(888, 898), rnd.uniform(110, 890)])
        yy = rnd.choice([rnd.uniform(252, 262), rnd.uniform(508, 532), rnd.uniform(788, 798)])
        s += path(f"M{f(xx)} {f(yy)} q2 10 -1 22", "none", "", ' stroke="#5d5640" stroke-width="2.5" opacity=".55"')
    s += cobweb(142, 250, 1, -1, 40)
    for i in range(10):
        cx = rnd.uniform(110, 890)
        s += path(blob(cx, rnd.uniform(812, 840), 7, 3, 90 + i), rnd.choice(["#a07a3c", "#8a6230", "#b48a4c"]), "", ' opacity=".9"')
    s += rect(0, 806, W, 74, "#a3a07a", 0, "", ' opacity=".6"')
    return s


DRAW = {
    "bed": (bed_base, bed_clean, bed_dirt),
    "bath": (bath_base, bath_clean, bath_dirt),
    "living": (living_base, living_clean, living_dirt),
    "kitchen": (kitchen_base, kitchen_clean, kitchen_dirt),
}

STYLE = (
    f".o{{stroke:{OUT};stroke-width:3;stroke-linejoin:round;stroke-linecap:round}}"
    f".t{{stroke:{OUT};stroke-width:1.6;stroke-linejoin:round;stroke-linecap:round}}"
)


def squeegee(name):
    x, y, w, h = ROOMS[name]
    return (
        f'<g class="sq" id="sq-{name}" opacity="0">'
        + rect(-16, -4, 16, h + 8, "#ffffff", 0, "", ' opacity=".35"')
        + rect(-10, -10, 10, h + 20, YELLOW, 3)
        + rect(0, -12, 5, h + 24, OUT, 2, "")
        + rect(-96, h / 2 - 7, 88, 14, "#3d5a63", 7)
        + rect(-104, h / 2 - 9, 26, 18, OUT, 8, "")
        + "</g>"
    )


def scene(animated=True, view=None, title="A house cutaway with a kitchen, bathroom, bedroom and living room"):
    """animated=True builds the dirty-to-clean scroll version, False a clean static picture."""
    vb = view or (0, 0, W, H)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(f(v) for v in vb)}" role="img" aria-labelledby="scene-t">',
             f'<title id="scene-t">{title}</title>', f"<style>{STYLE}</style>"]
    if animated:
        defs = ["<defs>"]
        for name, (x, y, w, h) in ROOMS.items():
            defs.append(f'<mask id="md-{name}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
                        + rect(x, y, w, h, "#fff", 0, "") + f'<rect class="wd" id="wd-{name}" x="{x}" y="{y}" width="0" height="{h}" fill="#000"/></mask>')
            defs.append(f'<mask id="mc-{name}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
                        + f'<rect class="wc" id="wc-{name}" x="{x}" y="{y}" width="0" height="{h}" fill="#fff"/></mask>')
        defs.append("</defs>")
        parts.append("".join(defs))
    parts.append(outside_base())
    if animated:
        parts.append(f'<g class="dirt-out" id="outside-dirt">{outside_dirt()}</g>')
    parts.append(f'<g class="bloomset" id="outside-clean" opacity="0">{outside_clean()}</g>' if animated else outside_clean())
    for name, (base, clean, dirt) in DRAW.items():
        x, y, w, h = ROOMS[name]
        parts.append(f'<g id="room-{name}">')
        parts.append(base())
        if animated:
            parts.append(f'<g class="clean" mask="url(#mc-{name})">{clean()}</g>')
            parts.append(f'<g class="dirt" mask="url(#md-{name})">{dirt()}</g>')
        else:
            parts.append(clean())
        parts.append(rect(x, y, w, h, "none", 0))
        parts.append("</g>")
    if animated:
        parts.extend(squeegee(n) for n in ROOMS)
    parts.append("</svg>")
    return "".join(parts)


CROPS = {
    "kitchen": ((556, 524, 342, 272), "Illustrated kitchen with a clean counter, stove and fridge"),
    "bath": ((518, 252, 380, 264), "Illustrated bathroom with a clean tub, toilet and vanity"),
    "bed": ((102, 252, 416, 264), "Illustrated bedroom with a made bed and nightstand"),
    "living": ((102, 524, 464, 272), "Illustrated living room with a tidy couch and coffee table"),
}
