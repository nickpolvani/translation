from app.audio_processor import AudioProcessorThread
from app.lang import Language
from app.mic_listener import MicrophoneListenerThread
from app.translator import TranslatorThread
from PyQt5.QtCore import QThread, pyqtSignal


class Controller(QThread):
    initializations_finished = pyqtSignal()

    def __init__(self, language1: Language, language2: Language, parent=None):
        super(Controller, self).__init__(parent)
        self.language1 = language1
        self.language2 = language2
        self.microphone_listener = MicrophoneListenerThread(
            length_chunk_seconds=0.5, parent=self.parent()
        )
        self.audio_processor = AudioProcessorThread(
            audio_queue=self.microphone_listener.audio_queue,
            input_rate=self.microphone_listener.RATE,
            length_chunk_seconds=self.microphone_listener.length_chunk_seconds,
            max_chunk_length_seconds=10.0,
            sec_silence_before_processing=1.5,
            parent=self.parent(),
        )
        self.translator = TranslatorThread(
            language1=self.language1,
            language2=self.language2,
            input_rate=self.microphone_listener.RATE,
            sentence_queue=self.audio_processor.sentence_queue,
            parent=self.parent(),
        )
        
    def get_translation_available_signal(self) -> pyqtSignal:
        return self.translator.translations_available
    
    def get_vad_available_signal(self) -> pyqtSignal:
        return self.audio_processor.vad_available
    
    def get_processing_finished_signal(self) -> pyqtSignal:
        return self.translator.processing_finished
    
    def get_processing_started_signal(self) -> pyqtSignal:
        return self.translator.processing_started

    def _initialize(self):
        self.translator.initialize_model()
        self.microphone_listener.open_stream()
        self.initializations_finished.emit()


    def run(self):
        self._initialize()
        self.microphone_listener.start()
        self.audio_processor.start()
        self.translator.start()



if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    controller = Controller(Language.ENGLISH, Language.ITALIAN)

    controller.start()
    app.exec_()
