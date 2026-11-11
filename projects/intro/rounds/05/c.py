from engine import *

TITLE = "Klassiek: strijkers + piano"
DESCRIPTION = (
    "Hetzelfde deuntje als A (108 BPM), nu met een klein strijkorkest: strijkers spelen de akkoorden met korte "
    "accenten op de tel, cello's tokkelen de baslijn (pizzicato) en een zachte pauk-achtige kick blijft. "
    "De piano speelt de melodie, met een glockenspiel op de slotnoot. Filmisch en sfeervol.\n"
    "Akkoorden Am – F – C – G – Am."
)

BPM = 108
T0 = 2.4
LENGTH = 10.0

CHORDS = [(0, ['A3', 'C4', 'E4']), (2, ['F3', 'A3', 'C4']), (4, ['G3', 'C4', 'E4']), (6, ['G3', 'B3', 'D4'])]
FINAL = ['A3', 'C4', 'E4', 'A4']
BASS = ['A2', 'F2', 'C3', 'G2']
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
    s.add(c, at=0, gain=-1)
    s.add(reverb(final_whistle(long=0.9, gap=0.45), decay=2.0, mix=0.35), at=0.5, gain=-9, pan=0.15)


def render():
    s = Track(bpm=BPM)
    at = lambda beat: T0 + s.b(beat)  # noqa: E731
    stadium(s)

    o = Track(bpm=BPM)
    # strijkers: aangehouden akkoord + kort accent op tel 2
    for beat, notes in CHORDS:
        o.add(strings(notes, s.b(2), attack=0.12, release=0.35, bright=0.45), at=at(beat), gain=-4)
        o.add(strings([transpose(n, 12) for n in notes[-2:]], s.b(0.4), attack=0.03, release=0.2, bright=0.55),
              at=at(beat + 1), gain=-12)
    o.add(strings(FINAL, s.b(4), attack=0.1, release=1.2, bright=0.4), at=at(8), gain=-4)
    o.add(strings(['A2'], s.b(4), attack=0.1, release=1.2, bright=0.3), at=at(8), gain=-7)
    # cello pizzicato in achtsten
    for i, root in enumerate(BASS):
        for e in range(4):
            note = root if e % 2 == 0 else transpose(root, 7 if e == 1 else 12)
            o.add(pizzicato(note, 0.25), at=at(i * 2 + e * 0.5), gain=-5 if e == 0 else -9, pan=-0.3)
    s.add(reverb(o.render(), decay=2.2, mix=0.28))

    # pauk-achtige kick
    for k in range(9):
        s.add(lowpass(kick(punch=0.4, decay=0.4, tone=55, click=0.0), 600), at=at(k),
              gain=-11 if k % 2 == 0 else -15)

    # piano-melodie + glockenspiel op de slotnoot
    p = Track(bpm=BPM)
    for beat, note, length in MELODY:
        p.add(piano(note, s.b(length) + 0.2, bright=0.55, release=0.8), at=at(beat), pan=0.15)
    p.add(bell('A5', 0.2, 2.0, 0.3), at=at(8), gain=-12, pan=0.3)
    s.add(reverb(p.render(), decay=2.2, mix=0.25), gain=-1)

    return finalize(s.render()[:ns(LENGTH)], fade_out=1.6, loud=1.5)
