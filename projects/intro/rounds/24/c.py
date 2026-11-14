from engine import *

TITLE = "Met 5 s zacht doorspelend deuntje"
DESCRIPTION = (
    "De gekozen intro (identiek aan A), en daarna speelt het deuntje gewoon zachtjes door: na één maat aanloop "
    "begint de gefloten melodie opnieuw, met de e-piano-groove, bas, claps en shaker, heel zacht (~13 dB onder de "
    "muziek, hoog iets weggefilterd) zodat de podcast eroverheen kan beginnen. Loopt aan het eind rustig weg. Totaal 14,2 s."
)

BPM = 104
T0 = 2.0  # muziek start tijdens de laatste lange fluitstoot
WHISTLE = 'louder'
WHISTLE_GAIN = -9  # was -14
LENGTH = 9.2
TAIL = 5.0        # extra seconden zachte laag
BED_LEVEL = -28   # dBFS (RMS) van de laag  # slotakkoord krijgt ~2 s om weg te faden, net als A en C

CHORDS = [(0, ['G3', 'B3', 'D4']), (2, ['E3', 'G3', 'B3']), (4, ['C4', 'E4', 'G4']), (6, ['D4', 'F#4', 'A4'])]
FINAL = ['G3', 'B3', 'D4', 'G4']
BASS = ['G1', 'E1', 'C2', 'D2']
COMP = [0.0, 0.75, 1.5]  # syncopisch aanslagpatroon binnen elk akkoord (2 tellen)
CH = {'G': (['G3', 'B3', 'D4'], 'G1'), 'Em': (['E3', 'G3', 'B3'], 'E1'),
      'C': (['C4', 'E4', 'G4'], 'C2'), 'D': (['D4', 'F#4', 'A4'], 'D2')}
MELODY = [  # geschreven in octaaf 5; gefloten een octaaf hoger
    (0, 'D5', 1), (1, 'B4', 0.5), (1.5, 'D5', 0.5),
    (2, 'E5', 1.5), (3.5, 'D5', 0.5),
    (4, 'C5', 0.5), (4.5, 'E5', 0.5), (5, 'G5', 1),
    (6, 'D5', 0.5), (6.5, 'E5', 0.5), (7, 'F#5', 1),
    (8, 'G5', 2.5),
]


def stadium(s):
    seed(1000 + ord('b'))  # exact dezelfde opening als optie A
    dur_c = 6.5
    t = tvec(dur_c)
    ex = 0.5 + 0.45 * np.exp(-((t - 2.2) / 0.7) ** 2)
    c = fade(crowd(dur_c, excitement=ex), 0.3, 0)
    c = fade_away(c, start=2.0, dur=3.0, cutoff=400)
    s.add(c, at=0, gain=-1)
    w_ref = reverb(final_whistle(long=0.8, gap=0.75), decay=2.0, mix=0.35)     # fluit zoals in A (referentie)
    if WHISTLE == 'pea':
        w_new = reverb(final_whistle(long=0.8, gap=0.75, kind='pea'), decay=1.4, mix=0.18)  # droger, dichterbij
    else:
        w_new = w_ref
    seed(2000 + ord('c'))
    return w_ref, w_new


def bed_tune(s, at, exact):
    """Het deuntje speelt gewoon door (zelfde arrangement als de intro), daarna wordt het geheel heel zacht gezet."""
    R0 = 12                                     # herhaling begint op tel 12 (G), na één maat aanloop vanaf tel 10
    e, perc = Track(bpm=BPM), Track(bpm=BPM)
    chords = [(10 - R0, CH['G'][0])] + CHORDS  # aanloopmaat + de vier akkoorden van het deuntje
    roots = ['G1'] + BASS
    for i, (beat, notes) in enumerate(chords):
        b0 = R0 + beat
        for j, off in enumerate(COMP):
            e.add(poly(keys, notes, s.b(0.5 if j < 2 else 0.4), bright=0.5, release=0.12), at=at(b0 + off),
                  gain=(-5 if j == 0 else -8) + vel(1.2), pan=-0.2)
        perc.add(upright_bass(roots[i], s.b(0.7), bright=0.45), at=at(b0), gain=-5 + vel(1))
        perc.add(upright_bass(roots[i], s.b(0.3), bright=0.45), at=at(b0 + 0.75), gain=-10 + vel(1))
        perc.add(upright_bass(transpose(roots[i], 7), s.b(0.4), bright=0.45), at=at(b0 + 1.5), gain=-8 + vel(1))
        for k in (0, 1):
            if k == 1:
                perc.add(reverb(group_clap(4), 1.0, 0.2), at=at(b0 + k), gain=-9 + vel(1), pan=0.15)
            for h in (0, 0.5):
                perc.add(shaker(0.07), at=at(b0 + k + h), gain=(-20 if h else -23) + vel(2), pan=0.4)
    t = Track(bpm=BPM)
    t.add(reverb(e.render(), decay=1.5, mix=0.2))
    t.add(perc.render())
    # gefloten melodie opnieuw, met de zachte fluitklank van de intro
    events = [(humanize(exact(R0 + b), 0.01), transpose(n, 12), s.b(l) * (0.95 if b < 8 else 1.0)) for b, n, l in MELODY]
    w = whistling(events, vib=0.28, breath=0.023)
    t.add(reverb(lowpass(w, 2400), decay=1.8, mix=0.34), at=0, gain=-10, pan=0.1)
    return lowpass(t.render(), 3200)            # iets ruimer dan C zodat de melodie herkenbaar blijft


