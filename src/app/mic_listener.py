import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import queue
import librosa
import wave
from app.lang import Language
import time
from PyQt5.QtCore import QThread, pyqtSignal
import torch.quantization
from app.translator import AudioProcessorThread


class MicrophoneListenerThread(QThread):
    """
    A class to process audio data in real-time, perform speech-to-text translation,
    and visualize the audio data as a spectrogram using Matplotlib.
    """

    def __init__(self, parent=None):
        super(MicrophoneListenerThread, self).__init__(parent)
        """
        Initializes the AudioProcessor class with necessary configurations,
        model, processor, and PyAudio stream.
        """
        # Constants
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.length_chunk = 0.5  # seconds
        self.CHUNK = int(self.RATE * self.length_chunk)
        self.audio_queue = queue.Queue()

        # Initialize PyAudio
        self.p = None
        self.stream = None

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

    def run(self):
        """
        Starts the audio processing and plotting routine. Continues until the specified
        number of frames are processed or a KeyboardInterrupt is received.
        """
        self.translator.initialize_model()
        self.start_recording()
        self.initializations_finished.emit()
        print("Start to record...")
        try:
            while self.stream.is_active():
                translations = self.translator.consume_audio_queue()
                if translations is not None:
                    self.translations_available.emit(translations)

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
    audio_processor = MicrophoneListenerThread(
        language1=Language.ENGLISH, language2=Language.ITALIAN
    )
    audio_processor.run()
