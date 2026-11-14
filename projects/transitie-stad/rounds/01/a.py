from engine import *

TITLE = "Fietsbel en wandelbas"
DESCRIPTION = (
    "Stadsgeluid zwelt aan, een fietsbel (tring-tring), dan één maat vrolijke groove: wandelende bas (G–A–B–D), "
    "e-piano in het intro-ritme, klappen en shaker, met een e-piano-loopje omhoog naar de landing op G. "
    "Eindigt met een zacht belletje. Werkt als begin én eind van de reportage. 104 BPM, G groot, ~4,2 s."
)

BPM = 104
T0 = 0.5
OVERALL = -7.0


def render():
    s = Track(bpm=BPM)
    at = lambda b: T0 + s.b(humanize(b, 0.006, BPM))  # noqa: E731
    exact = lambda b: T0 + s.b(b)  # noqa: E731
    total = exact(4) + 1.45

    # stad + fietsbel
    s.add(fade(city(total, traffic=0.5, voices=0.5), 0.5, 1.2), at=0, gain=1)
    s.add(reverb(highpass(bike_bell(2, 0.18, 0.09), 600), 0.9, 0.2), at=0.02, gain=-15, pan=0.35)

    # groove (één maat)
    e = Track(bpm=BPM)
    for b, notes in ((0, ['G3', 'B3', 'D4']), (0.75, ['G3', 'B3', 'D4']), (1.5, ['G3', 'B3', 'D4']),
                     (2, ['C4', 'E4', 'G4']), (2.75, ['C4', 'E4', 'G4']), (3.5, ['D4', 'F#4', 'A4'])):
        e.add(poly(keys, notes, s.b(0.5), bright=0.5, release=0.12), at=at(b),
              gain=(-7 if b % 1 == 0 else -9) + vel(1), pan=-0.2)
    for b, n in ((0, 'G2'), (1, 'A2'), (2, 'B2'), (3, 'D3')):
        s.add(upright_bass(n, s.b(0.9), bright=0.45), at=at(b), gain=-6 + vel(1))
    for b in (1, 3):
        s.add(reverb(group_clap(4), 1.0, 0.2), at=at(b), gain=-10, pan=0.15)
    for h in range(8):
        s.add(shaker(0.07), at=at(h * 0.5), gain=(-21 if h % 2 else -24) + vel(1.5), pan=0.4)
    # e-piano-loopje omhoog naar de landing
    for b, n in ((2.5, 'B4'), (3.0, 'D5'), (3.5, 'E5')):
        e.add(keys(n, s.b(0.45), bright=0.55, release=0.15), at=at(b), gain=-9 + vel(1), pan=0.1)

    # landing op G (tel 4)
    e.add(poly(keys, ['G3', 'B3', 'D4', 'G4'], s.b(2.4), bright=0.45, release=1.0, decay=2.0), at=exact(4),
          gain=-6, pan=-0.2)
    e.add(keys('G5', s.b(2.0), bright=0.5, release=1.0, decay=2.0), at=exact(4), gain=-9, pan=0.1)
    s.add(upright_bass('G1', s.b(2), bright=0.4, release=0.5), at=exact(4), gain=-5)
    s.add(reverb(group_clap(5), 1.2, 0.25), at=exact(4), gain=-8, pan=0.1)
    s.add(reverb(e.render(), decay=1.5, mix=0.2))
    s.add(reverb(highpass(bike_bell(1, 0.03, 0.0), 600), 1.2, 0.25), at=exact(5), gain=-22, pan=0.35)

    x = s.render(length=total)[:ns(total)]
    x = finalize(x, loud=2.0, trim=False)
    return gain(fade(x, 0.5, 1.0), OVERALL)