BED = bed_tune


def render():
    s = Track(bpm=BPM)
    at = lambda beat: T0 + s.b(humanize(beat, 0.008, BPM))  # noqa: E731
    exact = lambda beat: T0 + s.b(beat)  # noqa: E731
    w_ref, w_new = stadium(s)

    # --- e-piano groove
    e = Track(bpm=BPM)
    for beat, notes in CHORDS:
        for j, off in enumerate(COMP):
            length = 0.5 if j < 2 else 0.4
            e.add(poly(keys, notes, s.b(length), bright=0.5, release=0.12), at=at(beat + off),
                  gain=(-5 if j == 0 else -8) + vel(1.2), pan=-0.2)
    e.add(poly(keys, FINAL, s.b(3), bright=0.45, release=1.2, decay=2.2), at=exact(8), gain=-5, pan=-0.2)
    s.add(reverb(e.render(), decay=1.5, mix=0.2), gain=0)

    # --- bas
    for i, root in enumerate(BASS):
        s.add(upright_bass(root, s.b(0.7), bright=0.45), at=at(i * 2), gain=-5 + vel(1))
        s.add(upright_bass(root, s.b(0.3), bright=0.45), at=at(i * 2 + 0.75), gain=-10 + vel(1))
        s.add(upright_bass(transpose(root, 7), s.b(0.4), bright=0.45), at=at(i * 2 + 1.5), gain=-8 + vel(1))
    s.add(upright_bass('G1', s.b(3), bright=0.4, release=0.5), at=exact(8), gain=-5)

    # --- percussie: claps op 2 en 4, zachte shaker in achtsten
    for k in range(8):
        if k % 2 == 1:
            s.add(reverb(group_clap(4), 1.0, 0.2), at=at(k), gain=-9 + vel(1), pan=0.15)
        for h in (0, 0.5):
            s.add(shaker(0.07), at=at(k + h), gain=(-20 if h else -23) + vel(2), pan=0.4)
    s.add(reverb(group_clap(5), 1.2, 0.25), at=exact(8), gain=-8)

    # --- gefloten melodie
    events = [(exact(b) - T0 + 0.0, transpose(n, 12), s.b(l) * (0.95 if b < 8 else 1.0)) for b, n, l in MELODY]
    events = [(humanize(t0, 0.01), n, d) for t0, n, d in events]
    state = rng().bit_generator.state
    w_b = reverb(whistling(events, vib=0.28, breath=0.05), decay=1.8, mix=0.22)          # = fluit van B
    rng().bit_generator.state = state
    w_c = whistling(events, vib=0.28, breath=0.023)                                       # minder adem
    w_c = reverb(lowpass(w_c, 2400), decay=1.8, mix=0.34)                                 # minder fel, meer galm

    base = s.render(length=LENGTH)
    mix_b, mix_c = Track(bpm=BPM), Track(bpm=BPM)
    mix_b.add(base).add(w_ref, at=0.15, gain=-14, pan=0.15).add(w_b, at=T0, gain=-3, pan=0.1)   # referentie-niveau
    mix_c.add(base).add(w_new, at=0.15, gain=WHISTLE_GAIN, pan=0.15).add(w_c, at=T0, gain=-10, pan=0.1)
    mix_b = mix_b.render(length=LENGTH)[:ns(LENGTH)]
    mix_c = mix_c.render(length=LENGTH)[:ns(LENGTH)]

    # zelfde eindversterking als B, zodat alleen de fluit verandert
    g = db(2.0) / np.max(np.abs(highpass(mix_b, 25)))
    x = limit(highpass(mix_c, 25) * g, -1.0)
    x = fade(x, 0, 1.4)
    x = gain(x, 0.45)                                   # = A, tot hier identiek

    # --- 5 seconden zachte nagloei-laag waar de podcast overheen begint
    total = LENGTH + TAIL
    bed = BED(s, at, exact)
    out = np.zeros((ns(total), 2))
    out[:len(x)] += x
    n = min(len(bed), len(out))
    tt = np.arange(n) / SR
    t_in = exact(10)                                    # 2 tellen na het slotakkoord
    env = np.clip((tt - t_in) / 1.0, 0, 1) * np.clip((total - tt) / 3.0, 0, 1)
    bed = bed[:n] * env[:, None]
    act = bed[ns(LENGTH):ns(LENGTH + 2)]
    bed *= db(BED_LEVEL) / (np.sqrt(np.mean(act ** 2)) + 1e-12)
    out[:n] += bed
    return np.clip(out, -db(-0.5), db(-0.5))
