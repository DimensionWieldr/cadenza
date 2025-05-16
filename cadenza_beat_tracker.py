from madmom.features.beats import RNNBeatProcessor
from madmom.features.tempo import CombFilterTempoHistogramProcessor, TempoEstimationProcessor
from madmom.features.downbeats import RNNDownBeatProcessor, DBNDownBeatTrackingProcessor
import math

# Returns first entry of first tuple from a list of tuples [bpm, probability]
def getBPM(path):
    act = RNNBeatProcessor()(path)
    histogram_proc = CombFilterTempoHistogramProcessor(min_bpm=40,max_bpm=250,fps=100)
    tempo_proc = TempoEstimationProcessor(fps=100,histogram_processor=histogram_proc)
    tempo = tempo_proc(act)
    return math.ceil(tempo[0][0])

# Returns list of tuples [time, beat_num]
def getBeats(path, beats_per_bar):
    proc = RNNDownBeatProcessor()
    act = proc(path)
    track = DBNDownBeatTrackingProcessor(beats_per_bar=[beats_per_bar], fps=100)
    beats = track(act)
    return beats