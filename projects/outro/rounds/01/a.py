from engine import *

TITLE = "Het deuntje, met een duidelijk slot"
DESCRIPTION = (
    "Het intro-deuntje (gefloten melodie, e-piano-groove, bas, claps, shaker) in hetzelfde tempo, zonder publiek. De melodie klinkt twee keer; de tweede keer vertraagt het aan het eind naar een groot slotakkoord met een laatste klap, zodat je hoort: dit is het einde. 104 BPM."
)

BPM = 104
KEY_UP = 0            # halve tonen omhoog bij de tweede keer (modulatie, klinkt opgewekt)
KICKOFF = False          # aftrapfluit (één lange stoot) aan het begin
FADE_IN = False          # begint zacht, alsof het al onder de laatste woorden speelde
END_WHISTLE = False  # eindsignaal (tuut-tuut-tuuut) als afsluiter
RIT = 0.6                    # vertraging in de laatste 2 tellen (60% langzamer op het slotakkoord)

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
LEAD = 2                     # tellen groove-aanloop vóór de melodie
END = LEAD + 16              # slotakkoord na twee keer de melodie
START = 1.3 if KICKOFF else 0.15


def bt(b):
    """Tel -> seconden, met een ritardando (vertraging) in de laatste 2 tellen voor het slot."""
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

    # aanloop (1 maat G) + twee keer het deuntje
    blocks = [(0, 0, [(0, CH0)], ['G1'])]
    for p in range(2):
        semis = KEY_UP if p == 1 else 0
        blocks.append((LEAD + 8 * p, semis, CHORDS, BASS))
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
        if b0 >= LEAD:  # melodie (de eerste keer zonder slotnoot, die valt samen met de tweede keer)
            for b, n, l in MELODY:
                if b0 == LEAD and b >= 8:
                    continue
                t0, t1 = bt(b0 + b), bt(b0 + b + l)
                events.append((humanize(t0, 0.01), transpose(transpose(n, 12), semis),
                               (t1 - t0) * (0.95 if b < 8 else 1.0)))

    # groot slotakkoord (na de vertraging)
    fin = [transpose(n, KEY_UP) for n in FINAL]
    e.add(poly(keys, fin, 2.2, bright=0.5, release=1.4, decay=2.4), at=bt(END), gain=-4, pan=-0.2)
    e.add(poly(keys, [transpose(n, -12) for n in fin[:2]], 2.2, bright=0.4, release=1.4, decay=2.4),
          at=bt(END), gain=-8, pan=-0.2)
    rest.add(upright_bass(transpose('G1', KEY_UP), 2.2, bright=0.4, release=0.6), at=bt(END), gain=-4)
    rest.add(reverb(group_clap(6), 1.4, 0.3), at=bt(END), gain=-6)

    mixdown = Track(bpm=BPM)
    mixdown.add(reverb(e.render(), decay=1.5, mix=0.2))
    mixdown.add(rest.render())
    w = whistling(events, vib=0.28, breath=0.023)              # zelfde zachte fluitklank als de intro
    mixdown.add(reverb(lowpass(w, 2400), decay=1.8, mix=0.34), at=0, gain=-10, pan=0.1)

    total = bt(END) + 3.2
    if KICKOFF:  # aftrap: één lange, duidelijke fluitstoot
        mixdown.add(reverb(pea_whistle(1.0), decay=1.4, mix=0.18), at=0.1, gain=-9, pan=0.15)
    if END_WHISTLE:  # eindsignaal na het slotakkoord
        mixdown.add(reverb(final_whistle(long=0.8, gap=0.75, kind='pea'), decay=1.4, mix=0.18),
                    at=bt(END) + 0.9, gain=-11, pan=0.15)
        total = bt(END) + 0.9 + 2.3 + 1.6
    x = mixdown.render(length=total)[:ns(total)]
    if FADE_IN:  # begint ~18 dB zachter en zwelt in 2 maten aan (spiegel van de intro-staart)
        tt = np.arange(len(x)) / SR
        rise = np.clip((tt - START) / (bt(LEAD + 4) - START), 0, 1)
        x = x * db(-18 * (1 - rise))[:, None]
    return finalize(x, fade_out=1.4, loud=2.0, trim=False)


CH0 = ['G3', 'B3', 'D4']
s_b = lambda beats: beats * 60 / BPM  # noqa: E731
