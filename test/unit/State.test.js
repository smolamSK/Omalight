const test = require("node:test")
const assert = require("node:assert/strict")
const State = require("../../lib/State.js")

test("normalize clamps numeric settings into range", () => {
  const s = State.normalize({ intensity: 150, width: 0, kelvin: 1000 })
  assert.equal(s.intensity, 100)
  assert.equal(s.width, 4)
  assert.equal(s.kelvin, 2700)
})

test("normalize replaces invalid enums and non-numeric values with defaults", () => {
  const s = State.normalize({ scope: "everywhere", intensity: "loud" })
  assert.equal(s.scope, "all")
  assert.equal(s.intensity, State.DEFAULTS.intensity)
})

test("normalize keeps valid values and drops removed keys", () => {
  const s = State.normalize({ intensity: 40, width: 30, kelvin: 3200, scope: "focused", auto: "camera" })
  assert.deepEqual(s, { intensity: 40, width: 30, kelvin: 3200, cursorHole: 110, scope: "focused" })
})

test("parseSettings falls back to defaults on broken JSON", () => {
  assert.deepEqual(State.parseSettings("{not json"), State.normalize({}))
  assert.deepEqual(State.parseSettings(""), State.normalize({}))
})

test("parseSettings reads a valid file", () => {
  assert.equal(State.parseSettings('{"intensity": 55}').intensity, 55)
})

test("merge returns a new object and the patch wins", () => {
  const base = { a: 1, b: 2 }
  const out = State.merge(base, { b: 3 })
  assert.deepEqual(out, { a: 1, b: 3 })
  assert.deepEqual(base, { a: 1, b: 2 })
})

test("normalize clamps the cursor gap and allows 0 to turn it off", () => {
  assert.equal(State.normalize({ cursorHole: 999 }).cursorHole, 300)
  assert.equal(State.normalize({ cursorHole: -5 }).cursorHole, 0)
  assert.equal(State.normalize({ cursorHole: 0 }).cursorHole, 0)
  assert.equal(State.normalize({}).cursorHole, State.DEFAULTS.cursorHole)
})
