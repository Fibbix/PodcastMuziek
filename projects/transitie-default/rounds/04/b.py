from engine import *

TITLE = "Fade-in middel (0,7 s)"
DESCRIPTION = (
    "Vorige C (zachte fluit, halve maat groove + gefloten handtekening), nu met een vloeiende fade-in van 0,7 s. "
    "De landing op de lange fluitnoot blijft op vol volume; de uitfade is ongewijzigd."
)

BPM = 104
T0 = 0.05
W_DROP = -9       # dB: fluit zachter t.o.v. vorige B
OVERALL = -4.5    # dB: geheel zachter
FADE_IN = 0.7     # seconden
W_BREATH = 0.018
W_LOWPASS = 2000
W_REVERB = 0.37


def render():
    seed(1000 + ord("b"))  # zelfde toeval als vorige B (anders speelt de groove net anders)
    s = Track(bpm=BPM)
    at = lambda b: T0 + s.b(humanize(b, 0.006, BPM))  # noqa: E731
    exact = lambda b: T0 + s.b(b)  # noqa: E731

    # halve maat groove op C (zelfde aanslagpatroon als de intro), dan D als opstap
    e = Track(bpm=BPM)
    for off, g in ((0.0, -6), (0.75, -9)):
        e.add(poly(keys, ['C4', 'E4', 'G4'], s.b(0.5), bright=0.5, release=0.12), at=at(off), gain=g + vel(1), pan=-0.2)
    e.add(poly(keys, ['D4', 'F#4', 'A4'], s.b(0.4), bright=0.5, release=0.12), at=at(1.5), gain=-8, pan=-0.2)
    s.add(upright_bass('C2', s.b(0.7), bright=0.45), at=at(0), gain=-5)
    s.add(upright_bass('C2', s.b(0.3), bright=0.45), at=at(0.75), gain=-10)
    s.add(upright_bass('D2', s.b(0.4), bright=0.45), at=at(1.5), gain=-8)
    s.add(reverb(group_clap(4), 1.0, 0.2), at=at(1), gain=-9, pan=0.15)
    for h in range(4):
        s.add(shaker(0.07), at=at(h * 0.5), gain=(-20 if h % 2 else -23) + vel(1.5), pan=0.4)

    # landing op G (tel 2)
    e.add(poly(keys, ['G3', 'B3', 'D4', 'G4'], s.b(2.4), bright=0.45, release=1.0, decay=2.0), at=exact(2), gain=-6, pan=-0.2)
    s.add(upright_bass('G1', s.b(2), bright=0.4, release=0.5), at=exact(2), gain=-5)
    s.add(reverb(group_clap(5), 1.2, 0.25), at=exact(2), gain=-7, pan=0.1)
    s.add(reverb(e.render(), decay=1.5, mix=0.2))

    # gefloten handtekening: B5 - D6 aanloop, lange G6 op de landing
    events = [(exact(1.5), 'B5', s.b(0.25) * 0.9), (exact(1.75), 'D6', s.b(0.25) * 0.9), (exact(2), 'G6', s.b(2.2))]
    state = rng().bit_generator.state
    w_ref = reverb(lowpass(whistling(events, vib=0.3, breath=0.025, glide=0.02), 2600), decay=1.8, mix=0.32)
    rng().bit_generator.state = state
    w_new = reverb(lowpass(whistling(events, vib=0.3, breath=W_BREATH, glide=0.02), W_LOWPASS), decay=1.8, mix=W_REVERB)

    total = exact(2) + 1.85
    base = s.render(length=total)
    ref, new = Track(bpm=BPM), Track(bpm=BPM)
    ref.add(base).add(w_ref, at=0, gain=-5, pan=0.1)                 # = vorige B
    new.add(base).add(w_new, at=0, gain=-5 + W_DROP, pan=0.1)        # zachtere fluit
    ref = fade(ref.render(length=total)[:ns(total)], 0.02, 0)
    new = fade(new.render(length=total)[:ns(total)], 0.02, 0)

    # eindversterking van de vorige B behouden (zachtere fluit maakt de rest niet harder), dan geheel zachter
    g = db(2.0) / np.max(np.abs(highpass(ref, 25)))
    x = limit(highpass(new, 25) * g, -1.0)
    return gain(fade(x, FADE_IN, 1.0), OVERALL)  # vloeiende fade-in (sin²), uitfade ongewijzigd
