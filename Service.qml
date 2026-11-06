import QtQuick
import Quickshell
import Quickshell.Io
import "lib/State.js" as State
import "lib/Theme.js" as Theme

// Service entry: owns all Edge Light state. The panel (EdgeLight.qml) renders
// the glow, and the bar popup (EdgeLightPopup.qml) reads and changes state
// through this object.
//
// Nothing here polls. Theme changes come from a file watch, so the service
// does no work while the light is idle.
Item {
  id: service

  readonly property string home: Quickshell.env("HOME")
  // Overridable so tests can use a scratch file instead of the user's config.
  readonly property string settingsPath: Quickshell.env("EDGE_LIGHT_SETTINGS")
    || (home + "/.config/omarchy/edge-light/settings.json")
  readonly property string settingsDir: settingsPath.substring(0, settingsPath.lastIndexOf("/"))
  readonly property string themePath: Quickshell.env("EDGE_LIGHT_THEME")
    || (home + "/.local/state/omarchy/current/theme/colors.toml")
  readonly property string shellTomlPath: Quickshell.env("EDGE_LIGHT_SHELL_TOML")
    || (home + "/.local/state/omarchy/current/theme/shell.toml")
  readonly property string lookPath: Quickshell.env("EDGE_LIGHT_LOOK")
    || (home + "/.config/hypr/looknfeel.lua")

  // Persisted settings. Changed through update(), never assigned directly.
  property var settings: State.normalize({})

  // Runtime state. Not persisted: the light starts off after every restart.
  property bool isOn: false

  // Omarchy UI tokens for the popup (see lib/Theme.js). Rebuilt whenever one
  // of the three source files changes.
  property string colorsText: ""
  property string shellText: ""
  property string lookText: ""
  property var ui: Theme.buildUi("", "", "")

  function refreshUi() {
    ui = Theme.buildUi(colorsText, shellText, lookText)
  }

  // Writes settings to disk. Failures are logged, not thrown.
  function saveSettings() {
    try {
      settingsFile.setText(JSON.stringify(service.settings, null, 2) + "\n")
    } catch (e) {
      console.warn("edge-light: could not save settings:", e)
    }
  }

  // Apply a partial settings change. `persist` writes it to disk. Sliders call
  // with persist=false while dragging and true on release.
  function update(patch, persist) {
    service.settings = State.normalize(State.merge(service.settings, patch))
    if (persist) saveSettings()
  }

  function setLight(on) {
    service.isOn = on === true
  }

  // Full screen brightness while the light is on. Set via Omarchy's own helper,
  // so it uses the same backlight and DDC handling as the brightness keys.
  // Tests set EDGE_LIGHT_BRIGHTNESS=0 so they never change the screen.
  readonly property bool brightenOnLight: Quickshell.env("EDGE_LIGHT_BRIGHTNESS") !== "0"
  onIsOnChanged: {
    if (isOn && brightenOnLight && !brightenProcess.running) brightenProcess.running = true
  }

  Process {
    id: brightenProcess
    command: ["omarchy", "brightness", "display", "--no-osd", "100%"]
  }

  Component.onCompleted: mkdirProcess.running = true

  Process {
    id: mkdirProcess
    command: ["mkdir", "-p", service.settingsDir]
  }

  FileView {
    id: settingsFile
    path: service.settingsPath
    atomicWrites: true
    printErrors: false
    onLoaded: service.settings = State.parseSettings(text())
    onLoadFailed: function(error) { service.settings = State.normalize({}) }
  }

  FileView {
    id: themeFile
    path: service.themePath
    watchChanges: true
    printErrors: false
    onLoaded: { service.colorsText = text(); service.refreshUi() }
    onLoadFailed: function(error) { service.colorsText = ""; service.refreshUi() }
    onFileChanged: reload()
  }

  FileView {
    id: shellTomlFile
    path: service.shellTomlPath
    watchChanges: true
    printErrors: false
    onLoaded: { service.shellText = text(); service.refreshUi() }
    onLoadFailed: function(error) { service.shellText = ""; service.refreshUi() }
    onFileChanged: reload()
  }

  FileView {
    id: lookFile
    path: service.lookPath
    watchChanges: true
    printErrors: false
    onLoaded: { service.lookText = text(); service.refreshUi() }
    onLoadFailed: function(error) { service.lookText = ""; service.refreshUi() }
    onFileChanged: reload()
  }
}
