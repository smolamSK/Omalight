# Edge Light for Omarchy

A soft light along the edges of your screen, to light your face on video calls.

- **Bottom-bar icon** (lightbulb). Click it to open the control popup above the icon. The icon is highlighted while the light is on.
- **Control popup** built from Omarchy's own UI kit: a power switch, and sliders for brightness, width, and warmth (2700 K warm to 6500 K cool).
- **Full screen brightness** when the light turns on. The light does not restore your old brightness when it turns off.
- **Keyboard shortcuts** to toggle the light and open the popup.

The light is an overlay. It does not capture the camera or read any video.

## Requirements

- Omarchy with Hyprland and the Omarchy shell (`omarchy-shell`).
- `omarchy brightness display`, which Omarchy provides. Without it the light still works, but the screen brightness is not changed.

## Install

```bash
omarchy plugin add https://github.com/vaibhavgupta5/Omalight.git --enable --yes
omarchy bar put io.github.vaibhavgupta5.edge-light right
```

The second command puts the lightbulb in the right section of your bar. Run `omarchy plugin list` to check that the plugin is enabled.

Remove it with:

```bash
omarchy plugin remove io.github.vaibhavgupta5.edge-light --yes
```

## Shortcuts

Omarchy keybindings live in `~/.config/hypr/bindings.lua`. The plugin does not edit that file. To use these shortcuts, paste the lines into your file and reload Hyprland:

```lua
o.bind("SUPER + ALT + E", "Edge Light: toggle light", "omarchy-shell shell call io.github.vaibhavgupta5.edge-light lightToggle ''")
o.bind("SUPER + ALT + P", "Edge Light: control popup", "omarchy-shell edge-light toggle")
```

`SUPER + ALT + P` needs the icon on the bar, because the popup belongs to the icon. Check for conflicts first with `omarchy menu keybindings --print`.

## Settings

Settings are saved to `~/.config/omarchy/edge-light/settings.json`. You can edit the file by hand, or change them in the popup.

| Key | Range | Default | Meaning |
|---|---|---|---|
| `intensity` | 0–100 | 70 | Brightness of the light, in percent |
| `width` | 4–120 | 28 | Thickness of each edge band, in px |
| `kelvin` | 2700–6500 | 4000 | Warmth of the light, warm to cool |
| `scope` | `all`, `focused` | `all` | Light every screen, or only the focused one |

The light itself is not saved. It starts off after every restart of the shell.

## IPC

Use `omarchy-shell shell call io.github.vaibhavgupta5.edge-light <method> <arg>` for these methods:

| Method | Argument | Effect |
|---|---|---|
| `lightToggle` | `''` | Turn the light on or off. Returns `on` or `off` |
| `lightOn` / `lightOff` | `''` | Force the light on or off |
| `setValue` | JSON | Save settings, for example `'{"intensity":60}'` |
| `status` | `''` | JSON with the current state |

The popup has its own IPC target: `omarchy-shell edge-light toggle`, `open`, or `close`.

## What the plugin does on your system

- Runs inside `omarchy-shell`, with your user's permissions. It does not use `sudo` and makes no network requests.
- Runs `omarchy brightness display --no-osd 100%` when the light turns on.
- Reads the current Omarchy theme from `~/.local/state/omarchy/current/theme/colors.toml` and `shell.toml`, and the Hyprland rounding from `~/.config/hypr/looknfeel.lua`. It uses them to match the popup to your theme.
- Writes its settings to `~/.config/omarchy/edge-light/settings.json`.

## Limits

- The popup appears only while the icon is on the bar.
- The light draws over fullscreen apps as well, because it is an overlay. There is no hide-on-fullscreen option yet.
- Full screen brightness is not restored when the light turns off.

## Development

```bash
node --test test/unit/*.test.js     # pure logic: settings and colors
test/harness/run-smoke.sh           # isolated Quickshell run: light, glow, settings
omarchy plugin validate .           # manifest check
```

The smoke test runs its own Quickshell process from copies of the plugin files, with a scratch settings file, and it never changes the real screen brightness.

## License

MIT. See [LICENSE](LICENSE).
