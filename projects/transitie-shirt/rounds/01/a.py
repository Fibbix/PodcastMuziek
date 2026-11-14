from engine import *

TITLE = "Kledingrek doorzoeken"
DESCRIPTION = (
    "Twee keer kleerhangers die langs een rek worden geschoven (zoeken...), met een speels e-piano-motiefje "
    "op staccato bas: Em – C – D, nog zoekend. Dan 'gevonden!': landing op G met klap. "
    "Het geschuif begint meteen (geen fade-in over het effect). 104 BPM, ~3,9 s."
)

BPM = 104
T0 = 0.35
OVERALL = -7.0
MELODY = [(0, 'B4'), (0.5, 'E5'), (1, 'D5'), (1.5, 'B4'), (2, 'C5'), (2.5, 'E5'), (3, 'D5'), (3.5, 'F#5')]


def render():
    s = Track(bpm=BPM)
    at = lambda b: T0 + s.b(humanize(b, 0.006, BPM))  # noqa: E731
    exact = lambda b: T0 + s.b(b)  # noqa: E731
    total = exact(4) + 1.5

    # kledingrek: schuiven, even kijken, nog eens schuiven
    s.add(reverb(rack_slide(0.45, 6, 1), 0.6, 0.12), at=0.0, gain=3, pan=-0.3)
    s.add(reverb(rack_slide(0.4, 5, -1), 0.6, 0.12), at=exact(1.75), gain=0, pan=0.3)

    # zoekend: staccato bas en e-piano (Em – C – D)
    e = Track(bpm=BPM)
    for b, n in ((0, 'E2'), (1, 'G2'), (2, 'C2'), (3, 'D2')):
        s.add(upright_bass(n, s.b(0.35), bright=0.45, release=0.05), at=at(b), gain=-6 + vel(1))
    for b, notes in ((0.5, ['E4', 'G4', 'B4']), (1.5, ['E4', 'G4', 'B4']), (2.5, ['C4', 'E4', 'G4']),
                     (3.5, ['D4', 'F#4', 'A4'])):
        e.add(poly(keys, notes, s.b(0.25), bright=0.5, release=0.06), at=at(b), gain=-11 + vel(1), pan=-0.2)
    for i, (b, n) in enumerate(MELODY):
        e.add(keys(n, s.b(0.3), bright=0.55, release=0.08), at=at(b), gain=-9 + vel(1), pan=0.1)
    for h in range(8):
        s.add(shaker(0.05), at=at(h * 0.5), gain=(-23 if h % 2 else -26) + vel(1.5), pan=0.4)

    # gevonden: landing op G (tel 4)
    e.add(poly(keys, ['G3', 'B3', 'D4', 'G4'], s.b(2.4), bright=0.5, release=1.0, decay=2.0), at=exact(4),
          gain=-6, pan=-0.2)
    e.add(keys('G5', s.b(2.0), bright=0.55, release=1.0, decay=2.0), at=exact(4), gain=-9, pan=0.1)
    s.add(upright_bass('G1', s.b(2), bright=0.4, release=0.5), at=exact(4), gain=-5)
    s.add(reverb(group_clap(6), 1.2, 0.25), at=exact(4), gain=-7, pan=0.1)
    s.add(reverb(e.render(), decay=1.5, mix=0.2))

    x = s.render(length=total)[:ns(total)]
    x = finalize(x, loud=2.0, trim=False)
    return gain(fade(x, 0.02, 1.0), OVERALL)
