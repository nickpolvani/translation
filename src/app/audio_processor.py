import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import queue
import librosa
from transformers import AutoProcessor, SeamlessM4TModel, SeamlessM4TForSpeechToText, TextStreamer
import wave
from app.lang import Language
import time
from PyQt5.QtCore import QThread, pyqtSignal
import torch.quantization


class AudioProcessor(QThread):
    """
    A class to process audio data in real-time, perform speech-to-text translation,
    and visualize the audio data as a spectrogram using Matplotlib.
    """

    translations_available = pyqtSignal(tuple)
    initializations_finished = pyqtSignal()

    def __init__(self, language1: Language, language2: Language, parent=None):
        super(AudioProcessor, self).__init__(parent)
        """
        Initializes the AudioProcessor class with necessary configurations,
        model, processor, and PyAudio stream.
        """
        # Constants
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.length_chunk = 3.5  # seconds
        self.CHUNK = int(self.RATE * self.length_chunk)  

        self.MAX_NUM_FRAMES = 100
        self.CUR_FRAME = 0

        self.frames = []
        self.audio_queue = queue.Queue()
        self.language1 = language1
        self.language2 = language2

        self.processor = None
        self.model = None

        # Initialize PyAudio
        self.p = None

        self.stream = None

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

    def start_recording(self):
        # Open stream
        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            stream_callback=self.callback,
        )

    def callback(self, in_data, frame_count, time_info, status):
        """
        Callback function for the PyAudio stream. It's called with new audio data.

        Args:
            in_data (bytes): The buffer containing the audio data.
            frame_count (int): The number of frames in the buffer.
            time_info (dict): Information about the timing.
            status (int): Status flag indicating underflow or overflow.

        Returns:
            tuple: A tuple (None, pyaudio.paContinue) to continue recording.
        """
        self.audio_queue.put(np.frombuffer(in_data, dtype=np.int16))
        return (None, pyaudio.paContinue)

    def consume_audio_queue(self):
        """
        Updates the plot with new audio data from the queue. Processes the audio data,
        translates it to text, and updates the spectrogram plot.
        """
        if not self.audio_queue.empty():
            audio_data = self.audio_queue.get()
            self.frames.append(audio_data)

            # measure the time to process audio data
            start = time.time()

            # Audio processing
            audio_data = self.__resample_audio(audio_data)
            print(f"range of audio data: {np.min(audio_data)} to {np.max(audio_data)}")
            # Speech-to-text translation
            translation1 = self.translate_speech(
                audio_data, target_language=self.language1.value
            )
            translation2 = self.translate_speech(
                audio_data, target_language=self.language2.value
            )
            print(f"Translation in {self.language1}: {translation1}")
            print(f"Translation in {self.language2}: {translation2}")

            end = time.time()
            print(f"Processing time: {end - start} seconds")

            # Update spectrogram plot
            # self.plot_spectrogram(audio_data)

            self.CUR_FRAME += 1
            return translation1, translation2
        else:
            return None

    def __resample_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Processes the audio data by resampling and normalizing it.

        Args:
            audio_data (np.ndarray): The raw audio data.

        Returns:
            np.ndarray: The processed audio data.
        """
        new_rate = 16000
        audio_data = audio_data / 32768.0  # Convert to float [-1, 1]
        return librosa.resample(y=audio_data, orig_sr=self.RATE, target_sr=new_rate)

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
        """
        Starts the audio processing and plotting routine. Continues until the specified
        number of frames are processed or a KeyboardInterrupt is received.
        """
        self.initialize_model()
        self.start_recording()
        self.initializations_finished.emit()
        print("Start to record...")
        try:
            while self.stream.is_active():
                translations = self.consume_audio_queue()
                if translations is not None:
                    self.translations_available.emit(translations)
                if self.CUR_FRAME >= self.MAX_NUM_FRAMES:
                    break
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.stop_recording()

    def stop_recording(self):
        """
        Stops the PyAudio stream.
        """
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


if __name__ == "__main__":
    # Create and run the audio processor
    audio_processor = AudioProcessor(
        language1=Language.ENGLISH, language2=Language.ITALIAN
    )
    audio_processor.run()