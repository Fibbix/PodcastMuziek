from engine import *

TITLE = "Zachte piano in tertsen"
DESCRIPTION = (
    "Warmer en wat rustiger (96 BPM): de zachte piano uit de intro speelt een melodie in tertsen (twee stemmen) "
    "over C – D – Em – D, met lang aangehouden e-piano-akkoorden, bas, een zachte hartslag-kick en shaker. "
    "Landt op G met klap. Nostalgisch maar opgewekt, zoals bladeren door oude spullen. ~4,7 s."
)

BPM = 96
T0 = 0.65
OVERALL = -7.0
FADE_IN = 0.25
# melodie (boven) met terts eronder
MELODY = [(0, 'E5', 'C5'), (0.5, 'G5', 'E5'), (1, 'F#5', 'D5'), (1.5, 'A5', 'F#5'),
          (2, 'G5', 'E5'), (2.5, 'B5', 'G5'), (3, 'A5', 'F#5'), (3.5, 'F#5', 'D5')]
CHORDS = [(0, ['C4', 'E4', 'G4'], 'C2'), (1, ['D4', 'F#4', 'A4'], 'D2'), (2, ['E3', 'G3', 'B3'], 'E2'),
          (3, ['D4', 'F#4', 'A4'], 'D2')]


def soft_piano(n, dur):
    return lowpass(piano(n, dur, bright=0.25, release=0.5), 3500)


def render():
    s = Track(bpm=BPM)
    at = lambda b: T0 + s.b(humanize(b, 0.007, BPM))  # noqa: E731
    exact = lambda b: T0 + s.b(b)  # noqa: E731
    total = exact(4) + 1.5

    # aanloop: bas + shaker
    s.add(upright_bass('D2', s.b(0.9), bright=0.4), at=at(-1), gain=-6)
    for h in range(2):
        s.add(shaker(0.07), at=at(-1 + h * 0.5), gain=-25 + h * 2, pan=0.4)

    e = Track(bpm=BPM)
    for b, notes, root in CHORDS:
        e.add(poly(keys, notes, s.b(0.95), bright=0.4, release=0.3), at=at(b), gain=-10 + vel(1), pan=-0.2)
        s.add(upright_bass(root, s.b(0.8), bright=0.4), at=at(b), gain=-6 + vel(1))
        s.add(lowpass(kick(0.6, 0.35, 50, 0.0), 180), at=exact(b), gain=-12)
    for b in (1, 3):
        s.add(reverb(group_clap(4), 1.0, 0.2), at=at(b), gain=-12, pan=0.15)
    for h in range(8):
        s.add(shaker(0.07), at=at(h * 0.5), gain=(-22 if h % 2 else -25) + vel(1.5), pan=0.4)

    p = Track(bpm=BPM)
    for i, (b, hi, lo) in enumerate(MELODY):
        nxt = MELODY[i + 1][0] if i + 1 < len(MELODY) else 4
        d = s.b((nxt - b) * 0.95)
        g = vel(1)
        p.add(soft_piano(hi, d), at=at(b), gain=-6 + g, pan=0.1)
        p.add(soft_piano(lo, d), at=at(b), gain=-10 + g, pan=0.05)

    # landing op G (tel 4)
    e.add(poly(keys, ['G3', 'B3', 'D4', 'G4'], s.b(2.4), bright=0.4, release=1.0, decay=2.0), at=exact(4),
          gain=-7, pan=-0.2)
    p.add(soft_piano('G5', s.b(2.2)), at=exact(4), gain=-6, pan=0.1)
    p.add(soft_piano('B4', s.b(2.2)), at=exact(4), gain=-10, pan=0.05)
    s.add(upright_bass('G1', s.b(2), bright=0.4, release=0.5), at=exact(4), gain=-5)
    s.add(lowpass(kick(0.6, 0.35, 50, 0.0), 180), at=exact(4), gain=-11)
    s.add(reverb(group_clap(5), 1.2, 0.25), at=exact(4), gain=-9, pan=0.1)
    s.add(reverb(e.render(), decay=1.5, mix=0.2))
    s.add(reverb(p.render(), decay=1.8, mix=0.22))

    x = s.render(length=total)[:ns(total)]
    x = finalize(x, loud=2.0, trim=False)
    return gain(fade(x, FADE_IN, 1.0), OVERALL)
