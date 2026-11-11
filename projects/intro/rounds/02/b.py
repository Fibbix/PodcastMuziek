from engine import *

TITLE = "Fluitsignaal: elektrische piano"
DESCRIPTION = (
    "Zelfde opening (fluitsignaal, publiek sterft weg), maar de muziek is een moderne, heldere elektrische piano "
    "met een zachte pad en subbas. De akkoorden worden licht gesyncopeerd aangeslagen, met een heel zachte shaker "
    "op de achtergrond. Middelste stap qua energie."
)

BPM = 92
T0 = 2.4
LENGTH = 10.0

CHORDS = [  # (beat, noten)
    (0, ['A3', 'C4', 'E4', 'G4']),      # Am7
    (2, ['F3', 'A3', 'C4', 'E4']),      # Fmaj7
    (4, ['C3', 'G3', 'D4', 'E4']),      # Cadd9
    (6, ['G3', 'B3', 'D4']),            # G
]
FINAL = ['A3', 'C4', 'E4', 'G4', 'B4']  # Am9
BASS = ['A1', 'F1', 'C2', 'G1']
MELODY = [
    (0, 'E5', 1), (1, 'D5', 0.5), (1.5, 'C5', 0.5),
    (2, 'C5', 1), (3, 'A4', 1),
    (4, 'G4', 0.5), (4.5, 'A4', 0.5), (5, 'C5', 1),
    (6, 'D5', 1.5), (7.5, 'B4', 0.5),
    (8, 'A4', 3),
]


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

    m = Track(bpm=BPM)
    for i, (beat, notes) in enumerate(CHORDS):
        m.add(poly(keys, notes, s.b(1.4), bright=0.45, release=0.4), at=at(beat), gain=-4, pan=-0.1)
        m.add(poly(keys, notes, s.b(0.4), bright=0.35, release=0.3), at=at(beat + 1.5), gain=-9, pan=-0.1)
        m.add(soft_pad(notes, s.b(2), attack=0.3, release=0.8, bright=0.35), at=at(beat), gain=-15)
        m.add(sub(BASS[i], s.b(1.8), release=0.2), at=at(beat), gain=-8)
    m.add(poly(keys, FINAL, s.b(3), bright=0.4, release=1.2, decay=2.5), at=at(8), gain=-4, pan=-0.1)
    m.add(soft_pad(FINAL, s.b(3), attack=0.3, release=1.5, bright=0.35), at=at(8), gain=-15)
    m.add(sub('A1', s.b(3), release=0.8), at=at(8), gain=-8)
    for beat, note, length in MELODY:
        m.add(keys(note, s.b(length), bright=0.65, release=0.5), at=at(beat), gain=-1, pan=0.15)
    for k in range(16):
        m.add(shaker(), at=at(k * 0.5), gain=-22 if k % 2 else -26, pan=0.4)
    s.add(reverb(m.render(), decay=1.8, mix=0.22))

    return finalize(s.render()[:ns(LENGTH)], fade_out=1.2, loud=1.5)
