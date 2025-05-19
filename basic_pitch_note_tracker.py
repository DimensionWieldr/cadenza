from basic_pitch.inference import predict

# Supports mp3, ogg, wav, flac, m4a
# note_events is a list of tuples: [start_time, end_time, pitch, confidence]
def getNotes(path):
    _, _, note_events = predict(path)
    return note_events
