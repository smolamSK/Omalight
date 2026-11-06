#!/usr/bin/env python3
"""Draws the Omalight graphics as SVG and renders them to PNG.

Run from the repo root:  python3 docs/build_graphics.py
Needs rsvg-convert (librsvg). Colours come from the Omarchy theme used at the
time of drawing, so the images match the look of the popup.
"""
import os
import subprocess
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Omarchy theme colours (Tokyo-style dark theme used for the screenshots)
BG = "#0B0C16"
FG = "#DDF7FF"
ACCENT = "#82FB9C"
ACTIVE = "#50F872"
EDGE_A = "#26A269"
EDGE_B = "#2EC27E"
MUTED = "#6A6E95"
LIGHT = "#FFCE96"   # warm light, about 4000 K
FONT = "JetBrainsMono Nerd Font, JetBrains Mono, monospace"
BULB = "\U000F0335"  # nf-md-lightbulb (Nerd Font)


def svg_doc(w, h, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" font-family="{FONT}">'
            f'<defs>{defs}</defs>'
            f'<rect width="{w}" height="{h}" fill="{BG}"/>{body}</svg>')


def text(x, y, s, size=14, fill=FG, weight="normal", opacity=1.0, anchor="start", spacing=0):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'opacity="{opacity}" text-anchor="{anchor}" letter-spacing="{spacing}">{s}</text>')


def edge_glow(w, h, band=120):
    """Warm light along all four screen edges, fading inward."""
    defs = (
        f'<linearGradient id="gt" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{LIGHT}" stop-opacity="0.75"/>'
        f'<stop offset="1" stop-color="{LIGHT}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="gb" x1="0" y1="1" x2="0" y2="0">'
        f'<stop offset="0" stop-color="{LIGHT}" stop-opacity="0.75"/>'
        f'<stop offset="1" stop-color="{LIGHT}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="gl" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{LIGHT}" stop-opacity="0.75"/>'
        f'<stop offset="1" stop-color="{LIGHT}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="gr" x1="1" y1="0" x2="0" y2="0">'
        f'<stop offset="0" stop-color="{LIGHT}" stop-opacity="0.75"/>'
        f'<stop offset="1" stop-color="{LIGHT}" stop-opacity="0"/></linearGradient>'
    )
    body = (
        f'<rect x="0" y="0" width="{w}" height="{band}" fill="url(#gt)"/>'
        f'<rect x="0" y="{h - band}" width="{w}" height="{band}" fill="url(#gb)"/>'
        f'<rect x="0" y="0" width="{band}" height="{h}" fill="url(#gl)"/>'
        f'<rect x="{w - band}" y="0" width="{band}" height="{h}" fill="url(#gr)"/>'
    )
    return defs, body


def slider(x, y, w, frac, label, value):
    """Label and value on one line, a rounded track below, a knob on the fill."""
    fill_w = w * frac
    body = text(x, y, label, size=11, opacity=0.6, spacing=0.8)
    body += text(x + w, y, value, size=11, anchor="end")
    body += f'<rect x="{x}" y="{y + 10}" width="{w}" height="4" rx="2" fill="{FG}" fill-opacity="0.18"/>'
    body += f'<rect x="{x}" y="{y + 10}" width="{fill_w:.1f}" height="4" rx="2" fill="{FG}"/>'
    body += (f'<rect x="{x + fill_w - 6:.1f}" y="{y + 6}" width="12" height="12" rx="6" '
             f'fill="{FG}" stroke="{BG}" stroke-width="2"/>')
    return body


def toggle(x, y, on):
    """Boxy switch: square track, square knob, matches the kit's sharp corners."""
    track_fill = FG if on else BG
    body = (f'<rect x="{x}" y="{y}" width="44" height="22" fill="{BG}" '
            f'stroke="{FG}" stroke-opacity="0.4" stroke-width="1"/>')
    if on:
        body += f'<rect x="{x + 1}" y="{y + 1}" width="42" height="20" fill="{FG}" fill-opacity="0.18"/>'
        body += f'<rect x="{x + 24}" y="{y + 4}" width="16" height="14" fill="{FG}"/>'
    else:
        body += f'<rect x="{x + 4}" y="{y + 4}" width="16" height="14" fill="{FG}"/>'
    return body


