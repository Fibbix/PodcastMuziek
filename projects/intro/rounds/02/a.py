from engine import *

TITLE = "Fluitsignaal: piano, net iets lichter"
DESCRIPTION = (
    "Dichtst bij de vorige A: fluitsignaal, het publiek juicht en sterft weg, dan solopiano. Het tempo is hoger "
    "(92 BPM) en de akkoorden zijn hoopvoller (Am – F – C – G – Am). Een doorlopende linkerhand geeft wat beweging. "
    "Minst energiek van de drie."
)

BPM = 92
T0 = 2.4      # muziek start
LENGTH = 10.0

MELODY = [
    (0, 'E5', 1), (1, 'D5', 0.5), (1.5, 'C5', 0.5),
    (2, 'C5', 1), (3, 'A4', 1),
    (4, 'G4', 0.5), (4.5, 'A4', 0.5), (5, 'C5', 1),
    (6, 'D5', 1.5), (7.5, 'B4', 0.5),
    (8, 'A4', 3),
]
LEFT = [['A2', 'E3', 'A3', 'E3'], ['F2', 'C3', 'F3', 'C3'], ['C3', 'G3', 'C4', 'G3'], ['G2', 'D3', 'G3', 'D3']]


def stadium(s):
    dur_c = 6.5
    t = tvec(dur_c)
    ex = 0.5 + 0.45 * np.exp(-((t - 2.6) / 0.8) ** 2)
    c = fade(crowd(dur_c, excitement=ex), 0.3, 0)
    c = fade_away(c, start=2.4, dur=3.8, cutoff=400)
    s.add(c, at=0, gain=-1)
    s.add(reverb(final_whistle(long=0.9, gap=0.45), decay=2.0, mix=0.35), at=0.5, gain=-9, pan=0.15)


def render():
    s = Track(bpm=BPM)
    at = lambda beat: T0 + s.b(beat)  # noqa: E731
    stadium(s)

    p = Track(bpm=BPM)
    for beat, note, length in MELODY:
        p.add(piano(note, s.b(length) + 0.2, bright=0.5, release=0.8), at=at(beat), pan=0.1)
    for bar, notes in enumerate(LEFT):
        for i, note in enumerate(notes):
            p.add(piano(note, s.b(1.2), bright=0.3, release=0.6), at=at(bar * 2 + i * 0.5), gain=-8, pan=-0.15)
    for note in ['A2', 'E3', 'A3', 'C4']:
        p.add(piano(note, s.b(3), bright=0.3, release=1.5), at=at(8), gain=-8, pan=-0.15)
    s.add(reverb(p.render(), decay=2.2, mix=0.28, tone=5500))

    return finalize(s.render()[:ns(LENGTH)], fade_out=1.2, loud=1.5)
