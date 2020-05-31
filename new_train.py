import numpy as np
import os
import tensorflow.keras.layers as layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import ModelCheckpoint
from music21 import converter, instrument, note, chord, stream


def parse_files(genre):
    compositions = []
    with os.scandir("data/" + genre) as files:
        for f in files:
            if f.name.endswith(".mid") or f.name.endswith(".MID") and f.is_file():
                print("Parsing {}".format(f.name))
                midi = converter.parse(f.path)
                sounds = []
                try:
                    p = instrument.partitionByInstrument(midi)
                    notes_to_parse = p.parts[0].recurse()
                except AttributeError:
                    notes_to_parse = midi.flat.notes

                for sound in notes_to_parse:
                    if isinstance(sound, note.Note):
                        sounds.append(
                            [
                                int(sound.pitch.midi),
                                int(12 * sound.offset),
                                int(12 * sound.duration.quarterLength),
                            ]
                        )
                    elif isinstance(sound, chord.Chord):
                        sounds.append(
                            [n.midi for n in sound.pitches]
                            + [
                                int(12 * sound.offset),
                                int(12 * sound.duration.quarterLength),
                            ]
                        )

                if sounds:
                    compositions.append(sounds)

    return compositions


def prepare_data(compositions):
    block_size = 96
    combination_size = 7
    superture_size = 0

    for sounds in compositions:
        start = sounds[0][-2]
        for sound in sounds:
            sound[-2] -= start
        superture_size += sounds[-1][-2] + sounds[-1][-1]
    composition_arrays = []

    for sounds in compositions:
        composition_offset = 0
        cur_sounds = []
        i = 0
        end_offset = (sounds[-1][-2] + sounds[-1][-1]) // block_size
        sounds_array = np.zeros((end_offset, block_size, 128), dtype=bool)

        while (composition_offset) // block_size < end_offset:
            while i < len(sounds) and sounds[i][-2] == composition_offset:
                cur_sounds.append(sounds[i][:])
                i += 1
            for sound_idx in range(len(cur_sounds) - 1, -1, -1):
                if cur_sounds[sound_idx][-1] > 0:
                    for note in cur_sounds[sound_idx][:-2]:
                        sounds_array[
                            (composition_offset) // block_size,
                            (composition_offset) % block_size,
                            note,
                        ] = 1
                    cur_sounds[sound_idx][-1] -= 1
                else:
                    del cur_sounds[sound_idx]
            composition_offset += 1

        composition_arrays.append(sounds_array)

    blocks_amount = 0
    for block in composition_arrays:
        blocks_amount += max([block.shape[0] - combination_size, 0])

    network_inputs = np.zeros((blocks_amount, combination_size, block_size, 128), dtype=bool)
    network_targets = np.zeros((blocks_amount, block_size, 128), dtype=bool)
    offset = 0

    for block_idx in range(len(composition_arrays)):
        for idx in range(composition_arrays[block_idx].shape[0] - combination_size):
            network_inputs[offset, :, :, :] = composition_arrays[block_idx][idx : idx+combination_size, :, :]
            network_targets[offset, :, :] = composition_arrays[block_idx][idx+combination_size, :, :]
            offset += 1

    return network_inputs, network_targets


def prepare_model(input_shape):
    combination_size = input_shape[0]
    block_size = input_shape[1]

    model = Sequential()
    model.add(layers.Input(shape=input_shape))
    model.add(layers.TimeDistributed(layers.Dense(1024)))
    model.add(layers.TimeDistributed(layers.LSTM(512, return_sequences=True)))
    model.add(layers.Dropout(0.1))
    model.add(layers.Reshape((combination_size*block_size,512)))
    model.add(layers.LSTM(64,return_sequences=True))
    model.add(layers.Dropout(0.1))
    model.add(layers.Reshape((combination_size,block_size*64)))
    model.add(layers.LSTM(block_size*32,return_sequences=False))
    model.add(layers.Dropout(0.1))
    model.add(layers.Reshape((block_size,32)))
    model.add(layers.LSTM(128,return_sequences=True))
    model.add(layers.BatchNormalization())
    model.add(layers.TimeDistributed(layers.Dense(128, activation="softmax")))

    model.compile(loss="binary_crossentropy", optimizer="rmsprop")
    return model


def train(genre):
    compositions = parse_files(genre)
    input, target = prepare_data(compositions)
    model = prepare_model(input.shape[1:])

    checkpoint = ModelCheckpoint(
        genre + "_model.h5", monitor="loss", verbose=0, save_best_only=True, mode="min"
    )

    print(
        "Your new model is located at {0}/{1}_model.h5.\n"
        "In order to use it for generating, move it to models/{1}/ "
        "in the project's directory along with the {1}_notes file.".format(
            os.getcwd(), genre
        ),
    )

    model.fit(input, target, epochs=200, batch_size=1024, callbacks=[checkpoint])


if __name__ == "__main__":
    train("test")
