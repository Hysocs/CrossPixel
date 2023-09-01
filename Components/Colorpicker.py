from PyQt5.QtWidgets import QWidget, QSlider, QHBoxLayout, QSizePolicy, QVBoxLayout
from PyQt5.QtCore import Qt, QRect, QPointF, QLineF, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPaintEvent, QResizeEvent, QConicalGradient, QRadialGradient, QMouseEvent, QLinearGradient
from Components.Styles import StylesSetupMixin

class ColorCircle(QWidget):
    currentColorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None, startupcolor: list = [255, 255, 255], margin=10) -> None:
        super().__init__(parent=parent)
        self.side_length = 0
        self.selected_color = QColor(
            startupcolor[0], startupcolor[1], startupcolor[2], 255)
        self.x = 0.5
        self.y = 0.5
        self.h = self.selected_color.hueF()
        self.s = self.selected_color.saturationF()
        self.v = self.selected_color.valueF()
        self.margin = margin
        self.zoom_level = 1.1
        self.brightness_adjusted = False

        self._cached_gradient = None

        qsp = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        qsp.setHeightForWidth(True)
        self.setSizePolicy(qsp)

    def resizeEvent(self, ev: QResizeEvent) -> None:
        size = min(self.width(), self.height()) - self.margin * 2
        size = int(size * self.zoom_level)
        self.side_length = size
        self.square = QRect(0, 0, size, size)
        self.square.moveCenter(self.rect().center())

    def paintEvent(self, ev: QPaintEvent) -> None:
        center = QPointF(self.width() / 2, self.height() / 2)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.HighQualityAntialiasing)

        adjusted_side_length = int(self.side_length * self.zoom_level)
        adjusted_square = QRect(0, 0, adjusted_side_length, adjusted_side_length)
        adjusted_square.moveCenter(self.rect().center())

        # Check if gradient is cached
        if not hasattr(self, '_cached_gradient') or self._cached_gradient is None:
            # Create horizontal gradient for hue
            hsv_grad = QLinearGradient(adjusted_square.topLeft(), adjusted_square.topRight())
            granularity = 360
            for deg in range(granularity):
                hue_value = deg / granularity
                col = QColor.fromHsvF(hue_value, 1, self.v, self.selected_color.alphaF())
                hsv_grad.setColorAt(hue_value, col)
            self._cached_gradient = hsv_grad
        else:
            hsv_grad = self._cached_gradient

        # Draw the hue gradient
        p.setPen(Qt.transparent)
        p.setBrush(hsv_grad)
        p.drawRect(adjusted_square)

        # Create vertical gradient for saturation
        val_grad = QLinearGradient(adjusted_square.topLeft(), adjusted_square.bottomLeft())
        val_grad.setColorAt(0.0, Qt.transparent)
        
        adjusted_alpha = self.selected_color.alphaF() ** 0.45
        val_grad.setColorAt(1.0, QColor.fromHsvF(self.h, 0, self.v, adjusted_alpha))

        # Draw the saturation gradient
        p.setBrush(val_grad)
        p.drawRect(adjusted_square)

        # Draw the selection point
        rounded_point = QPointF(self.x * self.width(), self.y * self.height())
        if self.brightness_adjusted:
            adjusted_value = max(self.v - 0.1, 0)
            darker_color = self.selected_color.toHsv()
            darker_color.setHsv(darker_color.hue(), darker_color.saturation(), int(adjusted_value * 255))
            darker_color.setAlpha(self.selected_color.alpha())
            p.setPen(Qt.black)
            p.setBrush(darker_color)
        else:
            p.setPen(Qt.black)
            p.setBrush(self.selected_color)

        p.drawEllipse(rounded_point, 8, 8)

    def recalc(self) -> None:
        alpha = self.selected_color.alpha()  # Preserve the current alpha value
        prev_v = self.selected_color.valueF() # Store the previous brightness value
        self.selected_color.setHsvF(self.h, self.s, self.v)
        
        # If brightness has changed, invalidate the cached gradient
        if prev_v != self.selected_color.valueF():
            self._cached_gradient = None
        
        self.selected_color.setAlpha(alpha)  # Re-apply the preserved alpha value
        self.currentColorChanged.emit(self.selected_color)
        self.repaint()

    def map_color(self, x: int, y: int) -> tuple:
        # Ensure x and y are within the bounds of the square
        x = max(0, min(x, self.side_length))
        y = max(0, min(y, self.side_length))

        # Calculate the hue and saturation based on the position within the square
        self.h = min((x - self.square.left()) / float(self.side_length), 1.0)
        self.s = 1.0 - min((y - self.square.top()) / float(self.side_length), 1.0)

        return self.h, self.s, self.v

    def processMouseEvent(self, ev: QMouseEvent) -> None:
        x, y = ev.x(), ev.y()

        # Check bounds and adjust if necessary
        if x < self.square.left():
            x = self.square.left()
        elif x > self.square.right():
            x = self.square.right()

        if y < self.square.top():
            y = self.square.top()
        elif y > self.square.bottom():
            y = self.square.bottom()

        if ev.button() == Qt.MouseButton.RightButton:
            self.h, self.s, self.v = 0, 0, 1  # Set to white
            self.x, self.y = 0.5, 0.9  # Set to the center
        else:
            self.h, self.s, self.v = self.map_color(x, y)
            self.x = x / self.width()
            self.y = y / self.height()

        self.recalc()

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        self.processMouseEvent(ev)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        self.processMouseEvent(ev)

    def setHue(self, hue: float) -> None:
        if 0 <= hue <= 1:
            self.h = float(hue)
            self.recalc()
        else:
            raise TypeError("Value must be between 0.0 and 1.0")

    def setSaturation(self, saturation: float) -> None:
        if 0 <= saturation <= 1:
            self.s = float(saturation)
            self.recalc()
        else:
            raise TypeError("Value must be between 0.0 and 1.0")

    def setValue(self, value: float) -> None:
        if 0 <= value <= 1:
            self.v = float(value)
            
            # Check if brightness is adjusted from its default value
            self.brightness_adjusted = self.v != 1.0
            
            self.recalc()
        else:
            raise TypeError("Value must be between 0.0 and 1.0")

    def setAlpha(self, alpha: float) -> None:
        """Set the alpha (opacity) of the current color."""
        self.selected_color.setAlpha(alpha)
        self._cached_gradient = None  # Invalidate the cached gradient
        self.recalc()

    def setColor(self, color: QColor) -> None:
        self.h = color.hueF()
        self.s = color.saturationF()
        self.v = color.valueF()
        self.recalc()

    def getHue(self) -> float:
        return self.h

    def getSaturation(self) -> float:
        return self.s

    def getValue(self) -> float:
        return self.v

    def getColor(self) -> QColor:
        return self.selected_color


