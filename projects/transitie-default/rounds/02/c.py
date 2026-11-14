from engine import *

TITLE = "Korte handtekening"
DESCRIPTION = (
    "Uitgekleed tot de kern: twee gefloten noten (D → hoge G) die meteen landen op een e-piano-akkoord met bas en "
    "klap. Geen aanloop, kortere uitklank: het snelste en strakste van de drie. ~1,9 s."
)

BPM = 104
T0 = 0.03


def render():
    s = Track(bpm=BPM)
    exact = lambda b: T0 + s.b(b)  # noqa: E731

    events = [(exact(0), 'D6', s.b(0.25) * 0.9), (exact(0.25), 'G6', s.b(1.6))]
    w = whistling(events, vib=0.28, breath=0.025, glide=0.02)
    s.add(reverb(lowpass(w, 2600), decay=1.6, mix=0.3), at=0, gain=-4, pan=0.1)

    s.add(reverb(poly(keys, ['G3', 'B3', 'D4', 'G4'], s.b(1.8), bright=0.5, release=0.8, decay=1.6), 1.3, 0.2),
          at=exact(0.25), gain=-6, pan=-0.2)
    s.add(upright_bass('G1', s.b(1.5), bright=0.45, release=0.4), at=exact(0.25), gain=-5)
    s.add(reverb(group_clap(6), 1.0, 0.22), at=exact(0.25), gain=-6, pan=0.1)
    s.add(shaker(0.06), at=exact(0), gain=-22, pan=0.4)

    x = s.render()
    total = exact(0.25) + 1.7
    return finalize(fade(x[:ns(total)], 0.01, 0), fade_out=0.8, loud=2.0, trim=False)
