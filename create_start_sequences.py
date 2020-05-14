import os
from music21 import converter, instrument, note, chord, stream

#TODO: read the notes file and filter the lines accordingly so that it doesn't have to be done in generate.py, maybe?
lines = []
for file in os.listdir("./startseq"):
    file = "./startseq/"+file
    midi = converter.parse(file)
    part = sorted(instrument.partitionByInstrument(midi), key=lambda p: len(p), reverse=True)

    for p in part:
        current_instrument = p.getInstrument()
        if 'Percussion' in current_instrument.classes or 'Piano' in current_instrument.classes:
            continue
        else:
            notes_to_parse = p.recurse()
            break
    else:
        notes_to_parse = part[0].recurse()

    notes = []
    for sound in notes_to_parse:
        if isinstance(sound, note.Note):
            notes.append(str(sound.pitch))
        elif isinstance(sound, chord.Chord):
            notes.append('.'.join(str(n) for n in sound.normalOrder))
    lines.append(notes)

with open("start_sequences", 'w') as f:
    for line in lines:
        f.write(" ".join(line))
        f.write('\n')