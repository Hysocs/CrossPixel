from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QSlider, QKeySequenceEdit, QHBoxLayout, QGroupBox, QWidget, QApplication, QLineEdit, QCheckBox, QComboBox, QLabel
from PyQt5.QtCore import Qt, QPoint
from PyQt5 import QtGui
from PyQt5.QtGui import QIntValidator
from Components.Styles import StylesSetupMixin
from Components.Settings.Keybinds import Keybinds
from Components.EventHandlers import EventHandlersMixin

class SettingsDialog(QDialog, EventHandlersMixin):
    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent)
        self.styles_setup = StylesSetupMixin()
        
        # Initialize properties for mouse event handlers
        self.moving = False
        self.offset = QPoint()
        
        self.setupUI()
        self.load_keybinds(Keybinds().keybinds)

    def setupUI(self):
        self.setWindowTitle("   ")
        self.setStyleSheet("background-color: rgb(24, 24, 24); color: white;")
        self.resize(520, 300)
        layout = QVBoxLayout()
        self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags())


        self.createTitleBar()
        layout.addWidget(self.title_bar)

        horizontal_layout = QHBoxLayout()
        keybinds_group = self.createGroup("Settings", 200, 300)
        self.undoKeybind = self.createSequenceEdit("Undo:", keybinds_group.layout())
        self.redoKeybind = self.createSequenceEdit("Redo:", keybinds_group.layout())
        self.hideCrosshairKeybind = self.createSequenceEdit("Hide Crosshair:", keybinds_group.layout())
        self.selfDestructKeybind = self.createSequenceEdit("Self Destruct:", keybinds_group.layout())
        horizontal_layout.addWidget(keybinds_group)
        

        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()

        offset_group = self.createGroup("Crosshair Settings", 300, 300)
        self.offsetKeybind = self.createSequenceEdit("Crosshair Offset:", offset_group.layout())
        self.offsetXSlider, self.offsetXLabel = self.createSlider("Offset X:", offset_group.layout(), -screen_width//2, screen_width//2, 0)
        self.offsetYSlider, self.offsetYLabel = self.createSlider("Offset Y:", offset_group.layout(), -screen_height//2, screen_height//2, 0)
        crosshairModeLabel = QLabel("Hide Crosshair during Event:")
        offset_group.layout().addWidget(crosshairModeLabel)

        self.crosshairDisableModeDropdown = QComboBox()
        self.crosshairDisableModeDropdown.addItems(["Disabled","Hide while holding right click", "Hide while holding left click", "Hide while holding left click or right click"])
        offset_group.layout().addWidget(self.crosshairDisableModeDropdown)
        horizontal_layout.addWidget(offset_group)

        layout.addLayout(horizontal_layout)

        button_layout = QHBoxLayout()
        closeButton = QPushButton("Save and Close")
        closeButton.setStyleSheet(self.styles_setup.button_stylesheet())
        closeButton.setFixedWidth(closeButton.sizeHint().width() // 1)
        closeButton.clicked.connect(self.saveAndExit)
        button_layout.addWidget(closeButton, alignment=Qt.AlignCenter)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def createGroup(self, title, width, height):
        group = QGroupBox(title)
        group.setFixedSize(width, height)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)  # Prevent vertical centering
        group.setLayout(layout)
        return group
    
    def closeEvent(self, event):
        self.hide()  # Hide the settings dialog instead of closing it
        keybinds = Keybinds()
        keybinds.update_keybinds(self.get_keybinds())
        self.accept()
        event.ignore()  # Ignore the close event to prevent the application from closing

    def createTitleBar(self):
        self.title_bar = QWidget(self)
        title_bar_layout = QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.title_bar.setMaximumHeight(30)

        self.title_label = QLabel("Settings")
        self.title_label.setStyleSheet("font-size: 14pt; color: white; letter-spacing: 2px;")
        title_bar_layout.addWidget(self.title_label, alignment=Qt.AlignLeft)
        title_bar_layout.addStretch(1)

        closeButton = QPushButton("X")
        closeButton.clicked.connect(self.close)
        closeButton.setFixedSize(25, 25)
        closeButton.setStyleSheet(self.styles_setup.setupCloseButtonStylesheet())  # Applying the style
        title_bar_layout.addWidget(closeButton)

    def createSlider(self, label_text, layout, min_val, max_val, default_val):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)

        desired_num_ticks = 10
        range_x = abs(max_val - min_val)
        common_tick_interval = round(range_x / desired_num_ticks)

        slider.setTickInterval(common_tick_interval)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setStyleSheet(self.styles_setup.slider_stylesheet())

        label = QLabel(label_text)
        value_edit = QLineEdit(str(default_val))
        value_edit.setValidator(QtGui.QIntValidator(min_val, max_val))
        value_edit.setFixedWidth(50)
        value_edit.setStyleSheet(self.styles_setup.line_edit_stylesheet())  # Apply the modified stylesheet here


        slider.valueChanged.connect(lambda: value_edit.setText(str(slider.value())))

        def update_slider_value():
            try:
                slider.setValue(int(value_edit.text()))
            except ValueError:
                pass

        value_edit.textChanged.connect(update_slider_value)

        h_layout = QHBoxLayout()
        h_layout.addWidget(label)
        h_layout.addWidget(slider)
        h_layout.addWidget(value_edit)
        layout.addLayout(h_layout)

        return slider, value_edit

    def createSequenceEdit(self, label_text, layout):
        key_sequence_edit = QKeySequenceEdit()
        key_sequence_edit.setStyleSheet(self.styles_setup.key_sequence_edit_stylesheet())
        label = QLabel(label_text)
        
        h_layout = QHBoxLayout()
        h_layout.addWidget(label)
        h_layout.addWidget(key_sequence_edit)
        layout.addLayout(h_layout)
        
        return key_sequence_edit
    
    def createCheckbox(self, label_text, layout):
        checkbox = QCheckBox(label_text)
        #checkbox.setStyleSheet(self.styles_setup.checkbox_stylesheet())
        layout.addWidget(checkbox)
        return checkbox
    
    def get_keybinds(self):
        return {
            "undo": self.undoKeybind.keySequence().toString(),
            "redo": self.redoKeybind.keySequence().toString(),
            "hide_crosshair": self.hideCrosshairKeybind.keySequence().toString(),
            "self_destruct": self.selfDestructKeybind.keySequence().toString(),
            "offset_keybind": self.offsetKeybind.keySequence().toString(),
            "offset_x": self.offsetXSlider.value(),
            "offset_y": self.offsetYSlider.value(),
            "crosshair_disable_mode": self.crosshairDisableModeDropdown.currentIndex()
        }

    def saveAndExit(self):
        keybinds = Keybinds()
        keybinds.update_keybinds(self.get_keybinds())
        self.accept()

    def load_keybinds(self, keybinds):
        self.undoKeybind.setKeySequence(keybinds.get("undo", ""))
        self.redoKeybind.setKeySequence(keybinds.get("redo", ""))
        self.hideCrosshairKeybind.setKeySequence(keybinds.get("hide_crosshair", ""))
        self.selfDestructKeybind.setKeySequence(keybinds.get("self_destruct", ""))
        self.offsetKeybind.setKeySequence(keybinds.get("offset_keybind", ""))
        self.crosshairDisableModeDropdown.setCurrentIndex(keybinds.get("crosshair_disable_mode", 0))

        
        self.offsetXSlider.setValue(keybinds.get("offset_x", 0))
        self.offsetYSlider.setValue(keybinds.get("offset_y", 0))

    @staticmethod
    def open_and_process(parent):
        settingsDialog = SettingsDialog(parent)
        result = settingsDialog.exec_()

        if result == QDialog.Accepted:
            updated_keybinds = settingsDialog.get_keybinds()
