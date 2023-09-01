from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPoint

def apply_drawing_preset(drawArea, preset_func):
    drawArea.clearDrawing()
    preset_func(drawArea.pixmap, drawArea.drawingColor, drawArea.penSize)
    drawArea.scene.clear()
    drawArea.scene.addPixmap(drawArea.pixmap)

def applyPreset1(pixmap, drawingColor, penSize):
    with QPainter(pixmap) as painter:
        pen = QPen(drawingColor, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        center = QPoint(50, 50)
        offset = penSize  # Use the penSize as the size for the preset
        painter.drawLine(center.x() - offset, center.y(), center.x() + offset, center.y())
        painter.drawLine(center.x(), center.y() - offset, center.x(), center.y() + offset)

def applyPreset2(pixmap, drawingColor, penSize):
    with QPainter(pixmap) as painter:
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(drawingColor)
        painter.setPen(Qt.NoPen)
        center = QPoint(50, 50)
        radius = penSize + 1  # Adjusted for visual similarity with 4-pixel width
        painter.drawEllipse(center, radius, radius)

