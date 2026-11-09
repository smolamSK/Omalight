# Omalight

**A soft edge light for video calls, for Omarchy.**

Omalight lights your face by glowing along the edges of your screen, the way a
ring light would. Turn it on from the bottom bar, pick the brightness, width,
and warmth you like, and the glow covers every screen.

<p align="center">
  <img src="preview.png" alt="Omalight: the control popup above the lightbulb icon on the bottom bar, with a warm glow along the screen edges" width="720">
</p>

## Install

```bash
omarchy plugin add https://github.com/vaibhavgupta5/Omalight.git --enable --yes
omarchy bar put io.github.vaibhavgupta5.omalight right
```

The second command puts the lightbulb on the right of your bottom bar. Check
the plugin is on with `omarchy plugin list`.

Remove it with:

```bash
omarchy plugin remove io.github.vaibhavgupta5.omalight --yes
```

## Features

- **Lightbulb on the bottom bar.** It is lit while the light is on.
- **Control popup** that opens above the icon. Escape or a click outside closes it.
- **Power switch**, **brightness** (0–100%), **width** (4–120 px), and **warmth** (2700 K warm to 6500 K cool).
- **Full screen brightness** when the light turns on, through Omarchy's own brightness helper.
- **Every screen** gets the glow, or only the focused one (set in the settings file).
- **Keyboard shortcuts** to turn the light on or off, and to open the popup.
- **Uses your theme.** The popup takes its colours, corners, and type from your Omarchy theme.

<p align="center">
  <img src="docs/controls.png" alt="The Omalight popup with each control numbered and described" width="720">
</p>

## How it works

<p align="center">
  <img src="docs/how-it-works.png" alt="Diagram: bar icon, control popup, service, and edge light, with the shortcuts underneath" width="720">
</p>

## Shortcuts

Omarchy keybindings live in `~/.config/hypr/bindings.lua`. Omalight does not edit that file, so paste these lines into yours, then reload Hyprland:

```lua
o.bind("SUPER + ALT + E", "Omalight: toggle light", "omarchy-shell shell call io.github.vaibhavgupta5.omalight lightToggle ''")
o.bind("SUPER + ALT + P", "Omalight: control popup", "omarchy-shell omalight toggle")
```

`SUPER + ALT + P` needs the icon on the bar, because the popup opens from the icon.
Check for conflicts first with `omarchy menu keybindings --print`.

## Settings

Settings are saved to `~/.config/omarchy/omalight/settings.json`. The popup writes them for you. You can also edit the file by hand.

| Key | Range | Default | Meaning |
|---|---|---|---|
| `intensity` | 0–100 | 70 | Brightness of the light, in percent |
| `width` | 4–120 | 28 | Thickness of each edge band, in px |
| `kelvin` | 2700–6500 | 4000 | Warmth of the light, warm to cool |
| `cursorHole` | 0–300 | 110 | Radius in px around the mouse kept free of light (0 = off) |
| `scope` | `all`, `focused` | `all` | Light every screen, or only the focused one |

The light itself is not saved. It starts off after every restart of the shell.

## IPC

These calls work from scripts, Hyprland bindings, and the Omarchy menu:

```bash
omarchy-shell shell call io.github.vaibhavgupta5.omalight <method> <arg>
```

| Method | Argument | Effect |
|---|---|---|
| `lightToggle` | `''` | Turn the light on or off. Returns `on` or `off` |
| `lightOn` / `lightOff` | `''` | Force the light on or off |
| `setValue` | JSON | Save settings, for example `'{"intensity":60}'` |
| `status` | `''` | JSON with the current state |

The popup has its own target, which only exists while the icon is on the bar: `omarchy-shell omalight toggle`, `open`, or `close`.

## What it does on your system

- **Brightness:** when the light turns on, it runs `omarchy brightness display --no-osd 100%`. Your old brightness is not restored when it turns off.
- **Theme:** reads `~/.local/state/omarchy/current/theme/colors.toml` and `shell.toml`, and the Hyprland rounding from `~/.config/hypr/looknfeel.lua`.
- **Settings:** writes `~/.config/omarchy/omalight/settings.json`. Nothing else is saved.
- **Runs** inside `omarchy-shell`, with your user's permissions. No `sudo`, and no network requests.
- **Does not read** the camera, the microphone, or any video.

## Limits

- The popup opens only while the icon is on the bar.
- The light draws over fullscreen apps too, because it is an overlay. There is no hide-on-fullscreen option yet.
- Your old screen brightness is not restored when the light turns off.

## Development

```bash
node --test test/unit/*.test.js    # settings and colour logic
test/harness/run-smoke.sh          # isolated Quickshell run: light, glow, settings
omarchy plugin validate .          # manifest check
```

The smoke test builds its own Quickshell root from copies of the plugin files, with a scratch settings file. It never changes your screen brightness.

The graphics are drawn by `docs/build_graphics.py`, which writes SVG and renders it with `rsvg-convert`.

## License

MIT. See [LICENSE](LICENSE).
