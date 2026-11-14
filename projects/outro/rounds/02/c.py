from engine import *

TITLE = "Spiegelbeeld met langer zacht deel"
DESCRIPTION = (
    "Zoals A, maar het zachte begin duurt langer: het deuntje klinkt eerst twee keer heel zacht (handig als er langer overheen gepraat wordt), dan over naar normaal, slotakkoord met klap en afgefloten."
)

BPM = 104
KEY_UP = 0        # halve tonen omhoog voor het normale (luide) deel
SOFT_PASSES = 2     # aantal keer het deuntje heel zacht vóór het normale deel
SOFT_LEVEL = -28         # dBFS (RMS) aan het eind van het zachte deel = niveau van de intro-staart
RISE_DB = 22             # het zachte deel begint zoveel dB zachter en zwelt gelijkmatig aan
XFADE = 1.4              # seconden overgang zacht -> normaal (eindigt op de eerste tel van het normale deel)
RIT = 0.6                # vertraging in de laatste 2 tellen voor het slotakkoord

# Zelfde deuntje als de intro (ronde 25 B)
CHORDS = [(0, ['G3', 'B3', 'D4']), (2, ['E3', 'G3', 'B3']), (4, ['C4', 'E4', 'G4']), (6, ['D4', 'F#4', 'A4'])]
BASS = ['G1', 'E1', 'C2', 'D2']
FINAL = ['G3', 'B3', 'D4', 'G4']
COMP = [0.0, 0.75, 1.5]
MELODY = [  # geschreven in octaaf 5; gefloten een octaaf hoger
    (0, 'D5', 1), (1, 'B4', 0.5), (1.5, 'D5', 0.5),
    (2, 'E5', 1.5), (3.5, 'D5', 0.5),
    (4, 'C5', 0.5), (4.5, 'E5', 0.5), (5, 'G5', 1),
    (6, 'D5', 0.5), (6.5, 'E5', 0.5), (7, 'F#5', 1),
    (8, 'G5', 2.5),
]
LEAD = 2                                # tellen groove-aanloop
LOUD = LEAD + 8 * SOFT_PASSES           # eerste tel van het normale deel
END = LOUD + 8                          # slotakkoord
START = 0.15
s_b = lambda beats: beats * 60 / BPM  # noqa: E731


def bt(b):
    """Tel -> seconden, met een ritardando in de laatste 2 tellen voor het slot."""
    spb = 60 / BPM
    R = END - 2
    if b <= R:
        return START + b * spb
    x = min(b, END) - R
    t = START + R * spb + spb * (x + RIT * x * x / 4)
    if b > END:
        t += (b - END) * spb * (1 + RIT)
    return t


def render():
    at = lambda b: bt(humanize(b, 0.008, BPM))  # noqa: E731
    e, rest = Track(bpm=BPM), Track(bpm=BPM)
    events = []
    blocks = [(0, 0, [(0, ['G3', 'B3', 'D4'])], ['G1'])]                      # aanloop
    for p in range(SOFT_PASSES + 1):
        blocks.append((LEAD + 8 * p, KEY_UP if p == SOFT_PASSES else 0, CHORDS, BASS))
    for b0, semis, chords, roots in blocks:
        for i, (beat, notes) in enumerate(chords):
            nb = b0 + beat
            notes = [transpose(n, semis) for n in notes]
            root = transpose(roots[i], semis)
            for j, off in enumerate(COMP):
                e.add(poly(keys, notes, s_b(0.5 if j < 2 else 0.4), bright=0.5, release=0.12), at=at(nb + off),
                      gain=(-5 if j == 0 else -8) + vel(1.2), pan=-0.2)
            rest.add(upright_bass(root, s_b(0.7), bright=0.45), at=at(nb), gain=-5 + vel(1))
            rest.add(upright_bass(root, s_b(0.3), bright=0.45), at=at(nb + 0.75), gain=-10 + vel(1))
            rest.add(upright_bass(transpose(root, 7), s_b(0.4), bright=0.45), at=at(nb + 1.5), gain=-8 + vel(1))
            for k in (0, 1):
                if k == 1:
                    rest.add(reverb(group_clap(4), 1.0, 0.2), at=at(nb + k), gain=-9 + vel(1), pan=0.15)
                for h in (0, 0.5):
                    rest.add(shaker(0.07), at=at(nb + k + h), gain=(-20 if h else -23) + vel(2), pan=0.4)
        if b0 >= LEAD:   # melodie; alleen de laatste keer mét slotnoot
            for b, n, l in MELODY:
                if b0 != LOUD and b >= 8:
                    continue
                t0, t1 = bt(b0 + b), bt(b0 + b + l)
                events.append((humanize(t0, 0.01), transpose(transpose(n, 12), semis),
                               (t1 - t0) * (0.95 if b < 8 else 1.0)))

    # slotakkoord met klap
    fin = [transpose(n, KEY_UP) for n in FINAL]
    e.add(poly(keys, fin, 2.2, bright=0.5, release=1.4, decay=2.4), at=bt(END), gain=-4, pan=-0.2)
    rest.add(upright_bass(transpose('G1', KEY_UP), 2.2, bright=0.4, release=0.6), at=bt(END), gain=-4)
    rest.add(reverb(group_clap(6), 1.4, 0.3), at=bt(END), gain=-6)

    mixdown = Track(bpm=BPM)
    mixdown.add(reverb(e.render(), decay=1.5, mix=0.2))
    mixdown.add(rest.render())
    w = whistling(events, vib=0.28, breath=0.023)               # zelfde zachte fluitmelodie als de intro
    mixdown.add(reverb(lowpass(w, 2400), decay=1.8, mix=0.34), at=0, gain=-10, pan=0.1)
    # afgefloten: zelfde scheidsrechtersfluit als in de intro (klassiek, -9 dB)
    t_wh = bt(END) + 0.9
    mixdown.add(reverb(final_whistle(long=0.8, gap=0.75), decay=2.0, mix=0.35), at=t_wh, gain=-9, pan=0.15)
    total = t_wh + 2.3 + 1.6

    y = finalize(mixdown.render(length=total)[:ns(total)], fade_out=1.4, loud=2.0, trim=False)

    # --- spiegelbeeld van de intro: eerst heel zacht en gedempt, dan over naar normaal
    tt = np.arange(len(y)) / SR
    t_loud = bt(LOUD)
    loud = np.clip((tt - (t_loud - XFADE)) / XFADE, 0, 1)
    loud = np.sin(loud * np.pi / 2) ** 2                       # vloeiende overgang
    soft_src = lowpass(y, 3200)                                # gedempt, zoals de intro-staart
    w0, w1 = ns(t_loud - XFADE - 2.0), ns(t_loud - XFADE)
    k = db(SOFT_LEVEL) / (np.sqrt(np.mean(soft_src[w0:w1] ** 2)) + 1e-12)
    rise = np.clip((tt - START) / (t_loud - XFADE - START), 0, 1)
    soft_env = k * db(-RISE_DB * (1 - rise)) * (1 - loud)
    return y * loud[:, None] + soft_src * soft_env[:, None]
