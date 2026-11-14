from engine import *

TITLE = "Handtekening met akkoordwissel"
DESCRIPTION = (
    "Zoals de vorige B, maar met vier gefloten noten (G – B – D → lange hoge G) en een akkoordwissel D → G "
    "eronder (e-piano en bas), zodat het sterker 'aankomt'. De fluit klinkt iets zachter en ronder, meer zoals in "
    "de intro. Shaker zwelt aan, klap op de landing. ~2,8 s."
)

BPM = 104
T0 = 0.35


def render():
    s = Track(bpm=BPM)
    exact = lambda b: T0 + s.b(b)  # noqa: E731

    for i in range(6):  # shaker zwelt aan naar de landing
        s.add(shaker(0.06), at=T0 - 0.3 + i * s.b(0.25), gain=-28 + i * 2.2, pan=0.4)

    # D-akkoord onder de aanloopnoten, G op de landing
    s.add(reverb(poly(keys, ['D4', 'F#4', 'A4'], s.b(0.7), bright=0.45, release=0.15), 1.4, 0.2),
          at=exact(0), gain=-10, pan=-0.2)
    s.add(upright_bass('D2', s.b(0.7), bright=0.45), at=exact(0), gain=-7)
    s.add(reverb(poly(keys, ['G3', 'B3', 'D4', 'G4'], s.b(2.4), bright=0.45, release=1.0, decay=2.0), 1.5, 0.2),
          at=exact(0.75), gain=-7, pan=-0.2)
    s.add(upright_bass('G1', s.b(2), bright=0.4, release=0.5), at=exact(0.75), gain=-6)
    s.add(reverb(group_clap(5), 1.2, 0.25), at=exact(0.75), gain=-8, pan=0.1)

    events = [(exact(0), 'G5', s.b(0.25) * 0.9), (exact(0.25), 'B5', s.b(0.25) * 0.9),
              (exact(0.5), 'D6', s.b(0.25) * 0.9), (exact(0.75), 'G6', s.b(2.2))]
    w = whistling(events, vib=0.3, breath=0.023, glide=0.02)
    s.add(reverb(lowpass(w, 2400), decay=1.8, mix=0.34), at=0, gain=-6, pan=0.1)

    x = s.render()
    total = exact(0.75) + 2.0
    return finalize(fade(x[:ns(total)], 0.02, 0), fade_out=1.0, loud=2.0, trim=False)
