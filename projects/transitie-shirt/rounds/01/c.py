from engine import *

TITLE = "Gevonden!"
DESCRIPTION = (
    "Kort rommelen, dan een snel e-piano-loopje omhoog (G – B – D – G – B) als 'onthulling', en op de landing "
    "een kort juichend stadionpubliek dat vanzelf wegsterft (vóór de uitfade) — het shirt is terug! "
    "Verbindt de rubriek met het stadion uit de intro. 104 BPM, ~3,6 s."
)

BPM = 104
T0 = 0.6
OVERALL = -8.2


def render():
    s = Track(bpm=BPM)
    at = lambda b: T0 + s.b(humanize(b, 0.005, BPM))  # noqa: E731
    exact = lambda b: T0 + s.b(b)  # noqa: E731
    total = exact(2) + 1.9

    s.add(reverb(rummage(0.7, 16), 0.7, 0.15), at=0.0, gain=11, pan=-0.2)
    s.add(reverb(hanger_click(0.8), 0.8, 0.2), at=0.75, gain=-2, pan=0.3)

    # onthulling: loopje omhoog op D -> G
    e = Track(bpm=BPM)
    run = [(0, 'G4'), (0.25, 'B4'), (0.5, 'D5'), (0.75, 'G5'), (1.0, 'B5')]
    for b, n in run:
        e.add(keys(n, s.b(0.3), bright=0.55, release=0.1), at=at(b), gain=-10 + b * 2, pan=0.1)
    e.add(poly(keys, ['D4', 'F#4', 'A4'], s.b(0.9), bright=0.5, release=0.15), at=at(0), gain=-10, pan=-0.2)
    s.add(upright_bass('D2', s.b(0.9), bright=0.45), at=at(0), gain=-7)
    for h in range(4):
        s.add(shaker(0.05), at=at(h * 0.5), gain=-26 + h * 1.5, pan=0.4)

    # landing op G (tel 2) + kort gejuich dat binnen ~1,4 s uitsterft
    e.add(poly(keys, ['G3', 'B3', 'D4', 'G4'], s.b(2.6), bright=0.5, release=1.0, decay=2.0), at=exact(2),
          gain=-6, pan=-0.2)
    e.add(keys('G5', s.b(2.2), bright=0.55, release=1.0, decay=2.0), at=exact(2), gain=-9, pan=0.1)
    s.add(upright_bass('G1', s.b(2.2), bright=0.4, release=0.5), at=exact(2), gain=-5)
    s.add(reverb(group_clap(6), 1.2, 0.25), at=exact(2), gain=-7, pan=0.1)
    cd = 1.6
    t = tvec(cd)
    cheer = crowd(cd, excitement=np.clip(1.0 - t / 1.2, 0, 1) * 0.9)
    env = np.minimum(t / 0.06, 1) * np.clip(1 - (t - 0.3) / 1.1, 0, 1) ** 2
    s.add(cheer * env[:, None], at=exact(2) - 0.03, gain=-17)
    s.add(reverb(e.render(), decay=1.5, mix=0.2))

    x = s.render(length=total)[:ns(total)]
    x = finalize(x, loud=2.0, trim=False)
    return gain(fade(x, 0.02, 0.9), OVERALL)
