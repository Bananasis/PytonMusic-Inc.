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

# W tym skrypcie rytm generowany jest półlosowo - dlaczego "pół", o tym poniżej.
# Rytm (choć to, co będziemy generować, do końca rytmem nie jest, to duże uproszczenie) składa się z dwóch elementów:
# - momentu rozpoczęcia trwania nuty na skali czasu (offset) - tutaj losować będziemy postęp offsetu, tzn. o ile później od rozpoczęcia poprzedniego dźwięku/akordu ma się rozpocząć kolejny,
# długości trwania dźwięku - czyli przez jaki czas od rozpoczęcia swego trwania dźwięk będzie grany.
# Musimy rozróżnić offset od długości trwania dźwięku z jednego prostego powodu - w muzyce rzadko kiedy jest tak, że dźwięk zawsze kończy się z momentem rozpoczęcia kolejnego - często jest nawet tak, że kilka dźwięków jest granych na tle ciągle trwającego w tle akordu.
# Żeby jednak nasz rytm miał muzyczny sens, musimy zwrócić uwagę na przynajmniej kilka spraw:
# - długość trwania dźwięku ani zależności czasowe pomiędzy kolejnymi dźwiękami nie mogą być losowane z ciągłego przedziału od zera do nieskończoności - prowadziłoby to do przedziwnych efektów, jak na przykład kilkuminutowa przerwa między kolejnymi dźwiękami, gdzie pierwszy trwa 14 milisekund, a kolejny 3 minuty - dlatego też definiujemy zbiór dopuszczalnych, dyskretnych wartości;
# - zazwyczaj pewne wartości rytmiczne występują częściej niż inne - np. możemy się spodziewać, że ćwierćnuta będzie w utworze występować częściej niż cała nuta z kropką - dlatego też musimy jeszcze trochę zmniejszyć losowość spowodować, by rzeczywiście pewne wartości występowały częściej niż inne - stąd w naszych zbiorach dopuszczalne wartości nie będą występwały z jednakowym prawdopodobieństwem, niektóre będziemy faworyzować poprzez powtórzenie ich na liście;
# - w większości przypadków struktura rytmiczna utworu opiera się na tym, że pewne sekwencje rytmiczne się powtarzają - ale nie każda i nie zawsze - więc powinniśmy po raz kolejny zmniejszyć poziom losowości, tym razem poprzez losowanie powtórzeń sekwencji.

offset_progression = [0.5, 0.5, 0.5, 1.0, 1.5]  # dopuszczalne wartości postępu offsetu
# dopuszczalne wartości rytmiczne (jednostką bazową jest ćwierćnuta) -
# przy czym do każdej z nich należy dodać jeszcze różnicę offsetu,
# a więc jest to w istocie zbiór dopuszczalnych "przedłużeń" dźwięku -
# 0 NIE oznacza, że dźwięk zostanie pominięty
rhythmic_values = [0.0, 0.0, 0.5, 1.0, 1.5, 2.0]

offsets = []  # lista kolejnych wartości postępu offsetu
rhythm = []  # lista kolejnych wartości rytmicznych w utworze (długości trwania dźwięków)

while len(offsets) < 501:  # generujemy 501 wartości postępu offsetu i wartości rytmicznych
    sequence_length = np.random.randint(2, 6)  # losujemy, ile dźwięków/akordów wystąpi w naszej sekwencji
    repetition_number = np.random.randint(1, 5)  # i ile razy sekwencja zostanie powtórzona
    offset_sequence = []  # kolejne postępy offsetu w sekwencji
    rhythmic_sequence = []  # kolejne długości trwania dźwięków w sekwencji - nazwa `sekwencja_rytmiczna` może być nieco myląca (bo w istocie offset też się do rytmu zalicza, i to bardzo), ale lepszej nie wymyśliłem

    for j in range(0, sequence_length):
        # do sekwencji offsetów dodajemy wylosowaną z listy `postęp_offsetów` wartość
        offset_sequence.append(offset_progression[np.random.randint(0, len(offset_progression))])
        # do sekwencji długości trwania dźwięków dodajemy ostatnią (przed chwilą dodaną) wartość postępu offsetu (a więc co najmniej ósemkę) + wylosowaną dodatkową długość trwania dźwięku
        rhythmic_sequence.append(
            offset_sequence[-1] + rhythmic_values[np.random.randint(0, len(rhythmic_values))])

    # obydwie sekwencje powtarzamy tyle razy, ile wylosowaliśmy
    for j in range(0, repetition_number):
        offsets += offset_sequence
        rhythm += rhythmic_sequence

# tu zaczyna się generowanie pliku MIDI na podstawie tego, co zwróciła nam sieć
offset = 0  # offset będziemy zwiększać o kolejne wylosowane wartości - startujemy od zera, bo zakładamy, że nie ma pauzy na początku (przynajmniej w prostej wersji)
counter = 0  # licznik będzie służył do pobierania wylosowanych wartości rytmicznych i postępu offsetu
partition = []  # tu będziemy przechowywać wygenerowane dźwięki
for initial_pattern in output:
    d = duration.Duration()  # tworzymy obiekt klasy Duration, dzięki któremu będziemy mogli ustalić długość trwania dźwięku/akordu samotności
    d.quarterLength = rhythm[
        counter]  # pobieramy koleją wylosowaną długość trwania dźwięku/akordu (gdzie jednostką czasu jest liczba ćwierćnut)

    # jeśli wzorzec jest akordem (zawiera kropkę lub jest liczbą, zgodnie z tym co zaimplementowaliśmy przy trenowaniu sieci), musimy stworzyć akord
    if ('.' in initial_pattern) or initial_pattern.isdigit():
        partials_sounds = list(map(int, initial_pattern.split('.')))
        notes_in_chord = []
        # current_note = None
        for n in partials_sounds:
            current_note = note.Note(n)  # tworzymy obiekt nuta
            current_note.storedInstrument = instrument.Piano()  # wybieramy fortepian jako instrument
            notes_in_chord.append(current_note)

        current_chord = chord.Chord(notes_in_chord)  # z nut składowych tworzymy akord

        current_chord.offset = offset  # ustalamy moment rozpoczęcia trwania akordu
        # TODO  current_note.duration = d  # ustalamy długość trwania akordu
        current_chord.duration = d  # ustalamy długość trwania akordu
        partition.append(current_chord)  # dodajemy akord do partytury
    # jeśli jest pojedynczą nutą
    else:
        current_note = note.Note(initial_pattern)  # tworzymy obiekt nuty
        current_note.offset = offset  # ustalamy moment rozpoczęcia trwania nuty
        current_note.duration = d  # ustalamy długość trwania dźwięku
        current_note.storedInstrument = instrument.Piano()  # wybieramy fortepian jako instrument
        partition.append(current_note)  # dodajemy utworzony dźwięk do partytury

    offset += offsets[counter]  # zwiększamy offset - tak by kolejna nuta nie nakładała się na obecną
    counter += 1

# z utworzonej partytury musimi utworzyć obiekt klasy Strea, by móc zapisać ją jako plik MIDI
midi_stream = stream.Stream(partition)

# zapisujemy wygenerowaną partyturę do pliku MIDI
midi_stream.write('midi', fp=output_file)
