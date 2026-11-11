# Podcast Studio

Podcastmuziek maken (intro, outro, transities, achtergrond) in iteratierondes.
De gebruiker communiceert in het Nederlands; UI-teksten en optiebeschrijvingen ook in het Nederlands.

## Workflow per verzoek
1. Nieuw verzoek → `python studio.py new <id> --title "..." --category intro|outro|transitie|achtergrond|overig --prompt "<verzoek van gebruiker>" --note "..."`
2. Schrijf **3 duidelijk verschillende** opties: `projects/<id>/rounds/NN/a.py`, `b.py`, `c.py`.
3. `python studio.py render <id>` → WAV's + metadata in `round.json`. Controleer de output (duur, piek, RMS).
4. De webpagina (`python studio.py serve`, http://localhost:8765) pikt nieuwe rondes automatisch op.
5. Gebruiker geeft feedback op de pagina → lees met `python studio.py feedback <id>`.
6. Volgende ronde: `python studio.py round <id> --note "wat is er veranderd t.o.v. vorige ronde"`, kopieer/varieer de scripts. Bij duidelijke favoriet: 3 variaties daarop; anders: 3 nieuwe richtingen.
7. Gekozen versie (knop op de pagina) wordt gekopieerd naar `final/<id>.wav`.

Kleine aanpassing aan één optie: bewerk het script en `python studio.py render <id> b` (alleen optie b, laatste ronde). Oude rondes nooit overschrijven.

## Optie-script
```python
from engine import *
TITLE = "Korte naam"
DESCRIPTION = "1-2 zinnen: sfeer, instrumenten, tempo/toonsoort."
def render():
    s = Track(bpm=110)
    s.add(pad(chord('C4', 'maj7'), s.b(4)), beat=0, gain=-6, pan=-0.2)
    return finalize(reverb(s.render(), 1.8, 0.25), fade_out=0.5)
```
Engine (`engine/`): `core.py` = noten/akkoorden/schalen, oscillators, envelopes, filters (ook sweeps), stereo, effecten
(reverb, delay, chorus, drive, bitcrush, tape_stop, stutter, sidechain), `Track`, `mix`, `loopify`, `finalize`.
`instruments.py` = pad, soft_pad, keys, piano, pluck, bell, bass, sub, lead, chip, strum, poly; drums (kick, snare, clap,
hat, shaker, crash, tom); FX (riser, downlifter, whoosh, impact, reverse_swell, sparkle).

## Richtlijnen
- Altijd `finalize()` aan het eind (piek −1 dBFS). Achtergrondmuziek: `loud=0`, rustig middengebied (laat 1–4 kHz ruimte voor stemmen), loopbaar maken met `loopify()`.
- Intro/outro uit dezelfde 'familie' (zelfde toonsoort/motief) als de gebruiker daarvoor kiest.
- Synthetische klank is de beperking: geen realistische akoestische instrumenten of zang beloven.
