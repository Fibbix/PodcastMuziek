from engine import *

TITLE = "Stadionorgel + handclaps"
DESCRIPTION = (
    "Na het fluitsignaal vallen stampende voeten en handclaps in, zoals op een tribune. Een stadionorgel "
    "(Hammond-achtig, met draaiende luidspreker) speelt een opgewekte, pakkende melodie, met tamboerijn en een "
    "getokkelde bas eronder. Energiek en nostalgisch voetbal.\nAkkoorden C – Am – F – G – C, 112 BPM."
)

BPM = 112
T0 = 2.4
LENGTH = 10.0

CHORDS = [(0, ['C4', 'E4', 'G4']), (2, ['A3', 'C4', 'E4']), (4, ['F3', 'A3', 'C4']), (6, ['G3', 'B3', 'D4'])]
FINAL = ['C4', 'E4', 'G4']
BASS = ['C2', 'A1', 'F1', 'G1']
MELODY = [
    (0, 'C5', 0.5), (0.5, 'E5', 0.5), (1, 'G5', 1),
    (2, 'A5', 0.5), (2.5, 'G5', 0.5), (3, 'E5', 1),
    (4, 'F5', 0.5), (4.5, 'A5', 0.5), (5, 'G5', 0.5), (5.5, 'F5', 0.5),
    (6, 'E5', 0.5), (6.5, 'D5', 0.5), (7, 'B4', 0.5), (7.5, 'D5', 0.5),
    (8, 'C5', 3),
]


def stadium(s):
    seed(1000 + ord('b'))  # exact dezelfde opening als optie A
    dur_c = 6.5
    t = tvec(dur_c)
    ex = 0.5 + 0.45 * np.exp(-((t - 2.6) / 0.8) ** 2)
    c = fade(crowd(dur_c, excitement=ex), 0.3, 0)
    c = fade_away(c, start=2.4, dur=3.8, cutoff=400)
    s.add(c, at=0, gain=-1)
    s.add(reverb(final_whistle(long=0.8, gap=0.75), decay=2.0, mix=0.35), at=0.15, gain=-14, pan=0.15)
    seed(2000 + ord('b'))


def render():
    s = Track(bpm=BPM)
    at = lambda beat: T0 + s.b(humanize(beat, 0.008, BPM))  # noqa: E731
    exact = lambda beat: T0 + s.b(beat)  # noqa: E731
    stadium(s)

    # --- tribune-ritme: stamp op elke tel, handclap op 2 en 4, tamboerijn op de 'en'
    p = Track(bpm=BPM)
    for k in range(8):
        p.add(stomp(4), at=at(k), gain=-4 + vel(1))
        if k % 2 == 1:
            p.add(group_clap(6), at=at(k), gain=-5 + vel(1), pan=0.1)
        p.add(tambourine(0.12), at=at(k + 0.5), gain=-17 + vel(2), pan=0.45)
    p.add(stomp(5), at=exact(8), gain=-3)
    p.add(group_clap(7), at=exact(8), gain=-4)
    p.add(tambourine(0.4, shake=0.05), at=exact(8), gain=-14, pan=0.45)
    s.add(reverb(p.render(), decay=1.6, mix=0.25), gain=0)

    # --- getokkelde bas: grondtoon, octaaf erboven op de 'en' van 2
    for i, root in enumerate(BASS):
        s.add(upright_bass(root, s.b(0.9), bright=0.45), at=at(i * 2), gain=-6 + vel(1))
        s.add(upright_bass(transpose(root, 12), s.b(0.4), bright=0.45), at=at(i * 2 + 1.5), gain=-9 + vel(1))
    s.add(upright_bass('C2', s.b(3), bright=0.4, release=0.5), at=exact(8), gain=-6)

    # --- orgel: akkoorden (zacht, laag register) + melodie (helder register)
    o = Track(bpm=BPM)
    for beat, notes in CHORDS:
        o.add(organ(notes, s.b(1.9), drawbars=(0, 0, 8, 6, 0, 0, 0, 0, 0), leslie='slow'), at=exact(beat), gain=-11)
    o.add(organ(FINAL, s.b(3.5), drawbars=(0, 0, 8, 6, 0, 0, 0, 0, 0), leslie='fast', release=0.6), at=exact(8), gain=-10)
    for beat, note, length in MELODY:
        last = beat == 8
        o.add(organ(note, s.b(length) * (1.0 if last else 0.85), drawbars=(0, 0, 8, 8, 6, 0, 0, 0, 4),
                    leslie='fast', release=0.6 if last else 0.06), at=at(beat), gain=-2 + (0 if last else vel(1)))
    s.add(reverb(o.render(), decay=1.8, mix=0.22), gain=0)

    return finalize(s.render(length=LENGTH)[:ns(LENGTH)], fade_out=1.4, loud=2.0, trim=False)
