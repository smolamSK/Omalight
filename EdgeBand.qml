import QtQuick

// One edge of the glow. Fades from `color` at the screen edge to transparent
// inward. Size and position come from the parent.
Item {
  id: band

  // "top" | "right" | "bottom" | "left": the screen edge the light comes from.
  property string edge: "top"
  property color color: "white"
  // Peak alpha at the edge, 0-1.
  property real strength: 0.7

  readonly property bool fromStart: edge === "top" || edge === "left"
  readonly property color lit: Qt.rgba(band.color.r, band.color.g, band.color.b, band.strength)
  readonly property color clear: Qt.rgba(band.color.r, band.color.g, band.color.b, 0)

  Rectangle {
    anchors.fill: parent
    gradient: Gradient {
      orientation: (band.edge === "top" || band.edge === "bottom") ? Gradient.Vertical : Gradient.Horizontal
      GradientStop { position: 0.0; color: band.fromStart ? band.lit : band.clear }
      GradientStop { position: 1.0; color: band.fromStart ? band.clear : band.lit }
    }
  }
}
