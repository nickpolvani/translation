from PyQt5 import QtWidgets

# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import time
from gui.language_select import LanguageSelectWidget
from gui.recording_window import RecordingWidget
from gui.loading_window import LoadingDialog
from app.lang import Language, get_language_from_name


class MainWindow(QMainWindow):
    # EXIT_CODE_REBOOT = -12345678

    def __init__(self) -> None:
        super().__init__()
        self.restart_recording()
        self.setGeometry(100, 100, 800, 500)

    def restart_recording(self):
        self.main_widget = MainWidget(parent=self)
        self.setCentralWidget(self.main_widget)


class MainWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.UI()

    def UI(self):
        layout = QVBoxLayout()
        self.language_window = LanguageSelectWidget(parent=self)

        layout.addWidget(self.language_window)

        self.setLayout(layout)

        self.setWindowTitle("PyQt5 Layout")
        self.show()

    def on_language_select(self, language1: str, language2: str):
        self.language_window.hide()

        self.recording_window = RecordingWidget(
            parent=self,
            language1=get_language_from_name(language1),
            language2=get_language_from_name(language2),
        )
        self.loading_window = LoadingDialog(parent=self)
        self.layout().addWidget(self.loading_window)
        self.recording_window.audio_processor.initializations_finished.connect(
            self.onRecordingReady
        )

    def onRecordingReady(self):
        self.loading_window.stop_loading()
        self.layout().removeWidget(self.loading_window)
        self.layout().addWidget(self.recording_window)
        self.recording_window.show()

    # def recording_finished(self):
    #     print("Finished all recordings")
    #     self.recording_window.destroy()
    #     self.layout().removeWidget(self.recording_window)
    #     self.restart_button.show()


def main():
    a = QApplication(sys.argv)
    font = QFont("Arial", 26)
    a.setFont(font)
    w = MainWindow()
    w.showMaximized()
    currentExitCode = a.exec_()


if __name__ == "__main__":
    main()
