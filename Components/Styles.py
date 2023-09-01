class StylesSetupMixin:
    
    def button_stylesheet(self):
        button_color = "background-color: rgb(40, 40, 40);"  # Replace with your desired button color
        text_color = "color: rgb(255, 255, 255);"  # Replace with your desired text color
        return button_color + text_color

    def combobox_stylesheet(self):
        combobox_color = "background-color: rgb(40, 40, 40);"  # Replace with your desired combo box color
        text_color = "color: rgb(255, 255, 255);"  # Replace with your desired text color
        border_style = "border: 1px solid gray;"
        arrow_style = "QComboBox::down-arrow {image: url(path_to_your_arrow_image.png);}"  # If you don't have an image, you can remove this line or replace with a suitable one
        popup_style = "QComboBox QAbstractItemView { background-color: rgb(40, 40, 40); color: rgb(255, 255, 255); selection-background-color: rgb(60, 60, 60);}"  # Styles the dropdown list
        return combobox_color + text_color + border_style + arrow_style + popup_style

    def setupCloseButtonStylesheet(self):
        button_color = "background-color: rgb(40, 40, 40);"  # Replace with your desired button color
        text_color = "color: rgb(255, 255, 255);"  # Replace with your desired text color
        return button_color + text_color
    
    def slider_stylesheet(self):
        return """
            QSlider {
                background: transparent;
            }
            QSlider::handle:horizontal {
                background: rgb(40, 40, 40);
                width: 15px;
                border: 1px solid rgb(60, 60, 60);
                margin-top: -7px; 
                margin-bottom: -7px;
            }
            QSlider::sub-page:horizontal {
                background: repeating-linear-gradient(90deg, rgb(60, 60, 60), rgb(60, 60, 60) 1px, transparent 1px, transparent 4px);
            }
            QSlider::add-page:horizontal {
                background: repeating-linear-gradient(90deg, rgb(60, 60, 60), rgb(60, 60, 60) 1px, transparent 1px, transparent 4px);
            }
        """

    def key_sequence_edit_stylesheet(self):
        return """
        QKeySequenceEdit QLineEdit {
            border: 1px solid rgb(60, 60, 60);
            background-color: rgb(40, 40, 40);  /* Change to your desired background color */
        }
        QKeySequenceEdit QLineEdit:focus {
            border: 1px solid rgb(125, 125, 125);  /* Change 'red' to your preferred color */
        }
        """

    def line_edit_stylesheet(self):
        return """
            QLineEdit {
                border: 1px solid rgb(60, 60, 60);
                background-color: rgb(40, 40, 40);
                color: rgb(255, 255, 255);
            }
            QLineEdit:focus {
                border: 1px solid rgb(125, 125, 125);
            }
        """




