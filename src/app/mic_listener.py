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


class MicrophoneListenerThread(QThread):
    """
    A class to process audio data in real-time, perform speech-to-text translation,
    and visualize the audio data as a spectrogram using Matplotlib.
    """

    def __init__(self, length_chunk_seconds=0.5, parent=None):
        super(MicrophoneListenerThread, self).__init__(parent)
        """
        Initializes the AudioProcessor class with necessary configurations,
        model, processor, and PyAudio stream.
        """
        # Constants
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.length_chunk_seconds = length_chunk_seconds  # seconds
        self.CHUNK = int(self.RATE * self.length_chunk_seconds)
        self.audio_queue = queue.Queue()

        # Initialize PyAudio
        self.p = None
        self.stream = None
        self.initialized = False

    def open_stream(self):
        # Open stream
        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )
        self.initialized = True

    def run(self):
        """
        Starts the audio processing and plotting routine. Continues until the specified
        number of frames are processed or a KeyboardInterrupt is received.
        """
        if not self.initialized:
            raise RuntimeError("MicrophoneListener is not initialized.")
        print("Start to record...")
        try:
            while self.stream.is_active():
                in_data = self.stream.read(self.CHUNK)
                self.audio_queue.put(np.frombuffer(in_data, dtype=np.int16))
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
        print("Finished recording from microphone.")
