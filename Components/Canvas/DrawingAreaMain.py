import os
import time
import glob
import logging
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, QPoint, QTimer, QRect, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QColor
from Components.Canvas.DrawingBrushes import PenType
from Components.Canvas.DrawingOverlays import DrawOverlaysMixin
from Components.Canvas.DrawingEventHandlers import DrawEventsMixin
from Components.Canvas.DrawingPresets import applyPreset1, applyPreset2, apply_drawing_preset
from Components.Settings.Keybinds import Keybinds

logging.basicConfig(level=logging.INFO)

appdata_local_path = os.path.join(os.path.expanduser("~"), "AppData", "Local")
CROSSPIXEL_DIR_PATH = os.path.join(appdata_local_path, "CrossPixel")

class DrawArea(DrawEventsMixin, DrawOverlaysMixin, QGraphicsView):
    def __init__(self, scale_factor, parent=None):
        super().__init__(parent)
        self.setupAttributes(scale_factor)
        self.setupUI()
        self.initializeEventsAndTimers()

    def setupAttributes(self, scale_factor):
        """Initialize attributes for the drawing area."""
        self.scale_factor = scale_factor
        self.penSize = 1
        self.drawingColor = QColor(Qt.black)
        self.lastPoint = None
        self.drawing = False
        self.showBrushSizeIndicator = True
        self.showCenterCross = False
        self.showCenter = False
        self.pixmap = QPixmap(100, 100)
        self.pixmap.fill(Qt.transparent)
        self.penType = PenType.DEFAULT
        self.previousDrawings = []  # Store previous drawings
        self.redoDrawings = []      # Store redo drawings
        self.polylinePoints = []    # Store polyline points
        self.startPoint = None
        self.showEraserIndicator = False
        self.presetCleared = False
        self.ctrl_pressed = False
        self.zoom_level = 1         # Initial zoom level
        self.zoom_changed = True
        self.last_draw_time = None
        self.in_undo_redo_action = False
        self.mousePos = QPoint(0, 0)

    def setupUI(self):
        """Setup UI components for the drawing area."""
        self.scene = QGraphicsScene(self)
        self.scene.addPixmap(self.pixmap)
        self.setScene(self.scene)
        self.scale(self.scale_factor, self.scale_factor)
        self.setFixedSize(int(100 * self.scale_factor), int(100 * self.scale_factor))
        # Turn off scroll bars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(235, 235, 235))  # Set to off-white
        self.setPalette(p)

    def initializeEventsAndTimers(self):
        """Initialize event handlers and timers."""
        # QTimer for updating overlays
        self.overlayUpdateTimer = QTimer(self)
        self.overlayUpdateTimer.timeout.connect(self.update_overlays)
        self.overlayUpdateTimer.start(100)

        # Keybinds handler
        self.keybinds = Keybinds()
        self.keybinds.register_action("undo", self.undoLastDrawing)
        self.keybinds.register_action("redo", self.redoLastDrawing)
     
    # Setters and Getters
    def setPenSize(self, size):
        self.penSize = size

    def setDrawingColor(self, color):
        self.drawingColor = color

    def setPenType(self, pen_type):  
        self.penType = pen_type

    def isPresetCleared(self):
        return self.presetCleared

    # Drawing and UI update methods
    def updateDrawing(self):
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)
        if self.showCenterCross:
            self.drawCenterCross()

    def update_overlays(self):
        self.viewport().update()

    def paintEvent(self, event: QEvent):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        self.draw_overlays(painter)

    def clearDrawing(self):
        file_path = self.cache_pixmap_to_disk(self.pixmap)
        self.previousDrawings.append(file_path)
        self.pixmap.fill(Qt.transparent)
        self.updateDrawing()
        self.presetCleared = True

    # Preset methods
    def applyPreset1(self):
        apply_drawing_preset(self, applyPreset1)

    def applyPreset2(self):
        apply_drawing_preset(self, applyPreset2)

    # Utility methods
    def getRelativePos(self, global_pos):
        widget_global_pos = self.mapToGlobal(QPoint(0, 0))
        relative_pos = global_pos - widget_global_pos
        relative_pos -= QPoint(1, 0)
        return relative_pos / self.transform().m11()

    def map_mouse_to_scene(self, event_pos):
        scene_point = self.mapToScene(event_pos)
        x = round(scene_point.x())
        y = round(scene_point.y())
        return QPoint(x, y)
    
    def scene_point_from_event(self, event):
        """Convert the event position to a scene point."""
        scenePointF = self.mapToScene(event.pos())
        adjusted_x = scenePointF.x() - 0.5
        adjusted_y = scenePointF.y() - 0.5
        return QPoint(round(adjusted_x), round(adjusted_y))

    def setPixmap(self, pixmap):
        self.pixmap = pixmap.scaled(self.pixmap.width(), self.pixmap.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.updateDrawing()

    def cache_pixmap_to_disk(self, pixmap: QPixmap) -> str:
        """Save the given pixmap to disk and return its filename."""
        timestamp = str(int(time.time() * 1000))  # Using milliseconds for uniqueness
        file_path = os.path.join(CROSSPIXEL_DIR_PATH, f"{timestamp}.png")
        pixmap.save(file_path)
        return file_path

    def load_pixmap_from_disk(self, file_path: str) -> QPixmap:
        """Load a QPixmap from the given file path."""
        if os.path.exists(file_path):
            return QPixmap(file_path)
        else:
            # Handle the error appropriately, maybe log it
            logging.error(f"Error: File {file_path} not found.")
            return QPixmap()

    def undoLastDrawing(self):
        """Undo the last drawing action."""
        print("Attempting to undo last drawing")

        if self.previousDrawings:
            # Set in_undo_redo_action to True to prevent state save in mousePressEvent
            self.in_undo_redo_action = True

            # Move the current state to the redo list
            current_state_path = self.cache_pixmap_to_disk(self.pixmap)
            self.redoDrawings.append(current_state_path)

            # Load the previous state from previousDrawings
            file_path_to_load = self.previousDrawings.pop()
            loaded_pixmap = self.load_pixmap_from_disk(file_path_to_load)
            
            # Ensure the loaded pixmap is valid before using it
            if not loaded_pixmap.isNull():
                self.pixmap = loaded_pixmap
                self.updateDrawing()

            # Set in_undo_redo_action back to False after the operation
            self.in_undo_redo_action = False

    def redoLastDrawing(self):
        """Redo the last drawing action."""
        print("Attempting to redo last drawing")

        if self.redoDrawings:
            # Load and display the pixmap from redoDrawings (don't pop yet)
            file_path_to_load = self.redoDrawings[-1]
            loaded_pixmap = self.load_pixmap_from_disk(file_path_to_load)
            
            # Ensure the loaded pixmap is valid before using it
            if not loaded_pixmap.isNull():
                # Save the current state to previousDrawings
                current_state_path = self.cache_pixmap_to_disk(self.pixmap)
                self.previousDrawings.append(current_state_path)

                # Update the pixmap and remove the redone drawing from redoDrawings
                self.pixmap = loaded_pixmap
                self.updateDrawing()
                self.redoDrawings.pop()

    def clearDrawing(self):
        file_path = self.cache_pixmap_to_disk(self.pixmap)
        self.previousDrawings.append(file_path)
        self.pixmap.fill(Qt.transparent)
        self.updateDrawing()
        self.presetCleared = True

    def clear_saved_pixmaps(self):
        """Delete all saved pixmap images."""
        for filepath in glob.glob(os.path.join(CROSSPIXEL_DIR_PATH, "*.png")):
            try:
                os.remove(filepath)
            except Exception as e:
                logging.error(f"Error deleting {filepath}: {e}")