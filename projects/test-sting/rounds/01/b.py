from engine import *

TITLE = "Energiek & punchy"
DESCRIPTION = "Korte riser die eindigt in een klap met bas, clap en een synth-stab. Upbeat, radio-achtig."


def render():
    s = Track(bpm=124)
    s.add(riser(s.b(2), 400, 7000, tone=0.25, note='A3'), beat=0, gain=-8)
    hit = 2
    s.add(impact(1.2, low=45, brightness=0.6), beat=hit, gain=-3)
    s.add(clap(), beat=hit, gain=-6)
    s.add(bass('A1', s.b(1.5), cutoff=300, env=1800), beat=hit, gain=-3)
    stab = mix(pad(chord('A3', 'min7'), s.b(0.5), bright=0.8, attack=0.005, release=0.3))
    s.add(delay(stab, s.b(0.75), feedback=0.35, mix=0.35), beat=hit, gain=-4)
    s.add(hat(), beat=hit + 0.5, gain=-12)
    s.add(hat(open=True), beat=hit + 1, gain=-14)
    return finalize(s.render(), fade_out=0.4)
