// Omarchy UI tokens for the control strip. Plain JS with no QML imports, so
// Node can unit-test it (see test/unit).
//
// The strip reads the same files the shell reads, so it matches Omarchy's own
// popups and controls: the theme's shell.toml ([popups], [controls], [font]),
// colors.toml, and the Hyprland rounding (square corners on boxy themes).

// Flat TOML reader for shell.toml and colors.toml. Keys in a [section] come
// back as "section.key". Handles quoted strings, inline "# comments", and
// hex colors that contain '#'.
function parseToml(text) {
  var out = {}
  var section = ""
  var lines = String(text || "").split(/\r?\n/)
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim()
    if (line === "" || line.charAt(0) === "#") continue
    var head = line.match(/^\[([^\]]+)\]$/)
    if (head) { section = head[1]; continue }
    var kv = line.match(/^([A-Za-z0-9_.-]+)\s*=\s*(.*)$/)
    if (!kv) continue
    var raw = kv[2].trim()
    var value
    if (raw.charAt(0) === "\"") {
      var end = raw.indexOf("\"", 1)
      value = end > 0 ? raw.substring(1, end) : raw.substring(1)
    } else {
      value = raw.replace(/\s+#.*$/, "").trim()
    }
    out[(section ? section + "." : "") + kv[1]] = value
  }
  return out
}

// "rgba(26a269ee)" -> "#ee26a269" (Qt's #AARRGGBB). "#82fb9c" -> "#ff82fb9c".
// Returns "" for anything else.
function parseColor(token) {
  var s = String(token || "").trim()
  var rgba = s.match(/^rgba\(([0-9a-fA-F]{6})([0-9a-fA-F]{2})?\)$/)
  if (rgba) return "#" + (rgba[2] || "ff") + rgba[1]
  if (/^#[0-9a-fA-F]{6}$/.test(s)) return "#ff" + s.substring(1)
  return ""
}

// Hyprland-style gradient: "rgba(...) rgba(...) 45deg" -> { colors, angle }.
function parseGradient(text) {
  var colors = []
  var angle = 0
  var parts = String(text || "").trim().split(/\s+/)
  for (var i = 0; i < parts.length; i++) {
    if (/^-?\d+(\.\d+)?deg$/.test(parts[i])) angle = Number(parts[i].replace("deg", ""))
    else if (parseColor(parts[i])) colors.push(parseColor(parts[i]))
  }
  return { colors: colors, angle: angle }
}

// Apply an alpha (0-1) to a "#rrggbb" color, giving "#AARRGGBB".
function withAlpha(hex, alpha) {
  var a = Math.round(Math.max(0, Math.min(1, Number(alpha))) * 255)
  var h = a.toString(16)
  return "#" + (h.length < 2 ? "0" + h : h) + String(hex).replace("#", "").slice(0, 6)
}

// Corner radius from Hyprland's looknfeel.lua (`rounding = N`). 0 on boxy themes.
function parseRounding(luaText) {
  var m = String(luaText || "").match(/rounding\s*=\s*(\d+)/)
  return m ? Number(m[1]) : 0
}

// Build every token the strip needs. Any missing file or key falls back to
// the same defaults the shell uses.
function buildUi(colorsText, shellText, lookText) {
  var colors = parseToml(colorsText)
  var shell = parseToml(shellText)

  function hexOr(value, fallback) {
    var c = parseColor(value)
    return c ? "#" + c.substring(3) : fallback
  }
  function num(key, fallback) {
    var v = shell[key]
    var n = Number(v)
    return v !== undefined && v !== "" && isFinite(n) ? n : fallback
  }

  var accent = hexOr(colors.accent, "#8ab4ff")
  var background = hexOr(shell["popups.background"], hexOr(colors.background, "#0b0c16"))
  var foreground = hexOr(shell["popups.text"], hexOr(colors.foreground, "#ddf7ff"))
  var backgroundAlpha = num("popups.background-alpha", 1)

  // popups.border may point at another key, e.g. "hyprland.active-border".
  var borderRaw = shell["popups.border"] || ""
  if (shell[borderRaw] !== undefined) borderRaw = shell[borderRaw]
  var border = parseGradient(borderRaw)
  if (border.colors.length === 0) border.colors = [withAlpha(accent, 1)]
  if (border.colors.length === 1) border.colors.push(border.colors[0])

  var radius = parseRounding(lookText)
  var borderWidth = Math.max(1, Math.round(num("popups.border-width", 2)))
  var barActive = hexOr(shell["bar.active"], accent)

  return {
    family: "monospace",
    radius: radius,
    background: withAlpha(background, backgroundAlpha),
    text: withAlpha(foreground, 1),
    border: border.colors,
    borderWidth: borderWidth,
    accent: accent,
    active: withAlpha(barActive, 1),
    // Same alphas as Omarchy's Ui/Button and PanelSlider.
    normalFill: withAlpha(foreground, num("controls.normal-fill-alpha", 0.04)),
    normalBorder: withAlpha(foreground, num("controls.normal-border-alpha", 0.4)),
    normalBorderWidth: Math.max(0, Math.round(num("controls.normal-border-width", 1))),
    hoverFill: withAlpha(foreground, num("controls.hover-cursor-fill-alpha", 0.08)),
    hoverBorder: withAlpha(foreground, num("controls.hover-cursor-border-alpha", 0.25)),
    selectedFill: withAlpha(foreground, num("controls.selected-fill-alpha", 0.18)),
    selectedBorderWidth: Math.max(0, Math.round(num("controls.selected-border-width", 0))),
    pressedFill: withAlpha(foreground, num("controls.pressed-fill-alpha", 0.22)),
    sliderTrack: withAlpha(foreground, num("controls.selected-fill-alpha", 0.18)),
    // Type scale from [font] base-size, as in Commons/Style.qml.
    body: Math.round(num("font.base-size", 12)),
    caption: Math.round(num("font.base-size", 12) * 0.833),
    subtitle: Math.round(num("font.base-size", 12) * 1.083)
  }
}

if (typeof module !== "undefined") {
  module.exports = {
    parseToml: parseToml,
    parseColor: parseColor,
    parseGradient: parseGradient,
    withAlpha: withAlpha,
    parseRounding: parseRounding,
    buildUi: buildUi
  }
}
