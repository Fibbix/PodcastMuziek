from engine import *

TITLE = "Tribuneklappen"
DESCRIPTION = (
    "Ritmisch klappen zoals op de tribune (ta-ta-TAM), met e-piano-stoten op hetzelfde ritme (D – D – G) en de bas "
    "eronder. Kort, punchy en voetbal, in dezelfde klankkleur als intro/outro. ~2,4 s."
)

BPM = 104
T0 = 0.05
HITS = [(0.0, ['D4', 'F#4', 'A4'], 'D2', -8), (0.5, ['D4', 'F#4', 'A4'], 'D2', -8),
        (1.0, ['G3', 'B3', 'D4', 'G4'], 'G1', -5)]


def render():
    s = Track(bpm=BPM)
    at = lambda b: T0 + s.b(humanize(b, 0.005, BPM))  # noqa: E731

    e = Track(bpm=BPM)
    for i, (b, notes, root, g) in enumerate(HITS):
        last = i == len(HITS) - 1
        e.add(poly(keys, notes, s.b(2.2 if last else 0.3), bright=0.55, release=1.0 if last else 0.08,
                   decay=2.0 if last else 1.0), at=at(b), gain=g + (0 if last else vel(1)), pan=-0.2)
        s.add(upright_bass(root, s.b(2 if last else 0.35), bright=0.45, release=0.5 if last else 0.05), at=at(b),
              gain=-5 if last else -7)
        s.add(reverb(group_clap(7 if last else 6), 1.2 if last else 0.8, 0.25), at=at(b),
              gain=-4 if last else -6, pan=0.1)
    # gefloten accent op de landing (heel kort, zacht)
    w = whistling([(T0 + s.b(1.0), 'G6', s.b(0.6))], vib=0.2, breath=0.02)
    s.add(reverb(lowpass(w, 2400), 1.6, 0.3), at=0, gain=-12, pan=0.1)
    s.add(reverb(e.render(), decay=1.4, mix=0.2))

    x = s.render()
    total = T0 + s.b(1.0) + 1.8
    return finalize(fade(x[:ns(total)], 0.02, 0), fade_out=0.9, loud=2.0, trim=False)
