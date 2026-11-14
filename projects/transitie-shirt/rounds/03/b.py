from engine import *

TITLE = "Zacht gefloten, Em – C – G – D"
DESCRIPTION = (
    "Iets vlotter (108 BPM) met een andere akkoordenreeks: Em – C – G – D, die begint met een vleugje weemoed en "
    "opklaart naar de landing op G. Zacht, rond gefloten melodie (zoals in de intro), e-piano in syncopisch ritme, "
    "bas, klappen en tamboerijn op de 'en'. ~4,3 s."
)

BPM = 108
T0 = 0.6
OVERALL = -7.0
FADE_IN = 0.5
MELODY = [(0, 'B5'), (0.5, 'G5'), (1, 'C6'), (1.5, 'E6'), (2, 'D6'), (2.5, 'B5'), (3, 'A5'), (3.5, 'F#5')]
LANDING = 'G5'
CHORDS = [(0, ['E3', 'G3', 'B3'], 'E2'), (1, ['C4', 'E4', 'G4'], 'C2'), (2, ['G3', 'B3', 'D4'], 'G2'),
          (3, ['D4', 'F#4', 'A4'], 'D2')]
W_BREATH = 0.022
W_LOWPASS = 2400
W_REVERB = 0.34


def render():
    s = Track(bpm=BPM)
    at = lambda b: T0 + s.b(humanize(b, 0.006, BPM))  # noqa: E731
    exact = lambda b: T0 + s.b(b)  # noqa: E731
    total = exact(4) + 1.5

    # aanloop: bas + shaker
    s.add(upright_bass('B1', s.b(0.4), bright=0.45), at=at(-1), gain=-9)
    s.add(upright_bass('D2', s.b(0.4), bright=0.45), at=at(-0.5), gain=-9)
    for h in range(2):
        s.add(shaker(0.07), at=at(-1 + h * 0.5), gain=-25 + h * 2, pan=0.4)

    e = Track(bpm=BPM)
    for b, notes, root in CHORDS:
        e.add(poly(keys, notes, s.b(0.4), bright=0.5, release=0.12), at=at(b), gain=-8 + vel(1), pan=-0.2)
        e.add(poly(keys, notes, s.b(0.2), bright=0.5, release=0.08), at=at(b + 0.75), gain=-11 + vel(1), pan=-0.2)
        s.add(upright_bass(root, s.b(0.6), bright=0.45), at=at(b), gain=-6 + vel(1))
        s.add(tambourine(0.1), at=at(b + 0.5), gain=-22 + vel(1.5), pan=0.35)
    for b in (1, 3):
        s.add(reverb(group_clap(4), 1.0, 0.2), at=at(b), gain=-10, pan=0.15)

    # zacht gefloten melodie met lange landingsnoot
    ev = []
    for i, (b, n) in enumerate(MELODY):
        nxt = MELODY[i + 1][0] if i + 1 < len(MELODY) else 4
        ev.append((exact(b), n, s.b(nxt - b) * 0.9))
    ev.append((exact(4), LANDING, s.b(2.2)))
    w = whistling(ev, vib=0.3, breath=W_BREATH, glide=0.03)
    s.add(reverb(lowpass(w, W_LOWPASS), decay=1.8, mix=W_REVERB), at=0, gain=-12, pan=0.1)

    # landing op G (tel 4)
    e.add(poly(keys, ['G3', 'B3', 'D4', 'G4'], s.b(2.4), bright=0.45, release=1.0, decay=2.0), at=exact(4),
          gain=-6, pan=-0.2)
    s.add(upright_bass('G1', s.b(2), bright=0.4, release=0.5), at=exact(4), gain=-5)
    s.add(reverb(group_clap(5), 1.2, 0.25), at=exact(4), gain=-8, pan=0.1)
    s.add(reverb(e.render(), decay=1.5, mix=0.2))

    x = s.render(length=total)[:ns(total)]
    x = finalize(x, loud=2.0, trim=False)
    return gain(fade(x, FADE_IN, 1.0), OVERALL)