class ColorCircleDialog(QWidget, StylesSetupMixin):  # Mixin Integration
    currentColorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None, width: int = 500, startupcolor: list = [255, 255, 255]) -> None:
        super().__init__(parent=parent)
        self.resize(width, width)

        mainlay = QVBoxLayout()

        self.wid = ColorCircle(self, startupcolor=startupcolor)
        self.wid.setFixedSize(110, 110)  # Set a fixed size for the ColorCircle widget
        self.wid.currentColorChanged.connect(lambda x: self.currentColorChanged.emit(x))
        mainlay.addWidget(self.wid, alignment=Qt.AlignTop | Qt.AlignHCenter)  # Align the ColorCircle to the top center

        # Brightness Slider layout with spacers for centering
        brightness_slider_layout = QHBoxLayout()
        brightness_slider_layout.addStretch(1)  # Spacer on the left
        brightness_fader = QSlider(Qt.Horizontal)  # Horizontal slider for brightness
        brightness_fader.setMinimum(0)
        brightness_fader.setMaximum(511)
        brightness_fader.setValue(511)
        brightness_fader.valueChanged.connect(lambda x: self.wid.setValue(x/511))
        brightness_fader.setFixedHeight(10)  # Set the desired height for the slider
        brightness_fader.setFixedWidth(108)  # Set the desired width for the slider
        brightness_fader.setStyleSheet(self.slider_stylesheet())  # Apply Stylesheet
        brightness_slider_layout.addWidget(brightness_fader)
        brightness_slider_layout.addStretch(1)  # Spacer on the right

        mainlay.addLayout(brightness_slider_layout)

        # Opacity Slider layout with spacers for centering
        opacity_slider_layout = QHBoxLayout()
        opacity_slider_layout.addStretch(1)  # Spacer on the left
        opacity_fader = QSlider(Qt.Horizontal)  # Horizontal slider for opacity
        opacity_fader.setMinimum(0)
        opacity_fader.setMaximum(255)
        opacity_fader.setValue(255)
        opacity_fader.valueChanged.connect(self.updateOpacity)
        opacity_fader.setFixedHeight(10)  # Set the desired height for the slider
        opacity_fader.setFixedWidth(108)  # Set the desired width for the slider
        opacity_fader.setStyleSheet(self.slider_stylesheet())  # Apply Stylesheet
        opacity_slider_layout.addWidget(opacity_fader)
        opacity_slider_layout.addStretch(1)  # Spacer on the right

        mainlay.addLayout(opacity_slider_layout)
        
        # Adjust the margins to reduce padding
        mainlay.setContentsMargins(0, 0, 0, 0)  # Set all margins to 0

        self.setLayout(mainlay)

    def updateOpacity(self, value):
        self.wid.setAlpha(value)  # Use the new setAlpha method
        self.currentColorChanged.emit(self.wid.getColor())
