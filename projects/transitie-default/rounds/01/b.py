from engine import *

TITLE = "Gefloten handtekening"
DESCRIPTION = (
    "Drie snelle gefloten noten omhoog (B – D – G) die landen op een lange hoge G, met een zacht e-piano-akkoord, "
    "bas en een klap op de landing; een shaker zwelt er kort naartoe. De fluit is het herkenbaarste element van de "
    "podcast, maar dit motief komt niet uit het intro-deuntje. ~2,6 s."
)

BPM = 104
T0 = 0.35  # ruimte voor de aanzwellende shaker


def render():
    s = Track(bpm=BPM)
    exact = lambda b: T0 + s.b(b)  # noqa: E731

    # shaker die aanzwelt naar de landing
    for i in range(6):
        s.add(shaker(0.06), at=T0 - 0.3 + i * s.b(0.25), gain=-28 + i * 2.2, pan=0.4)

    # gefloten motief: B5 - D6 - G6 (lang)
    events = [(exact(0) , 'B5', s.b(0.25) * 0.9), (exact(0.25), 'D6', s.b(0.25) * 0.9),
              (exact(0.5), 'G6', s.b(2.2))]
    w = whistling(events, vib=0.3, breath=0.025, glide=0.02)
    s.add(reverb(lowpass(w, 2600), decay=1.8, mix=0.32), at=0, gain=-4, pan=0.1)

    # landing
    s.add(reverb(poly(keys, ['G3', 'B3', 'D4', 'G4'], s.b(2.2), bright=0.45, release=1.0, decay=2.0), 1.5, 0.2),
          at=exact(0.5), gain=-7, pan=-0.2)
    s.add(upright_bass('G1', s.b(2), bright=0.4, release=0.5), at=exact(0.5), gain=-6)
    s.add(reverb(group_clap(5), 1.2, 0.25), at=exact(0.5), gain=-8, pan=0.1)

    x = s.render()
    total = exact(0.5) + 2.0
    return finalize(fade(x[:ns(total)], 0.02, 0), fade_out=1.0, loud=2.0, trim=False)
