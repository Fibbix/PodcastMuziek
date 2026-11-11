from engine import *

TITLE = "Energiek: elektronisch met drop"
DESCRIPTION = (
    "Tijdens het fluitsignaal bouwt een riser op die in een dikke klap eindigt. Daarna volgt een elektronische "
    "beat op 120 BPM: kick op elke tel, clap, open hihats, een bas tussen de tellen, een snelle getokkelde arpeggio "
    "en een pompende pad. De pianomelodie gaat erbovenop. Eindigt met een klap en een uitwaaierende sweep."
)

BPM = 120
T0 = 2.4
LENGTH = 10.0

CHORDS = [
    (0, ['A3', 'C4', 'E4']), (2, ['F3', 'A3', 'C4', 'E4']), (4, ['C4', 'E4', 'G4']), (6, ['G3', 'B3', 'D4']),
]
ARP = [['A3', 'C4', 'E4', 'A4'], ['F3', 'A3', 'C4', 'F4'], ['C4', 'E4', 'G4', 'C5'], ['G3', 'B3', 'D4', 'G4']]
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

    # --- riser naar de drop, klap op T0 en op het slotakkoord
    s.add(riser(1.3, 300, 6000, tone=0.3, note='A3'), at=T0 - 1.3, gain=-9)
    s.add(impact(1.5, low=45, brightness=0.5), at=T0, gain=-5)
    s.add(impact(1.8, low=45, brightness=0.4), at=at(8), gain=-6)
    s.add(downlifter(2.0, 4000, 200), at=at(8), gain=-14)

    # --- drums
    d = Track(bpm=BPM)
    for k in range(8):
        d.add(kick(punch=1.1, decay=0.3), at=at(k), gain=-3)
        d.add(hat(open=True, decay=0.18), at=at(k + 0.5), gain=-13, pan=0.3)
        d.add(hat(), at=at(k + 0.25), gain=-19, pan=-0.3)
        d.add(hat(), at=at(k + 0.75), gain=-19, pan=-0.3)
        if k % 2 == 1:
            d.add(clap(), at=at(k), gain=-7)
    s.add(reverb(d.render(), decay=0.9, mix=0.1))

    # --- muziek (pompend)
    m = Track(bpm=BPM)
    for i, (beat, notes) in enumerate(CHORDS):
        m.add(pad(notes, s.b(2), bright=0.55, attack=0.01, release=0.3, detune=0.15), at=at(beat), gain=-11)
        for e in range(2):
            m.add(bass(BASS[i], s.b(0.35), shape='saw', cutoff=600, env=1500), at=at(beat + e + 0.5), gain=-6)
        for x in range(8):
            m.add(pluck(ARP[i][x % 4], 0.4, bright=0.6), at=at(beat + x * 0.25),
                  gain=-11, pan=-0.4 + 0.25 * (x % 4))
    music = m.render(length=LENGTH + 1)
    a, b = ns(T0), ns(at(8))
    pump = np.ones(len(music))
    pump[a:b] = sidechain(np.ones(b - a), BPM, depth=0.6, every=1)
    music = delay(music * pump[:, None], s.b(0.75), feedback=0.25, mix=0.15)[:len(music)]
    s.add(reverb(music, decay=1.5, mix=0.18))

    # --- slotakkoord + melodie
    f = Track(bpm=BPM)
    f.add(pad(FINAL, s.b(3), bright=0.45, attack=0.01, release=1.5), at=at(8), gain=-10)
    f.add(sub('A1', s.b(3), release=0.8), at=at(8), gain=-6)
    for beat, note, length in MELODY:
        f.add(piano(note, s.b(length) + 0.15, bright=0.75, release=0.6), at=at(beat), gain=0, pan=0.1)
    f.add(piano('A5', s.b(4), bright=0.5, release=0.8), at=at(8), gain=-8, pan=0.1)
    s.add(reverb(f.render(), decay=1.8, mix=0.22))

    return finalize(s.render()[:ns(LENGTH)], fade_out=1.4, loud=3.0)
