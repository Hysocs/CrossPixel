from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QKeySequence
from Components.Canvas.DrawingAreaMain import DrawArea, PenType


class EventHandlersMixin:
    # ----- Drawing Methods -----
    def applyCrosshair(self):
        drawn_pixmap = self.drawingBoard.pixmap.copy()
        self.overlay.setOverlayImage(drawn_pixmap)
        self.overlay.show()  # Make sure the overlay widget is shown after setting the overlay image

    def changeDrawingColor(self, color: QColor):
        # Use the QColor object as needed
        self.drawingBoard.setDrawingColor(color)


    def toggleCenterCross(self, state):
        self.drawingBoard.showCenterCross = state == Qt.Checked
        self.drawingBoard.updateDrawing()

    def toggleCenterView(self):
        self.drawingBoard.showCenter = not self.drawingBoard.showCenter
        self.drawingBoard.updateDrawing()

    def changePenType(self, index):
        pen_types = [PenType.DEFAULT, PenType.ROUNDED, PenType.SQUARE, PenType.POLYLINE, PenType.LINE, PenType.ERASER]
        self.drawingBoard.setPenType(pen_types[index])

    def updatePresetWithSize(self):
        self.drawingBoard.setPenSize(self.penSizeSlider.value())
        if self.activePreset:
            self.activePreset()

    # ----- Window and Overlay Methods -----
    def closeEvent(self, event):
        self.overlay.close()
        event.accept()

    # ----- Mouse Event Handlers -----
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.moving:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = False

    def toggleCenterCrossPosition(self):
        if self.overlay.isVisible():
            if self.crosshair_at_default:
                # Set custom offsets
                x_offset = self.x_offset_value
                y_offset = self.y_offset_value
            else:
                # Set default offsets (0, 0)
                x_offset = 0
                y_offset = 0
            
            self.overlay.setOffsets(x_offset, y_offset)
            self.crosshair_at_default = not self.crosshair_at_default  # Toggle the attribute