import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QComboBox, QLabel, QFileDialog, QDialog, QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QPixmap, QMovie, QIcon
from Components.OverlayCrosshairToScreen import OverlayCrosshairToScreen
from Components.Canvas.DrawingAreaMain import DrawArea, PenType
from Components.Settings.Settings import SettingsDialog
from Components.Colorpicker import ColorCircle,  ColorCircleDialog

class GuiSetupMixin:
    
    def setupAttributes(self):
        """Setup any required attributes for the UI."""
        self.overlay = OverlayCrosshairToScreen()
        self.buttonLayout = QVBoxLayout()
        self.current_keybind = None  # Add this line to store current keybind
        self.x_offset_value = 0  # Add this line to store current x offset
        self.y_offset_value = 0  # Add this line to store current y offset

    def setupDrawingBoard(self):
        """Setup the drawing board and associated controls."""
        self.drawingBoard = DrawArea(scale_factor=4)
        self.penSizeSlider = QSlider(Qt.Horizontal, minimum=1, maximum=50, value=1, tickInterval=1, tickPosition=QSlider.TicksBelow)
        self.penSizeSlider.valueChanged.connect(self.updatePresetWithSize)
        self.drawingBoard.setPenSize(self.penSizeSlider.value())
        self.drawingBoard.setPenType(PenType.DEFAULT)
        
        # Apply the style, dimensions, and layout properties to the penSizeSlider
        self.penSizeSlider.setTickPosition(QSlider.NoTicks)
        self.penSizeSlider.setFixedHeight(10)  # Set the desired height for the slider
        self.penSizeSlider.setFixedWidth(108)  # Set the desired width for the slider
        self.penSizeSlider.setStyleSheet(self.slider_stylesheet())  # Apply Stylesheet


    def setupControls(self):
        """Setup the control buttons and their styles."""
        # Control buttons
        self.applyButton = self.createButton("Apply Crosshair", self.applyCrosshair)
        self.applyButton.setFixedSize(402, 23)

        self.colorCircle =  ColorCircleDialog()
        self.colorCircle.currentColorChanged.connect(self.changeDrawingColor)
        self.colorCircle.setFixedSize(110, 140)  # Or any size you deem appropriate


        self.clearButton = self.createButton("Clear", self.drawingBoard.clearDrawing)
        self.presetButton = self.createButton("+ Preset", self.drawingBoard.applyPreset1)
        self.preset2Button = self.createButton("⬤ Preset", self.drawingBoard.applyPreset2)
        self.centerViewButton = self.createButton("Center View", self.toggleCenterView)
        self.undoButton = self.createButton("Undo", self.drawingBoard.undoLastDrawing)
        self.redoButton = self.createButton("Redo", self.drawingBoard.redoLastDrawing)
        self.undoButton.setFixedSize(54, 25)  # Adjust 50 to your preferred dimension
        self.redoButton.setFixedSize(54, 25)


        # Settings Button
        self.settingsButton = QPushButton("Settings", self)
        self.settingsButton.clicked.connect(self.openSettings)
        self.settingsButton.setStyleSheet(self.button_stylesheet())

        # Save Button
        self.saveButton = QPushButton("Save", self)
        self.saveButton.clicked.connect(self.saveDrawing)
        self.saveButton.setStyleSheet(self.button_stylesheet())  # Apply the stylesheet here
        self.buttonLayout.addWidget(self.saveButton)

        # Upload Button
        self.uploadButton = QPushButton("Upload", self)
        self.uploadButton.clicked.connect(self.uploadDrawing)
        self.uploadButton.setStyleSheet(self.button_stylesheet())  # Apply the stylesheet here
        self.buttonLayout.addWidget(self.uploadButton)

        # Pen ComboBox
        self.penComboBox = QComboBox()
        self.penComboBox.addItems(["Default Pen", "Rounded Pen", "Square Pen", "Poly Line", "Line Tool", "Eraser"])
        self.penComboBox.currentIndexChanged.connect(self.changePenType)
        self.penComboBox.setCurrentIndex(0)

        # Set the styles
        self.setStyles()

    def saveDrawing(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Crosshair", "", "PNG Files (*.png);;JPEG Files (*.jpeg *.jpg);;All Files (*)")
        if filePath:
            self.drawingBoard.pixmap.save(filePath)

    def uploadDrawing(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Upload Crosshair", "", "Image Files (*.png *.jpeg *.jpg);;All Files (*)")
        if filePath:
            pixmap = QPixmap(filePath)
            self.drawingBoard.setPixmap(pixmap)

    def createButton(self, text, callback):
        """Utility function to create a button."""
        button = QPushButton(text, self)
        button.clicked.connect(callback)
        return button

    def setStyles(self):
        """Set styles for the controls."""
        base_button_stylesheet = self.button_stylesheet()
        text_style = "color: white; letter-spacing: 2px;"
        combobox_stylesheet = self.combobox_stylesheet()
        
        buttons = [self.applyButton, self.colorCircle, self.clearButton, self.presetButton, self.preset2Button, self.centerViewButton, self.undoButton, self.redoButton]
        
        for button in buttons:
                button.setStyleSheet(base_button_stylesheet + text_style)
                
        self.penComboBox.setStyleSheet(combobox_stylesheet)

    def arrangeLayouts(self):
        """Arrange layouts for the main window."""
        self.createTitleBar()
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_bar)

        content_layout = self.createBottomLayout()
        main_layout.addLayout(content_layout)


        centralWidget = QWidget()
        centralWidget.setLayout(main_layout)
        self.setCentralWidget(centralWidget)

    def createTitleBar(self):
        """Create the custom title bar."""
        self.title_bar = QWidget(self)
        title_bar_layout = QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)  # Increase the left margin by 5 pixels
        self.title_bar.setMaximumHeight(30)  # Limit the height of the title bar

        # Title label
        self.title_label = QLabel("CrossPixel")
        self.title_label.setStyleSheet("font-size: 14pt; color: white; letter-spacing: 2px;")
        title_bar_layout.addWidget(self.title_label, alignment=Qt.AlignLeft)
        
        title_bar_layout.addStretch(1)  # Centering stretch

        # Minimize button
        minimize_button = QPushButton("🗕", self)
        minimize_button.clicked.connect(self.showMinimized)
        minimize_button.setFixedSize(25, 25)  # A fixed size for the minimize button
        minimize_button.setStyleSheet(self.setupCloseButtonStylesheet())
        title_bar_layout.addWidget(minimize_button)

        # Close button
        close_button = QPushButton("X", self)
        close_button.clicked.connect(self.close)
        close_button.setFixedSize(25, 25)  # A fixed size for the close button
        close_button.setStyleSheet(self.setupCloseButtonStylesheet())
        title_bar_layout.addWidget(close_button)
        
        title_bar_layout.setSpacing(5)  # Spacing between the widgets


    def createBottomLayout(self):
        """Create the main content layout."""
        content_layout = QHBoxLayout()
        
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.drawingBoard)
        
        # Add a spacing before the "Apply Crosshair" button to move it down
        left_layout.addSpacing(10)  # Adjust the value as needed for desired spacing
        
        left_layout.addWidget(self.applyButton)
        
        right_layout = self.createRightLayout()

        content_layout.addLayout(left_layout)
        content_layout.addLayout(right_layout)

        return content_layout


    def createRightLayout(self):
        right_layout = QVBoxLayout()

        # Add individual buttons directly to the QVBoxLayout
        buttons = [self.centerViewButton, self.colorCircle]
        for button in buttons:
            right_layout.addWidget(button)

        # Spacer to add padding below the color wheel and before the pen selector
        right_layout.addSpacing(1)  # Adjust the value as needed for desired spacing

        right_layout.addWidget(self.penComboBox)
        right_layout.addWidget(self.penSizeSlider)  # Add the penSizeSlider under the penComboBox
        
        # Continue with the rest of the buttons
        right_layout.addWidget(self.clearButton)

        # Horizontal layout for Undo and Redo
        undo_redo_layout = QHBoxLayout()
        undo_redo_layout.setSpacing(2)  # Set spacing to 0
        undo_redo_layout.setContentsMargins(-20, 0, 0, 0)
        undo_redo_layout.addWidget(self.undoButton)
        undo_redo_layout.addWidget(self.redoButton)

        undo_margin = self.undoButton.contentsMargins()
        undo_margin.setRight(-10)  # Adjust the value to get the desired overlap
        self.undoButton.setContentsMargins(undo_margin)

        right_layout.addLayout(undo_redo_layout)

        right_layout.addSpacing(8)
        # Preset buttons
        preset_buttons = [self.presetButton, self.preset2Button]
        for button in preset_buttons:
            right_layout.addWidget(button)

        right_layout.addStretch(1)

        # Save, Upload, and Settings buttons
        save_upload_buttons = [self.saveButton, self.uploadButton, self.settingsButton]
        for button in save_upload_buttons:
            right_layout.addWidget(button)

        return right_layout

    def openSettings(self):
        # Fetch and print current keybinds before opening the settings dialog
        current_keybinds = {
            "undo": self.keybinds.get_keybind("undo"),
            "redo": self.keybinds.get_keybind("redo"),
            "hide_crosshair": self.keybinds.get_keybind("hide_crosshair"),
            "self_destruct": self.keybinds.get_keybind("self_destruct"),
            "offset_keybind": self.keybinds.get_keybind("offset_keybind"),
            "crosshair_disable_mode": self.keybinds.get_keybind("crosshair_disable_mode"),
        }
        print("Current keybinds before opening settings:", current_keybinds)

        settingsDialog = SettingsDialog(self)  # No need to pass current_keybinds
        result = settingsDialog.exec_()

        if result == QDialog.Accepted:
            # Fetch and print the updated keybinds to ensure they are set correctly
            post_update_keybinds = {
                "undo": self.drawingBoard.keybinds.get_keybind("undo"),
                "redo": self.drawingBoard.keybinds.get_keybind("redo"),
                "hide_crosshair": self.drawingBoard.keybinds.get_keybind("hide_crosshair"),
                "self_destruct": self.drawingBoard.keybinds.get_keybind("self_destruct"),
                "offset_keybind": self.drawingBoard.keybinds.get_keybind("offset_keybind"),
                "offset_x": settingsDialog.offsetXSlider.value(), 
                "offset_y": settingsDialog.offsetYSlider.value(),
                "crosshair_disable_mode": settingsDialog.crosshairDisableModeDropdown.currentText()  # Fetch the dropdown value
            }
            print("Keybinds immediately after updating:", post_update_keybinds)

    def setupMainWindowProperties(self):
        """Setup main window properties."""
        self.setWindowTitle('CrossPixel')
        self.setGeometry(100, 100, 535, 480)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Set application icon using QApplication
        self.setWindowIcon(QIcon("logo2.ico"))

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(18, 18, 18))
        self.setPalette(palette)

