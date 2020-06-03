import os
import random
import numpy as np
from tensorflow.keras.models import load_model
from music21 import instrument, note, stream, chord, duration

lazy_models = {}

project_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/..")
model_dir = os.path.join(project_dir, "data/net1/models")
start_dir = os.path.join(project_dir, "data/net1/start")
output_dir = os.path.join(project_dir, "lib")

def prepare_model(genre):
    global lazy_models
    if genre not in lazy_models:
        model = load_model(os.path.join(model_dir, genre, "model.h5"))
        lazy_models.setdefault(genre, model)
    else:
        model = lazy_models.get(genre)

    with open(os.path.join(model_dir, genre, "notes"), "r") as file:
        notes = file.read().split()
    sounds = sorted(set(notes))
    return model, sounds


def prepare_start_sequence(sounds, name):
    file = {
        "The Stranger Things Theme": "Stranger",
        "Africa by Toto": "Toto",
        "Clocks by Coldplay": "Coldplay",
        "Dancing Queen by Abba": "Abba",
        "Don't Start Now by Dua Lipa": "Dua",
    }[name]
    sound_to_int = {n: i for i, n in enumerate(sounds)}
    with open(os.path.join(start_dir, file), "r") as path:
        chosen_seq = path.read().split()
    sequence = [sound_to_int[s] for s in chosen_seq if s in sounds][:100]
    return sequence, chosen_seq[-15:]


def sequence_to_song(sequence):
    possible_offsets = [0.5, 0.5, 0.5, 1.0, 1.5]
    rhythmic_values = [0.0, 0.0, 0.5, 1.0, 1.5, 2.0]
    offsets = []
    rhythm = []

    while len(offsets) < 116:
        sequence_length = np.random.randint(2, 6)
        repeat_count = np.random.randint(1, 3)

        offset_sequence = [
            random.choice(possible_offsets) for _ in range(sequence_length)
        ]
        rhythmic_sequence = [
            off + random.choice(rhythmic_values) for off in offset_sequence
        ]

        offsets += repeat_count * offset_sequence
        rhythm += repeat_count * rhythmic_sequence

    offset = 0
    part = []
    for i, sound in enumerate(sequence):
        dur = duration.Duration()
        dur.quarterLength = rhythm[i]

        if ("." in sound) or sound.isdigit():
            int_notes = [int(n) for n in sound.split(".")]
            real_notes = []

            for n in int_notes:
                current_note = note.Note(n)
                current_note.storedInstrument = instrument.Piano()
                real_notes.append(current_note)

            current_chord = chord.Chord(real_notes)
            current_chord.offset = offset
            current_chord.duration = dur
            part.append(current_chord)

        else:
            current_note = note.Note(sound)
            current_note.offset = offset
            current_note.duration = dur
            current_note.storedInstrument = instrument.Piano()
            part.append(current_note)

        offset += offsets[i]

    return stream.Stream(part)


def generate(genre, start_seq, name):
    model, sounds = prepare_model(genre)
    int_to_sound = {i: n for i, n in enumerate(sounds)}
    input_sequence, output_sequence = prepare_start_sequence(sounds, start_seq)

    for note_index in range(100):
        yield note_index
        real_input = np.reshape(input_sequence, (1, len(input_sequence), 1))/len(sounds)
        output = model.predict(real_input, verbose=0)
        predicted_index = np.argmax(output)
        output_sequence.append(int_to_sound[predicted_index])
        input_sequence.append(predicted_index)
        input_sequence = input_sequence[1:]

    song = sequence_to_song(output_sequence)
    song.write("midi", os.path.join(output_dir, name))


if __name__ == "__main__":
    list(generate("test", "Clocks by Coldplay", "nwm"))
