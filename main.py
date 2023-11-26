from transformers import AutoProcessor, SeamlessM4TModel
import torch 


processor = AutoProcessor.from_pretrained("facebook/hf-seamless-m4t-medium")
model = SeamlessM4TModel.from_pretrained("facebook/hf-seamless-m4t-medium")

# let's load an audio sample from an Arabic speech corpus
from datasets import load_dataset
dataset = load_dataset("arabic_speech_corpus", split="test", streaming=True)
audio_sample = next(iter(dataset))["audio"]

# now, process it
audio_inputs = processor(audios=audio_sample["array"], return_tensors="pt")

# now, process some English test as well
text_inputs = processor(text = "Hello, my dog is cute", src_lang="eng", return_tensors="pt")

audio_array_from_text = model.generate(**text_inputs, tgt_lang="rus")[0].cpu().numpy().squeeze()
audio_array_from_audio = model.generate(**audio_inputs, tgt_lang="rus")[0].cpu().numpy().squeeze()

# from audio
# calculate time to execute this code
import time
start = time.time()
output_tokens = model.generate(**audio_inputs, tgt_lang="fra", generate_speech=False)
translated_text_from_audio = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
end = time.time()
print(end - start)

# from text
output_tokens = model.generate(**text_inputs, tgt_lang="fra", generate_speech=False)
translated_text_from_text = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)

print(translated_text_from_audio)
print(translated_text_from_text)