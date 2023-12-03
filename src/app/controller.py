from app.audio_processor import AudioProcessorThread
from app.lang import Language
from app.mic_listener import MicrophoneListenerThread
from app.translator import TranslatorThread
from PyQt5.QtCore import QThread, pyqtSignal

class Controller(QThread):
    initializations_finished = pyqtSignal()

    def __init__(self, language1: Language, language2: Language):
        self.language1 = language1
        self.language2 = language2
        self.translator = AudioProcessorThread(
            language1=language1,
            language2=language2,
            audio_queue=self.audio_queue,
            input_rate=self.RATE,
            length_chunk_seconds=self.length_chunk,
            max_chunk_length_seconds=10.0,
            sec_silence_before_processing=1.5,
        )


    def _initialize(self):
        self.translator.initialize_model()
        self.translator.start()
        self.translator.initializations_finished.connect(self.start_recording)

    def run(self):
        self._initialize()