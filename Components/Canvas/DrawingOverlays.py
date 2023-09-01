from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPointF, QPoint, QRect
from Components.Canvas.DrawingBrushes import PenType

class DrawOverlaysMixin:
    
    def draw_overlays(self, painter: QPainter):
        """Main function to draw overlays."""
        self.update_view_center_if_zoomed()
        self.draw_center_overlay(painter)
        self.draw_border_overlay(painter)
        # Use the penSize attribute to draw the brush size indicator
        self.draw_brush_size_indicator(painter)

    def update_view_center_if_zoomed(self):
        """Update view center if zoom has changed."""
        if self.zoom_changed:
            canvas_center = QPointF(50, 50)  # Center of the canvas in canvas coordinates
            self.view_center = self.mapFromScene(canvas_center)  # Convert to view coordinates
            self.zoom_changed = False

    def draw_center_overlay(self, painter: QPainter):
        """Draw center overlay."""
        if self.showCenter:
            self._draw_crosshair(painter, self.view_center)

    def draw_border_overlay(self, painter: QPainter):
        """Draw border overlay."""
        border_thickness = self.calculate_border_thickness()
        border_color = QColor("#C0C0C0")
        border_pen = QPen(border_color, border_thickness)
        viewport_rect = self.viewport().rect()
        painter.setPen(border_pen)
        painter.drawRect(viewport_rect)

    def calculate_border_thickness(self) -> int:
        """Calculate border thickness based on zoom level."""
        return max(1, int((4 - self.transform().m11()) * 100))
    
    def draw_brush_size_indicator(self, painter: QPainter):
        """Draw a brush size indicator around the mouse position."""
        if not getattr(self, 'showBrushSizeIndicator', False):
            return

        scaled_pen_size = max(1, int(self.penSize * self.transform().m11() * 0.5))
        indicator_pen = QPen(QColor(150, 150, 150, 55), 2, Qt.DotLine)
        painter.setPen(indicator_pen)

        if self.penType in (PenType.SQUARE, PenType.LINE):
            half_size = scaled_pen_size
            painter.drawRect(QRect(self.mousePos - QPoint(half_size, half_size), self.mousePos + QPoint(half_size, half_size)))
        else:
            painter.drawEllipse(self.mousePos, scaled_pen_size, scaled_pen_size)

    def _draw_crosshair(self, painter, center):
        """Draw a crosshair at the provided center point."""
        line_length = 500
        pen_width = 6
        center_pen = QPen(QColor(150, 150, 150, 55), pen_width, Qt.SolidLine)
        painter.setPen(center_pen)
        painter.drawLine(center.x() - line_length, center.y(), center.x() + line_length, center.y())  # Horizontal line
        painter.drawLine(center.x(), center.y() - line_length, center.x(), center.y() + line_length)  # Vertical line
