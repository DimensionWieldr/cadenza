from music21 import converter, tempo, note, chord, stream, meter
import math
import numpy as np

# TODO clean up functions

# Maps audio time in seconds to beat index using interpolation
def seconds_to_beat(time_sec, beat_times):
    if time_sec <= beat_times[0]:
        return 0.0
    if time_sec >= beat_times[-1]:
        return len(beat_times)
    idx = np.searchsorted(beat_times, time_sec) - 1
    t0 = beat_times[idx]
    t1 = beat_times[idx + 1]
    frac = (time_sec - t0) / (t1 - t0)
    return idx + frac

# Creates a new .mid file, quantized to the resolution
def quantizeMIDI(path, bpm, resolution):
    score = converter.parse(path)
    score.insert(0, tempo.MetronomeMark(number=bpm))
    quantized_score = score.quantize((resolution,),True,True,False,True)
    name, _ = path.rsplit(".", 1)
    quantized_path = f"{name}_quantized.mid"
    quantized_score.write("midi", fp=quantized_path)
    return quantized_path

def master(path, resolution):
    # TODO Add time and key signature, which should be gotten from the full song
    # Choose correct clef(s)/tabs based on instrument type
    # What are we going to do about durations? probably just ignore info, don't even save it
    # We eventually need to deal with tuplets... wonder how that's gonna pan out

    # Load the MIDI file
    score = converter.parse(path)

    # Create a list to hold note info
    notes_data = []

    # Iterate through all elements in all parts
    for element in score.recurse():
        if isinstance(element, note.Note):
            notes_data.append({
                "pitches": [element.pitch.nameWithOctave],
                "start": element.getOffsetInHierarchy(score),
                # "durations": [float(element.quarterLength)],
                # "velocities": [element.volume.velocity]
            })
        elif isinstance(element, chord.Chord):
            pitches = [n.pitch.nameWithOctave for n in element.notes]
            # durations = [float(n.quarterLength) for n in element.notes]
            # velocities = [n.volume.velocity for n in element.notes]
            notes_data.append({
                "pitches": pitches,
                "start": element.getOffsetInHierarchy(score),
                # "durations": durations,
                # "velocities": velocities
            })
    notes_data.sort(key=lambda x: x['start'])

    # CONFIRM NATURE OF INPUT
    # print(notes_data)
    # print(len(notes_data))
    # quit()

    score_out = stream.Score()
    part = stream.Part()

    time_signature = "4/4"
    ts = meter.TimeSignature(time_signature)
    measure_length = ts.barDuration.quarterLength

    event_index = 0
    event = notes_data[event_index]

    while event_index < len(notes_data):
        measure_number = math.floor(event["start"] / measure_length)
        current_measure = stream.Measure(number=measure_number+1)
        event_offset = event["start"] - (measure_length * measure_number)

        while event_offset < measure_length:
            pitches = event["pitches"]
            # durations = event["durations"]
            # velocities = event["velocities"]

            if len(pitches) == 1:
                n = note.Note(pitches[0])
                # n.quarterLength = durations[0]
                n.quarterLength = 1.0 / resolution
                # if velocities[0] is not None:
                #     n.volume.velocity = velocities[0]
                current_measure.insertIntoNoteOrChord(event_offset, n)
            else:
                ch = chord.Chord(pitches)
                # ch.quarterLength = min(durations)
                ch.quarterLength = 1.0 / resolution
                # if all(v is not None for v in velocities):
                #     ch.volume.velocity = int(sum(velocities) / len(velocities))
                current_measure.insertIntoNoteOrChord(event_offset, ch)
            
            event_index += 1
            if event_index >= len(notes_data): break
            event = notes_data[event_index]
            event_offset = event["start"] - (measure_length * measure_number)
        
        part.append(current_measure)

    def extend_notes_and_fill_start(measure):
        """
        Modifies the given measure by:
        - Inserting a rest at the start if the first note doesn't begin at offset 0.0
        - Extending each note to the start of the next note or the end of the measure
        """
        elements = list(measure.notes)
        
        # Skip if no notes
        if not elements:
            return

        # Step 1: Add rest at the beginning if first note starts late
        first_note = elements[0]
        if first_note.offset > 0.0:
            start_rest = note.Rest(quarterLength=first_note.offset)
            measure.insert(0.0, start_rest)

        # Step 2: Extend each note to next note or end of measure
        for i, n in enumerate(elements):
            start = n.offset
            if i < len(elements) - 1:
                end = elements[i + 1].offset
            else:
                end = measure_length

            new_duration = end - start
            if new_duration > n.quarterLength:
                n.quarterLength = new_duration

    for m in part.getElementsByClass('Measure'):
        extend_notes_and_fill_start(m)

    score_out.append(part)
    # score_out.show()
    score_out.write('musicxml', fp='output.xml')