import sounddevice as sd
import numpy as np
from pynput.keyboard import Controller, Key
import time


RATE = 44100
CHUNK = 1024


keyboard = Controller()

# ----------------------------
freq_history = []
last_trigger_time = 0
COOLDOWN = 0.5 

# ----------------------------
# FFT zur Frequenzbestimmung
# ----------------------------
def get_frequency(signal):
    windowed = signal * np.hanning(len(signal))
    fft = np.fft.rfft(windowed)
    freqs = np.fft.rfftfreq(len(windowed), 1 / RATE)

    peak = np.argmax(np.abs(fft))
    return freqs[peak]

# ----------------------------
# Audio Callback
# ----------------------------
def audio_callback(indata, frames, time_info, status):
    global freq_history, last_trigger_time

    data = indata[:, 0]

    #  Lautstärke filtern 
    volume = np.linalg.norm(data)
    if volume < 0.01:
        return

    freq = get_frequency(data)

    #  Frequenzbereich einschränken (Pfeifen) 
    if freq < 400 or freq > 2500:
        return

    #  Verlauf speichern 
    freq_history.append(freq)

    if len(freq_history) > 8:
        freq_history.pop(0)

    #  Nur auswerten wenn genug Daten 
    if len(freq_history) < 5:
        return

    start = freq_history[0]
    end = freq_history[-1]

    diff = end - start

    now = time.time()

    # Cooldown, um Mehrfacherfassungen zu vermeiden
    if now - last_trigger_time < COOLDOWN:
        return

    # Hoch pfeifen erkennen
    if diff > 150:
        print("UP erkannt")
        keyboard.press(Key.up)
        keyboard.release(Key.up)
        last_trigger_time = now
        freq_history.clear()

    # Runter pfeifen erkennen
    elif diff < -150:
        print("DOWN erkannt")
        keyboard.press(Key.down)
        keyboard.release(Key.down)
        last_trigger_time = now
        freq_history.clear()

# ----------------------------
# Start Audio Stream
# ----------------------------
stream = sd.InputStream(
    channels=1,
    samplerate=RATE,
    blocksize=CHUNK,
    callback=audio_callback
)

print("Pfeife nach oben oder unten, um die Pfeiltasten zu steuern.")

with stream:
    while True:
        time.sleep(0.1)