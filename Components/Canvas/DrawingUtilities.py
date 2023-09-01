from PyQt5.QtCore import Qt, QPoint
from Components.Canvas.DrawingBrushes import PenType, drawRoundedPen, drawSquarePen, drawDefaultPen, drawLineTool, drawEraser, drawPolyline

def drawWithPen(painter, penType, drawingColor, penSize, point=QPoint(), startPoint=None, polylinePoints=[]):
    draw_methods = {
        PenType.ROUNDED: drawRoundedPen,
        PenType.SQUARE: drawSquarePen,
        PenType.DEFAULT: drawDefaultPen,
        PenType.POLYLINE: lambda p, pt, color, size: drawPolyline(p, polylinePoints, color, size),
        PenType.LINE: lambda p, pt, color, size: drawLineTool(p, startPoint, pt, color, size) if startPoint else None,
        PenType.ERASER: drawEraser,
    }

    draw_function = draw_methods.get(penType)
    if draw_function:
        draw_function(painter, point, drawingColor, penSize)

def interpolatedPoints(start: QPoint, end: QPoint):
    x_start, y_start = start.x(), start.y()
    x_end, y_end = end.x(), end.y()
    delta_x, delta_y = abs(x_end - x_start), abs(y_end - y_start)
    step_x = -1 if x_start > x_end else 1
    step_y = -1 if y_start > y_end else 1
    error = delta_x - delta_y

    while True:
        yield QPoint(x_start, y_start)
        if (x_start, y_start) == (x_end, y_end):
            break
        double_error = 2 * error
        if double_error > -delta_y:
            x_start += step_x
            error -= delta_y
        if double_error < delta_x:
            y_start += step_y
            error += delta_x

