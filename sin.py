import wave
import numpy
import struct

a = 1
fs = 44100
freq = 440
sec = 10

s_wav = [a * numpy.sin(2.0 * numpy.pi * freq * i / fs) for i in numpy.arange(fs * sec)]
s_wav = [int(x * 32767.0) for x in s_wav]

bin_wave = struct.pack("h" * len(s_wav),*s_wav)

_w = wave.open("sin.wav",mode="wb")
_w.setnchannels(1)
_w.setsampwidth(2)
_w.setframerate(fs)
_w.setnframes(len(bin_wave))
_w.writeframes(bin_wave)
_w.close()