import queue
from app.vad import Vad
from PyQt5.QtCore import QThread
import numpy as np
from PyQt5.QtCore import pyqtSignal

class AudioProcessorThread(QThread):

    vad_available = pyqtSignal(float, int)

    def __init__(
        self,
        audio_queue: queue.Queue,
        input_rate: int,
        length_chunk_seconds: float,
        max_chunk_length_seconds: float = 15.0,
        sec_silence_before_processing: float = 3.0,
        parent=None,
    ):
        super(AudioProcessorThread, self).__init__(parent)

        self.audio_queue = audio_queue
        self.input_rate = input_rate
        self.length_chunk_seconds = length_chunk_seconds
        self.vad = Vad(
            threshold=0.05,
            frame_duration_ms=self.length_chunk_seconds * 1000,
            sample_rate=self.input_rate,
            plot_vad=True,
        )

        self.max_chunk_length_seconds = max_chunk_length_seconds
        self.sec_silence_before_processing = sec_silence_before_processing
        self.current_silence_seconds = 0

        self.audio_frames = []
        self.sentence_queue = queue.Queue()
        self.current_time = 0

    def _get_accumulated_audio_seconds(self) -> float:
        return len(self.audio_frames) * self.length_chunk_seconds

    def consume_audio_queue(self) -> None:
        """
        Updates the plot with new audio data from the queue. Processes the audio data,
        translates it to text, and updates the spectrogram plot.
        """
        audio_data = self.audio_queue.get()  # This blocks until audio data is available
        self.current_time += self.length_chunk_seconds
        # discard the first 2 seconds of audio data
        if self.current_time < 2:
            return None

        # measure the time to process audio data
        audio_data = audio_data / 32768.0  # Convert to float [-1, 1]
        # print(f"range of audio data: {np.min(audio_data)} to {np.max(audio_data)}")

        is_speech = self.vad.is_speech(audio_data)
        self.vad_available.emit(self.vad.cur_time, int(is_speech))

        #  discard audio data if it is not speech and we have not accumulated enough audio data
        if not is_speech:
            if len(self.audio_frames) == 0:
                self.current_silence_seconds = 0
                return None

        # add to current audio frames
        self.audio_frames.append(audio_data)

        # if we have accumulated the max amount of audio data, process it
        if self._get_accumulated_audio_seconds() > self.max_chunk_length_seconds:
            self._ask_for_translation()

        # if we have accumulated enough silence, process the audio data
        if not is_speech and len(self.audio_frames) > 0:
            self.current_silence_seconds += self.length_chunk_seconds
            if self.current_silence_seconds > self.sec_silence_before_processing:
                self._ask_for_translation()
            else:
                return None

        if is_speech:
            self.current_silence_seconds = 0
            return None

    def _ask_for_translation(self) -> None:
        audio_data = np.concatenate(self.audio_frames)
        self.sentence_queue.put(audio_data)
        self.audio_frames = []
        self.current_silence_seconds = 0

    def run(self) -> None:
        while True:
            self.consume_audio_queue()
