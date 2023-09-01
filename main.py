import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QAction, QMenu
from PyQt5.QtGui import QColor, QPalette, QIcon
from Components.OverlayCrosshairToScreen import OverlayCrosshairToScreen
from Components.Canvas.DrawingAreaMain import DrawArea, PenType
from Components.GuiSetup import GuiSetupMixin
from Components.EventHandlers import EventHandlersMixin
from Components.Styles import StylesSetupMixin
from Components.Canvas.DrawingOverlays import DrawOverlaysMixin
from Components.MemoryManager import MemoryManager
from Components.Settings.Settings import SettingsDialog
from Components.Settings.Keybinds import Keybinds

logging.basicConfig(level=logging.INFO)


class CrosshairDesigner(GuiSetupMixin, EventHandlersMixin, StylesSetupMixin, DrawOverlaysMixin, QMainWindow):
    def __init__(self, memory_manager: MemoryManager, keybinds: Keybinds, drawing_area: DrawArea):
        super().__init__()
        
        self.memory_manager = memory_manager
        self.keybinds = keybinds
        self.drawingArea = drawing_area
        
        self._initialize_components()
        self._initialize_UI()
        self.setWindowIcon(QIcon("logo.ico"))

    def _initialize_components(self):
        self.keybinds.register_action("self_destruct", self.close_app)

        EventHandlersMixin.__init__(self)

        self.moving = False
        self.offset = None
        self.activePreset = None
        self.presetCleared = False
        self.keybind = None
        self.x_offset = 0
        self.y_offset = 0
        self.x_offset_value = 0
        self.y_offset_value = 0
        self.crosshair_at_default = True

    def _initialize_UI(self):
        self.setupAttributes()
        self.setupMainWindowProperties()
        self.setupDrawingBoard()
        self.setupControls()
        self.arrangeLayouts()
        self._set_main_window_palette()

    def _set_main_window_palette(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(24, 24, 24))
        self.setPalette(palette)

    def getCloseButton(self):
        return self.centralWidget().layout().itemAt(0).widget().layout().itemAt(2).widget()

    def closeEvent(self, event):
        try:
            self.keybinds._unregister_global_hotkeys()
            self.memory_manager.release_memory()
            self.drawingArea.clear_saved_pixmaps()
        except Exception as e:
            logging.error(f"Error in closeEvent: {e}")

        super().closeEvent(event)

    def close_app(self):
        self.closeEvent(None)


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("logo.ico"))

    memory_manager = MemoryManager()
    keybinds = Keybinds()
    drawing_area = DrawArea(1.0)

    window = CrosshairDesigner(memory_manager, keybinds, drawing_area)

    close_button_stylesheet = window.setupCloseButtonStylesheet()
    window.getCloseButton().setStyleSheet(close_button_stylesheet)

    window.show()
    window.setWindowIcon(QIcon("logo2.ico"))
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
