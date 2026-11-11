from engine import *

TITLE = "Energiek: met band"
DESCRIPTION = (
    "Zelfde opening, maar na het fluitsignaal valt een drumfill in en speelt een volle 'band' (110 BPM): "
    "kick, snare op 2 en 4, hihats, een bas in achtsten, e-piano-akkoorden op elke tel en de pianomelodie erboven. "
    "Eindigt met een crash op het slotakkoord."
)

BPM = 110
T0 = 2.4
LENGTH = 10.0

CHORDS = [
    (0, ['A3', 'C4', 'E4']), (2, ['F3', 'A3', 'C4', 'E4']), (4, ['C4', 'E4', 'G4']), (6, ['G3', 'B3', 'D4']),
]
FINAL = ['A3', 'C4', 'E4']
BASS = ['A1', 'F1', 'C2', 'G1']
MELODY = [
    (0, 'E5', 1), (1, 'D5', 0.5), (1.5, 'C5', 0.5),
    (2, 'C5', 1), (3, 'A4', 1),
    (4, 'G4', 0.5), (4.5, 'A4', 0.5), (5, 'C5', 1),
    (6, 'D5', 1), (7, 'B4', 1),
    (8, 'A4', 4),
]


def stadium(s):
    dur_c = 5.5
    t = tvec(dur_c)
    ex = 0.6 + 0.4 * np.exp(-((t - 2.4) / 0.8) ** 2)
    c = fade(crowd(dur_c, excitement=ex), 0.3, 0)
    c = fade_away(c, start=2.2, dur=3.0, cutoff=500)
    s.add(c, at=0, gain=-1)
    s.add(reverb(final_whistle(long=0.8, gap=0.42), decay=2.0, mix=0.35), at=0.4, gain=-9, pan=0.15)


def render():
    s = Track(bpm=BPM)
    at = lambda beat: T0 + s.b(beat)  # noqa: E731
    stadium(s)

    # --- drums
    d = Track(bpm=BPM)
    for b_, note in ((-1, 'D3'), (-0.5, 'A2')):      # tom-fill naar binnen
        d.add(tom(note, 0.3), at=at(b_), gain=-4, pan=0.3 if note == 'D3' else -0.3)
    d.add(snare(), at=at(-0.25), gain=-8)
    for bar in range(4):
        o = bar * 2
        d.add(kick(punch=1.0, decay=0.35), at=at(o), gain=-3)
        d.add(snare(), at=at(o + 1), gain=-5)
        if bar % 2 == 1:
            d.add(kick(punch=1.0, decay=0.3), at=at(o + 1.5), gain=-6)
        for e in range(4):
            d.add(hat(), at=at(o + e * 0.5), gain=-13 if e % 2 else -10, pan=0.35)
    d.add(snare(), at=at(7.5), gain=-7)
    d.add(snare(), at=at(7.75), gain=-5)
    for hit in (0, 8):
        d.add(crash(1.8), at=at(hit), gain=-10)
    d.add(kick(punch=1.2, decay=0.5), at=at(8), gain=-2)
    s.add(reverb(d.render(), decay=1.0, mix=0.12))

    # --- bas in achtsten
    for i, root in enumerate(BASS):
        for e in range(4):
            s.add(bass(root, s.b(0.4), cutoff=500, env=1200), at=at(i * 2 + e * 0.5), gain=-7)
    s.add(bass('A1', s.b(2), cutoff=500, env=1200, release=0.4), at=at(8), gain=-7)

    # --- e-piano op elke tel + melodie
    m = Track(bpm=BPM)
    for beat, notes in CHORDS:
        for q in range(2):
            m.add(poly(keys, notes, s.b(0.8), bright=0.45, release=0.2), at=at(beat + q), gain=-8, pan=-0.2)
        m.add(soft_pad(notes, s.b(2), attack=0.05, release=0.4, bright=0.5), at=at(beat), gain=-15)
    m.add(poly(keys, FINAL, s.b(4), bright=0.45, release=1.0, decay=2.0), at=at(8), gain=-7, pan=-0.2)
    for beat, note, length in MELODY:
        m.add(piano(note, s.b(length) + 0.15, bright=0.7, release=0.6), at=at(beat), gain=0, pan=0.1)
    m.add(piano('A5', s.b(4), bright=0.5, release=0.8), at=at(8), gain=-8, pan=0.1)
    s.add(reverb(m.render(), decay=1.6, mix=0.2))

    return finalize(s.render()[:ns(LENGTH)], fade_out=1.4, loud=2.5)
