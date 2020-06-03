import os
from music21 import converter, instrument, note, chord, stream

data_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../data/")
song_dir = os.path.join(data_dir, "start_songs")
output_dir = os.path.join(data_dir, "net1/start")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for file in os.listdir(song_dir):
    file_path = os.path.join(song_dir, file)
    midi = converter.parse(file_path)
    part = sorted(instrument.partitionByInstrument(midi), key=lambda p: len(p), reverse=True)

    for p in part:
        current_instrument = p.getInstrument()
        if 'Percussion' in current_instrument.classes:
            continue
        else:
            sounds_to_parse = p.recurse()
            break
    else:
        sounds_to_parse = part[0].recurse()

    sounds = []
    for sound in sounds_to_parse:
        if isinstance(sound, note.Note):
            sounds.append(str(sound.pitch))
        elif isinstance(sound, chord.Chord):
            sounds.append('.'.join(str(n) for n in sound.normalOrder))
            
    with open(os.path.join(output_dir, file.split()[0]), 'w') as f:
        f.write(" ".join(sounds))
        f.write('\n')