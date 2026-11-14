from engine import *

TITLE = "Bladeren in het album"
DESCRIPTION = (
    "Twee keer een bladzijde omslaan (bladeren door de verzameling), dan één maat warme groove zoals bij Pad door "
    "de Stad: G – Em – C – D met e-piano, bas, klappen en shaker, en een e-piano-melodie die oploopt naar de landing "
    "op G. 104 BPM, ~4,2 s."
)

BPM = 104
T0 = 0.6
OVERALL = -7.0
FX = 'pages'      # 'pages' = bladzijdes omslaan, 'crowd' = stadion-herinnering, None = geen effect
FADE_IN = 0.02
MELODY = [(0, 'D5'), (0.5, 'G5'), (1, 'E5'), (1.5, 'B4'), (2, 'C5'), (2.5, 'E5'), (3, 'D5'), (3.5, 'F#5')]
LANDING = 'G5'
CHORDS = [(0, ['G3', 'B3', 'D4'], 'G2'), (1, ['E3', 'G3', 'B3'], 'E2'), (2, ['C4', 'E4', 'G4'], 'C2'),
          (3, ['D4', 'F#4', 'A4'], 'D2')]
PICKUP = False    # halve maat aanloop (bas + shaker) vóór tel 0


def render():
    s = Track(bpm=BPM)
    at = lambda b: T0 + s.b(humanize(b, 0.006, BPM))  # noqa: E731
    exact = lambda b: T0 + s.b(b)  # noqa: E731
    total = exact(4) + 1.45

    if FX == 'pages':
        s.add(reverb(page_turn(0.35), 0.6, 0.12), at=0.0, gain=3, pan=-0.25)
        s.add(reverb(page_turn(0.3, 0.8), 0.6, 0.12), at=0.4, gain=0, pan=0.2)
    elif FX == 'crowd':  # vage herinnering aan een vol stadion, al weg voordat de melodie goed op gang is
        cd = exact(1.5)
        t = tvec(cd)
        env = np.clip(t / 0.4, 0, 1) * np.clip(1 - (t - T0) / (cd - T0), 0, 1) ** 1.5
        c = lowpass(crowd(cd, excitement=0.55), 2500) * env[:, None]
        s.add(reverb(c, 2.0, 0.3), at=0.0, gain=-10)

    if PICKUP:
        s.add(upright_bass('D2', s.b(0.4), bright=0.45), at=at(-1), gain=-9)
        s.add(upright_bass('D2', s.b(0.4), bright=0.45), at=at(-0.5), gain=-8)
        for h in range(2):
            s.add(shaker(0.07), at=at(-1 + h * 0.5), gain=-24 + h * 2, pan=0.4)

    e = Track(bpm=BPM)
    for b, notes, root in CHORDS:
        e.add(poly(keys, notes, s.b(0.45), bright=0.5, release=0.12), at=at(b), gain=-8 + vel(1), pan=-0.2)
        e.add(poly(keys, notes, s.b(0.35), bright=0.5, release=0.1), at=at(b + 0.5), gain=-11 + vel(1), pan=-0.2)
        s.add(upright_bass(root, s.b(0.45), bright=0.45), at=at(b), gain=-6 + vel(1))
        s.add(upright_bass(transpose(root, 12), s.b(0.3), bright=0.45), at=at(b + 0.5), gain=-11 + vel(1))
    for b in (1, 3):
        s.add(reverb(group_clap(4), 1.0, 0.2), at=at(b), gain=-10, pan=0.15)
    for h in range(8):
        s.add(shaker(0.07), at=at(h * 0.5), gain=(-21 if h % 2 else -24) + vel(1.5), pan=0.4)
    for i, (b, n) in enumerate(MELODY):
        nxt = MELODY[i + 1][0] if i + 1 < len(MELODY) else 4
        e.add(keys(n, s.b((nxt - b) * 0.9), bright=0.55, release=0.15), at=at(b), gain=-8 + vel(1), pan=0.1)

    # landing op G (tel 4)
    e.add(poly(keys, ['G3', 'B3', 'D4', 'G4'], s.b(2.4), bright=0.45, release=1.0, decay=2.0), at=exact(4),
          gain=-6, pan=-0.2)
    e.add(keys(LANDING, s.b(2.0), bright=0.5, release=1.0, decay=2.0), at=exact(4), gain=-8, pan=0.1)
    s.add(upright_bass('G1', s.b(2), bright=0.4, release=0.5), at=exact(4), gain=-5)
    s.add(reverb(group_clap(5), 1.2, 0.25), at=exact(4), gain=-8, pan=0.1)
    s.add(reverb(e.render(), decay=1.5, mix=0.2))

    x = s.render(length=total)[:ns(total)]
    x = finalize(x, loud=2.0, trim=False)
    return gain(fade(x, FADE_IN, 1.0), OVERALL)
