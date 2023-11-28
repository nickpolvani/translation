
import sys
import time
from PyQt5.QtWidgets import QListWidget, QWidget, QVBoxLayout, QLabel, QPushButton
from app.lang import Language
from app.audio_processor import AudioProcessor

class RecordingWidget(QWidget):
    def __init__(self, parent:QWidget, language1:Language, language2:Language):
        super().__init__(parent)
        self.language1 = language1
        self.language2 = language2

        self.title_label = QLabel()
        self.title_label.setText(f"Recording Window for: {self.language1} and {self.language2}")

        # self.start_rec_button = QPushButton("Start Recording")
        # self.start_rec_button.adjustSize()
        # self.start_rec_button.clicked.connect(self.start_recording)

        # self.stop_rec_button = QPushButton("Stop Recording")
        # self.stop_rec_button.adjustSize()
        # self.stop_rec_button.clicked.connect(self.stop_recording)

        self.text_panel1 = QLabel()
        self.text_panel1.setWordWrap(True)

        self.text_panel2 = QLabel()
        self.text_panel2.setWordWrap(True)

        
        self.audio_processor = AudioProcessor(language1=self.language1, language2=self.language2, parent=self)
        self.audio_processor.translations_available.connect(self.update_texts_panel)
        self.audio_processor.start()

        self.text1 = ""
        self.text2 = ""
        self.UI()
        

    def UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.text_panel1)
        layout.addWidget(self.text_panel2)
        # layout.addWidget(self.start_rec_button)
        # layout.addWidget(self.stop_rec_button)
        # self.stop_rec_button.hide()
        # self.text_panel.hide()
        self.setLayout(layout)
        self.show()


    def update_texts_panel(self, texts:tuple):
        self.text1 += texts[0]
        self.text2 += texts[1]
        self.text_panel1.setText(self.text1)
        self.text_panel2.setText(self.text2)



    def destroy(self):
        self.hide()
        self.deleteLater()