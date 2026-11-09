import QtQuick
import qs.Commons
import qs.Ui

// Omalight control popup. It opens above its bar icon, the way Omarchy's
// own popups do, and is built from the same kit parts: hero header, switches,
// section headers, and sliders. Escape and a click outside close it.
KeyboardPanel {
  id: popup

  property var service: null

  // Fallbacks keep the popup valid before the service is bound.
  readonly property var s: service ? service.settings
    : ({ intensity: 70, width: 28, kelvin: 4000, cursorHole: 110, scope: "all" })
  readonly property bool lightOn: service ? service.isOn : false
  readonly property var kit: bar

  contentWidth: Style.space(300)
  contentHeight: column.implicitHeight + 2 * popup.padding

  focusTarget: keyHolder

  Item {
    id: keyHolder
    anchors.fill: parent
    focus: true
    Keys.onEscapePressed: popup.close()
  }

  // What to do next, in one plain sentence.
  // Apply one slider value. `persist` is true on release, false while dragging.
  function setSetting(key, value, persist) {
    if (!service) return
    var patch = {}
    patch[key] = Math.round(value)
    service.update(patch, persist)
  }

  readonly property string hint: {
    if (lightOn) return "On now. Drag the sliders to change it."
    return "Off. Switch it on to light your face. The screen goes to full brightness."
  }

  Column {
    id: column
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.top: parent.top
    spacing: Style.spacing.md

    // Hero: icon, name, status line, and the main power switch on the right.
    Item {
      width: parent.width
      height: Style.space(44)

      Text {
        id: glyph
        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter
        text: "󰌵"
        color: popup.kit.foreground
        opacity: popup.lightOn ? 1 : 0.6
        font.family: popup.kit.fontFamily
        font.pixelSize: Style.font.display
      }

      Column {
        anchors.left: glyph.right
        anchors.leftMargin: Style.space(12)
        anchors.right: powerSwitch.left
        anchors.rightMargin: Style.space(12)
        anchors.verticalCenter: parent.verticalCenter

        Text {
          text: "Omalight"
          color: popup.kit.foreground
          font.family: popup.kit.fontFamily
          font.pixelSize: Style.font.subtitle
          elide: Text.ElideRight
          width: parent.width
        }

        Text {
          text: popup.lightOn
            ? "On · " + popup.s.intensity + "% · " + popup.s.kelvin + "K"
            : "Off"
          color: popup.kit.foreground
          opacity: 0.6
          font.family: popup.kit.fontFamily
          font.pixelSize: Style.font.caption
          elide: Text.ElideRight
          width: parent.width
        }
      }

      ToggleSwitch {
        id: powerSwitch
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        checked: popup.lightOn
        foreground: popup.kit.foreground
        accent: Color.accent
        onToggled: if (popup.service) popup.service.setLight(!popup.service.isOn)
      }
    }

    PanelSeparator {
      width: parent.width
      foreground: popup.kit.foreground
    }

    PanelSectionHeader {
      text: "LIGHT"
      foreground: popup.kit.foreground
      fontFamily: popup.kit.fontFamily
    }

    // One labelled slider per setting: name and value on one line, slider below.
    Repeater {
      model: [
        { key: "intensity", label: "Brightness", from: 0, to: 100, suffix: "%" },
        { key: "width", label: "Width", from: 4, to: 120, suffix: " px" },
        { key: "kelvin", label: "Warmth", from: 2700, to: 6500, suffix: " K" },
        { key: "cursorHole", label: "Gap around mouse", from: 0, to: 300, suffix: " px", zero: "Off" }
      ]

      Column {
        required property var modelData
        width: column.width
        spacing: Style.spacing.xs

        Item {
          width: parent.width
          height: Style.space(16)

          Text {
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            text: modelData.label
            color: popup.kit.foreground
            font.family: popup.kit.fontFamily
            font.pixelSize: Style.font.bodySmall
          }

          Text {
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            text: (modelData.zero && Math.round(popup.s[modelData.key]) === 0)
              ? modelData.zero
              : Math.round(popup.s[modelData.key]) + modelData.suffix
            color: popup.kit.foreground
            font.family: popup.kit.fontFamily
            font.pixelSize: Style.font.bodySmall
          }
        }

        PanelSlider {
          width: parent.width
          bar: popup.kit
          minimum: modelData.from
          maximum: modelData.to
          step: 1
          integer: true
          value: popup.s[modelData.key]
          onMoved: function(v) { popup.setSetting(modelData.key, v, false) }
          onReleased: function(v) { popup.setSetting(modelData.key, v, true) }
        }
      }
    }

    PanelSeparator {
      width: parent.width
      foreground: popup.kit.foreground
    }

    Text {
      width: parent.width
      text: popup.hint
      wrapMode: Text.WordWrap
      color: popup.kit.foreground
      opacity: 0.7
      font.family: popup.kit.fontFamily
      font.pixelSize: Style.font.caption
    }
  }
}
