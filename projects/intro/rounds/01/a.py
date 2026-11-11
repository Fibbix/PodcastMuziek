from engine import *

TITLE = "Het laatste fluitsignaal"
DESCRIPTION = (
    "Een vol stadion, dan klinkt het laatste fluitsignaal. Het publiek juicht nog één keer en sterft "
    "daarna langzaam weg, alsof je steeds verder wegloopt. Daaruit komt een sobere solopiano op: A mineur, 76 BPM.\n"
    "Akkoorden Am – F – Dm – E – Am. ±21 sec."
)

BPM = 76
T0 = 3.6  # piano begint na het fluitsignaal

MELODY = [  # (beat, noot, lengte in beats)
    (0, 'A4', 1), (1, 'C5', 1), (2, 'E5', 2),
    (4, 'F5', 1), (5, 'E5', 0.5), (5.5, 'D5', 0.5), (6, 'C5', 2),
    (8, 'D5', 1), (9, 'F5', 1), (10, 'E5', 1), (11, 'D5', 1),
    (12, 'C5', 1), (13, 'B4', 1), (14, 'G#4', 2),
    (16, 'A4', 4),
]
LEFT = [['A2', 'E3', 'A3', 'C4'], ['F2', 'C3', 'F3', 'A3'], ['D2', 'A2', 'D3', 'F3'], ['E2', 'B2', 'E3', 'G#3']]


def render():
    s = Track(bpm=BPM)
    at = lambda beat: T0 + s.b(beat)  # noqa: E731

    # --- publiek + fluitsignaal
    dur_c = 13.0
    t = tvec(dur_c)
    ex = 0.5 + 0.45 * np.exp(-((t - 3.8) / 1.2) ** 2)  # juichen na het eindsignaal
    c = crowd(dur_c, excitement=ex)
    c = fade_away(c, start=4.0, dur=8.5, cutoff=400)
    s.add(c, at=0, gain=-5)
    s.add(reverb(final_whistle(), decay=2.2, mix=0.35), at=1.2, gain=-9, pan=0.15)

    # --- piano
    piano_track = Track(bpm=BPM)
    for beat, note, length in MELODY:
        piano_track.add(piano(note, s.b(length) + 0.3, bright=0.4, release=0.8), at=at(beat), gain=0, pan=0.1)
    for bar, notes in enumerate(LEFT):
        for i, note in enumerate(notes):
            piano_track.add(piano(note, s.b(2.5), bright=0.25, release=0.8), at=at(bar * 4 + i), gain=-7, pan=-0.15)
    for note in ['A2', 'E3', 'A3', 'C4']:
        piano_track.add(piano(note, s.b(4), bright=0.25, release=2.0), at=at(16), gain=-7, pan=-0.15)
    s.add(reverb(piano_track.render(), decay=2.6, mix=0.3, tone=5000), gain=0)

    return finalize(s.render(), fade_out=1.5, loud=1.0)
