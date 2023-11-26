import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import queue
from scipy.signal import spectrogram
import threading
import librosa
from transformers import AutoProcessor, SeamlessM4TModel
import torch
import wave

processor = AutoProcessor.from_pretrained("facebook/hf-seamless-m4t-medium")
model = SeamlessM4TModel.from_pretrained("facebook/hf-seamless-m4t-medium")

# Constants
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = int(RATE * 10)  # 10-second chunks

frames = []
WAVE_OUTPUT_FILENAME = "output.wav"
MAX_NUM_FRAMES = 2
CUR_FRAME = 0

# Queue to hold audio data
audio_queue = queue.Queue()

# Initialize PyAudio
p = pyaudio.PyAudio()

# Set up the matplotlib interactive mode
plt.ion()

# Create a figure and axis for the spectrogram
fig, ax = plt.subplots()


def callback(in_data, frame_count, time_info, status):
    audio_queue.put(np.frombuffer(in_data, dtype=np.int16))
    return (None, pyaudio.paContinue)


def update_plot():
    if not audio_queue.empty():
        audio_data = audio_queue.get()
        frames.append(audio_data)

        # resample audio data to 16 KHz
        new_rate = 16000
        # convert from 16 bit to float in range [-1, 1]
        audio_data = audio_data / 32768.0
        audio_data = librosa.resample(y=audio_data, orig_sr=RATE, target_sr=new_rate)

        audio_inputs = processor(
            audios=audio_data, return_tensors="pt", sampling_rate=new_rate
        )
        # print(audio_inputs.shape)
        # print("Range of audio_inputs: ", audio_inputs.min(), audio_inputs.max())

        output_tokens = model.generate(**audio_inputs, tgt_lang="eng", generate_speech=False)
        translated_text_from_audio = processor.decode(
            output_tokens[0].tolist()[0],
            skip_special_tokens=True,
            generate_speech=False,
        )
        print(translated_text_from_audio)

        # Generate the spectrogram
        f, t, Sxx = spectrogram(audio_data, new_rate, nperseg=1024)
        ax.clear()
        ax.pcolormesh(t, f, 10 * np.log10(Sxx), shading="gouraud")
        ax.set_ylabel("Frequency [Hz]")
        ax.set_xlabel("Time [sec]")
        global CUR_FRAME
        CUR_FRAME += 1

        # Update the plot
        plt.draw()


# Open stream
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
    stream_callback=callback,
)

# Start the stream
stream.start_stream()

# Update the plot in the main thread
try:
    while stream.is_active():
        update_plot()
        if CUR_FRAME >= MAX_NUM_FRAMES:
            break
        plt.pause(0.1)
except KeyboardInterrupt:
    # Stop and close the stream and terminate PyAudio
    print("\nStopping...")
    stream.stop_stream()
    stream.close()
    p.terminate()

finally:
    # Save the recorded data as a WAV file
    wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()

    # Close the plot
    plt.close(fig)

    # Stop and close the stream and terminate PyAudio
    stream.stop_stream()
    stream.close()
    p.terminate()