def popup(x, y, scale=1.0, on=True, brightness=70, width=28, warmth=4000, pointer=True):
    """The control popup, drawn with the same parts as the live card."""
    s = scale
    W, H = 300 * s, 316 * s
    pad = 14 * s
    defs = (f'<linearGradient id="pg" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{EDGE_A}"/><stop offset="1" stop-color="{EDGE_B}"/>'
            f'</linearGradient>')
    body = f'<rect x="{x}" y="{y}" width="{W}" height="{H}" fill="url(#pg)"/>'
    body += f'<rect x="{x + 2 * s}" y="{y + 2 * s}" width="{W - 4 * s}" height="{H - 4 * s}" fill="{BG}"/>'
    cx = x + pad + 2 * s
    cw = W - 2 * (pad + 2 * s)
    # hero
    body += text(cx, y + 36 * s, BULB, size=22 * s, fill=FG, opacity=1.0 if on else 0.6)
    body += text(cx + 34 * s, y + 30 * s, "Omalight", size=15 * s, weight="bold")
    status = f"On · {brightness}% · {warmth}K" if on else "Off"
    body += text(cx + 34 * s, y + 46 * s, status, size=10.5 * s, opacity=0.6)
    body += toggle(x + W - pad - 2 * s - 44 * s, y + 24 * s, on).replace('44"', f'{44 * s}"')
    body += f'<rect x="{cx}" y="{y + 66 * s}" width="{cw}" height="1" fill="{FG}" fill-opacity="0.14"/>'
    body += text(cx, y + 90 * s, "LIGHT", size=10 * s, opacity=0.6, spacing=1.2)
    body += slider(cx, y + 110 * s, cw, brightness / 100, "Brightness", f"{brightness}%")
    body += slider(cx, y + 160 * s, cw, (width - 4) / 116, "Width", f"{width} px")
    body += slider(cx, y + 210 * s, cw, (warmth - 2700) / 3800, "Warmth", f"{warmth} K")
    body += f'<rect x="{cx}" y="{y + 252 * s}" width="{cw}" height="1" fill="{FG}" fill-opacity="0.14"/>'
    hint = "On now. Drag the sliders to change it." if on else \
        "Off. Switch it on to light your face. The screen goes to full brightness."
    body += text(cx, y + 280 * s, hint[:44], size=10.5 * s, opacity=0.7)
    if len(hint) > 44:
        body += text(cx, y + 296 * s, hint[44:], size=10.5 * s, opacity=0.7)
    # pointer down to the bulb on the bottom bar
    if pointer:
        body += (f'<polygon points="{x + W - 40 * s},{y + H} {x + W - 28 * s},{y + H} '
                 f'{x + W - 34 * s},{y + H + 8 * s}" fill="{EDGE_B}"/>')
    return defs, body


def bottom_bar(w, y, h=26, bulb_on=True):
    body = f'<rect x="0" y="{y}" width="{w}" height="{h}" fill="{BG}"/>'
    body += f'<rect x="0" y="{y}" width="{w}" height="1" fill="{FG}" fill-opacity="0.15"/>'
    body += text(w - 60, y + 18, BULB, size=15, fill=ACCENT if bulb_on else FG, opacity=1 if bulb_on else 0.6)
    return body


def write(name, svg, out_png, out_w=None):
    svg_path = os.path.join(HERE, name + ".svg")
    png_path = out_png
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)
    cmd = ["rsvg-convert", "-o", png_path]
    if out_w:
        cmd += ["-w", str(out_w)]
    subprocess.run(cmd + [svg_path], check=True)
    print("wrote", os.path.relpath(png_path, ROOT), os.path.relpath(svg_path, ROOT))


# 1. Hero preview, shown first on the marketplace (1280x720)
def hero():
    W, H = 1280, 720
    gdefs, gbody = edge_glow(W, H, band=130)
    body = gbody
    body += text(70, 120, "Omalight", size=64, weight="bold")
    body += text(72, 166, "A soft edge light for video calls. Built for Omarchy.", size=24, opacity=0.7)
    # a stand-in video call window
    body += (f'<rect x="120" y="230" width="640" height="370" fill="none" stroke="{FG}" '
             f'stroke-opacity="0.15"/>')
    body += (f'<rect x="120" y="230" width="640" height="34" fill="{FG}" fill-opacity="0.06"/>')
    body += text(140, 253, "Video call", size=14, opacity=0.6)
    body += f'<circle cx="440" cy="400" r="92" fill="{FG}" fill-opacity="0.08"/>'
    body += f'<ellipse cx="440" cy="560" rx="150" ry="110" fill="{FG}" fill-opacity="0.08"/>'
    pdefs, pbody = popup(959, 362, scale=1.0, on=True, brightness=70, width=28, warmth=4000)
    body += pbody
    body += bottom_bar(W, H - 26, bulb_on=True)
    write("hero", svg_doc(W, H, body, gdefs + pdefs), os.path.join(ROOT, "preview.png"))


