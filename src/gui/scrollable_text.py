from PyQt5.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import pyqtSignal, QTimer


class ScrollableTextPanel(QWidget):
    def __init__(
        self,
        title: str,
        processing_started: pyqtSignal,
        processing_finished: pyqtSignal,
        font_size=12,
        parent=None,
    ):
        super(ScrollableTextPanel, self).__init__(parent)

        # Create the QLabel for text display
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("border: 1px solid black;")

        font = self.text_label.font()
        font.setPointSize(font_size)
        self.text_label.setFont(font)
        self.text_label.setText(title)

        # Create a QScrollArea to add scrolling capability
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.text_label)

        # Initialize loading indicator attributes
        self.isLoading = False
        self.loadingText = "Processing"
        self.loadingDots = 0
        self.maxLoadingDots = 5
        self.originalText = self.text_label.text()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_loading_indicator)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

        processing_started.connect(self.start_loading)
        processing_finished.connect(self.stop_loading)

    def on_translation_ready(self, text):
        """Set the text of the text_label."""
        self.text_label.setText(text)
        self.originalText = text
        self.scroll_to_bottom()

    def get_text(self):
        """Return the current text of the text_label."""
        return self.originalText

    def scroll_to_bottom(self):
        """Scroll to the bottom of the scroll area."""
        vertical_bar = self.scroll_area.verticalScrollBar()
        vertical_bar.setValue(vertical_bar.maximum())

    def start_loading(self):
        """Start the loading indicator."""
        self.isLoading = True
        self.update_loading_indicator()
        self.timer.start(500)  # Update every 500 ms

    def stop_loading(self):
        """Stop the loading indicator."""
        self.isLoading = False
        self.timer.stop()
        # self.text_label.setText(self.originalText)

    def update_loading_indicator(self):
        """Update the loading text with additional dots."""
        if self.isLoading:
            self.loadingDots = (self.loadingDots + 1) % (self.maxLoadingDots + 1)
            loadingMessage = self.loadingText + "." * self.loadingDots
            self.text_label.setText(self.originalText + " " + loadingMessage)
