from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from Components.Canvas.DrawingBrushes import (PenType, drawRoundedPen, drawSquarePen, drawDefaultPen, drawLineTool, drawEraser, drawPolyline)
from Components.Canvas.DrawingUtilities import drawWithPen, interpolatedPoints


class DrawEventsMixin(QGraphicsView):

    def wheelEvent(self, event):
        """Handle mouse wheel event for zooming in and out."""
        zoomInFactor = 1.2
        zoomOutFactor = 1 / zoomInFactor
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)
        oldPos = self.mapToScene(event.pos())

        zoomFactor = zoomInFactor if event.angleDelta().y() > 0 else zoomOutFactor

        self.scale(zoomFactor, zoomFactor)
        self.zoom_level = self.transform().m11()

        newPos = self.mapToScene(event.pos())
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())
        self.zoom_changed = True

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.handle_left_button_press(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        self.mousePos = event.pos()
        if event.buttons() & Qt.LeftButton and self.drawing:
            self.handle_left_button_move(event)
        else:
            self.viewport().update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.LeftButton:
            self.handle_left_button_release(event)

    def handle_left_button_press(self, event):
        """Handle the logic when the left mouse button is pressed."""
        self.cache_current_state_if_needed()
        
        self.drawing = True
        self.lastPoint = self.scene_point_from_event(event)

        with QPainter(self.pixmap) as painter:
            self.draw_with_current_settings(painter)

        self.update_canvas_and_view()
        
        if self.penType in [PenType.LINE, PenType.POLYLINE]:
            self.handle_line_and_polyline()

        if self.penType == PenType.ERASER:
            self.showEraserIndicator = True

    def cache_current_state_if_needed(self):
        """Cache the current state if not in undo/redo action."""
        if not self.in_undo_redo_action:
            file_path = self.cache_pixmap_to_disk(self.pixmap)
            self.previousDrawings.append(file_path)
            self.redoDrawings.clear()  # Clear redo states since a new drawing action starts

    def draw_with_current_settings(self, painter):
        """Draw on the canvas using the current settings."""
        drawWithPen(painter, self.penType, self.drawingColor, self.penSize, point=self.lastPoint, startPoint=self.startPoint, polylinePoints=self.polylinePoints)

    def update_canvas_and_view(self):
        """Update the canvas and the view."""
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)
        self.update()

    def handle_line_and_polyline(self):
        """Handle specific logic for line and polyline."""
        self.startPoint = self.lastPoint
        self.tempPixmap = self.pixmap.copy()
        if self.penType == PenType.POLYLINE:
            self.polylinePoints.append(self.lastPoint)

    def start_drawing(self, event):
        """Initial setup when starting to draw."""
        self.drawing = True
        self.lastPoint = self.scene_point_from_event(event)

        # Additional setup for specific pen types
        if self.penType in [PenType.LINE, PenType.POLYLINE]:
            self.startPoint = self.lastPoint
            if self.penType == PenType.POLYLINE:
                self.polylinePoints.append(self.lastPoint)
            self.tempPixmap = self.pixmap.copy()

        if self.penType == PenType.ERASER:
            self.showEraserIndicator = True

    def handle_left_button_move(self, event):
        """Handle the drawing while the left mouse button is pressed."""
        currentPoint = self.scene_point_from_event(event)
        if self.penType in [PenType.LINE, PenType.POLYLINE]:
            self.draw_temp_pixmap(currentPoint)
        else:
            self.draw_continuous_line(currentPoint)

        self.lastPoint = currentPoint
        self.scene.update()

    def draw_temp_pixmap(self, currentPoint):
        """Draw on a temporary pixmap for tools like line and polyline."""
        self.pixmap = self.tempPixmap.copy()
        with QPainter(self.pixmap) as painter:
            if self.penType == PenType.LINE:
                drawLineTool(painter, self.startPoint, currentPoint, self.drawingColor, self.penSize)
            elif self.penType == PenType.POLYLINE:
                self.polylinePoints.append(currentPoint)
                drawPolyline(painter, self.polylinePoints, self.drawingColor, self.penSize)
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)

    def draw_continuous_line(self, currentPoint):
        """Draw continuous lines for tools like pencil and eraser."""
        with QPainter(self.pixmap) as painter:
            for point in interpolatedPoints(self.lastPoint, currentPoint):
                drawWithPen(painter, self.penType, self.drawingColor, self.penSize, point=point, startPoint=self.startPoint, polylinePoints=self.polylinePoints)
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)

    def handle_left_button_release(self, event):
        """Finish the drawing when the left mouse button is released."""
        endPoint = self.scene_point_from_event(event)
        if self.penType == PenType.LINE and self.startPoint and endPoint:
            with QPainter(self.pixmap) as painter:
                drawLineTool(painter, self.startPoint, endPoint, self.drawingColor, self.penSize)
            self.scene.clear()
            self.scene.addPixmap(self.pixmap)
        elif self.penType == PenType.POLYLINE:
            self.polylinePoints = []

        if self.penType == PenType.ERASER:
            self.showEraserIndicator = False

        self.drawing = False
        self.startPoint = None
        self.update()

    def update_current_pixmap(self):
        """Update the pixmap with the current drawing."""
        with QPainter(self.pixmap) as painter:
            drawWithPen(painter, self.penType, self.drawingColor, self.penSize, point=self.lastPoint, startPoint=self.startPoint, polylinePoints=self.polylinePoints)
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)
        self.update()
