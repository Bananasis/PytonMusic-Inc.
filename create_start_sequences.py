import os
from music21 import converter, instrument, note, chord, stream

lines = []
for file in os.listdir("./startseq"):
    file = "./startseq/"+file
    midi = converter.parse(file)
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
            
    lines.append(sounds)

with open("start_sequences", 'w') as f:
    for line in lines:
        f.write(" ".join(line))
        f.write('\n')