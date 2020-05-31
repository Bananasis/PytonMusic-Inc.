import numpy as np
import random
from tensorflow.keras.models import load_model
from music21 import instrument, note, stream, chord, duration

generated_song = None
lazy_models = {}

def prepare_model(genre):
    if genre not in lazy_models:
        model = load_model("models/{0}/{0}_model.h5".format(genre))
        lazy_models.setdefault(genre, model)
    else:
        model = lazy_models.get(genre)

    with open("models/{0}/{0}_notes".format(genre), "r") as file:
        notes = file.read().split()
    sounds = sorted(set(notes))
    return model, sounds


def prepare_start_sequence(sounds, name):
    index = {
        "The Stranger Things Theme": 0,
        "Africa by Toto": 1,
        "Clocks by Coldplay": 2,
        "Dancing Queen by Abba": 3,
        "Don't Start Now by Dua Lipa": 4,
    }[name]
    sound_to_int = {n: i for i, n in enumerate(sounds)}
    with open("data/start_sequences", "r") as path:
        sequences = path.read().splitlines()
    chosen_seq = sequences[index].split()
    sequence = [sound_to_int[s] for s in chosen_seq if s in sounds][:100]
    return sequence, chosen_seq[-15:]


def sequence_to_song(sequence):
    global generated_song

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

    generated_song = stream.Stream(part)


def generate(genre, start_seq, monitoring_progress=False):
    model, sounds = prepare_model(genre)
    int_to_sound = {i: n for i, n in enumerate(sounds)}
    input_sequence, output_sequence = prepare_start_sequence(sounds, start_seq)

    for note_index in range(100):
        if monitoring_progress: yield note_index
        real_input = np.reshape(input_sequence, (1, len(input_sequence), 1)) / len(sounds)
        output = model.predict(real_input, verbose=0)
        predicted_index = np.argmax(output)
        output_sequence.append(int_to_sound[predicted_index])
        input_sequence.append(predicted_index)
        input_sequence = input_sequence[1:]

    sequence_to_song(output_sequence)


def play():
    if generated_song:
        generated_song.show("midi")


def save(path):
    if generated_song:
        generated_song.write("midi", path)


if __name__ == "__main__":
    generate("test", "clocks")
    save("out.mid")

