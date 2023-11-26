import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import queue
import librosa
from scipy.signal import spectrogram
from transformers import AutoProcessor, SeamlessM4TModel
import wave

class AudioProcessor:
    def __init__(self):
        # Constants
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = int(self.RATE * 10)  # 10-second chunks
        self.WAVE_OUTPUT_FILENAME = "output.wav"
        self.MAX_NUM_FRAMES = 2
        self.CUR_FRAME = 0

        self.frames = []
        self.audio_queue = queue.Queue()

        # Initialize model and processor
        self.processor = AutoProcessor.from_pretrained("facebook/hf-seamless-m4t-medium")
        self.model = SeamlessM4TModel.from_pretrained("facebook/hf-seamless-m4t-medium")

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()

        # Set up Matplotlib interactive mode
        plt.ion()
        self.fig, self.ax = plt.subplots()

        # Open stream
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            stream_callback=self.callback,
        )

    def callback(self, in_data, frame_count, time_info, status):
        self.audio_queue.put(np.frombuffer(in_data, dtype=np.int16))
        return (None, pyaudio.paContinue)

    def update_plot(self):
        if not self.audio_queue.empty():
            audio_data = self.audio_queue.get()
            self.frames.append(audio_data)

            # Audio processing
            audio_data = self.process_audio(audio_data)

            # Speech-to-text translation
            self.translate_speech(audio_data)

            # Update spectrogram plot
            self.plot_spectrogram(audio_data)

            self.CUR_FRAME += 1

    def process_audio(self, audio_data):
        new_rate = 16000
        audio_data = audio_data / 32768.0  # Convert to float [-1, 1]
        return librosa.resample(y=audio_data, orig_sr=self.RATE, target_sr=new_rate)

    def translate_speech(self, audio_data):
        audio_inputs = self.processor(
            audios=audio_data, return_tensors="pt", sampling_rate=16000
        )
        output_tokens = self.model.generate(**audio_inputs, tgt_lang="eng", generate_speech=False)
        translated_text = self.processor.decode(
            output_tokens[0].tolist()[0],
            skip_special_tokens=True,
            generate_speech=False,
        )
        print(translated_text)

    def plot_spectrogram(self, audio_data):
        f, t, Sxx = spectrogram(audio_data, 16000, nperseg=1024)
        self.ax.clear()
        self.ax.pcolormesh(t, f, 10 * np.log10(Sxx), shading="gouraud")
        self.ax.set_ylabel("Frequency [Hz]")
        self.ax.set_xlabel("Time [sec]")
        plt.draw()

    def run(self):
        try:
            while self.stream.is_active():
                self.update_plot()
                if self.CUR_FRAME >= self.MAX_NUM_FRAMES:
                    break
                plt.pause(0.1)
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.cleanup()

    def cleanup(self):
        # Save recorded data
        wf = wave.open(self.WAVE_OUTPUT_FILENAME, "wb")
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b"".join(self.frames))
        wf.close()

        # Close Matplotlib plot
        plt.close(self.fig)

        # Close PyAudio stream
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

# Create and run the audio processor
audio_processor = AudioProcessor()
audio_processor.run()
