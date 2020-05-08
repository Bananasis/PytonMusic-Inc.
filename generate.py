import pickle
import numpy as np

from music21 import instrument, note, stream, chord, duration

import os
import sys
import tensorflow as tf

# program arguments:
# - path to file with notes,
# - path to trained model,
# - output MIDI file.
path_to_note_file = sys.argv[1]
path_to_model = sys.argv[2]
output_file = sys.argv[3]

# loading, loading, loading note file
with open(path_to_note_file, 'rb') as path:
    notes = list(pickle.load(path))

sounds_names = sorted(set(notes))
number_of_sounds = len(sounds_names)

# mapping
notes_in_int = dict((n, i) for i, n in enumerate(sounds_names))

sequence_length = 64
network_input = []

# also important for random sequence
for i in range(0, len(notes) - sequence_length):
    sequence_input = notes[i:i + sequence_length]
    sequence_output = notes[i + sequence_length]
    network_input.append([notes_in_int[n] for n in sequence_input])

number_of_patterns = len(network_input)

normalized_input = np.reshape(network_input, (number_of_patterns, sequence_length, 1))
normalized_input = normalized_input / float(number_of_sounds)

model = tf.keras.models.load_model(path_to_model, compile=False)  # loading model
opt = tf.compat.v1.train.RMSPropOptimizer(
    0.002)  # not used, only for model to compile

model.compile(loss='categorical_crossentropy', optimizer=opt)

# decoder from int to natural representation
notes_in_notes = dict((i, n) for i, n in enumerate(sounds_names))

# choose random start sequence
start = np.random.randint(0, len(network_input))
initial_pattern = network_input[start]  # TODO fix this idea with random pattern

output = []

# actual notes generation
for note_index in range(500):  # TODO uzmiennic
    input_pattern = np.reshape(initial_pattern, (1, len(initial_pattern), 1))  # preparing input for model
    input_pattern = input_pattern / float(number_of_sounds)  # normalization

    output_vector = model.predict(input_pattern,
                                  verbose=0)  # predicting

    # picking best note
    best_note_index = np.argmax(output_vector)
    best = notes_in_notes[best_note_index]  # avoiding strange behavior
    output.append(best)

    # adding predicted note to pattern we use for prediction
    initial_pattern.append(best_note_index)
    # transform onr to right, discard first note from pattern and add best
    initial_pattern = initial_pattern[1:len(initial_pattern)]


offset_progression = [0.5, 0.5, 0.5, 1.0, 1.5]
rhythmic_values = [0.0, 0.0, 0.5, 1.0, 1.5, 2.0]

offsets = []
rhythm = [] 

while len(offsets) < 501: 
    sequence_length = np.random.randint(2, 6)  
    repetition_number = np.random.randint(1, 5) 
    offset_sequence = []  
    rhythmic_sequence = []  

    for j in range(0, sequence_length):
        offset_sequence.append(offset_progression[np.random.randint(0, len(offset_progression))])
        rhythmic_sequence.append(
            offset_sequence[-1] + rhythmic_values[np.random.randint(0, len(rhythmic_values))])

    for j in range(0, repetition_number):
        offsets += offset_sequence
        rhythm += rhythmic_sequence

offset = 0 
counter = 0  
partition = []  
for initial_pattern in output:
    d = duration.Duration()  
    d.quarterLength = rhythm[counter]  

    if ('.' in initial_pattern) or initial_pattern.isdigit():
        partials_sounds = list(map(int, initial_pattern.split('.')))
        notes_in_chord = []

        for n in partials_sounds:
            current_note = note.Note(n) 
            current_note.storedInstrument = instrument.Piano()  
            notes_in_chord.append(current_note)

        current_chord = chord.Chord(notes_in_chord) 

        current_chord.offset = offset 
        current_chord.duration = d 
        partition.append(current_chord)  

    else:
        current_note = note.Note(initial_pattern)  
        current_note.offset = offset  
        current_note.duration = d  
        current_note.storedInstrument = instrument.Piano()  
        partition.append(current_note)  

    offset += offsets[counter]  
    counter += 1

midi_stream = stream.Stream(partition)
midi_stream.write('midi', fp=output_file)