# 2. Annotated popup, what each control does (1100x640)
def controls():
    W, H = 1100, 640
    sc, px, py = 1.45, 600, 90
    pdefs, pbody = popup(px, py, scale=sc, on=True, brightness=70, width=28, warmth=4000, pointer=False)
    body = pbody
    # badge sits just left of each control, on the card edge
    rows = [(24, "1"), (46, "2"), (118, "3"), (168, "4"), (218, "5"), (290, "6")]
    for dy, num in rows:
        cy = py + dy * sc
        bx = px - 36
        body += f'<rect x="{bx}" y="{cy - 12}" width="26" height="26" fill="{ACCENT}"/>'
        body += text(bx + 13, cy + 6, num, size=15, weight="bold", fill=BG, anchor="middle")
    notes = [
        ("1", "Power switch", "Turns the light on or off."),
        ("2", "Status line", "On or Off, with brightness and warmth."),
        ("3", "Brightness", "How strong the light is, 0 to 100%."),
        ("4", "Width", "How thick the edge band is, 4 to 120 px."),
        ("5", "Warmth", "Warm 2700 K to cool 6500 K."),
        ("6", "Hint", "What you can do next."),
    ]
    body += text(40, 80, "What each control does", size=24, weight="bold")
    for i, (num, title, desc) in enumerate(notes):
        yy = 150 + i * 80
        body += f'<rect x="40" y="{yy - 24}" width="26" height="26" fill="{ACCENT}"/>'
        body += text(53, yy - 5, num, size=15, weight="bold", fill=BG, anchor="middle")
        body += text(84, yy - 4, title, size=18, weight="bold")
        body += text(84, yy + 18, desc, size=14, opacity=0.7)
    write("controls", svg_doc(W, H, body, pdefs), os.path.join(ROOT, "docs", "controls.png"))


# 3. How it works (1280x640)
def how_it_works():
    W, H = 1280, 680
    body = text(50, 70, "How Omalight works", size=34, weight="bold")
    body += text(52, 104, "One click on the bottom bar, and the light covers every screen edge.", size=17, opacity=0.7)
    steps = [
        ("1", "Bottom-bar icon", "Click the lightbulb, or press SUPER + ALT + P."),
        ("2", "Control popup", "Opens above the icon. Power, brightness, width, warmth."),
        ("3", "Service", "Holds the state and saves your settings to a file."),
        ("4", "Edge light", "A click-through glow on each screen's edges."),
    ]
    bw, bh, gap = 270, 170, 40
    x0, y0 = 50, 150
    for i, (num, title, desc) in enumerate(steps):
        x = x0 + i * (bw + gap)
        body += f'<rect x="{x}" y="{y0}" width="{bw}" height="{bh}" fill="none" stroke="{FG}" stroke-opacity="0.25"/>'
        body += f'<rect x="{x}" y="{y0}" width="{bw}" height="4" fill="{ACCENT}"/>'
        body += text(x + 18, y0 + 44, num, size=28, weight="bold", fill=ACCENT)
        body += text(x + 52, y0 + 44, title, size=20, weight="bold")
        for j, line in enumerate(textwrap.wrap(desc, width=24)):
            body += text(x + 18, y0 + 84 + j * 22, line, size=14, opacity=0.75)
        if i < len(steps) - 1:
            ax = x + bw + 6
            body += (f'<polygon points="{ax},{y0 + bh / 2 - 9} {ax + 16},{y0 + bh / 2} '
                     f'{ax},{y0 + bh / 2 + 9}" fill="{FG}" fill-opacity="0.5"/>')
    # side facts
    fy = 380
    body += text(50, fy, "What it touches on your system", size=20, weight="bold")
    facts = [
        "Brightness: sets the screen to 100% when the light turns on (omarchy brightness).",
        "Theme: reads your Omarchy colours so the popup matches the theme you use.",
        "Settings: saved to ~/.config/omarchy/edge-light/settings.json, nothing else.",
        "Network: none. No camera, no microphone, no video is read.",
    ]
    for i, f in enumerate(facts):
        body += f'<rect x="50" y="{fy + 26 + i * 40 - 14}" width="8" height="8" fill="{ACCENT}"/>'
        body += text(72, fy + 26 + i * 40, f, size=15, opacity=0.85)
    # shortcuts strip
    sy = 618
    body += f'<rect x="50" y="{sy - 28}" width="1180" height="1" fill="{FG}" fill-opacity="0.15"/>'
    body += text(50, sy, "SHORTCUTS", size=13, opacity=0.6, spacing=1.2)
    body += text(220, sy, "SUPER + ALT + E", size=16, weight="bold", fill=ACCENT)
    body += text(420, sy, "turn the light on or off", size=15, opacity=0.8)
    body += text(760, sy, "SUPER + ALT + P", size=16, weight="bold", fill=ACCENT)
    body += text(960, sy, "open the popup", size=15, opacity=0.8)
    write("how-it-works", svg_doc(W, H, body), os.path.join(ROOT, "docs", "how-it-works.png"))


if __name__ == "__main__":
    hero()
    controls()
    how_it_works()
