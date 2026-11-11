from engine import *

TITLE = "Nieuw deuntje: stijgend (104 BPM)"
DESCRIPTION = (
    "Nieuwe melodie met een opwaartse 'hook' in achtsten (A–C–E omhoog). Voelt vastberaden en vooruitkijkend, "
    "maar nog steeds met een weemoedig randje. Zelfde rustige bezetting en opening.\n"
    "Akkoorden Am – G – F – G – Am, 104 BPM."
)

BPM = 104
T0 = 2.4
LENGTH = 10.0

CHORDS = [(0, ['A3', 'C4', 'E4']), (2, ['G3', 'B3', 'D4']), (4, ['F3', 'A3', 'C4']), (6, ['G3', 'B3', 'D4'])]
BASS = ['A1', 'G1', 'F1', 'G1']
FINAL, FINAL_BASS, FINAL_OCT = ['A3', 'C4', 'E4'], 'A1', 'A3'
MELODY = [
    (0, 'A4', 0.5), (0.5, 'C5', 0.5), (1, 'E5', 1),
    (2, 'D5', 0.5), (2.5, 'B4', 0.5), (3, 'G4', 1),
    (4, 'A4', 0.5), (4.5, 'C5', 0.5), (5, 'F5', 1),
    (6, 'D5', 0.5), (6.5, 'E5', 0.5), (7, 'D5', 0.5), (7.5, 'B4', 0.5),
    (8, 'A4', 4),
]


# ---- gedeelde opbouw (gelijk in a/b/c van deze ronde) ----
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
        m.add(poly(keys, notes, s.b(1.8), bright=0.3, release=0.4), at=at(beat), gain=-6, pan=-0.15)
        m.add(soft_pad(notes, s.b(2), attack=0.05, release=0.6, bright=0.4), at=at(beat), gain=-12)
        m.add(bass(BASS[i], s.b(1.8), shape='triangle', cutoff=300, env=300, sub=0.8), at=at(beat), gain=-8)
    music = m.render(length=LENGTH + 1)
    a, b = ns(T0), ns(at(8))
    pump = np.ones(len(music))
    pump[a:b] = sidechain(np.ones(b - a), BPM, depth=0.35, every=1)
    music = music * pump[:, None]

    f = Track(bpm=BPM)
    f.add(poly(keys, FINAL, s.b(4), bright=0.35, release=1.0, decay=2.0), at=at(8), gain=-6, pan=-0.15)
    f.add(soft_pad(FINAL, s.b(3), attack=0.05, release=1.2, bright=0.35), at=at(8), gain=-13)
    f.add(sub(FINAL_BASS, s.b(3), release=0.8), at=at(8), gain=-8)

    for k in range(9):
        s.add(lowpass(kick(punch=0.5, decay=0.3, tone=50, click=0.05), 900), at=at(k),
              gain=-10 if k % 2 == 0 else -13)

    p = Track(bpm=BPM)
    for beat, note, length in MELODY:
        p.add(piano(note, s.b(length) + 0.2, bright=0.55, release=0.8), at=at(beat), pan=0.1)
    p.add(piano(FINAL_OCT, s.b(4), bright=0.4, release=0.8), at=at(8), gain=-6, pan=0.1)

    s.add(reverb(mix(music, f.render(), p.render()), decay=2.0, mix=0.25))
    return finalize(s.render()[:ns(LENGTH)], fade_out=1.6, loud=1.5)
