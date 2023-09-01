#from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QPushButton
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QPainterPath
from enum import Enum
from math import atan2

class PenType(Enum):
    ROUNDED = 1
    SQUARE = 2
    DEFAULT = 3
    LINE = 4
    ERASER = 5
    POLYLINE = 6

def drawRoundedPen(painter, point, drawingColor, penSize):
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setBrush(drawingColor)
    painter.setPen(Qt.NoPen)

    if penSize == 1:
        painter.drawRect(QRect(point.x(), point.y(), 1, 1))
    else:
        painter.drawEllipse(point, penSize/2, penSize/2)

def drawSquarePen(painter, point, drawingColor, penSize):
    painter.setRenderHint(QPainter.Antialiasing, False)
    pen = QPen(drawingColor, penSize, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
    painter.setPen(pen)
    painter.drawPoint(point)

def drawDefaultPen(painter, point, drawingColor, penSize):
    painter.setRenderHint(QPainter.Antialiasing, False)
    pen = QPen(drawingColor, penSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)
    painter.drawPoint(point)

def drawLineTool(painter, startPoint, currentPoint, drawingColor, penSize):
    painter.setRenderHint(QPainter.Antialiasing, False)
    pen = QPen(drawingColor, penSize, Qt.SolidLine, Qt.FlatCap, Qt.RoundJoin)
    painter.setPen(pen)
    painter.drawLine(startPoint, currentPoint)

def drawEraser(painter, point, drawingColor, penSize):
    eraserSize = penSize
    painter.setCompositionMode(QPainter.CompositionMode_Clear)
    painter.setRenderHint(QPainter.Antialiasing, False)
    painter.setBrush(Qt.SolidPattern)
    painter.drawEllipse(point, eraserSize / 2, eraserSize / 2)

from PyQt5.QtGui import QPainterPath, QPen
from PyQt5.QtCore import Qt

def point_to_line_distance(point, start, end):
    """Compute the perpendicular distance from a point to a line."""
    if start == end:
        return ((point.x() - start.x()) ** 2 + (point.y() - start.y()) ** 2) ** 0.5
    
    n = abs((end.x() - start.x()) * (start.y() - point.y()) - 
            (start.x() - point.x()) * (end.y() - start.y()))
    d = ((end.x() - start.x()) ** 2 + (end.y() - start.y()) ** 2) ** 0.5
    return n / d

def find_furthest_point(points, epsilon):
    """Find the point in the list that is the furthest from the line formed by the start and end points."""
    dmax = 0
    index = 0
    end = len(points) - 1
    for i in range(1, end):
        d = point_to_line_distance(points[i], points[0], points[end])
        if d > dmax:
            index = i
            dmax = d
    return index, dmax

def ramer_douglas_peucker(points, epsilon):
    """The Ramer-Douglas-Peucker algorithm for polyline simplification."""
    if not points:  # Safety check to ensure the points list is not empty
        return []
    index, dmax = find_furthest_point(points, epsilon)
    if dmax > epsilon:
        left_recursive = ramer_douglas_peucker(points[:index+1], epsilon)
        right_recursive = ramer_douglas_peucker(points[index:], epsilon)
        return left_recursive[:-1] + right_recursive
    return [points[0], points[-1]]

def compute_average_distance(points):
    """Compute the average distance of each point to the line formed by its neighboring points."""
    distances = [point_to_line_distance(points[i], points[i-1], points[i+1]) for i in range(1, len(points) - 1)]
    return sum(distances) / len(distances)

def adaptive_epsilon(points):
    """Compute epsilon value based on the characteristics of the points."""
    if len(points) < 3:
        return 5.0  
    
    avg_distance = compute_average_distance(points)
    
    if avg_distance < 0.5:
        return 5.0 
    elif avg_distance < 1.5:
        return 2.0 
    else:
        return 0.2 

def drawPolyline(painter, polylinePoints, drawingColor, penSize):
    """Draw a simplified polyline."""
    if not polylinePoints:  # check if the list is empty
        return

    painter.setRenderHint(QPainter.Antialiasing, False)
    pen = QPen(drawingColor, penSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)
    
    epsilon = adaptive_epsilon(polylinePoints)
    simplified_points = ramer_douglas_peucker(polylinePoints, epsilon)
    
    if not simplified_points:  # check if the list is empty after simplification
        return

    path = QPainterPath()
    path.moveTo(simplified_points[0])
    for point in simplified_points[1:]:
        path.lineTo(point)
    painter.drawPath(path)
