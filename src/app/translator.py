from PyQt5.QtCore import QThread
import time
import librosa
import numpy as np
from typing import Tuple
from app.lang import Language
from transformers import (
    AutoProcessor,
    SeamlessM4TModel,
    SeamlessM4TForSpeechToText,
    TextStreamer,
)
import torch
import queue
from PyQt5.QtCore import pyqtSignal


class TranslatorThread(QThread):
    translations_available = pyqtSignal(tuple)
    processing_finished = pyqtSignal()
    processing_started = pyqtSignal()

    def __init__(
        self,
        language1: Language,
        language2: Language,
        input_rate: int,
        sentence_queue: queue.Queue,
        parent=None,
    ):
        super(TranslatorThread, self).__init__(parent)
        self.language1 = language1
        self.language2 = language2
        self.input_rate = input_rate
        self.processor = None
        self.model = None
        self.sentence_queue = sentence_queue
        self.initialized = False

    def initialize_model(self):
        # Initialize model and processor
        self.processor = AutoProcessor.from_pretrained(
            "facebook/hf-seamless-m4t-medium"
        )
        model = SeamlessM4TModel.from_pretrained("facebook/hf-seamless-m4t-medium")
        # quantized_model = torch.quantiezation.quantize_dynamic(
        #     model, {torch.nn.Linear}, dtype=torch.qint8
        # )
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = model.to(device)
        self.initialized = True
        print("Translator initialized.")

    def _get_translations(self, audio_data: np.ndarray) -> Tuple[str, str]:
        # Audio processing
        audio_data = self.__resample_audio(audio_data)
        # Speech-to-text translation
        translation1 = self.translate_speech(
            audio_data, target_language=self.language1.value
        )
        translation2 = self.translate_speech(
            audio_data, target_language=self.language2.value
        )
        print(f"Translation in {self.language1}: {translation1}")
        print(f"Translation in {self.language2}: {translation2}")
        # Update spectrogram plot
        # self.plot_spectrogram(audio_data)

        return translation1, translation2

    def __resample_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Processes the audio data by resampling and normalizing it.

        Args:
            audio_data (np.ndarray): The raw audio data.

        Returns:
            np.ndarray: The processed audio data.
        """
        new_rate = 16000
        return librosa.resample(
            y=audio_data, orig_sr=self.input_rate, target_sr=new_rate
        )

    def translate_speech(self, audio_data: np.ndarray, target_language: str) -> str:
        """
        Translates speech in the audio data to text using a pre-trained model.

        Args:
            audio_data (np.ndarray): The processed audio data.
        """
        audio_inputs = self.processor(
            audios=audio_data, return_tensors="pt", sampling_rate=16000
        )
        output_tokens = self.model.generate(
            **audio_inputs, tgt_lang=target_language, generate_speech=False
        )
        translated_text = self.processor.decode(
            output_tokens[0].tolist()[0],
            skip_special_tokens=True,
            generate_speech=False,
        )
        return translated_text

    def run(self):
        if not self.initialized:
            raise ValueError("Translator has not been initialized.")
        while True:
            current_sentence = self.sentence_queue.get()
            self.processing_started.emit()
            translation1, translation2 = self._get_translations(
                audio_data=current_sentence
            )
            self.translations_available.emit((translation1, translation2))
            self.processing_finished.emit()
