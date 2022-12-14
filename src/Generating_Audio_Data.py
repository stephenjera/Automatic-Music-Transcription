"""
This code creates sine waves at the frequency of musical notes and
adds some variance to them
"""

import numpy as np
import matplotlib.pyplot as plt
import wave
import struct
import os
import random
from Notes_to_Frequency import notes_to_frequency

random.seed(20)

directory = "Simulated_Dataset"
# Parent Directory path
parent_dir = ""
# Path
# path = os.path.join(parent_dir, directory)
path = directory
sr = 44100.0  # sample rate (hertz)


def create_wav(filename, freq, sample_rate=44100.0,  amplitude=20):
    # y = A*sin(w*t + phase) = A*sin(2*pi*f*t + phase)
    period = 1/sample_rate  # period for 1 sample
    t = 20  # how log to generate signal (seconds)
    n = sr * t  # number of data points (time)

    omega = 2*np.pi*freq  # angular frequency
    t_seq = np.arange(n)*period

    y = amplitude*np.sin(omega*t_seq)
    #plt.plot(t_seq, y)
    #plt.show()

    obj = wave.open(filename+".wav", "w")
    obj.setnchannels(1)  # mono
    obj.setsampwidth(2)
    obj.setframerate(sr)

    for i in y:
        print(i)
        data = struct.pack("b", int(i))
        obj.writeframesraw(data)
    obj.close()


if __name__ == "__main__":
    # Create the directory
    if not os.path.exists(path):
        os.mkdir(path)
        print("Directory '% s' created" % directory)
    else:
        print("Already a directory")

    for key, value in notes_to_frequency.items():
        # create notes directory
        note_path = os.path.join(path, key)
        if not os.path.exists(note_path):
            os.mkdir(note_path)
            # generate correct pitch signal
            create_wav(filename=note_path+"\\" + key, sample_rate=sr, freq=value)
            for j in range(10):
                amplitude_random = random.randint(5, 20)
                freq_shift = random.uniform(-10, 10)  # random float to change frequency
                new_freq = value + freq_shift
                # append a number up to 10 to identify modified data
                create_wav(filename=note_path + "\\" + key + str(j),
                           sample_rate=sr, freq=new_freq, amplitude=amplitude_random)
            print("Directory '% s' created" % key)
        else:
            print("Already a directory")


