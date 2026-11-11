from engine import *

TITLE = "Mysterieus"
DESCRIPTION = "Donkere pad in D mineur met een omgekeerde galm die aanzwelt naar een belletje. Spannend, filmisch."


def render():
    s = Track(bpm=80)
    b = bell('A5', 0.3, 1.8, 0.6)
    swell = reverse_swell(b[:ns(0.6)], decay=1.0)
    t_bell = len(swell) / SR
    s.add(swell, at=0, gain=-6)
    s.add(b, at=t_bell, gain=-3, pan=0.2)
    s.add(pad(chord('D3', 'min9'), 2.0, bright=0.3, attack=0.8, release=1.0, motion=0.5), at=0.2, gain=-4)
    s.add(sub('D1', 1.5, release=0.8), at=t_bell, gain=-8)
    return finalize(reverb(s.render(), decay=2.2, mix=0.3), fade_out=1.0, loud=1.0)
