import sounddevice as sd
import numpy as np

latest_freq = 0

def get_frequency(signal, samplerate):
    windowed = signal * np.hanning(len(signal))
    fft = np.fft.rfft(windowed)
    freqs = np.fft.rfftfreq(len(windowed), 1 / samplerate)

    peak = np.argmax(np.abs(fft))
    return freqs[peak]

# Set up audio stream
# reduce chunk size and sampling rate for lower latency
CHUNK_SIZE = 1024 # Number of audio frames per buffer
RATE = 44100 # Audio sampling rate (HZ)
CHANNELS = 1 # Mono audio

# print info about audio devices

print("Available input devices:\n")
devices = sd.query_devices()

input_devices = []
for i, dev in enumerate(devices):
    if dev['max_input_channels'] > 0:
        print(f"{i}: {dev['name']}")
        input_devices.append(i)

# let user select audio device
input_device = int(input("\nSelect input device: "))



def start_stream(callback):
    # audio callback to safe data
    def audio_callback(indata, frames, time, status):
        

        data = indata[:, 0]  # mono

        volume = np.linalg.norm(data)  # Lautstärke

        if volume < 0.03: 
            return

        # Frequenz berechnen
        freq = get_frequency(data, RATE)

        # Rauschen von Frequenzen unter 50 Hz ignorieren
        if freq > 50:
             callback(freq)


    # open audio input stream
    stream = sd.InputStream(
        device=input_device,
        channels=CHANNELS,
        samplerate=RATE,
        blocksize=CHUNK_SIZE,
        callback=audio_callback,
        latency='low'
    )
    return stream


