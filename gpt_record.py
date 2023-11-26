import pyaudio
import numpy as np
import time

# Constants
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1              # Single channel for microphone
RATE = 44100              # Sampling rate
CHUNK_DURATION = 10       # Duration of a chunk in seconds
CHUNK_SIZE = int(RATE * CHUNK_DURATION)  # Size of a chunk in frames

def process_audio_data(in_data, frame_count, time_info, status):
    audio_data = np.frombuffer(in_data, dtype=np.int16)

    # Process the chunk here
    print("Processing chunk...")

    # For demonstration, just sleep (simulate processing)
    time.sleep(1)

    return (None, pyaudio.paContinue)

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open stream in callback mode
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE,
                stream_callback=process_audio_data)

print("Recording...")

# Start the stream
stream.start_stream()

try:
    # Keep the script running as long as the stream is open
    while stream.is_active():
        time.sleep(0.1)
except KeyboardInterrupt:
    # Stop and close the stream and terminate PyAudio
    print("\nStopping...")
    stream.stop_stream()
    stream.close()
    p.terminate()
