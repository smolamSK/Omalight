// Pure state logic for Omalight. Plain JS with no QML imports, so Node can
// unit-test it directly (see test/unit).

var DEFAULTS = {
  intensity: 70,    // 0-100, peak brightness of the edge light
  width: 28,        // px, thickness of each edge band
  kelvin: 4000,     // 2700-6500, warm to cool
  cursorHole: 110,  // px radius around the pointer kept free of light; 0 = off
  scope: "all"      // "all" | "focused": which screens get the glow
}

function clamp(value, min, max, fallback) {
  var n = Number(value)
  if (!isFinite(n)) return fallback
  return Math.max(min, Math.min(max, n))
}

// Coerce any input into a valid settings object. Unknown keys are dropped.
function normalize(raw) {
  var s = raw || {}
  return {
    intensity: Math.round(clamp(s.intensity, 0, 100, DEFAULTS.intensity)),
    width: Math.round(clamp(s.width, 4, 120, DEFAULTS.width)),
    kelvin: Math.round(clamp(s.kelvin, 2700, 6500, DEFAULTS.kelvin)),
    cursorHole: Math.round(clamp(s.cursorHole, 0, 300, DEFAULTS.cursorHole)),
    scope: s.scope === "focused" ? "focused" : "all"
  }
}

// Parse the settings file. Invalid or missing JSON falls back to defaults.
function parseSettings(text) {
  try {
    return normalize(JSON.parse(text || "{}"))
  } catch (e) {
    return normalize({})
  }
}

// Shallow merge that returns a new object; `patch` wins.
function merge(base, patch) {
  var out = {}
  var key
  for (key in base) out[key] = base[key]
  for (key in patch) out[key] = patch[key]
  return out
}

if (typeof module !== "undefined") {
  module.exports = {
    DEFAULTS: DEFAULTS,
    normalize: normalize,
    parseSettings: parseSettings,
    merge: merge
  }
}
