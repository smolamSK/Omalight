// Color helpers for Omalight. Plain JS with no QML imports, so Node can
// unit-test it directly (see test/unit).

function clampByte(value) {
  return Math.max(0, Math.min(255, Math.round(value)))
}

// Approximate color of a black-body radiator at `kelvin` (Tanner Helland's fit).
// Lower temperatures are warm (orange), higher ones are cool (blue-white).
function kelvinToRgb(kelvin) {
  var t = Math.max(1000, Math.min(40000, Number(kelvin) || 6500)) / 100
  var r = t <= 66 ? 255 : 329.698727446 * Math.pow(t - 60, -0.1332047592)
  var g = t <= 66
    ? 99.4708025861 * Math.log(t) - 161.1195681661
    : 288.1221695283 * Math.pow(t - 60, -0.0755148492)
  var b = 0
  if (t >= 66) b = 255
  else if (t > 19) b = 138.5177312231 * Math.log(t - 10) - 305.0447927307
  return { r: clampByte(r), g: clampByte(g), b: clampByte(b) }
}

if (typeof module !== "undefined") {
  module.exports = { kelvinToRgb: kelvinToRgb }
}
