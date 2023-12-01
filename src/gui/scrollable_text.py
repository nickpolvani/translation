from PyQt5.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class ScrollableTextPanel(QWidget):
    def __init__(self, parent=None):
        super(ScrollableTextPanel, self).__init__(parent)

        # Create the QLabel for text display
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("border: 1px solid black;")

        # Create a QScrollArea to add scrolling capability
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.text_label)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

    def set_text(self, text):
        """ Set the text of the text_label. """
        self.text_label.setText(text)

    def get_text(self):
        """ Return the current text of the text_label. """
        return self.text_label.text()
