from engine import *

TITLE = "Lege tribune"
DESCRIPTION = (
    "Een brullend stadion lost op in galm, tot alleen de wind over een lege tribune overblijft. "
    "Een getokkelde gitaar-arpeggio en een eenzame, fluitachtige melodie vertellen verder. Filmisch en weemoedig: "
    "D mineur, 70 BPM.\nAkkoorden Dm – Bb – F – C – Dm. ±21 sec."
)

BPM = 70
T0 = 3.0

ARP = [  # per maat: [laag, kwint, octaaf, terts]
    ['D3', 'A3', 'D4', 'F4'], ['Bb2', 'F3', 'Bb3', 'D4'], ['F2', 'C3', 'F3', 'A3'], ['C3', 'G3', 'C4', 'E4'],
]
PATTERN = [0, 1, 2, 3, 2, 1, 2, 1]
PADS = [chord('D3', 'min'), chord('Bb2', 'maj'), chord('F3', 'maj'), chord('C3', 'maj'), chord('D3', 'min')]
MELODY = [
    (0, 'A4', 2), (2, 'G4', 1), (3, 'F4', 1),
    (4, 'F4', 2), (6, 'D4', 2),
    (8, 'C5', 2), (10, 'A4', 1), (11, 'F4', 1),
    (12, 'G4', 3), (15, 'E4', 1),
    (16, 'D4', 4),
]


def render():
    s = Track(bpm=BPM)
    at = lambda beat: T0 + s.b(beat)  # noqa: E731
    total = T0 + s.b(20) + 4

    # --- brullend stadion dat in galm oplost
    dur_c = 11.0
    c = crowd(dur_c, excitement=ramp(0.85, 0.5, dur_c))
    c = fade_away(c, start=1.8, dur=8.5, cutoff=350, reverb_mix=0.45)
    s.add(c, at=0, gain=-5)

    # --- wind over de lege tribune, blijft het hele stuk
    w = wind(total, strength=0.4)
    w = fade(w, 4.0, 4.0)
    s.add(w, at=1.5, gain=-17)

    # --- gitaar
    g = Track(bpm=BPM)
    for bar, notes in enumerate(ARP):
        for i, idx in enumerate(PATTERN):
            g.add(pluck(notes[idx], 1.6, bright=0.45), at=at(bar * 4 + i * 0.5), gain=-4 if i == 0 else -7,
                  pan=-0.25 + 0.1 * idx)
    g.add(strum(['D3', 'A3', 'D4', 'F4', 'A4'], 4.0, spread=0.05, bright=0.45), at=at(16), gain=-3)
    s.add(reverb(g.render(), decay=2.0, mix=0.25), gain=0)

    # --- strijkers-pad, zacht eronder
    for i, notes in enumerate(PADS):
        s.add(soft_pad(notes, s.b(4), attack=1.2, release=1.5, bright=0.3), at=at(i * 4), gain=-15)

    # --- eenzame fluit
    fl = Track(bpm=BPM)
    for beat, note, length in MELODY:
        fl.add(lead(note, s.b(length) * 0.95, shape='triangle', cutoff=2500, vib=0.12, release=0.3), at=at(beat), pan=0.2)
    s.add(reverb(fl.render(), decay=3.0, mix=0.35), gain=-5)

    return finalize(s.render(length=total), fade_out=2.0, loud=1.0)
