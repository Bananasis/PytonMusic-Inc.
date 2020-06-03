import numpy as np
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, Activation
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.utils import to_categorical
from music21 import converter, instrument, note, chord, stream

data_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../data/")
models_dir =  os.path.join(data_dir, "net1/models")

def parse_files(genre):
    sounds = []
    with os.scandir(os.path.join(data_dir, genre)) as files:
        for f in files:
            if f.name.endswith(".mid") or f.name.endswith(".MID") and f.is_file():
                print("Parsing {}".format(f.name))
                midi = converter.parse(f.path)
                try:
                    p = instrument.partitionByInstrument(midi)
                    notes_to_parse = p.parts[0].recurse()
                except AttributeError:
                    notes_to_parse = midi.flat.notes

                for sound in notes_to_parse:
                    if isinstance(sound, note.Note):
                        sounds.append(str(sound.pitch))
                    elif isinstance(sound, chord.Chord):
                        sounds.append(".".join(str(n) for n in sound.normalOrder))

    notes_path = os.join(models_dir, genre, "notes")
    with open(notes_path, 'w') as f:
        f.write(" ".join(sounds))

    return sounds


def prepare_data(sounds):
    sequence_length = 100
    sound_names = sorted(set(sounds))
    sound_to_int = {s: i for i, s in enumerate(sound_names)}

    network_inputs = []
    network_targets = []
    for i in range(len(sounds) - sequence_length):
        input_sequence = [sound_to_int[s] for s in sounds[i : i + sequence_length]]
        target_output = sound_to_int[sounds[i + sequence_length]]
        network_inputs.append(input_sequence)
        network_targets.append(target_output)

    network_inputs = np.reshape(network_inputs, (len(network_inputs), sequence_length, 1))
    network_inputs = network_inputs / float(len(sound_names))
    network_targets = to_categorical(network_targets)

    return network_inputs, network_targets, len(sound_names)


def prepare_model(input_shape, output_range):
    model = Sequential()
    model.add(
        LSTM(
            512,
            input_shape=(input_shape[1], input_shape[2]),
            recurrent_dropout=0.3,
            return_sequences=True,
        )
    )
    model.add(LSTM(512, return_sequences=True, recurrent_dropout=0.3))
    model.add(LSTM(512))
    model.add(Dropout(0.3))
    model.add(Dense(256))
    model.add(Activation("relu"))
    model.add(Dropout(0.3))
    model.add(Dense(output_range))
    model.add(Activation("softmax"))
    model.compile(loss="categorical_crossentropy", optimizer="rmsprop")
    return model


def train(genre):
    sounds = parse_files(genre)
    input, target, output_range = prepare_data(sounds)
    model = prepare_model(input.shape, output_range)

    model_path = os.path.join(models_dir, genre, "model.h5")
    checkpoint = ModelCheckpoint(
        model_path, monitor="loss", verbose=0, save_best_only=True, mode="min"
    )

    print(f"Your new model is located at {model_path}.")

    model.fit(input, target, epochs=200, batch_size=1024, callbacks=[checkpoint])


if __name__ == "__main__":
    train("test")
