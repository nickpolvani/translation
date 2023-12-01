import sys
import time
from PyQt5.QtWidgets import *
from app.lang import Language
from app.audio_processor import AudioProcessor
from gui.scrollable_text import ScrollableTextPanel


class RecordingWidget(QWidget):
    def __init__(self, parent: QWidget, language1: Language, language2: Language):
        super().__init__(parent)
        self.language1 = language1
        self.language2 = language2

        self.title_label = QLabel()
        self.title_label.setText(
            f"Recording Window for: {self.language1} and {self.language2}"
        )

        self.text_panel1 = TextPanelTitle(
            f"Transcription in {str(self.language1)}", parent=self
        )

        self.text_panel2 = TextPanelTitle(
            f"Transcription in {str(self.language2)}", parent=self
        )

        self.audio_processor = AudioProcessor(
            language1=self.language1, language2=self.language2, parent=self
        )
        self.audio_processor.translations_available.connect(self.update_texts_panel)
        self.audio_processor.start()

        self.text1 = ""
        self.text2 = ""
        self.UI()

    def UI(self):
        layout = QHBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.text_panel1)
        layout.addWidget(self.text_panel2)
        self.setLayout(layout)
        self.show()

    def update_texts_panel(self, texts: tuple):
        self.text1 += texts[0]
        self.text2 += texts[1]
        self.text_panel1.set_text(self.text1)
        self.text_panel2.set_text(self.text2)

    def destroy(self):
        self.hide()
        self.deleteLater()


class TextPanelTitle(QWidget):
    def __init(self, title: str, parent: QWidget):
        super().__init__(parent)
        self.title_label = QLabel()
        self.title_label.setText(title)

        self.text_label = ScrollableTextPanel()
        self.UI()

    def UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.text_label)
        self.setLayout(layout)
        self.show()

    def set_text(self, text: str):
        self.text_label.set_text(text)

    def get_text(self) -> str:
        return self.text_label.get_text()
