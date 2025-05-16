import cadenza_beat_tracker
import cadenza_transformer
import subprocess

# TODO test a song with a proper pickup (mainly want to see if beats are mapped correctly)
# TODO beats_per_bar needs to be entered by user? and some values are still hardcoded like the quantizeMIDI resolution parameter
# TODO BIG CHANGE: need to use downbeat information the whole way through, that way we can process non-constant tempos
    # madmom can handle small fluctuations in tempo (but NOT changing time signatures)
    # right now we're only using the first beat of the beats list, we should capitalize on the entire thing, by accessing the basic_pitch
    # midi file with timestamps generated in beats list; this would also deprecate the need for silence padding or cutting of the audio file
    # check GPT for method, quantize after that :)

path = "despa.wav"
beats_per_bar = 4
resolution = 4

bpm = cadenza_beat_tracker.getBPM(path)
beats = cadenza_beat_tracker.getBeats(path, beats_per_bar)
# print(bpm, beats)
# quit()

# do some math, call silence, call basic-pitch, call quantize
path_with_edit = ""
seconds_per_beat = 60.0 / bpm
first_beat = beats[0]
offset = first_beat[1] - 1
if offset == 0: offset = beats_per_bar # wrap around
offset *= seconds_per_beat
if first_beat[0] < offset:
    path_with_edit = cadenza_transformer.prependSilence(path, 1000*(offset - first_beat[0]))
elif first_beat[0] > offset:
    path_with_edit = cadenza_transformer.trimAudio(path, 1000*(first_beat[0] - offset))
else:
    path_with_edit = path

# basic-pitch parameters
    # onset_threshold = 0.5 # Default: 0.5
    # frame_threshold = 0.3 # Default: 0.3
    # minimum_note_length = 100 # Default: 100 ms
cmd = ["basic-pitch", "./", path_with_edit, "--midi-tempo", str(bpm)]
subprocess.run(cmd, check=True)
# quit()
name, _ = path_with_edit.rsplit(".", 1)
midi_path = f"{name}_basic_pitch.mid"
quantized_path = cadenza_transformer.quantizeMIDI(midi_path, bpm, resolution)
cadenza_transformer.master(quantized_path, resolution)