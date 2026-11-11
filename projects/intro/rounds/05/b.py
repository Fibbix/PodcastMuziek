from engine import *

TITLE = "Akoestisch: gitaar + contrabas"
DESCRIPTION = (
    "Hetzelfde deuntje als A (108 BPM), nu akoestisch: een geslagen gitaar speelt de akkoorden ritmisch, een tweede "
    "gitaar speelt de melodie, er is een getokkelde contrabas en de zachte kick blijft. Warm, 'singer-songwriter'.\n"
    "Akkoorden Am – F – C – G – Am."
)

BPM = 108
T0 = 2.4
LENGTH = 10.0

# gitaargrepen (laag -> hoog)
SHAPES = [
    (0, ['A2', 'E3', 'A3', 'C4', 'E4']),
    (2, ['F2', 'C3', 'F3', 'A3', 'C4']),
    (4, ['C3', 'E3', 'G3', 'C4', 'E4']),
    (6, ['G2', 'B2', 'D3', 'G3', 'B3']),
]
FINAL = ['A2', 'E3', 'A3', 'C4', 'E4']
BASS = ['A1', 'F1', 'C2', 'G1']
STRUM = [(0.0, 'down', 0), (1.0, 'down', -3), (1.5, 'up', -7)]  # (beat binnen akkoord, richting, dB)
MELODY = [
    (0, 'E5', 1), (1, 'D5', 0.5), (1.5, 'C5', 0.5),
    (2, 'C5', 1), (3, 'A4', 1),
    (4, 'G4', 0.5), (4.5, 'A4', 0.5), (5, 'C5', 1),
    (6, 'D5', 1), (7, 'B4', 1),
    (8, 'A4', 4),
]


def stadium(s):
    dur_c = 6.5
    t = tvec(dur_c)
    ex = 0.5 + 0.45 * np.exp(-((t - 2.6) / 0.8) ** 2)
    c = fade(crowd(dur_c, excitement=ex), 0.3, 0)
    c = fade_away(c, start=2.4, dur=3.8, cutoff=400)
    s.add(c, at=0, gain=-6)
    s.add(reverb(final_whistle(long=0.9, gap=0.45), decay=2.0, mix=0.35), at=0.5, gain=-9, pan=0.15)


def render():
    s = Track(bpm=BPM)
    at = lambda beat: T0 + s.b(beat)  # noqa: E731
    stadium(s)

    # slaggitaar
    g = Track(bpm=BPM)
    for i, (beat, shape) in enumerate(SHAPES):
        for off, direction, dbv in STRUM:
            notes = shape if direction == 'down' else shape[::-1][:3]
            g.add(strum(notes, s.b(0.9), spread=0.012, instrument=guitar, bright=0.45), at=at(beat + off), gain=dbv)
    g.add(strum(FINAL, s.b(5), spread=0.03, instrument=guitar, bright=0.45, decay=6.0, release=1.0), at=at(8), gain=0)
    gb = g.render()
    gb = drive(gb / (np.max(np.abs(gb)) + 1e-9), 2.0)  # aanslagen iets afvlakken
    s.add(reverb(gb, decay=1.4, mix=0.18), gain=-3, pan=-0.25)

    # contrabas
    for i, root in enumerate(BASS):
        s.add(upright_bass(root, s.b(1.0)), at=at(i * 2), gain=-6)
        s.add(upright_bass(root if i % 2 else transpose(root, 7), s.b(0.8)), at=at(i * 2 + 1), gain=-9)
    s.add(upright_bass('A1', s.b(3), release=0.6), at=at(8), gain=-6)

    # zachte kick
    for k in range(9):
        s.add(lowpass(kick(punch=0.5, decay=0.3, tone=50, click=0.05), 900), at=at(k),
              gain=-11 if k % 2 == 0 else -14)

    # melodiegitaar
    m = Track(bpm=BPM)
    for beat, note, length in MELODY:
        m.add(guitar(note, s.b(length) + 0.3, bright=0.6, decay=4.0 if beat == 8 else 2.0,
                     release=0.8 if beat == 8 else 0.08), at=at(beat))
    mb = m.render()
    mb = drive(mb / (np.max(np.abs(mb)) + 1e-9), 1.8)
    s.add(reverb(mb, decay=1.8, mix=0.22), gain=-2, pan=0.2)

    return finalize(s.render(length=LENGTH)[:ns(LENGTH)], fade_out=1.6, loud=3.0, trim=False)
