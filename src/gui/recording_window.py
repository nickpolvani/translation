import sys
import time
from PyQt5.QtWidgets import *
from app.lang import Language
from gui.scrollable_text import ScrollableTextPanel
from app.controller import Controller
from gui.vad_plotter import VadPlotter
from PyQt5.QtCore import pyqtSignal


class RecordingWidget(QWidget):
    def __init__(self, parent: QWidget, language1: Language, language2: Language):
        super().__init__(parent)
        self.language1 = language1
        self.language2 = language2

        self.controller = Controller(self.language1, self.language2, parent=self)

        self.text_panel1 = ScrollableTextPanel(
            title=f"Transcription in {str(self.language1)}:\n",
            parent=self,
            processing_started=self.controller.get_processing_started_signal(),
            processing_finished=self.controller.get_processing_finished_signal(),
        )

        self.text_panel2 = ScrollableTextPanel(
            title=f"Transcription in {str(self.language2)}:\n",
            parent=self,
            processing_started=self.controller.get_processing_started_signal(),
            processing_finished=self.controller.get_processing_finished_signal(),
        )

        self.controller.get_translation_available_signal().connect(
            self.update_texts_panel
        )
        self.vad_plotter = VadPlotter(
            max_time=30,
            vad_prediction_ready=self.controller.get_vad_available_signal(),
            parent=self,
        )
        self.controller.start()

        self.UI()

    def UI(self):
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.vad_plotter)
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.text_panel1)
        bottom_layout.addWidget(self.text_panel2)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)
        self.show()

    def update_texts_panel(self, texts: tuple):
        text1 = self.text_panel1.get_text()
        text2 = self.text_panel2.get_text()
        text1 += texts[0] + "\n"
        text2 += texts[1] + "\n"
        self.text_panel1.on_translation_ready(text1)
        self.text_panel2.on_translation_ready(text2)

    def destroy(self):
        self.hide()
        self.deleteLater()
