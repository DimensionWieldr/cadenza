import cadenza_beat_tracker
import cadenza_transformer
import basic_pitch_note_tracker
import pretty_midi

# TODO beats_per_bar needs to be entered by user? and some values are still hardcoded
# TODO can we make the alg flow more efficient? better?

path = "despa.wav"
beats_per_bar = 4
resolution = 4

bpm = cadenza_beat_tracker.getBPM(path)
seconds_per_beat = 60.0 / bpm
downbeats = cadenza_beat_tracker.getBeats(path, beats_per_bar)
beat_times = [t[0] for t in downbeats]
note_events = basic_pitch_note_tracker.getNotes(path)
# print(bpm, downbeats)
# print(note_events)
# quit()

# basic-pitch parameters
    # onset_threshold = 0.5 # Default: 0.5
    # frame_threshold = 0.3 # Default: 0.3
    # minimum_note_length = 100 # Default: 100 ms

note_beats = []
for start_sec, end_sec, pitch, confidence, activations in note_events:
    beat_start = cadenza_transformer.seconds_to_beat(start_sec, beat_times)
    beat_end = cadenza_transformer.seconds_to_beat(end_sec, beat_times)
    note_beats.append((beat_start, beat_end, pitch, confidence))

# print(note_beats)
# quit()

# Create a PrettyMIDI object and an instrument
midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
instrument = pretty_midi.Instrument(program=0)  # Acoustic Grand Piano

for beat_start, beat_end, pitch, confidence in note_beats:
    start_time = beat_start * seconds_per_beat
    end_time = beat_end * seconds_per_beat
    note = pretty_midi.Note(
        velocity=int(confidence * 127),
        pitch=int(pitch),
        start=start_time,
        end=end_time
    )
    instrument.notes.append(note)

midi.instruments.append(instrument)

# Write to file
midi.write("expressive_output.mid")

quantized_path = cadenza_transformer.quantizeMIDI("expressive_output.mid", bpm, resolution)
cadenza_transformer.master(quantized_path, resolution)