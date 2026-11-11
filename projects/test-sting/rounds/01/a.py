from engine import *

TITLE = "Warm & vriendelijk"
DESCRIPTION = "Elektrische piano met een getokkeld melodietje in C groot, zachte galm. Rustig en uitnodigend."


def render():
    s = Track(bpm=100)
    s.add(poly(keys, chord('C4', 'maj7'), s.b(4), bright=0.4), beat=0, gain=-2)
    s.add(sub('C2', s.b(3.5)), beat=0, gain=-6)
    for i, n in enumerate(['E5', 'G5', 'B5', 'C6']):
        s.add(pluck(n, 1.2, bright=0.5), beat=0.5 + i * 0.5, pan=-0.3 + i * 0.2, gain=-5)
    s.add(bell('G6', 0.2, 1.5, 0.3), beat=2.5, pan=0.4, gain=-14)
    return finalize(reverb(s.render(), decay=1.8, mix=0.25), fade_out=0.6)
