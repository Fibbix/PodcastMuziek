from engine import *

TITLE = "Gezongen: Pad door de Stad"
DESCRIPTION = (
    "'Pad – door de – Stad!' gezongen (B – D – D → hoge G), met een opstap op D en de landing op G met klap; "
    "zacht stadsgeluid en een belletje als staartje. De stem is de Nederlandse Windows-stem (Frank), door de "
    "engine op de noten gezet en verdubbeld tot een klein koortje: verstaanbaar maar wat robotachtig/autotune. "
    "Met een eigen opname van het team wordt dit veel echter. 104 BPM, G groot, ~3,7 s."
)

BPM = 104
T0 = 0.35
OVERALL = -6.0
A = 'projects/transitie-stad/assets/'


def syllables():
    return {'pad': {'x': load_voice(A + 'syl_pad.wav'), 'vowel': (0.22, 0.43), 'hold': 0.30},
            'door': {'x': load_voice(A + 'syl_door.wav'), 'vowel': (0.16, 0.62), 'hold': 0.30},
            'de': {'x': load_voice(A + 'syl_de.wav'), 'vowel': (0.14, 0.46), 'hold': 0.28},
            'stad': {'x': load_voice(A + 'syl_stad.wav'), 'vowel': (0.43, 0.60), 'hold': 0.50}}


def render():
    s = Track(bpm=BPM)
    at = lambda b: T0 + s.b(humanize(b, 0.006, BPM))  # noqa: E731
    exact = lambda b: T0 + s.b(b)  # noqa: E731
    total = exact(3) + 1.65

    s.add(fade(city(total, traffic=0.4, voices=0.4), 0.4, 1.2), at=0, gain=-2)

    # zang: Pad (tel 1) – door (2) – de (2,5) – Stad (3, lang)
    S = syllables()
    ev = [(exact(1), 'B2', s.b(0.85), S['pad']), (exact(2), 'D3', s.b(0.42), S['door']),
          (exact(2.5), 'D3', s.b(0.4), S['de']), (exact(3), 'G3', s.b(1.9), S['stad'])]
    lead = sing(ev, total=total)
    dbl1 = sing([(t + 0.014, n, d, x) for t, n, d, x in ev], total=total, formant=0.94, cents=9, vib=0.3)
    dbl2 = sing([(t - 0.009, n, d, x) for t, n, d, x in ev], total=total, formant=1.07, cents=-8, vib=0.2)
    v = Track(bpm=BPM)
    v.add(lead, at=0, gain=0, pan=0.0).add(dbl1, at=0, gain=-7, pan=-0.45).add(dbl2, at=0, gain=-8, pan=0.45)
    voc = reverb(eq(highpass(v.render(length=total), 110), 3000, 3, 0.8), decay=1.4, mix=0.22)
    s.add(voc, at=0, gain=9)

    # opstap op D, dan G – C – G
    e = Track(bpm=BPM)
    e.add(poly(keys, ['D4', 'F#4', 'A4'], s.b(0.45), bright=0.5, release=0.12), at=at(0), gain=-9, pan=-0.2)
    s.add(upright_bass('D2', s.b(0.8), bright=0.45), at=at(0), gain=-8)
    for b, notes, root in ((1, ['G3', 'B3', 'D4'], 'G2'), (2, ['C4', 'E4', 'G4'], 'C2')):
        e.add(poly(keys, notes, s.b(0.5), bright=0.5, release=0.12), at=at(b), gain=-8 + vel(1), pan=-0.2)
        e.add(poly(keys, notes, s.b(0.4), bright=0.5, release=0.12), at=at(b + 0.75), gain=-10 + vel(1), pan=-0.2)
        s.add(upright_bass(root, s.b(0.9), bright=0.45), at=at(b), gain=-6)
    s.add(reverb(group_clap(4), 1.0, 0.2), at=at(2), gain=-11, pan=0.15)
    for h in range(6):
        s.add(shaker(0.07), at=at(h * 0.5), gain=(-22 if h % 2 else -25) + vel(1.5), pan=0.4)
    # landing op G (tel 3) op "Stad"
    e.add(poly(keys, ['G3', 'B3', 'D4', 'G4'], s.b(2.4), bright=0.45, release=1.0, decay=2.0), at=exact(3),
          gain=-7, pan=-0.2)
    s.add(upright_bass('G1', s.b(2), bright=0.4, release=0.5), at=exact(3), gain=-6)
    s.add(reverb(group_clap(6), 1.2, 0.25), at=exact(3), gain=-8, pan=0.1)
    s.add(reverb(e.render(), decay=1.5, mix=0.2))
    s.add(reverb(highpass(bike_bell(1, 0.03, 0.0), 600), 1.2, 0.25), at=exact(4.6), gain=-23, pan=0.35)

    x = s.render(length=total)[:ns(total)]
    x = finalize(x, loud=2.0, trim=False)
    return gain(fade(x, 0.4, 1.0), OVERALL)
