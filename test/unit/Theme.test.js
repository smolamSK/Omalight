const test = require("node:test")
const assert = require("node:assert/strict")
const Theme = require("../../lib/Theme.js")

const SHELL = `
[bar]
active           = "#50f872"

[hyprland]
active-border            = "rgba(26a269ee) rgba(2ec27eee) 45deg"

[controls]
normal-fill-alpha   = 0.04
normal-border       = "#ddf7ff"
normal-border-alpha = 0.4
hover-cursor-fill-alpha   = 0.08
hover-cursor-border-alpha = 0.25
selected-fill-alpha   = 0.18
selected-border-width = 0

[popups]
background       = "#0B0C16"
background-alpha = 1.0
text             = "#ddf7ff"
border           = "hyprland.active-border"
border-alpha     = 1.0
# border-width     = 2

[font]
base-size = 12
`

test("parseToml reads sections, quoted values, and hex colors with #", () => {
  const t = Theme.parseToml(SHELL)
  assert.equal(t["popups.background"], "#0B0C16")
  assert.equal(t["controls.normal-fill-alpha"], "0.04")
  assert.equal(t["hyprland.active-border"], "rgba(26a269ee) rgba(2ec27eee) 45deg")
  assert.equal(t["font.base-size"], "12")
})

test("parseToml ignores commented-out keys", () => {
  assert.equal(Theme.parseToml(SHELL)["popups.border-width"], undefined)
})

test("parseToml strips inline comments from bare values", () => {
  assert.equal(Theme.parseToml("x = 3 # three")["x"], "3")
})

test("parseColor converts Hyprland rgba to Qt #AARRGGBB", () => {
  assert.equal(Theme.parseColor("rgba(26a269ee)"), "#ee26a269")
  assert.equal(Theme.parseColor("#82fb9c"), "#ff82fb9c")
  assert.equal(Theme.parseColor("red"), "")
})

test("parseGradient reads colors and angle", () => {
  const g = Theme.parseGradient("rgba(26a269ee) rgba(2ec27eee) 45deg")
  assert.deepEqual(g.colors, ["#ee26a269", "#ee2ec27e"])
  assert.equal(g.angle, 45)
})

test("withAlpha produces #AARRGGBB", () => {
  assert.equal(Theme.withAlpha("#0b0c16", 1), "#ff0b0c16")
  assert.equal(Theme.withAlpha("#ffffff", 0.5), "#80ffffff")
  assert.equal(Theme.withAlpha("#ffffff", 9), "#ffffffff")
})

test("parseRounding reads Hyprland rounding and defaults to 0", () => {
  assert.equal(Theme.parseRounding("decoration = {\n    rounding = 0,\n}"), 0)
  assert.equal(Theme.parseRounding("rounding = 8,"), 8)
  assert.equal(Theme.parseRounding(""), 0)
})

test("buildUi is boxy (square corners) when Hyprland rounding is 0", () => {
  const ui = Theme.buildUi('accent = "#82FB9C"\nforeground = "#ddf7ff"\n', SHELL, "rounding = 0,")
  assert.equal(ui.radius, 0)
})

test("buildUi resolves the gradient border and control alphas", () => {
  const ui = Theme.buildUi('accent = "#82FB9C"\n', SHELL, "rounding = 0,")
  assert.deepEqual(ui.border, ["#ee26a269", "#ee2ec27e"])
  assert.equal(ui.borderWidth, 2)
  assert.equal(ui.normalFill, Theme.withAlpha("#ddf7ff", 0.04))
  assert.equal(ui.hoverFill, Theme.withAlpha("#ddf7ff", 0.08))
  assert.equal(ui.selectedBorderWidth, 0)
  assert.equal(ui.active, "#ff50f872")
  assert.equal(ui.body, 12)
})

test("buildUi falls back cleanly with no files", () => {
  const ui = Theme.buildUi("", "", "")
  assert.equal(ui.radius, 0)
  assert.equal(ui.border.length, 2)
  assert.equal(ui.family, "monospace")
  assert.match(ui.background, /^#ff[0-9a-f]{6}$/)
})
