import os
import numpy as np
from music21 import converter, instrument, note, chord, stream

data_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../data/")
song_dir = os.path.join(data_dir, "start_songs")
output_dir = os.path.join(data_dir, "net2/start")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for file in os.listdir(song_dir):
    file_path = os.path.join(song_dir, file)
    midi = converter.parse(file_path)

    sounds = []
    for sound in midi.flat:
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
                
    block_size = 96
    combination_size = 7

    start = sounds[0][-2]
    for sound in sounds:
        sound[-2] -= start
    composition_arrays = []

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
                for note_num in cur_sounds[sound_idx][:-2]:
                    sounds_array[
                        (composition_offset) // block_size,
                        (composition_offset) % block_size,
                        note_num,
                    ] = 1
                cur_sounds[sound_idx][-1] -= 1
            else:
                del cur_sounds[sound_idx]
        composition_offset += 1

    network_input = sounds_array[:7, :, :]

    os.ch
    with open(os.path.join(output_dir, file.split()[0]), 'w') as f:
        for i in range(7):
            val = np.base_repr(int("".join('1' if v else '0' for j in range(96) for v in network_input[i, j, :].tolist()), base=2), base=16)
            f.write((3072-len(val))*"0" + val)
            f.write('\n')
