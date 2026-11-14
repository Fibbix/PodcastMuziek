from engine import *

TITLE = "E-piano-loopje"
DESCRIPTION = (
    "Kort opwaarts e-piano-loopje over C – D – G (IV–V–I, klinkt als 'afronden en door'), met bas en een "
    "zachte shaker; landt op G met een klap. Zelfde klankkleur als intro/outro, eigen motief. ~2,7 s."
)

BPM = 104
T0 = 0.05


def render():
    s = Track(bpm=BPM)
    at = lambda b: T0 + s.b(humanize(b, 0.006, BPM))  # noqa: E731
    exact = lambda b: T0 + s.b(b)  # noqa: E731

    e = Track(bpm=BPM)
    steps = [(0.0, ['C4', 'E4', 'G4'], 'E5', 'C2'), (0.5, ['C4', 'E4', 'G4'], 'G5', None),
             (1.0, ['D4', 'F#4', 'A4'], 'F#5', 'D2'), (1.5, ['D4', 'F#4', 'A4'], 'A5', None)]
    for b, chord_notes, top, root in steps:
        e.add(poly(keys, chord_notes, s.b(0.45), bright=0.5, release=0.1), at=at(b), gain=-8 + vel(1), pan=-0.2)
        e.add(keys(top, s.b(0.45), bright=0.6, release=0.15), at=at(b), gain=-3 + vel(1), pan=0.1)
        if root:
            s.add(upright_bass(root, s.b(0.9), bright=0.45), at=at(b), gain=-5)
    # landing op G
    e.add(poly(keys, ['G3', 'B3', 'D4', 'G4'], s.b(2), bright=0.5, release=1.0, decay=2.0), at=exact(2), gain=-5, pan=-0.2)
    e.add(keys('B5', s.b(2), bright=0.6, release=1.0, decay=2.0), at=exact(2), gain=-3, pan=0.1)
    s.add(upright_bass('G1', s.b(2), bright=0.4, release=0.5), at=exact(2), gain=-5)
    s.add(reverb(group_clap(5), 1.2, 0.25), at=exact(2), gain=-7, pan=0.1)
    for h in range(4):
        s.add(shaker(0.07), at=at(h * 0.5), gain=-22 + h * 1.5 + vel(1.5), pan=0.4)
    s.add(reverb(e.render(), decay=1.5, mix=0.22))

    x = s.render()
    total = exact(2) + 1.5
    return finalize(fade(x[:ns(total)], 0.02, 0), fade_out=0.9, loud=2.0, trim=False)
