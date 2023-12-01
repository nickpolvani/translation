from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt

class LoadingDialog(QWidget):  # Subclass QWidget instead of QLabel
    def __init__(self, parent=None):
        super(LoadingDialog, self).__init__(parent)

        self.setWindowTitle("Loading...")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        # Set up the label for the loading GIF
        self.label = QLabel(self)
        self.movie = QMovie("media/loading.gif")  # Ensure this path is correct
        self.label.setMovie(self.movie)
        self.label.setAlignment(Qt.AlignCenter)  # Center alignment for the label

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.movie.start()

        # Optional: Adjust size and position
        self.resize(200, 200)  # Adjust size as needed
        self.move(parent.width() // 2 - self.width() // 2, 
                  parent.height() // 2 - self.height() // 2)  # Center in parent

    def stop_loading(self):
        self.movie.stop()
        self.hide()  # Hide instead of accept, since it's no longer a QDialog
