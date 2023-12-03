import numpy as np
from app.vad_plotter import VadPlotter

class Vad:

    def __init__(self, threshold:float, frame_duration_ms:float, sample_rate:int, plot_vad=False):
        self.threshold = threshold
        self.frame_duration_ms = frame_duration_ms
        self.sample_rate = sample_rate

        self.current_silence_seconds = 0
        self.current_speech_seconds = 0
        self.cur_time = 0

        if plot_vad:
            self.vad_plotter = VadPlotter()
        else:
            self.vad_plotter = None

    def is_speech(self, audio_data:np.ndarray) -> bool:
        """
        Returns True if the audio data contains speech, False otherwise.
        """
        result = None
        self.cur_time += self.frame_duration_ms / 1000
        if self.__is_silence(audio_data):
            self.current_silence_seconds += self.frame_duration_ms / 1000
            self.current_speech_seconds = 0
            result =  False
        else:
            self.current_speech_seconds += self.frame_duration_ms / 1000
            self.current_silence_seconds = 0
            result = True
        if self.vad_plotter:
            self.vad_plotter.update_plot(self.cur_time, result)
        return result
        
    def __is_silence(self, audio_data:np.ndarray) -> bool:
        """
        Returns True if the audio data is silent, False otherwise.
        audio data is float in range [-1, 1]
        """
        audio_range = np.max(audio_data) - np.min(audio_data)
        max_amplitude = 2.0
        if audio_range > max_amplitude:
            raise ValueError("Audio data is not in range [-1, 1]. Range is:", audio_range)
        if audio_range / max_amplitude < self.threshold:
            return True
        else:
            return False
        
