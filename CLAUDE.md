# Podcast Studio

Podcastmuziek maken (intro, outro, transities) in iteratierondes van telkens 3 opties.
De gebruiker communiceert in het Nederlands; UI-teksten en optiebeschrijvingen ook in het Nederlands.

> **Houd dit bestand bij.** Werk na elke ronde het logboek (§3) en de geleerde voorkeuren (§4) bij:
> wat er veranderd is, wat de feedback was en welke richting we op gaan. Nieuwe sessies starten hier.

## 1. De podcast: "Verdwenen maar niet vergeten"
- Studentenproject (7 makers) in het kader van **70 jaar Eredivisie**. Per aflevering staat één **verdwenen profclub**
  centraal: clubs die ooit Eredivisie speelden en nu niet meer in het betaald voetbal zitten.
  Afl. 1 **FC Wageningen** (o.a. 1-6 bij PSV in 1977, Ab de Wit / nacompetitie, faillissement 1992, stadion staat er nog),
  afl. 2 **HFC Haarlem** (Ruud Gullit, Europees voetbal jaren '80, Loezjniki-ramp, faillissement 2010).
- Vorm: talkshow met 2 presentatoren + 2 gasten (oud-spelers/trainers), afgewisseld met reportages; ~30–45 min;
  chronologische tijdlijn met pieken en dalen; eindigt met de huidige situatie + teaser voor de volgende club.
- Doelgroep: voetbalnostalgici en -nerds (25–50 jr) + mensen uit de stad van de club. Toon: rustig, verhalend, nostalgisch.
  Opnames bij voorkeur op locatie (lege tribunes, kantine) → echte omgevingsgeluiden mogelijk.
- Referenties: Staantribune Podcast, Hard Gras, NOS *Vergeten Helden* (Tom Egbers), Van Wasmand tot Wereldtop.
- De gebruiker doet **sound design + montage**.

### Geluidsvormgeving (brief van de gebruiker)
- **Intro:** rustig, licht sombere melodie; op de achtergrond een volle tribune die langzaam wegsterft = symbool voor de verdwenen club.
- **Outro:** sluit het verhaal positief af (toekomst van de club) → energieker dan de intro, **géén** tribunegeluid.
- **Transities:** verschillende soorten — één voor verhalen over **glorie**, één voor **diepe dalen**; belangrijk om goede
  en slechte momenten in de tijdlijn te scheiden en in te leiden.
- **Geen achtergrondmuziek** onder de interviews.

## 2. Stand van zaken (bijgewerkt 2026-11-11)
| Project | Status | Basis voor verder werk |
|---|---|---|
| `intro` | Ronde 10, nog niet definitief gekozen | `projects/intro/rounds/10/` |
| outro | nog niet gestart | moet aansluiten op de intro (zelfde familie: A mineur/C-groot, piano/e-piano) |
| transities (glorie / dal) | nog niet gestart | — |

**Huidige intro (ronde 10), 10,0 s:**
- 0–2,4 s: synthetisch stadionpubliek (`crowd`), scheidsrechter fluit af (`final_whistle(long=0.8, gap=0.75)`,
  start 0,15 s, gain −14 dB): tuut – tuut – tuuut met echte pauzes. Publiek juicht nog even en sterft weg
  (`fade_away`: volume omlaag + filter dicht, start 2,4 s, 3,8 s lang).
- Vanaf 2,4 s: **100 BPM**, Am – F – C – G – Am (2 tellen per akkoord, slotakkoord Am op tel 8).
  Melodie (piano): E5 D5 C5 | C5 A4 | G4 A4 C5 | D5 B4 | A4. E-piano-akkoorden + zachte pad + triangle-bas met lichte
  sidechain-pomp **die stopt op het slotakkoord**; zachte lowpass-"hartslag"-kick op elke tel incl. landing op tel 8.
- A/B/C verschillen alleen in de piano: A normaal (`bright=0.55`), B zachter (`bright=0.25`, lowpass 3,5 kHz, −4 dB),
  C nog doffer (`bright≈0.05–0.08`, lowpass 2 kHz). De gebruiker heeft A en B "behouden"; keuze tussen A/B/C staat open.
- Scripts eindigen met `gain(finalize(...), x)`: compensatie zodat het **muziekniveau gelijk blijft** aan eerdere rondes
  (gebruiker wil de piano-intensiteit niet zien veranderen). Bij wijzigingen: muziekdeel (3–9 s) meten en opnieuw compenseren.

## 3. Logboek intro
| Ronde | Wat we probeerden | Feedback |
|---|---|---|
| 1 | A fluitsignaal + solopiano (Am, 76 BPM); B oude radio + Rhodes; C lege tribune + wind + gitaar/fluit (~20–25 s) | **Max 10 s.** A leuk maar te somber → klein beetje energieker. Geen oude radio, moet modern; e-piano wel leuk. C: tribune-effect niet duidelijk, instrument "helemaal niks" |
| 2 | 3 variaties op A, 10 s, 92 BPM, hoopvollere akkoorden Am–F–C–G; oplopend in energie (piano / e-piano / piano+e-piano+hartslag-kick) | C de goede kant op, maar het **einde klonk raar** |
| 3 | A = C met nieuw einde (pomp stopt, opgelost naar Am); B band met drums 110 BPM; C elektronisch met riser/drop 120 BPM | "Energieker" = **tempo omhoog of ander deuntje**, **geen rare dingen in de achtergrond** (geen drums/riser/arps) |
| 4 | Zelfde rustige bezetting; A zelfde deuntje 108 BPM; B/C nieuwe melodieën | **A goed.** B/C: probeer andere "normale" instrumenten |
| 5 | A ongewijzigd; B akoestische gitaar + contrabas; C strijkers + piano + glockenspiel (deuntje van A) | A zo houden. Gitaar te hard → zachtere gitaar + ander deuntje. Strijkers "helemaal niks" |
| 6 | B zachte fingerpicking-gitaar (nieuw deuntje); C vibrafoon (nieuw deuntje) | Behoud A; B = A met minder intense piano; C = A zonder piano |
| 7 | B zachtere piano; C melodie op e-piano i.p.v. piano | Behoud A en B; C = B met nog doffere piano |
| 8 | C doffere piano (lowpass 2 kHz) | Fluit **minder luid + grotere pauzes** (echt affluiten); piano-intensiteit behouden |
| 9 | Fluit −5 dB, gap 0,45→0,75 s; niveaucompensatie | Tempo iets lager dan 108 |
| 10 | 100 BPM, niveaucompensatie | — (wacht op feedback) |

## 4. Geleerde voorkeuren (richting)
- **Kort**: intro maximaal 10 seconden.
- **Rustig maar niet somber**: licht hoopvol (Am–F–C–G), tempo rond 100 BPM; "energieker" betekent tempo/melodie, niet meer lagen.
- **Eenvoudige, "normale" bezetting**: piano + e-piano + zachte pad + subtiele kick. Geen drums, risers, arpeggio's,
  glitch of andere "rare dingen in de achtergrond". Geen retro/radio-effect: modern klinken.
- **Werkte niet**: oude radio, synthetische strijkers, geslagen (harde) gitaar, wind/lege-tribune-concept, fluitachtige lead.
- **Werkte wel**: fluitsignaal + juichend publiek dat wegsterft (herkenbaar "logo"), e-piano, warme/zachte piano.
- Kleine, gerichte aanpassingen per ronde; wat goed is ongewijzigd laten staan (kopieer het script naar de nieuwe ronde,
  controleer met `np.array_equal` dat het bit-identiek is).
- Zelf niet kunnen luisteren → altijd meten: RMS per halve seconde (balans publiek/muziek, eindes), spectrum (helderheid),
  en vergelijk met de vorige ronde.

## 5. Workflow per verzoek
1. Nieuw verzoek → `python studio.py new <id> --title "..." --category intro|outro|transitie|achtergrond|overig --prompt "<verzoek>" --note "..."`
2. Schrijf **3 opties**: `projects/<id>/rounds/NN/a.py`, `b.py`, `c.py` (eerste ronde: duidelijk verschillend).
3. `python studio.py render <id> [ronde] [opties]` → WAV's + metadata in `round.json`. Controleer duur, piek, RMS.
4. Webpagina: `python studio.py serve` (of `start-studio.bat`), http://localhost:8765 — pikt nieuwe rondes automatisch op.
   Na wijzigingen aan `studio.py` de server herstarten; na wijzigingen aan `web/index.html` moet de gebruiker verversen.
5. Feedback lezen: `python studio.py feedback <id> [ronde]` (soms geeft de gebruiker feedback direct in de chat).
6. Volgende ronde: `python studio.py round <id> --note "wat is er veranderd"`, scripts kopiëren/aanpassen. Oude rondes nooit overschrijven.
7. "Kies deze als definitief" op de pagina → `final/<id>.wav` + `.mp3`.
8. **Werk §2–§4 van dit bestand bij.**

Downloadknop levert MP3 (320 kbps, via `lameenc`, endpoint `/mp3/<pad>.wav?name=...`; MP3 wordt naast de WAV gecachet).

## 6. Optie-script en engine
```python
from engine import *
TITLE = "Korte naam"
DESCRIPTION = "1-2 zinnen: sfeer, instrumenten, tempo/toonsoort."
def render():
    s = Track(bpm=100)
    s.add(pad(chord('C4', 'maj7'), s.b(4)), beat=0, gain=-6, pan=-0.2)
    return finalize(reverb(s.render(), 1.8, 0.25), fade_out=0.5)
```
- `engine/core.py`: noten/akkoorden/schalen, oscillators, envelopes, filters (ook sweeps), stereo, effecten
  (reverb, delay, chorus, drive, bitcrush, tape_stop, stutter, sidechain), `Track`, `mix`, `loopify`, `finalize`, `gain`.
- `engine/instruments.py`: pad, soft_pad, keys (e-piano), piano, pluck, guitar, upright_bass, strings, pizzicato,
  vibraphone, marimba, bell, bass, sub, lead, chip, strum, poly; drums (kick, snare, clap, hat, shaker, crash, tom);
  FX (riser, downlifter, whoosh, impact, reverse_swell, sparkle).
- `engine/ambience.py`: crowd (stadionpubliek, `excitement` 0..1), applause, whistle, final_whistle, wind, crackle,
  old_radio, fade_away (wegsterven met dichtgaand filter), slow_noise.
- Altijd `finalize()` aan het eind (piek −1 dBFS). Synthetische klank is de beperking: geen realistische
  akoestische instrumenten of zang beloven; echte opnames kunnen via `load_wav()` worden ingemengd.
