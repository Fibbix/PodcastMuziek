from engine import *

TITLE = "Zachte gitaar, nieuw deuntje"
DESCRIPTION = (
    "Nieuwe melodie op een zachte, getokkelde gitaar (fingerpicking, warm en donker van klank, geen geslagen "
    "akkoorden). Een tweede gitaar speelt de melodie, met een ronde subbas en de zachte hartslag-kick eronder.\n"
    "Akkoorden Am – Em – F – G – Am, 100 BPM."
)

BPM = 100
T0 = 2.4
LENGTH = 10.0

SHAPES = [['A2', 'E3', 'A3', 'C4'], ['E2', 'B2', 'E3', 'G3'], ['F2', 'C3', 'F3', 'A3'], ['G2', 'D3', 'G3', 'B3']]
BASS = ['A1', 'E1', 'F1', 'G1']
FINAL = ['A2', 'E3', 'A3', 'C4', 'E4']
MELODY = [
    (0, 'C5', 0.5), (0.5, 'B4', 0.5), (1, 'A4', 1),
    (2, 'G4', 0.5), (2.5, 'A4', 0.5), (3, 'B4', 1),
    (4, 'C5', 0.5), (4.5, 'D5', 0.5), (5, 'E5', 1),
    (6, 'D5', 1), (7, 'B4', 1),
    (8, 'A4', 4),
]


def stadium(s):
    dur_c = 6.5
    t = tvec(dur_c)
    ex = 0.5 + 0.45 * np.exp(-((t - 2.6) / 0.8) ** 2)
    c = fade(crowd(dur_c, excitement=ex), 0.3, 0)
    c = fade_away(c, start=2.4, dur=3.8, cutoff=400)
    s.add(c, at=0, gain=-4)
    s.add(reverb(final_whistle(long=0.9, gap=0.45), decay=2.0, mix=0.35), at=0.5, gain=-9, pan=0.15)


def render():
    s = Track(bpm=BPM)
    at = lambda beat: T0 + s.b(beat)  # noqa: E731
    stadium(s)

    # fingerpicking: bas, midden, hoog, midden (achtsten)
    g = Track(bpm=BPM)
    for i, shape in enumerate(SHAPES):
        for e, idx in enumerate([0, 1, 3, 2]):
            g.add(guitar(shape[idx], s.b(1.5), bright=0.2, decay=2.5), at=at(i * 2 + e * 0.5),
                  gain=-2 if e == 0 else -6, pan=-0.3 + 0.15 * idx)
    for k, note in enumerate(FINAL):  # langzaam uitgerold slotakkoord
        g.add(guitar(note, s.b(4), bright=0.2, decay=5.0, release=1.0), at=at(8 + k * 0.12), gain=-4,
              pan=-0.3 + 0.12 * k)
    gb = lowpass(g.render(), 3200)
    s.add(reverb(gb, decay=1.8, mix=0.25), gain=-2)

    # melodiegitaar, ook zacht
    m = Track(bpm=BPM)
    for beat, note, length in MELODY:
        m.add(guitar(note, s.b(length) + 0.3, bright=0.3, decay=4.0 if beat == 8 else 2.5,
                     release=0.8 if beat == 8 else 0.1), at=at(beat), pan=0.2)
    s.add(reverb(lowpass(m.render(), 4000), decay=2.0, mix=0.25), gain=-1)

    # subbas + zachte kick
    for i, root in enumerate(BASS):
        s.add(sub(root, s.b(1.8), release=0.2), at=at(i * 2), gain=-10)
    s.add(sub('A1', s.b(3), release=0.8), at=at(8), gain=-10)
    for k in range(9):
        s.add(lowpass(kick(punch=0.5, decay=0.3, tone=50, click=0.05), 900), at=at(k),
              gain=-12 if k % 2 == 0 else -15)

    return finalize(s.render(length=LENGTH)[:ns(LENGTH)], fade_out=1.6, loud=2.0, trim=False)
