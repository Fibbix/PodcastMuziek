from engine import *

TITLE = "Toeter i.p.v. alle fietsbellen"
DESCRIPTION = (
    "Als A, maar de fietsbel aan het begin én het eind is vervangen door een zachte autotoeter: aan het begin één korte toet in de verte, op de landing toet-toet (gestemd op G–B). Geen fietsbel meer."
)

BPM = 104
T0 = 0.5
OVERALL = -7.0
MELODY = [(0, 'B4'), (0.5, 'C5'), (1, 'D5'), (1.5, 'G5'), (2, 'E5'), (2.5, 'D5'), (3, 'C5'), (3.5, 'A4')]
LANDING = 'G4'
BELL = dict(rings=2, ring_dur=0.15, gap=0.08)  # oude bel: alleen nog voor de timing van de uitfade
HORN = dict(toots=2, toot_dur=0.3, gap=0.16, pitches=(392.0, 494.0), soft=0.8, release=0.15)
HORN_GAIN = -3
HORN_LP = 3000
OPEN_HORN = True   # True = ook het belletje aan het begin wordt een (enkele, verre) toeter
OPEN_HORN_AT = 0.1
OPEN_HORN_GAIN = -10
BELL_AT = 4.5    # tel (bij 'landing')
BELL_MODE = 'landing'  # 'after' = na de uitgefade muziek, 'landing' = tijdens de landing, muziek fadet daarna
BELL_GAIN = -21
BELL_LP = 5000
BELL_REV = 0.4
BELL_PAN = 0.65
TAIL = 2.0     # s natuurlijke uitklank na de bel (alleen de laatste 0,5 s gefadet)


def render():
    seed(1000 + ord("a"))  # zelfde toeval als vorige A/B
    s = Track(bpm=BPM)
    at = lambda b: T0 + s.b(humanize(b, 0.006, BPM))  # noqa: E731
    exact = lambda b: T0 + s.b(b)  # noqa: E731
    total = exact(4) + 1.45

    # stad + fietsbel
    s.add(fade(city(total, traffic=0.5, voices=0.5), 0.5, 1.2), at=0, gain=1)
    open_bell = reverb(highpass(bike_bell(2, 0.18, 0.09), 600), 0.9, 0.2)
    if not OPEN_HORN:
        s.add(open_bell, at=0.02, gain=-15, pan=0.35)

    # groove (één maat)
    e = Track(bpm=BPM)
    for b, notes in ((0, ['G3', 'B3', 'D4']), (0.75, ['G3', 'B3', 'D4']), (1.5, ['G3', 'B3', 'D4']),
                     (2, ['C4', 'E4', 'G4']), (2.75, ['C4', 'E4', 'G4']), (3.5, ['D4', 'F#4', 'A4'])):
        e.add(poly(keys, notes, s.b(0.5), bright=0.5, release=0.12), at=at(b),
              gain=(-7 if b % 1 == 0 else -9) + vel(1), pan=-0.2)
    for b, n in ((0, 'G2'), (1, 'B2'), (2, 'C3'), (3, 'D3')):  # tel 2 = C (paste niet bij B)
        s.add(upright_bass(n, s.b(0.9), bright=0.45), at=at(b), gain=-6 + vel(1))
    for b in (1, 3):
        s.add(reverb(group_clap(4), 1.0, 0.2), at=at(b), gain=-10, pan=0.15)
    for h in range(8):
        s.add(shaker(0.07), at=at(h * 0.5), gain=(-21 if h % 2 else -24) + vel(1.5), pan=0.4)
    # melodie (e-piano); rng-toestand bewaren zodat de rest precies zo blijft als vorige A
    state = rng().bit_generator.state
    for i, (b, n) in enumerate(MELODY):
        nxt = MELODY[i + 1][0] if i + 1 < len(MELODY) else 4
        e.add(keys(n, s.b((nxt - b) * 0.9), bright=0.55, release=0.15), at=at(b), gain=-9 + vel(1), pan=0.1)
    rng().bit_generator.state = state

    # landing op G (tel 4)
    e.add(poly(keys, ['G3', 'B3', 'D4', 'G4'], s.b(2.4), bright=0.45, release=1.0, decay=2.0), at=exact(4),
          gain=-6, pan=-0.2)
    e.add(keys(LANDING, s.b(2.0), bright=0.5, release=1.0, decay=2.0), at=exact(4), gain=-9, pan=0.1)
    s.add(upright_bass('G1', s.b(2), bright=0.4, release=0.5), at=exact(4), gain=-5)
    s.add(reverb(group_clap(5), 1.2, 0.25), at=exact(4), gain=-8, pan=0.1)
    s.add(reverb(e.render(), decay=1.5, mix=0.2))
    base = s.render(length=total)[:ns(total)]
    # oude slotbelletje alleen nog voor de normalisatie (zodat de rest exact gelijk blijft aan vorige B)
    old = Track(bpm=BPM)
    if OPEN_HORN:
        old.add(open_bell, at=0.02, gain=-15, pan=0.35)
    old.add(base).add(reverb(highpass(bike_bell(1, 0.03, 0.0), 600), 1.2, 0.25), at=exact(5), gain=-22, pan=0.35)
    ref = old.render(length=total)[:ns(total)]
    g = db(2.0) / np.max(np.abs(highpass(to_stereo(ref), 25)))
    ring = BELL['rings'] * (BELL['ring_dur'] + BELL['gap'])
    if BELL_MODE == 'after':
        music_end = total                                   # muziek exact als vorige C (uitgefaded op `total`)
        bell_t = total - 0.1
    else:
        bell_t = exact(BELL_AT)
        music_end = max(total, bell_t + ring + 0.15 + 1.0)  # uitfade (1 s) begint pas na de bel
    mus = s.render(length=music_end)[:ns(music_end)]
    x = gain(fade(limit(highpass(to_stereo(mus), 25) * g, -1.0), 0.5, 1.0), OVERALL)

    # toeter apart, niet meegefadet: eigen natuurlijke uitklank
    seed(5)
    horn = reverb(lowpass(highpass(car_horn(**HORN), 200), HORN_LP), 1.2, BELL_REV)
    end = max(music_end, bell_t + ring + TAIL)
    bt = Track(bpm=BPM)
    bt.add(horn, at=bell_t, gain=HORN_GAIN, pan=BELL_PAN)
    if OPEN_HORN:
        h1 = reverb(lowpass(highpass(car_horn(1, 0.4, 0.0, soft=0.85, release=0.2), 200), 2500), 1.0, 0.35)
        bt.add(h1, at=OPEN_HORN_AT, gain=OPEN_HORN_GAIN, pan=0.35)
    bx = gain(highpass(to_stereo(bt.render(length=end)[:ns(end)]), 25) * g, OVERALL)
    out = np.zeros((ns(end), 2))
    out[:len(x)] += x
    out += bx
    out = fade(out, 0, 0.5)
    return limit(out, -1.0)
