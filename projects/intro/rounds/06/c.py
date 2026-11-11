from engine import *

TITLE = "Vibrafoon, nieuw deuntje"
DESCRIPTION = (
    "Compleet nieuwe melodie in D mineur op vibrafoon: zachte metalen klanken met een licht trillende "
    "'tremolo'. Klinkt dromerig en nostalgisch. Eronder een zachte pad, subbas en de hartslag-kick.\n"
    "Akkoorden Dm – Bb – F – C – Dm, 104 BPM."
)

BPM = 104
T0 = 2.4
LENGTH = 10.0

CHORDS = [['D3', 'F3', 'A3'], ['Bb2', 'D3', 'F3'], ['F3', 'A3', 'C4'], ['C3', 'G3', 'E4']]
BASS = ['D2', 'Bb1', 'F1', 'C2']
FINAL = ['D3', 'F3', 'A3', 'D4']
MELODY = [
    (0, 'A4', 1), (1, 'F4', 0.5), (1.5, 'A4', 0.5),
    (2, 'D5', 1.5), (3.5, 'C5', 0.5),
    (4, 'A4', 1), (5, 'C5', 0.5), (5.5, 'A4', 0.5),
    (6, 'G4', 1), (7, 'E4', 1),
    (8, 'D4', 4),
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

    v = Track(bpm=BPM)
    # vibrafoon-akkoorden op tel 1 en de 'en' van 2
    for i, notes in enumerate(CHORDS):
        for off, dbv in ((0, -9), (1.5, -13)):
            for n in notes:
                v.add(vibraphone(transpose(n, 12), s.b(1), release=0.6, bright=0.3), at=at(i * 2 + off), gain=dbv,
                      pan=-0.3)
    for n in FINAL:
        v.add(vibraphone(transpose(n, 12), s.b(3), release=1.5, bright=0.3), at=at(8), gain=-9, pan=-0.3)
    # melodie
    for beat, note, length in MELODY:
        last = beat == 8
        v.add(vibraphone(note, s.b(length), release=1.5 if last else 0.5, bright=0.5, decay=3.5 if last else 2.0),
              at=at(beat), gain=0, pan=0.15)
    s.add(reverb(v.render(), decay=2.2, mix=0.28))

    # zachte pad + subbas + kick
    for i, notes in enumerate(CHORDS):
        s.add(soft_pad(notes, s.b(2), attack=0.1, release=0.6, bright=0.3), at=at(i * 2), gain=-14)
        s.add(sub(BASS[i], s.b(1.8), release=0.2), at=at(i * 2), gain=-9)
    s.add(soft_pad(FINAL, s.b(3), attack=0.1, release=1.2, bright=0.3), at=at(8), gain=-14)
    s.add(sub('D2', s.b(3), release=0.8), at=at(8), gain=-9)
    for k in range(9):
        s.add(lowpass(kick(punch=0.5, decay=0.3, tone=50, click=0.05), 900), at=at(k),
              gain=-11 if k % 2 == 0 else -14)

    return finalize(s.render(length=LENGTH)[:ns(LENGTH)], fade_out=1.6, loud=1.5, trim=False)
