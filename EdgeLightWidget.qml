import QtQuick
import Quickshell
import Quickshell.Io
import qs.Ui

// Bottom-bar icon for Edge Light. A left click opens the control popup above
// the icon. The icon is highlighted while the light is on. The popup is an
// Omarchy KeyboardPanel anchored to this button, so it appears next to the
// icon, not at a fixed spot on the screen.
BarWidget {
  id: root
  moduleName: "io.github.vaibhavgupta5.edge-light"

  // A third-party widget gets the bar's plugin API as `bar`. That API carries
  // a scoped `shell`, whose serviceFor(own id) returns the service with all the
  // state. A bar widget gets no `shell` property of its own.
  readonly property var pluginShell: bar && bar.shell ? bar.shell : null
  readonly property var service: pluginShell ? pluginShell.serviceFor("io.github.vaibhavgupta5.edge-light") : null

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  BarIconButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: "󰌵"
    active: root.service ? root.service.isOn : false
    tooltipText: root.service && root.service.isOn ? "Edge Light: on" : "Edge Light: off"
    onPressed: function(mouseButton) {
      if (mouseButton === Qt.LeftButton && popupLoader.item) popupLoader.item.open = !popupLoader.item.open
    }
  }

  // The popup is loaded from its file, as the shell loads plugin entries, and
  // wired to the icon and the service once it exists.
  Loader {
    id: popupLoader
    // Bind the live service once the popup exists. A one-time binding made
    // before the loader had an item would never take effect.
    onLoaded: item.service = Qt.binding(function() { return root.service })
  }

  // Create the popup once the bar has been handed to us, so its required
  // properties are set at creation.
  onBarChanged: {
    if (bar && !popupLoader.item)
      popupLoader.setSource(Qt.resolvedUrl("EdgeLightPopup.qml"), {
        anchorItem: button,
        bar: root.bar,
        owner: root
      })
  }


  // Lets the shortcut open the popup: omarchy-shell edge-light toggle
  IpcHandler {
    target: "edge-light"

    function toggle(): void { if (popupLoader.item) popupLoader.item.open = !popupLoader.item.open }
    function open(): void { if (popupLoader.item) popupLoader.item.open = true }
    function close(): void { if (popupLoader.item) popupLoader.item.open = false }
  }
}
