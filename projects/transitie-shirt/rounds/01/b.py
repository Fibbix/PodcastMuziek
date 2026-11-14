from engine import *

TITLE = "Speurtocht"
DESCRIPTION = (
    "Rommelen in een doos met oude spullen, eronder een 'sluipend' pizzicato-loopje in E-mineur met "
    "vingerknippen (speurend, een beetje detective), dat via D oplost naar een vrolijke G-groot-landing "
    "met e-piano en klap. 104 BPM, ~4,0 s."
)

BPM = 104
T0 = 0.3
OVERALL = -5.5


def snap():
    dur = 0.12
    t = tvec(dur)
    y = bandpass(noise(dur), 2600, 2.0) * np.exp(-t / 0.010) * 2.5 + osc('sine', 1450, dur) * np.exp(-t / 0.006) * 0.3
    return reverb(y, 0.7, 0.15)


def render():
    s = Track(bpm=BPM)
    at = lambda b: T0 + s.b(humanize(b, 0.007, BPM))  # noqa: E731
    exact = lambda b: T0 + s.b(b)  # noqa: E731
    total = exact(4) + 1.5

    # rommelen in de doos (begint meteen, stopt vóór de landing)
    s.add(reverb(rummage(exact(3.3), 12), 0.7, 0.15), at=0.0, gain=6, pan=-0.25)

    # sluipend pizzicato-loopje: E G B G | A C B A -> (D) -> G
    line = [(0, 'E3'), (0.5, 'G3'), (1, 'B3'), (1.5, 'G3'), (2, 'A3'), (2.5, 'C4'), (3, 'B3'), (3.5, 'A3')]
    for b, n in line:
        s.add(pizzicato(n, s.b(0.4), bright=0.4), at=at(b), gain=-3 + vel(1), pan=-0.1)
        s.add(pizzicato(transpose(n, -12), s.b(0.4), bright=0.3), at=at(b), gain=-7 + vel(1), pan=-0.1)
    for b in (1, 3):
        s.add(snap(), at=at(b), gain=-12, pan=0.25)
    e = Track(bpm=BPM)
    e.add(poly(keys, ['D4', 'F#4', 'A4', 'C5'], s.b(0.45), bright=0.5, release=0.1), at=at(3.5), gain=-11, pan=-0.2)

    # gevonden: G-groot
    e.add(poly(keys, ['G3', 'B3', 'D4', 'G4'], s.b(2.4), bright=0.5, release=1.0, decay=2.0), at=exact(4),
          gain=-6, pan=-0.2)
    e.add(keys('B5', s.b(2.0), bright=0.55, release=1.0, decay=2.0), at=exact(4), gain=-10, pan=0.1)
    s.add(upright_bass('G1', s.b(2), bright=0.4, release=0.5), at=exact(4), gain=-5)
    s.add(reverb(group_clap(6), 1.2, 0.25), at=exact(4), gain=-7, pan=0.1)
    s.add(reverb(e.render(), decay=1.5, mix=0.2))

    x = s.render(length=total)[:ns(total)]
    x = finalize(x, loud=2.0, trim=False)
    return gain(fade(x, 0.02, 1.0), OVERALL)
