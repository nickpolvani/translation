import pandas as pd
import os 
import pyaudio 
import wave
import numpy as np
from scipy.io import wavfile




DEVICE_NAME = "MOTU Audio ASIO"
CHANNELS = 4

"""
DEVICE_NAME = "Microphone Array (Realtek Audio"
CHANNELS = 2
"""


def explore_devices(name):
  # establish index of input device for sound card
  pa = pyaudio.PyAudio()
  for id in range(pa.get_device_count()):
      dev_dict = pa.get_device_info_by_index(id)
      if dev_dict["name"] == name:
        print("Found: ", dev_dict)
        return dev_dict



class Recorder():
    def __init__(self, device_name=DEVICE_NAME) -> None:
        self.df = pd.read_csv("recordings/participants.csv")
        self.participant_info = {"participant_id": len(self.df), "first_name": None, 
                                "last_name": None, "gender": None, "language": None}

        self.save_dir = f"recordings/participant_{self.participant_info['participant_id']}"
        self.current_recording = 0
        self.rate = 44100
        self.channels = CHANNELS
        self.device_name = device_name
        dev_dict = explore_devices(name=self.device_name)
        if dev_dict is None:
            raise ValueError(f"Device with name: {self.device_name} not found.")
        self.device_idx = dev_dict["index"]


    def set_language(self, language:str):
        self.participant_info["language"] = language 
        self.check_info()
        self.df = self.df.append(self.participant_info, ignore_index=True)
        self.df.to_csv("recordings/participants.csv", index=False)
        os.mkdir(f"recordings/participant_{self.participant_info['participant_id']}")


    def set_info_participant(self, info:dict):
        self.participant_info.update(info)


    def check_info(self):
        assert self.participant_info["first_name"] is not None
        assert self.participant_info["last_name"] is not None
        assert self.participant_info["gender"] is not None
        assert self.participant_info["language"] is not None


    def callback(self, in_data, frame_count, time_info, flag):
        self.fulldata.append(in_data) #saves filtered data in an array
        return (in_data, pyaudio.paContinue)


    def start_recording(self, text_to_read:str):
        self.current_recording += 1
        self.save_text(text_to_read)
        self.pa = pyaudio.PyAudio()
        self.format = pyaudio.paInt16
        self.fulldata = []

        self.pa.is_format_supported(rate=self.rate,
                            input_device=self.device_idx,
                            input_channels=self.channels,
                            input_format=self.format)

        self.stream_in = self.pa.open(
            rate=self.rate,
            channels=self.channels,
            format=self.format,
            input=True,                   # input stream flag
            input_device_index=self.device_idx,         # input device index
            frames_per_buffer=1024,
            stream_callback=self.callback
        )
        self.stream_in.start_stream()


    def save_text(self, text_to_read:str):
        output_path = os.path.join(self.save_dir, f"{self.current_recording}.txt")
        out_file = open(output_path, "w", encoding=ENCODINGS[self.participant_info["language"]])
        out_file.write(text_to_read)
        out_file.close()
        

    def stop_recording(self):
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.save_recording()


    def save_recording(self):
        output_path = os.path.join(self.save_dir, f"{self.current_recording}_all_channels.wav")
        wav_file = wave.open(output_path, "wb")
        wav_file.setnchannels(self.channels)        # number of channels
        wav_file.setsampwidth(self.pa.get_sample_size(self.format))        # sample width in bytes
        wav_file.setframerate(self.rate) 
        wav_file.writeframes(b''.join(self.fulldata))
        wav_file.close()

        rate, all_channels = wavfile.read(output_path)

        air_demo_path = os.path.join(self.save_dir, f"{self.current_recording}_air_demo.wav")
        wavfile.write(air_demo_path, rate=rate, data=all_channels[:,0])
        bone_demo_path = os.path.join(self.save_dir, f"{self.current_recording}_bone_demo.wav")
        wavfile.write(bone_demo_path, rate=rate, data=all_channels[:,1])
        air_reference_path = os.path.join(self.save_dir, f"{self.current_recording}_air_reference.wav")
        wavfile.write(air_reference_path, rate=rate, data=all_channels[:,2])



if __name__ == "__main__":
    explore_devices("ciao")