from engine import *

TITLE = "Oude radio-uitzending"
DESCRIPTION = (
    "Het stadion klinkt alsof het uit een oude radio komt, met vinylgekraak erbij. Langzaam vervaagt het, "
    "en een warme elektrische piano met een zachte pad neemt het over. Nostalgisch en weemoedig: E mineur, 80 BPM, "
    "met een lichte 'tape-wobble'.\nAkkoorden Em9 – Cmaj7 – G – B7sus4/B7 – Em. ±19 sec."
)

BPM = 80
T0 = 3.2

CHORDS = [  # (beat, noten, lengte)
    (0, ['E3', 'G3', 'B3', 'D4', 'F#4'], 4),
    (4, ['C3', 'E3', 'G3', 'B3'], 4),
    (8, ['G3', 'B3', 'D4'], 4),
    (12, ['B2', 'E3', 'F#3', 'A3'], 2),
    (14, ['B2', 'D#3', 'F#3', 'A3'], 2),
    (16, ['E3', 'G3', 'B3', 'F#4'], 4),
]
BASS = [(0, 'E2'), (4, 'C2'), (8, 'B1'), (12, 'B1'), (16, 'E2')]
MELODY = [
    (0, 'B4', 2), (2, 'G4', 1), (3, 'A4', 1),
    (4, 'G4', 2), (6, 'E4', 2),
    (8, 'D4', 1), (9, 'E4', 1), (10, 'G4', 1), (11, 'B4', 1),
    (12, 'A4', 2), (14, 'F#4', 2),
    (16, 'E4', 4),
]


def render():
    s = Track(bpm=BPM)
    at = lambda beat: T0 + s.b(beat)  # noqa: E731

    # --- stadion via een oude radio
    dur_c = 10.0
    t = tvec(dur_c)
    c = crowd(dur_c, excitement=0.55 + 0.3 * slow_noise(dur_c, 0.4))
    c = old_radio(c)
    c = fade_away(c, start=2.5, dur=7.0, cutoff=700)
    s.add(c, at=0, gain=-6)

    # --- muziek
    m = Track(bpm=BPM)
    for beat, notes, length in CHORDS:
        m.add(poly(keys, notes, s.b(length), bright=0.35, release=0.8, decay=2.5), at=at(beat), gain=-3, pan=-0.1)
        m.add(soft_pad(notes, s.b(length), attack=0.8, release=1.5, bright=0.25), at=at(beat), gain=-14)
    for beat, note in BASS:
        m.add(sub(note, s.b(3.5), release=0.5), at=at(beat), gain=-9)
    for beat, note, length in MELODY:
        m.add(keys(note, s.b(length), bright=0.55, release=0.6, decay=2.0), at=at(beat), gain=-1, pan=0.15)
    music = m.render()
    music = chorus(music, depth_ms=1.5, rate=0.35, mix=0.35)  # tape-wobble
    music = lowpass(music, 7000)
    s.add(reverb(music, decay=2.2, mix=0.25), gain=0)

    # --- vinylgekraak over het hele stuk
    total = T0 + s.b(20) + 3
    s.add(fade(crackle(total, density=10), 0.5, 3.0), at=0, gain=-22)

    return finalize(s.render(), fade_out=1.5, loud=1.0)
