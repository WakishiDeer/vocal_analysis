import numpy as np
from shennong.audio import Audio
from shennong.processor.mfcc import MfccProcessor
from shennong.postprocessor.vad import VadPostProcessor
import pandas as pd

audio_data = Audio.load('../../etc/hu.wav')
# audio_data = Audio(data=audio_data, sample_rate=44100)
pd.DataFrame(audio_data.data).to_csv("data/women.csv")
# print(np.mean(audio_data.data))
mfcc = MfccProcessor(sample_rate=audio_data.sample_rate).process(audio_data)
pd.DataFrame(mfcc.data).to_csv("data/women_mfcc.csv")
processor = VadPostProcessor(energy_threshold=10.0)
vad = processor.process(mfcc)
nframes = mfcc.shape[0]
vad.shape == (nframes, 1)
nvoiced = sum(vad.data[vad.data == 1])
print('{} voiced frames out of {}'.format(nvoiced, nframes))
