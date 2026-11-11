from engine import *

TITLE = "Fluitsignaal: piano + e-piano + hartslag"
DESCRIPTION = (
    "Zelfde opening. Daarna speelt de piano de melodie boven warme e-piano-akkoorden, met een zachte, doffe "
    "'hartslag'-kick op elke tel en een licht pompende pad. Dat geeft een rustig voortstuwend gevoel. "
    "Meest energiek van de drie, maar nog steeds ingetogen."
)

BPM = 92
T0 = 2.4
LENGTH = 10.0

CHORDS = [
    (0, ['A3', 'C4', 'E4']), (2, ['F3', 'A3', 'C4', 'E4']), (4, ['C3', 'G3', 'C4', 'E4']), (6, ['G3', 'B3', 'D4']),
]
FINAL = ['A3', 'C4', 'E4', 'B4']
BASS = ['A1', 'F1', 'C2', 'G1']
MELODY = [
    (0, 'E5', 1), (1, 'D5', 0.5), (1.5, 'C5', 0.5),
    (2, 'C5', 1), (3, 'A4', 1),
    (4, 'G4', 0.5), (4.5, 'A4', 0.5), (5, 'C5', 1),
    (6, 'D5', 1.5), (7.5, 'B4', 0.5),
    (8, 'A4', 3),
]


def stadium(s):
    dur_c = 6.5
    t = tvec(dur_c)
    ex = 0.5 + 0.45 * np.exp(-((t - 2.6) / 0.8) ** 2)
    c = fade(crowd(dur_c, excitement=ex), 0.3, 0)
    c = fade_away(c, start=2.4, dur=3.8, cutoff=400)
    s.add(c, at=0, gain=-1)
    s.add(reverb(final_whistle(long=0.9, gap=0.45), decay=2.0, mix=0.35), at=0.5, gain=-9, pan=0.15)


def render():
    s = Track(bpm=BPM)
    at = lambda beat: T0 + s.b(beat)  # noqa: E731
    stadium(s)

    # e-piano akkoorden + pompende pad + bas
    m = Track(bpm=BPM)
    for i, (beat, notes) in enumerate(CHORDS):
        m.add(poly(keys, notes, s.b(1.8), bright=0.3, release=0.4), at=at(beat), gain=-6, pan=-0.15)
        m.add(soft_pad(notes, s.b(2), attack=0.05, release=0.6, bright=0.4), at=at(beat), gain=-12)
        m.add(bass(BASS[i], s.b(1.8), shape='triangle', cutoff=300, env=300, sub=0.8), at=at(beat), gain=-8)
    m.add(poly(keys, FINAL, s.b(3), bright=0.3, release=1.2, decay=2.5), at=at(8), gain=-6, pan=-0.15)
    m.add(soft_pad(FINAL, s.b(3), attack=0.05, release=1.5, bright=0.4), at=at(8), gain=-12)
    m.add(sub('A1', s.b(3), release=0.8), at=at(8), gain=-8)
    music = m.render()
    pump = np.concatenate([np.ones(ns(T0)), sidechain(np.ones(len(music) - ns(T0)), BPM, depth=0.35, every=1)])
    music = music * pump[:len(music), None]

    # zachte hartslag-kick op elke tel
    for k in range(8):
        m2 = lowpass(kick(punch=0.5, decay=0.3, tone=50, click=0.05), 900)
        music_at = at(k)
        s.add(m2, at=music_at, gain=-10 if k % 2 == 0 else -13)

    # piano-melodie
    p = Track(bpm=BPM)
    for beat, note, length in MELODY:
        p.add(piano(note, s.b(length) + 0.2, bright=0.55, release=0.8), at=at(beat), pan=0.1)
    s.add(reverb(mix(music, p.render()), decay=2.0, mix=0.25))

    return finalize(s.render()[:ns(LENGTH)], fade_out=1.2, loud=1.5)
