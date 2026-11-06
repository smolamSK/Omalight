#!/usr/bin/env python3
"""Builds the Omalight graphics: HTML pages rendered to PNG with headless Chromium.

Run from the repo root:  python3 docs/build_graphics.py
Needs the Python package `playwright` with its Chromium build.

Design rules come from the global design skills (landing-page-design and
minimalist-ui): a fixed spacing scale, Tailwind type steps, flat backgrounds,
no italics, no ultra bold, no hyphens in copy, balanced headings, and a
geometric sans with a monospace for numbers and keystrokes. The popup mock
keeps Omarchy's own monospace and colours, because it depicts the real UI.
"""
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Chrome palette (flat, from the skill's dark list and neutral greys)
BG = "#181818"
CARD = "#1F1F1F"
LINE = "#313131"
LINE_SOFT = "#272727"
MUTED = "#9B9B9B"
WHITE = "#FFFFFF"
# Product colours (Omarchy theme, as shown in the popup)
OMA_BG = "#0B0C16"
OMA_FG = "#DDF7FF"
OMA_EDGE_A = "#26A269"
OMA_EDGE_B = "#2EC27E"
OMA_ACTIVE = "#50F872"
WARM = "#FFCE96"  # the light itself, about 4000 K

BASE_CSS = f"""
:root {{
  --bg: {BG}; --card: {CARD}; --line: {LINE}; --line-soft: {LINE_SOFT};
  --muted: {MUTED}; --white: {WHITE}; --warm: {WARM}; --active: {OMA_ACTIVE};
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ background: var(--bg); color: var(--white); }}
body {{
  font-family: "Instrument Sans", system-ui, sans-serif;
  font-size: 16px; line-height: 24px; font-weight: 400;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}}
.mono {{ font-family: "JetBrains Mono", monospace; }}
p {{ text-wrap: pretty; color: var(--muted); }}
h1, h2, h3 {{ text-wrap: balance; font-weight: 500; }}
h1 {{
  font-size: 60px; line-height: 60px; letter-spacing: -0.04em;
  background: linear-gradient(90deg, #FFFFFF, #9B9B9B);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}}
h2 {{ font-size: 36px; line-height: 40px; letter-spacing: -0.02em; color: var(--white); }}
h3 {{ font-size: 20px; line-height: 28px; color: var(--white); }}
.eyebrow {{
  font-size: 12px; line-height: 16px; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--muted);
}}
.lead {{ font-size: 20px; line-height: 28px; color: var(--muted); }}
.small {{ font-size: 14px; line-height: 20px; }}
.caption {{ font-size: 12px; line-height: 16px; color: var(--muted); }}
.card {{ background: var(--card); border: 1px solid var(--line); border-radius: 8px; }}
kbd {{
  font-family: "JetBrains Mono", monospace; font-size: 14px; line-height: 20px;
  color: var(--white); background: var(--bg); border: 1px solid var(--line);
  border-radius: 4px; padding: 8px 12px;
}}
"""

# The control popup, drawn the way Omarchy draws it: square corners, a 2px
# gradient border, the popup background, JetBrains Mono, and the theme's
# control alphas. Sizes are the real popup sizes at scale 1.
def popup_html(on=True, brightness=70, width=28, warmth=4000, hint=None, badges=None):
    badges = badges or {}
    def badge(key, side="left", top=0):
        # Badges hang off their own row, so they stay aligned with it.
        if key not in badges:
            return ""
        pos = "left:-36px" if side == "left" else "right:-36px"
        return f'<span class="badge" style="{pos};top:{top}px">{key}</span>'
    status = f"On &middot; {brightness}% &middot; {warmth}K" if on else "Off"
    hint = hint or ("On now. Drag the sliders to change it." if on else
                    "Off. Switch it on to light your face. The screen goes to full brightness.")
    def slider(label, value_txt, frac, key):
        return f"""
        <div class="slider-row">{badge(key, top=8)}
        <div class="row-label"><span>{label}</span><span>{value_txt}</span></div>
        <div class="track"><div class="fill" style="width:{frac*100:.1f}%"></div>
          <div class="knob" style="left:{frac*100:.1f}%"></div></div></div>"""
    return f"""
    <div class="omcard">
      <div class="hero">
        <span class="bulb {'on' if on else ''}">&#xF0335;</span>
        <div class="title-col"><div class="name">Omalight</div><div class="status">{status}</div></div>
        <div class="switch {'on' if on else ''}"><span class="sw-knob"></span></div>
        {badge('1', side='right', top=10)}
        {badge('2', top=10)}
      </div>
      <div class="rule"></div>
      <div class="section">LIGHT</div>
      {slider('Brightness', f'{brightness}%', brightness/100, '3')}
      {slider('Width', f'{width} px', (width-4)/116, '4')}
      {slider('Warmth', f'{warmth} K', (warmth-2700)/3800, '5')}
      <div class="rule"></div>
      <div class="hint-row">{badge('6', top=0)}<div class="hint">{hint}</div></div>
    </div>"""

POPUP_CSS = f"""
.omcard {{
  position: relative; width: 300px; padding: 14px;
  background: {OMA_BG};
  border: 2px solid transparent;
  background-image: linear-gradient({OMA_BG}, {OMA_BG}), linear-gradient(90deg, {OMA_EDGE_A}, {OMA_EDGE_B});
  background-origin: border-box; background-clip: padding-box, border-box;
  font-family: "JetBrains Mono", monospace; color: {OMA_FG};
  border-radius: 0;
}}
.omcard .hero {{ position: relative; display: flex; align-items: center; height: 44px; }}
.omcard .bulb {{ font-size: 22px; opacity: 0.6; width: 30px; font-family: "JetBrains Mono", "Symbols Nerd Font", monospace; }}
.omcard .bulb.on {{ opacity: 1; }}
.omcard .title-col {{ flex: 1; margin-left: 4px; }}
.omcard .name {{ font-size: 15px; font-weight: 700; line-height: 18px; }}
.omcard .status {{ font-size: 10.5px; line-height: 14px; opacity: 0.6; margin-top: 2px; }}
.omcard .switch {{
  width: 44px; height: 22px; border: 1px solid rgba(221,247,255,0.4); position: relative;
  background: {OMA_BG};
}}
.omcard .switch .sw-knob {{ position: absolute; top: 3px; left: 3px; width: 16px; height: 14px; background: {OMA_FG}; }}
.omcard .switch.on {{ background: rgba(221,247,255,0.18); }}
.omcard .switch.on .sw-knob {{ left: 25px; }}
.omcard .rule {{ height: 1px; background: rgba(221,247,255,0.14); margin: 10px 0; }}
.omcard .section {{ font-size: 10px; letter-spacing: 1.2px; opacity: 0.6; margin: 4px 0 8px; }}
.omcard .row-label {{ display: flex; justify-content: space-between; font-size: 12px; line-height: 16px; margin-top: 10px; }}
.omcard .track {{ position: relative; height: 4px; margin: 12px 0 0; background: rgba(221,247,255,0.18); }}
.omcard .fill {{ position: absolute; left: 0; top: 0; bottom: 0; background: {OMA_FG}; }}
.omcard .knob {{ position: absolute; top: -4px; width: 12px; height: 12px; margin-left: -6px; border-radius: 6px; background: {OMA_FG}; border: 2px solid {OMA_BG}; }}
.omcard .slider-row {{ position: relative; }}
.omcard .hint-row {{ position: relative; }}
.omcard .title-col {{ position: relative; }}
.omcard .hint {{ font-size: 10.5px; line-height: 16px; opacity: 0.7; margin-top: 4px; }}
.badge {{
  position: absolute; width: 24px; height: 24px;
  display: flex; align-items: center; justify-content: center;
  background: #82FB9C; color: #0B0C16; font: 600 13px/1 "Instrument Sans", sans-serif;
}}
"""

def page(body_html, width, height, extra_css=""):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>{BASE_CSS}{POPUP_CSS}{extra_css}
html, body {{ width: {width}px; height: {height}px; overflow: hidden; }}
</style></head><body>{body_html}</body></html>"""


# 1. Hero preview, the marketplace's first image (1280 by 720)
def hero_html():
    glow_css = f"""
    .screen {{ position: absolute; left: 600px; top: 56px; width: 616px; height: 608px;
      background: {OMA_BG}; border: 1px solid {LINE}; overflow: hidden; }}
    .glow {{ position: absolute; background: {WARM}; filter: blur(36px); opacity: 0.8; }}
    .glow.t {{ left: -40px; right: -40px; top: -90px; height: 120px; }}
    .glow.b {{ left: -40px; right: -40px; bottom: -90px; height: 120px; }}
    .glow.l {{ top: -40px; bottom: -40px; left: -90px; width: 120px; }}
    .glow.r {{ top: -40px; bottom: -40px; right: -90px; width: 120px; }}
    .call {{ position: absolute; left: 40px; top: 40px; width: 400px; height: 360px;
      border: 1px solid {LINE_SOFT}; background: #111216; overflow: hidden; }}
    .call .head {{ height: 36px; border-bottom: 1px solid {LINE_SOFT}; padding: 10px 14px;
      font-size: 12px; color: {MUTED}; }}
    .call .face {{ position: absolute; left: 130px; top: 84px; width: 140px; height: 140px; border-radius: 70px; background: #23252d; }}
    .call .body {{ position: absolute; left: 90px; top: 236px; width: 220px; height: 124px; border-radius: 110px 110px 0 0; background: #23252d; }}
    .bar {{ position: absolute; left: 0; right: 0; bottom: 0; height: 26px; background: {OMA_BG};
      border-top: 1px solid rgba(221,247,255,0.15); }}
    .bar .bulb {{ position: absolute; right: 22px; top: 4px; font-family: "JetBrains Mono", "Symbols Nerd Font", monospace;
      font-size: 15px; color: {OMA_ACTIVE}; }}
    .pop {{ position: absolute; right: 44px; bottom: 44px; }}
    """
    html = f"""
    <div class="wrap">
      <section class="copy">
        <div class="eyebrow">Omarchy plugin</div>
        <h1>Light your face on every video call</h1>
        <p class="lead">Omalight glows along the edges of your screen, so you look good without
          moving a lamp. One click on the bottom bar sets the brightness, width, and warmth.</p>
        <div class="install card">
          <div class="caption">Install in one command</div>
          <code class="mono">omarchy plugin add<br>https://github.com/vaibhavgupta5/Omalight.git<br>--enable --yes</code>
        </div>
        <div class="chips">
          <span>Reads no camera or video</span><span>No network access</span><span>MIT license</span>
        </div>
      </section>
      <div class="screen">
        <div class="glow t"></div><div class="glow b"></div><div class="glow l"></div><div class="glow r"></div>
        <div class="call"><div class="head">Video call</div><div class="face"></div><div class="body"></div></div>
        <div class="pop">{popup_html(on=True, brightness=70, width=28, warmth=4000)}</div>
        <div class="bar"><span class="bulb">&#xF0335;</span></div>
      </div>
    </div>"""
    css = f"""
    .wrap {{ position: relative; width: 1280px; height: 720px; }}
    .copy {{ position: absolute; left: 64px; top: 80px; width: 480px; }}
    .copy .eyebrow {{ margin-bottom: 16px; }}
    .copy h1 {{ margin-bottom: 24px; }}
    .copy .lead {{ margin-bottom: 40px; }}
    .install {{ padding: 16px 24px; margin-bottom: 24px; }}
    .install .caption {{ margin-bottom: 8px; }}
    .install code {{ font-size: 14px; line-height: 24px; color: {WHITE}; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .chips span {{ font-size: 12px; line-height: 16px; color: {MUTED}; border: 1px solid {LINE};
      padding: 8px 12px; }}
    """
    return page(html, 1280, 720, glow_css + css)


# 2. Annotated popup: what each control does (1200 by 720)
def controls_html():
    notes = [
        ("1", "Power switch", "Turns the light on or off."),
        ("2", "Status line", "On or Off, with the brightness and warmth in use."),
        ("3", "Brightness", "How strong the light is, from 0 to 100 percent."),
        ("4", "Width", "How thick the edge band is, from 4 to 120 pixels."),
        ("5", "Warmth", "From 2700 K, a warm amber, to 6500 K, a cool white."),
        ("6", "Hint", "Tells you what you can do next."),
    ]
    rows = "".join(
        f"""<li><span class="num">{n}</span>
              <div><h3>{t}</h3><p class="small">{d}</p></div></li>"""
        for n, t, d in notes)
    html = f"""
    <div class="wrap">
      <section class="left">
        <div class="eyebrow">The control popup</div>
        <h2>What each control does</h2>
        <p class="lead lead-sm">Six parts on one card. Every change lands on the light as you drag.</p>
        <ol class="notes">{rows}</ol>
      </section>
      <div class="pop">{popup_html(on=True, brightness=70, width=28, warmth=4000,
          badges={k: True for k in '123456'})}</div>
    </div>"""
    css = f"""
    .wrap {{ position: relative; width: 1200px; height: 800px; }}
    .left {{ position: absolute; left: 80px; top: 96px; width: 500px; }}
    .left .eyebrow {{ margin-bottom: 16px; }}
    .left h2 {{ margin-bottom: 16px; }}
    .lead-sm {{ font-size: 18px; line-height: 28px; margin-bottom: 40px; }}
    .notes {{ list-style: none; display: flex; flex-direction: column; gap: 24px; }}
    .notes li {{ align-items: center; }}
    .notes li {{ display: flex; gap: 16px; align-items: flex-start; }}
    .notes .num {{ flex: 0 0 32px; height: 32px; display: flex; align-items: center; justify-content: center;
      background: #82FB9C; color: #0B0C16; font: 600 15px/1 "Instrument Sans", sans-serif; }}
    .notes h3 {{ font-size: 18px; line-height: 24px; margin-bottom: 4px; }}
    .pop {{ position: absolute; left: 690px; top: 230px; transform: scale(1.3); transform-origin: 0 0; }}
    """
    return page(html, 1200, 800, css)


# 3. How it works (1280 by 720)
def how_html():
    steps = [
        ("01", "Bottom bar icon", "Click the lightbulb, or press SUPER ALT P."),
        ("02", "Control popup", "Opens above the icon with the power switch and three sliders."),
        ("03", "Service", "Holds the state, and saves your settings to a file."),
        ("04", "Edge light", "A click through glow along each screen edge."),
    ]
    cards = "".join(
        f"""<div class="step card"><div class="step-num mono">{n}</div>
              <h3>{t}</h3><p class="small">{d}</p></div>"""
        for n, t, d in steps)
    touches = [
        "Brightness: sets the screen to 100 percent when the light turns on.",
        "Theme: matches the popup to your Omarchy colours.",
        "Settings: saved to ~/.config/omarchy/omalight/settings.json, and nothing else.",
        "Network and camera: none. No video or audio is read.",
    ]
    tlist = "".join(f"<li>{t}</li>" for t in touches)
    html = f"""
    <div class="wrap">
      <header>
        <div class="eyebrow">How it works</div>
        <h2>One click turns the light on across every screen</h2>
      </header>
      <section class="flow">{cards}</section>
      <div class="lower">
        <section class="touches">
          <h3>What it touches on your system</h3>
          <ul>{tlist}</ul>
        </section>
        <section class="keys card">
          <h3>Keyboard shortcuts</h3>
          <div class="key-row"><div><kbd>SUPER</kbd> <kbd>ALT</kbd> <kbd>E</kbd></div><p class="small">Turn the light on or off</p></div>
          <div class="key-row"><div><kbd>SUPER</kbd> <kbd>ALT</kbd> <kbd>P</kbd></div><p class="small">Open or close the popup</p></div>
        </section>
      </div>
    </div>"""
    css = f"""
    .wrap {{ position: relative; width: 1280px; height: 720px; padding: 64px; }}
    header {{ margin-bottom: 40px; }}
    header .eyebrow {{ margin-bottom: 16px; }}
    .flow {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-bottom: 40px; }}
    .step {{ padding: 24px; height: 200px; }}
    .step-num {{ font-size: 12px; line-height: 16px; color: #82FB9C; margin-bottom: 16px; letter-spacing: 0.06em; }}
    .step h3 {{ margin-bottom: 8px; }}
    .lower {{ display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: start; }}
    .touches h3 {{ margin-bottom: 16px; }}
    .touches ul {{ list-style: none; display: flex; flex-direction: column; gap: 16px; }}
    .touches li {{ font-size: 16px; line-height: 24px; color: {MUTED}; padding-left: 20px; position: relative; text-wrap: pretty; max-width: 640px; }}
    .touches li::before {{ content: ""; position: absolute; left: 0; top: 8px; width: 8px; height: 8px; background: #82FB9C; }}
    .keys {{ padding: 24px; }}
    .keys h3 {{ margin-bottom: 16px; }}
    .key-row {{ display: flex; justify-content: space-between; align-items: center; padding: 16px 0;
      border-top: 1px solid {LINE}; }}
    .key-row p {{ text-align: right; }}
    """
    return page(html, 1280, 720, css)


def render(pages):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for html, width, height, out_path in pages:
            ctx = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=2)
            pg = ctx.new_page()
            pg.set_content(html, wait_until="load")
            pg.wait_for_timeout(200)
            pg.screenshot(path=out_path, full_page=False)
            ctx.close()
            print("wrote", os.path.relpath(out_path, ROOT), f"({width * 2}x{height * 2})")
        browser.close()


if __name__ == "__main__":
    # keep the HTML sources next to the images, so the design can be re-read
    sources = {
        "hero": (hero_html(), 1280, 720, os.path.join(ROOT, "preview.png")),
        "controls": (controls_html(), 1200, 800, os.path.join(HERE, "controls.png")),
        "how-it-works": (how_html(), 1280, 720, os.path.join(HERE, "how-it-works.png")),
    }
    for name, (html, _, _, _) in sources.items():
        with open(os.path.join(HERE, name + ".html"), "w", encoding="utf-8") as f:
            f.write(html)
    render(sources.values())
