from engine import *

TITLE = "Gefloten melodie, zachter gefloten (9,2 s)"
DESCRIPTION = (
    "Precies B (gefloten melodie, e-piano-groove, bas, claps en shaker, 9,2 s), maar de fluit is zachter, zoals we "
    "eerder bij de piano deden: 4 dB zachter in de mix, minder fel (hoog weggefilterd), minder adem en iets meer "
    "galm. De fluit ligt daardoor meer ín de muziek dan erbovenop."
)

BPM = 104
T0 = 2.0  # muziek start tijdens de laatste lange fluitstoot
LENGTH = 9.2  # slotakkoord krijgt ~2 s om weg te faden, net als A en C

CHORDS = [(0, ['G3', 'B3', 'D4']), (2, ['E3', 'G3', 'B3']), (4, ['C4', 'E4', 'G4']), (6, ['D4', 'F#4', 'A4'])]
FINAL = ['G3', 'B3', 'D4', 'G4']
BASS = ['G1', 'E1', 'C2', 'D2']
COMP = [0.0, 0.75, 1.5]  # syncopisch aanslagpatroon binnen elk akkoord (2 tellen)
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
    s.add(reverb(final_whistle(long=0.8, gap=0.75), decay=2.0, mix=0.35), at=0.15, gain=-14, pan=0.15)
    seed(2000 + ord('c'))


def render():
    s = Track(bpm=BPM)
    at = lambda beat: T0 + s.b(humanize(beat, 0.008, BPM))  # noqa: E731
    exact = lambda beat: T0 + s.b(beat)  # noqa: E731
    stadium(s)

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
    w_c = whistling(events, vib=0.28, breath=0.03)                                        # minder adem
    w_c = reverb(lowpass(w_c, 2800), decay=1.8, mix=0.30)                                 # minder fel, meer galm

    base = s.render(length=LENGTH)
    mix_b, mix_c = Track(bpm=BPM), Track(bpm=BPM)
    mix_b.add(base).add(w_b, at=T0, gain=-3, pan=0.1)
    mix_c.add(base).add(w_c, at=T0, gain=-7, pan=0.1)                                     # 4 dB zachter
    mix_b = mix_b.render(length=LENGTH)[:ns(LENGTH)]
    mix_c = mix_c.render(length=LENGTH)[:ns(LENGTH)]

    # zelfde eindversterking als B, zodat alleen de fluit verandert
    g = db(2.0) / np.max(np.abs(highpass(mix_b, 25)))
    x = limit(highpass(mix_c, 25) * g, -1.0)
    x = fade(x, 0, 1.4)
    return gain(x, 0.45)
