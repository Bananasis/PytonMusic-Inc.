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
    return model


def prepare_start_sequence(name):
    file = {
        "The Stranger Things Theme": "Stranger",
        "Africa by Toto": "Toto",
        "Clocks by Coldplay": "Coldplay",
        "Dancing Queen by Abba": "Abba",
        "Don't Start Now by Dua Lipa": "Dua",
    }[name]

    with open("data/start/" + file, "r") as path:
        blocks = path.read().splitlines()

    arr = [
        [
            (128 - len(s)) * [0] + [int(c) for c in s]
            for i in range(0, 3072, 32)
            if (s := bin(int(b[i : i + 32], base=16))[2:])
        ]
        for b in blocks
    ]

    sequence = np.array(arr, dtype=bool)
    return sequence

def sequence_to_song(sequence):
    song = []
    dur = duration.Duration()
    dur.quarterLength = 1/12
    prev = {}
    for i in range(sequence.shape[0]):
        for j in range(sequence.shape[1]):
            indices = np.argwhere(sequence[i, j, :]).T[0]
            print(indices)
            cur_notes = {}
            for ind in indices:
                if ind in prev:
                    new_note = prev[ind]
                    new_note.duration.quarterLength += 1/12
                    cur_notes[ind] = new_note
                else:
                    new_note = note.Note(ind)
                    new_note.offset = (i*96+j)/12
                    new_note.duration = dur
                    song.append(new_note)
                    cur_notes[ind] = new_note
            prev = cur_notes

    return stream.Stream(song)

def generate(genre, start_seq):
    model = prepare_model(genre)
    input_sequence = prepare_start_sequence(start_seq)
    output_sequence = np.zeros(shape=(5, 96, 128), dtype=bool)
    output_sequence[0,:,:] = input_sequence[-1, :, :]

    for step in range(1, 5):
        yield step/5 * 100
        output = model.predict(input_sequence, verbose=0)
        real_output = 0.1 < (output / np.max(output))
        output_sequence[i, :, :] = real_output
        input_sequence[:-1, :, :] = input_sequence[1:, :, :]
        input_sequence[-1, :, :] = real_output

    return sequence_to_song(output_sequence)


def save(path, song):
    song.write("midi", path)


if __name__ == "__main__":
    list(generate("test", "Clocks by Coldplay"))
