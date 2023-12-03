from PyQt5.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import pyqtSignal


class ScrollableTextPanel(QWidget):
    def __init__(self, processing_started:pyqtSignal, processing_finished:pyqtSignal, font_size=12, parent=None):
        super(ScrollableTextPanel, self).__init__(parent)

        # Create the QLabel for text display
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("border: 1px solid black;")

        font = self.text_label.font()
        font.setPointSize(font_size)
        self.text_label.setFont(font)

        # Create a QLabel for the loading GIF
        self.loading_label = QLabel()
        self.movie = QMovie("media/loading.gif")
        self.loading_label.setMovie(self.movie)
        self.loading_label.hide()  # Initially hidden

        # Create a QScrollArea to add scrolling capability
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        # Create a container widget and layout for text and loading label
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.addWidget(self.text_label)
        self.container_layout.addWidget(self.loading_label)
        self.container_widget.setLayout(self.container_layout)

        # Set the container widget as the scroll area's widget
        self.scroll_area.setWidget(self.container_widget)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

        processing_started.connect(self.start_loading)
        processing_finished.connect(self.stop_loading)

    def set_text(self, text):
        """ Set the text of the text_label. """
        self.text_label.setText(text)
        self.scroll_to_bottom()

    def get_text(self):
        """ Return the current text of the text_label. """
        return self.text_label.text()
    
    def scroll_to_bottom(self):
        """ Scroll to the bottom of the scroll area. """
        vertical_bar = self.scroll_area.verticalScrollBar()
        vertical_bar.setValue(vertical_bar.maximum())

    def start_loading(self):
        """ Start the loading animation. """
        self.loading_label.show()
        self.movie.start()
        self.scroll_to_bottom()

    def stop_loading(self):
        """ Stop the loading animation. """
        self.movie.stop()
        self.loading_label.hide()
