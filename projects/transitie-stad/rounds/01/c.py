from engine import *

TITLE = "Wandelen door de stad"
DESCRIPTION = (
    "Voetstappen op straat die van links naar rechts langs lopen, stadsgeluid met stemmen, en een relaxte "
    "shuffle-groove: wandelende bas, e-piano op de 'en', vingerknippen op 2 en 4 en een kort e-piano-melodietje "
    "dat landt op G. Rustiger en 'slenteriger' dan A. 104 BPM, G groot, ~4,3 s."
)

BPM = 104
T0 = 0.55
OVERALL = -7.0
SW = 0.67  # swing: de 'en' valt op 2/3 van de tel


def snap():
    dur = 0.12
    t = tvec(dur)
    y = bandpass(noise(dur), 2600, 2.0) * np.exp(-t / 0.010) * 2.5 + osc('sine', 1450, dur) * np.exp(-t / 0.006) * 0.3
    return reverb(y, 0.7, 0.15)


def render():
    s = Track(bpm=BPM)
    at = lambda b: T0 + s.b(humanize(b, 0.008, BPM))  # noqa: E731
    exact = lambda b: T0 + s.b(b)  # noqa: E731
    total = exact(4) + 1.5

    s.add(fade(city(total, traffic=0.45, voices=0.8, cars=1), 0.5, 1.2), at=0, gain=-1)
    # voetstappen: lopen van links naar rechts, beginnen al vóór de muziek
    for i in range(8):
        b = i * 1.0 - 1.0
        s.add(footstep(0.5 + 0.2 * (i % 2)), at=max(0.0, at(b)), gain=-17 + vel(1.5), pan=-0.7 + i * 0.18)

    e = Track(bpm=BPM)
    for b, n in ((0, 'G2'), (1, 'B2'), (2, 'C3'), (3, 'D3')):
        s.add(upright_bass(n, s.b(0.85), bright=0.45), at=at(b), gain=-6 + vel(1))
    for b, notes in ((0, ['G3', 'B3', 'D4']), (1, ['G3', 'B3', 'D4']), (2, ['C4', 'E4', 'G4']),
                     (3, ['D4', 'F#4', 'A4'])):
        e.add(poly(keys, notes, s.b(0.3), bright=0.45, release=0.1), at=at(b + SW), gain=-10 + vel(1), pan=-0.25)
    for b in (1, 3):
        s.add(snap(), at=at(b), gain=-12, pan=0.25)
    # melodietje (geswingd): D5 B4 D5 | E5 D5 B4 A4 -> G4
    for b, n in ((0, 'D5'), (SW, 'B4'), (1, 'D5'), (2, 'E5'), (2 + SW, 'D5'), (3, 'B4'), (3 + SW, 'A4')):
        e.add(keys(n, s.b(0.4), bright=0.55, release=0.15), at=at(b), gain=-9 + vel(1), pan=0.1)

    # landing op G (tel 4)
    e.add(poly(keys, ['G3', 'B3', 'D4', 'G4'], s.b(2.4), bright=0.45, release=1.0, decay=2.0), at=exact(4),
          gain=-6, pan=-0.2)
    e.add(keys('G4', s.b(2.0), bright=0.5, release=1.0, decay=2.0), at=exact(4), gain=-9, pan=0.1)
    s.add(upright_bass('G1', s.b(2), bright=0.4, release=0.5), at=exact(4), gain=-5)
    s.add(snap(), at=exact(4), gain=-10, pan=0.25)
    s.add(reverb(e.render(), decay=1.5, mix=0.2))

    x = s.render(length=total)[:ns(total)]
    x = finalize(x, loud=2.0, trim=False)
    return gain(fade(x, 0.5, 1.0), OVERALL)
