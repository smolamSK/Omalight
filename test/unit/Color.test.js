const test = require("node:test")
const assert = require("node:assert/strict")
const Color = require("../../lib/Color.js")

test("kelvinToRgb is warm at 2700K and near white at 6500K", () => {
  const warm = Color.kelvinToRgb(2700)
  const cool = Color.kelvinToRgb(6500)
  assert.ok(warm.r > warm.g && warm.g > warm.b, "2700K should be red-heavy")
  assert.equal(warm.r, 255)
  assert.ok(cool.b > 240 && cool.r > 240 && cool.g > 240, "6500K should be near white")
})

test("kelvinToRgb blue channel rises with temperature", () => {
  let last = -1
  for (const k of [2700, 3500, 4500, 5500, 6500]) {
    const b = Color.kelvinToRgb(k).b
    assert.ok(b >= last, `blue dropped at ${k}K`)
    last = b
  }
})

test("kelvinToRgb always returns bytes", () => {
  for (const k of [0, 999999, NaN, 4000]) {
    const c = Color.kelvinToRgb(k)
    for (const ch of [c.r, c.g, c.b]) {
      assert.ok(Number.isInteger(ch) && ch >= 0 && ch <= 255)
    }
  }
})
