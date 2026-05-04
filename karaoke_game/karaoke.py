from audio_backend import start_stream
from mido import MidiFile
import pyglet
import pyglet.shapes
import numpy as np
import time


window = pyglet.window.Window(1000, 600, "Karaoke Game")


# ----------------------------
status_text = "Los geht's!"
current_freq = 0

current = 0
score = 0
game_over = False

freq_history = []
first_try = True

last_note_freq = 0
last_hit_time = 0
COOLDOWN = 0.5  # 0.5 Sekunden Pause zwischen Noten

# ----------------------------
# Noten und Frequenz Umrechnung
# ----------------------------
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F",
              "F#", "G", "G#", "A", "A#", "B"]

def midi_to_name(note):
    return NOTE_NAMES[note % 12] + str(note // 12 - 1)


def midi_to_notes(path):
    mid = MidiFile(path)
    notes = []

    for msg in mid:
        if msg.type == 'note_on' and msg.velocity > 0:
            if len(notes) == 0 or notes[-1] != msg.note:
                notes.append(msg.note)

    return notes


def midi_to_freq(note):
    return 440 * 2 ** ((note - 69) / 12)


def freq_to_y(freq):
    if freq <= 0:
        return 120
    return 120 + np.log2(freq) * 80


# ----------------------------
# Song laden und vorbereiten
# ----------------------------
song_notes = midi_to_notes("read_midi/freude.mid")
song_names = [midi_to_name(n) for n in song_notes]
song_freqs = [midi_to_freq(n) for n in song_notes]

# ----------------------------
# Visualisierung der Song-Noten
# ----------------------------
PITCH_X = 40
PITCH_STEP_X = 40

pitch_points = []

for i, f in enumerate(song_freqs):
    pitch_points.append(
        pyglet.shapes.Rectangle(
            PITCH_X + i * PITCH_STEP_X,
            freq_to_y(f),
            20,
            6,
            color=(200, 200, 200)
        )
    )

# ----------------------------
# Spiel-Logik
# ----------------------------
def game_step(freq):
    global current, score, status_text, current_freq
    global game_over, freq_history, first_try
    global last_note_freq, last_hit_time

    if game_over:
        return

    # Glättet die Frequenz über die letzten 5 Werte, um Rauschen zu reduzieren
    freq_history.append(freq)
    if len(freq_history) > 5:
        freq_history.pop(0)

    freq = np.mean(freq_history)
    current_freq = freq

    # Spielende 
    if current >= len(song_freqs):
        status_text = f"Ende"
        game_over = True
        return

    target = song_freqs[current]
    diff = abs(freq - target)

    now = time.time()

    # Pause zwischen Noten, um versehentliche Mehrfacherfassungen zu vermeiden
    if now - last_hit_time < COOLDOWN:
        return

    # nur bewerten, wenn sich die Tonhöhe deutlich geändert hat
    pitch_changed = abs(freq - last_note_freq) > 20

    #  Bewertung 
    if diff < 25 and pitch_changed:
        status_text = "perfekt"

        if first_try:
            score += 2

        last_note_freq = freq
        last_hit_time = now

        current += 1
        first_try = True

    elif diff < 50 and pitch_changed:
        status_text = "fast"

        if first_try:
            score += 1

        last_note_freq = freq
        last_hit_time = now

        current += 1
        first_try = True

    else:
        status_text = "falsch"
        first_try = False


# ----------------------------
# UI Elemente
# ----------------------------
note_label = pyglet.text.Label("", x=20, y=570, font_size=18)
info_label = pyglet.text.Label("", x=20, y=520, font_size=14, multiline=True, width=960)

# ----------------------------
# Drawing und Update
# ----------------------------
@window.event
def on_draw():
    window.clear()

    current_note = song_names[current] if current < len(song_names) else "Ende"
    target = song_freqs[current] if current < len(song_freqs) else 0

    note_label.text = f"Note: {current_note}"
    note_label.draw()

    info_label.text = (
        f"Ziel: {target:.1f} Hz\n"
        f"You: {current_freq:.1f} Hz\n"
        f"Score: {score}\n"
        f"{status_text}"
    )
    info_label.draw()

    # Noten anzeigen
    for p in pitch_points:
        p.draw()

    # Aktuelle Note markieren
    if current < len(pitch_points):
        pyglet.shapes.Rectangle(
            pitch_points[current].x,
            pitch_points[current].y,
            20,
            6,
            color=(0, 255, 0)
        ).draw()

    # gesungene Note anzeigen
    pyglet.shapes.Circle(
        PITCH_X + current * PITCH_STEP_X,
        freq_to_y(current_freq),
        6,
        color=(255, 50, 50)
    ).draw()


def update(dt):
    pass


pyglet.clock.schedule_interval(update, 1/30)

# ----------------------------
# Start Audio Stream und Spiel
# ----------------------------
stream = start_stream(game_step)

with stream:
    pyglet.app.run()