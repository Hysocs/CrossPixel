from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QRect, QEvent
from PyQt5.QtGui import QPainter, QBrush, QPixmap
from Components.Settings.Keybinds import Keybinds
from Components.Settings.Config import load_keybinds_from_file
from pynput import mouse

class OverlayCrosshairToScreen(QWidget):
    """A custom widget that provides an overlay functionality."""
    
    _IMAGE_SIZE = 100
    _IMAGE_OPACITY = 0.95

    def __init__(self):
        super().__init__()
        self._setupUI()
        self.start_mouse_listener()
        self.overlayImage = None
        self.x_offset = 0  # default x offset value
        self.y_offset = 0  # default y offset value

        self.image_opacity = self._IMAGE_OPACITY

        # Initialize the Keybinds system and register the toggle visibility action
        self.keybinds = Keybinds()
        self.keybinds.register_action("hide_crosshair", self.toggle_visibility)
        self.keybinds.register_action("offset_keybind", self.handle_offset_keybind)
        self.offset_applied = False

    def _setupUI(self):
        """Initialize the UI settings."""
        self._setWindowAttributes()
        self._setGeometryToScreenSize()
        self.installEventFilter(self)

    def _setWindowAttributes(self):
        """Set the window's appearance and behavior attributes."""
        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint | Qt.Tool | Qt.WindowDoesNotAcceptFocus | Qt.WA_X11DoNotAcceptFocus | Qt.WindowTransparentForInput
        self.setAttribute(Qt.WA_AlwaysStackOnTop, True)
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setStyleSheet("border: none;")

    def _setGeometryToScreenSize(self):
        """Set the geometry of the widget to match the primary screen size."""
        screen = QApplication.primaryScreen()
        self.setGeometry(screen.geometry())

    def setOverlayImage(self, image: QPixmap):
        if isinstance(image, QPixmap):  # Ensure that image is a QPixmap
            self.overlayImage = image
            self.update()  # Trigger a repaint

    def paintEvent(self, event):
        """Handle the paint event. Draw the overlay if the image is set."""
        if self.overlayImage:
            self._drawOverlayContent()

    def _drawOverlayContent(self):
        """Draw the overlay's content on the widget."""
        painter = QPainter(self)
        self._drawTransparentBackground(painter)
        self._drawCenteredOverlayImage(painter)

    def _drawTransparentBackground(self, painter: QPainter):
        """Draw a transparent background on the given painter."""
        painter.setBrush(QBrush(Qt.transparent))
        painter.drawRect(0, 0, self.width(), self.height())

    def _drawCenteredOverlayImage(self, painter: QPainter):
        """Draw the overlay image centered on the given painter considering the offsets."""
        x_offset = (self.width() - self._IMAGE_SIZE) // 2 + self.x_offset
        y_offset = (self.height() - self._IMAGE_SIZE) // 2 + self.y_offset
        painter.setOpacity(self.image_opacity)
        painter.drawImage(QRect(x_offset, y_offset, self._IMAGE_SIZE, self._IMAGE_SIZE), self.overlayImage.toImage())

    def eventFilter(self, obj, event):
        """Override event filter to ignore mouse events."""
        if obj == self:
            if event.type() in (QEvent.MouseButtonPress, 
                                QEvent.MouseButtonRelease, 
                                QEvent.MouseButtonDblClick,
                                QEvent.MouseMove):
                return True  # Ignore the event
        return super().eventFilter(obj, event)
    
    def toggle_visibility(self):
        """Toggle the visibility of the overlay."""
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def handle_offset_keybind(self):
        """Handle the offset keybind action."""
        if self.offset_applied:
            # If the offset is already applied, revert it to the center
            self.x_offset = 0
            self.y_offset = 0
        else:
            # If the offset is not applied, apply it
            x_offset, y_offset = self.get_offset_values_from_config()
            self.x_offset = x_offset
            self.y_offset = y_offset
            
        self.update()
        self.offset_applied = not self.offset_applied  # Toggle the flag

    def apply_offset(self, x_offset, y_offset):
        """Apply the offset values to the crosshair."""
        self.x_offset += x_offset
        self.y_offset += y_offset
        self.update()  # Trigger a repaint to reflect the new position

    def get_offset_values_from_config(self):
        """Fetch the offset values from the configuration file."""
        keybinds = load_keybinds_from_file()
        x_offset = keybinds.get("offset_x", 0)
        y_offset = keybinds.get("offset_y", 0)
        return x_offset, y_offset
    
    def get_crosshair_mode_from_config(self):
        """Fetch the crosshair mode from the configuration file."""
        keybinds = load_keybinds_from_file()
        return keybinds.get("crosshair_disable_mode", "Disabled")
    
    def start_mouse_listener(self):
        """Start a global mouse listener to handle mouse button presses."""
        self.mouse_listener = mouse.Listener(on_click=self.handle_mouse_click)
        self.mouse_listener.start()

    def handle_mouse_click(self, x, y, button, pressed):
        """Handle global mouse button presses."""
        crosshair_mode = self.get_crosshair_mode_from_config()
        #print(f"Mouse button {button} {'pressed' if pressed else 'released'}. Crosshair mode: {crosshair_mode}")

        # Logic to determine whether to hide the crosshair based on the integer value
        if crosshair_mode == 1 and button == mouse.Button.right:  
            self.toggle_visibility_based_on_press(pressed)
        elif crosshair_mode == 2 and button == mouse.Button.left:  
            self.toggle_visibility_based_on_press(pressed)
        elif crosshair_mode == 3 and button in [mouse.Button.left, mouse.Button.right]: 
            self.toggle_visibility_based_on_press(pressed)

    def toggle_visibility_based_on_press(self, pressed):
        """Toggle visibility based on mouse button press."""
        if pressed:
            self.set_opacity(0.0)  # Make the crosshair invisible
        else:
            self.set_opacity(self._IMAGE_OPACITY)  # Restore the crosshair's opacity

    def set_opacity(self, opacity_value):
        """Set the opacity of the crosshair."""
        self.image_opacity = opacity_value
        self.update()  # Trigger a repaint to reflect the new opacity
