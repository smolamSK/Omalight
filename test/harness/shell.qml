import QtQuick
import Quickshell
import Quickshell.Io

// Isolated test shell. It mounts the glow and the service the way the shell
// does: the service loads first, then the panel receives it as `service`.
// run-smoke.sh copies the plugin files next to this file, because Quickshell
// only loads files from its own config folder.
ShellRoot {
  Loader {
    id: serviceLoader
    source: Qt.resolvedUrl("Service.qml")
  }

  Loader {
    id: panelLoader
    source: Qt.resolvedUrl("EdgeLight.qml")
  }

  // Bound rather than assigned once in onLoaded, so the panel gets the service
  // whichever loads first.
  Binding {
    target: panelLoader.item
    property: "service"
    value: serviceLoader.item
    when: panelLoader.item !== null && serviceLoader.item !== null
  }

  IpcHandler {
    target: "edge"

    function call(method: string, arg: string): string {
      var panel = panelLoader.item
      if (!panel || typeof panel[method] !== "function") return "unknown"
      return String(panel[method](arg))
    }

    function diag(): string {
      return JSON.stringify({
        serviceStatus: serviceLoader.status,
        panelStatus: panelLoader.status,
        panelHasService: panelLoader.item && panelLoader.item.service ? "yes" : "no"
      })
    }
  }
}
