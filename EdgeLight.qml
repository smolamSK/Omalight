import QtQuick
import QtQuick.Effects
import QtQuick.Shapes
import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import Quickshell.Hyprland
import "lib/Color.js" as Color

// Panel entry. Draws the edge glow on each screen and the bottom control
// strip. It holds no state: everything is read from the service entry, which
// the shell injects as `service`.
//
// IPC (shell call <id> <method> <arg>): lightToggle, lightOn, lightOff,
// setValue, status. The control popup lives on the bar icon
// (EdgeLightWidget.qml), so it is not part of this panel.
Item {
  id: root

  property var service: null


  readonly property var settings: service ? service.settings
    : ({ intensity: 0, width: 28, kelvin: 4000, cursorHole: 0, scope: "all" })
  readonly property bool lightActive: service ? service.isOn : false
  readonly property string focusedName: Hyprland.focusedMonitor ? Hyprland.focusedMonitor.name : ""

  // Peak alpha of the light. Capped below 1 so it reads as light, not paint.
  readonly property real lightStrength: settings.intensity / 100 * 0.9
  readonly property color lightColor: lightFor(settings.kelvin)

  function lightFor(kelvin) {
    var c = Color.kelvinToRgb(kelvin)
    return Qt.rgba(c.r / 255, c.g / 255, c.b / 255, 1)
  }

  // Cursor cutout: the glow is cleared in a soft circle around the pointer so
  // whatever sits under the mouse stays readable. Position is polled from
  // Hyprland only while the light is on and the gap is enabled (radius > 0).
  readonly property real cursorHoleRadius: settings.cursorHole || 0
  readonly property bool cursorHoleOn: cursorHoleRadius > 0
  property real cursorX: -10000
  property real cursorY: -10000

  Process {
    id: cursorProc
    command: ["hyprctl", "cursorpos", "-j"]
    stdout: StdioCollector {
      onStreamFinished: {
        try {
          var p = JSON.parse(text)
          if (p.x !== root.cursorX) root.cursorX = p.x
          if (p.y !== root.cursorY) root.cursorY = p.y
        } catch (e) {}
      }
    }
  }

  Timer {
    interval: 33
    repeat: true
    running: root.lightActive && root.cursorHoleOn
    onTriggered: if (!cursorProc.running) cursorProc.running = true
  }

  function glowShown(screenName) {
    if (!service || !lightActive) return false
    return settings.scope !== "focused" || focusedName === "" || screenName === focusedName
  }



  function lightToggle() {
    if (!service) return "unavailable"
    service.setLight(!service.isOn)
    return service.isOn ? "on" : "off"
  }

  function lightOn() {
    if (!service) return "unavailable"
    service.setLight(true)
    return "on"
  }

  function lightOff() {
    if (!service) return "unavailable"
    service.setLight(false)
    return "off"
  }

  // payload: JSON object of settings, e.g. {"intensity": 60}. Persisted.
  function setValue(payload) {
    if (!service) return "unavailable"
    try {
      service.update(JSON.parse(payload || "{}"), true)
      return "ok"
    } catch (e) {
      return "invalid"
    }
  }

  function status() {
    return JSON.stringify({
      enabled: lightActive,
      intensity: settings.intensity,
      width: settings.width,
      kelvin: settings.kelvin,
      cursorHole: settings.cursorHole,
      scope: settings.scope,
      focused: focusedName
    })
  }

  // One click-through glow window per screen. Hidden when off, so an idle
  // light costs nothing.
  Variants {
    model: Quickshell.screens

    PanelWindow {
      id: glow
      required property var modelData

      screen: modelData
      visible: root.glowShown(modelData.name)
      color: "transparent"
      anchors { top: true; bottom: true; left: true; right: true }
      exclusionMode: ExclusionMode.Ignore
      // Empty input region: clicks pass through to whatever is underneath.
      mask: Region {}

      WlrLayershell.namespace: "omarchy-omalight"
      WlrLayershell.layer: WlrLayer.Overlay
      WlrLayershell.keyboardFocus: WlrKeyboardFocus.None

      readonly property real band: root.settings.width
      // Cursor in this screen's local coordinates.
      readonly property real localX: root.cursorX - (modelData.x || 0)
      readonly property real localY: root.cursorY - (modelData.y || 0)

      Item {
        id: bands
        anchors.fill: parent
        visible: false
        layer.enabled: true

        EdgeBand {
          edge: "top"
          anchors { top: parent.top; left: parent.left; right: parent.right }
          height: glow.band
          color: root.lightColor
          strength: root.lightStrength
        }
        EdgeBand {
          edge: "right"
          anchors { top: parent.top; right: parent.right; bottom: parent.bottom }
          width: glow.band
          color: root.lightColor
          strength: root.lightStrength
        }
        EdgeBand {
          edge: "bottom"
          anchors { left: parent.left; right: parent.right; bottom: parent.bottom }
          height: glow.band
          color: root.lightColor
          strength: root.lightStrength
        }
        EdgeBand {
          edge: "left"
          anchors { top: parent.top; left: parent.left; bottom: parent.bottom }
          width: glow.band
          color: root.lightColor
          strength: root.lightStrength
        }
      }

      // Mask: opaque everywhere except a soft disc at the cursor. The radial
      // gradient pads its last stop, so everything outside the disc is white.
      Item {
        id: hole
        anchors.fill: parent
        visible: false
        layer.enabled: true

        Shape {
          anchors.fill: parent

          ShapePath {
            strokeWidth: -1
            fillGradient: RadialGradient {
              spread: ShapeGradient.PadSpread
              centerX: glow.localX; centerY: glow.localY
              centerRadius: root.cursorHoleRadius
              focalX: glow.localX; focalY: glow.localY
              GradientStop { position: 0.0; color: "transparent" }
              GradientStop { position: 0.5; color: "transparent" }
              GradientStop { position: 1.0; color: "white" }
            }
            startX: 0; startY: 0
            PathLine { x: glow.width; y: 0 }
            PathLine { x: glow.width; y: glow.height }
            PathLine { x: 0; y: glow.height }
            PathLine { x: 0; y: 0 }
          }
        }
      }

      MultiEffect {
        anchors.fill: parent
        source: bands
        maskEnabled: root.cursorHoleOn
        maskSource: hole
        maskThresholdMin: 0.5
        maskSpreadAtMin: 1.0
      }
    }
  }

}
