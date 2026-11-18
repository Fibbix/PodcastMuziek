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

## 2. Stand van zaken (bijgewerkt 2026-11-14)
| Project | Status | Basis voor verder werk |
|---|---|---|
| `intro` | ✅ **DEFINITIEF: ronde 25 B** → `final/intro.wav` + `.mp3` (16,3 s: intro 9,2 s + zacht doorspelend deuntje dat geleidelijk wegfadet) | `projects/intro/rounds/25/b.py` |
| `transitie-default` (`--category transitie`) | ✅ **DEFINITIEF: ronde 4 B** → `final/transitie-default.wav` + `.mp3` (3,05 s, fade-in 0,7 s) | `projects/transitie-default/rounds/04/b.py` |
| `transitie-stad` "Pad door de Stad" (`--category transitie-stad`) | Ronde 9 (fietsbel → autotoeter, toets lopen langer uit), wacht op feedback. Huidige definitief: ronde 4 B → `final/transitie-stad.wav` + `.mp3` (5,6 s) | `projects/transitie-stad/rounds/09/` — zie §3d |
| `transitie-shirt` Shirtje Zoeken (`--category transitie-shirt`) | Ronde 3 | `projects/transitie-shirt/rounds/03/` — zie §3e; rubriek = **een verzamelaar van clubspullen** vinden/bezoeken (niet per se shirts) |
| `outro` (`--category outro`) | ✅ **DEFINITIEF: ronde 2 C** → `final/outro.wav` + `.mp3` (20,3 s: 2× zacht, dan normaal, slotakkoord + klap, afgefloten) | `projects/outro/rounds/02/c.py` |

Tabbladen op de pagina (in deze volgorde) komen uit `CAT` in `web/index.html` en `CATEGORIES` in `studio.py`;
lege tabbladen tonen "Nog leeg". `test-sting` is een testproject (categorie `overig`).

**Ronde 11:** A = ronde-10-B (zachtere piano, 100 BPM; `seed(1000+ord("b"))` vastgezet → bit-identiek).
B = stadionorgel + stampen/handclaps + tamboerijn + bas (112 BPM, C–Am–F–G–C). C = gefloten melodie, e-piano-groove,
bas en claps/shaker (104 BPM, G–Em–C–D–G). B en C hergebruiken exact de opening van A (zelfde seed in `stadium()`).
Let op: `studio.py` seedt per optieletter → bij kopiëren naar een andere letter de seed expliciet vastzetten.

**Ronde 12:** A en C = ronde 11 (bit-identiek). B = A + extra pianotoetsen op de 'en' (`FILLS`: C5, F4, F4, E5, G4, G4
op tel 0.5/2.5/3.5/5.5/6.5/7.5; −1,5 dB t.o.v. melodie) → melodie in achtsten, klinkt vlotter.
Techniek om iets toe te voegen zónder de rest te veranderen: (1) rng-state opslaan/terugzetten rond de nieuwe noten
(anders verschuift het toeval van galm/publiek), (2) normalisatiefactor berekenen op de mix zónder de toevoeging en die
op de mix mét toevoeging toepassen (i.p.v. `finalize`). Resultaat: opening bit-identiek aan A, melodienoten even sterk.

**Favoriete intro (ronde 10 B = ronde 11 A), 10,0 s:**
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
| 10 | 100 BPM, niveaucompensatie | Behoud B (zachtere piano) als A; maak 2 compleet nieuwe intro's, 3 fluiten behouden, andere instrumenten/jingle, "lekker energiek maar goed klinkend" |
| 11 | A = ronde-10-B; B stadionorgel + handclaps/stampen (112 BPM); C gefloten melodie + e-piano-groove (104 BPM) | Behoud A en C; B vervangen door A met meer pianotoetsen tussendoor → klinkt sneller (orgel-versie viel af) |
| 12 | B = A + extra pianotoetsen op elke 'en' (achtsten-melodie), rest identiek | B net iets minder toetsen ertussen |
| 13 | B = 4 extra toetsen i.p.v. 6 (één per akkoord: tel 0.5, 3.5, 5.5, 7.5); A en C identiek | "B nu C maken, korter (8 s)" |
| 14 | ⚠ verkeerd begrepen: C = B ingekort tot 8 s | Bedoeld was: de gefloten C inkorten tot 8 s en op **B** zetten, C zelf ongewijzigd |
| 15 | A = zachtere piano (10 s); B = gefloten versie ingekort tot **8 s** (T0 2,0 s, fluit gelijk, publiek sneller weg, +0,45 dB compensatie); C = gefloten versie ongewijzigd (10 s) | B fadet te snel weg op het einde → langer laten uitfaden, rest gelijk |
| 16 | B: uitfade 1,0 → 1,6 s met zachtere curve (`fade(..., out_curve='cos')`), alles vóór 6,4 s identiek; A en C identiek | "De andere versies faden echt 2 s weg, dat wil ik ook bij B" → gekozen: B iets langer |
| 17 | B verlengd naar **9,2 s** met dezelfde fade als C (1,4 s): uitklinktijd na slotakkoord tot −20 dB = 2,0 s (A/C 2,2 s) | B kopiëren naar C, maar het gefluit zachter "zoals bij de piano" |
| 18 | A, B identiek. C = B met zachtere fluit: −4 dB, `breath` 0,05→0,03, lowpass 2,8 kHz, galm-mix 0,22→0,30; eindversterking van B hergebruikt (rest identiek) | "Mag nog wel meer zachter" |
| 19 | C: fluit −8 dB t.o.v. B (gain −11), `breath` 0,02, lowpass 2,2 kHz, galm-mix 0,35; gemeten fluitband −7,3 dB t.o.v. B | "Net ietsjes minder zacht" |
| 20 | C: fluit −7 dB t.o.v. B (gain −10), `breath` 0,023, lowpass 2,4 kHz, galm-mix 0,34; gemeten fluitband −6,4 dB t.o.v. B | **C wordt de keuze.** Alleen: duidelijker dat het een scheidsrechtersfluit is aan het begin, misschien juist niet zachter |
| 21 | A = gekozen C (referentie, scheidsfluit −14 dB). B = scheidsfluit +5 dB (−9), zelfde klank. C = nieuwe `pea_whistle` (ratelend balletje, luchtstootje, droger: galm 1,4 s/0,18), even hard als B (−7,6). Muziek vanaf 5 s bit-identiek | **B is het beste.** Wil 5 s heel zachte intro-klank aan het eind, waar de podcast overheen begint |
| 22 | A = ronde-21-B. B = A + 5 s zachte groove-staart (e-piano, bas, zachte shaker). C = A + 5 s zachte nagalm zonder ritme (pad/e-piano/sub). Laag start op tel 10 (7,77 s) met 1 s fade-in, fade-out laatste 3 s, lowpass 2,5 kHz, RMS −28 dBFS (~13 dB onder muziek); totaal 14,2 s; intro zelf bit-identiek | C het dichtst bij, maar eigenlijk moet **het deuntje gewoon doorspelen**, heel zacht. Behoud C, B opnieuw |
| 23 | A, C identiek. B = `bed_tune`: na 1 maat aanloop (tel 10) begint op tel 12 het hele deuntje opnieuw (gefloten melodie + e-piano + bas + claps + shaker), zelfde niveau/opbouw als C, lowpass 3,2 kHz | **B precies goed**; 5-s-limiet vervalt: hele muziekdeel (na fluit t/m einde) zacht erachter, netjes wegfaden |
| 24 | A identiek. B = staart loopt door t/m het slotakkoord van de herhaling (tel 20 = 13,54 s; slotakkoord e-piano/bas/klap toegevoegd), cos²-uitfade 2,4 s, totaal 16,3 s; tot 11,2 s bit-identiek aan ronde-23-B. C = ronde-23-B (5 s) | Moet extra wegfaden: vanaf het begin van het tweede muziekdeel al wegfaden, einde bijna onhoorbaar |
| 25 | A identiek. B = staart fadet vanaf tel 12 (8,92 s) gelijkmatig in dB, −19 dB bij het slotakkoord (tel 20), daarna cos²-staart naar stilte; startniveau en alles tot 8,92 s identiek. Gemeten: −28 → −46 (13 s) → −49 (14 s) dB. C = ronde-24-B | — (wacht op feedback) |

## 3b. Logboek outro
Verzoek: "heel erg op de intro lijken, maar duidelijk de outro". Brief: positief, energieker dan intro, géén tribune.
Alle opties delen één template (`rounds/01/*.py`, constanten bovenaan): intro-deuntje zonder publiek, 1 maat aanloop,
melodie 2× (eerste keer zonder slotnoot), ritardando in laatste 2 tellen (`bt()`, `RIT=0.6`) + groot slotakkoord met klap.

| Ronde | Wat we probeerden | Feedback |
|---|---|---|
| 1 | A puur deuntje met slot (104 BPM, 14,1 s); B aftrapfluit (`pea_whistle` 1 s) + 112 BPM + 2e keer toon hoger (G→A) (14,5 s); C begint −18 dB en zwelt aan + toon hoger + eindsignaal na slotakkoord, 108 BPM (15,3 s) | **C het dichtst bij.** Wil het spiegelbeeld van de intro: eerst deuntje heel heel zacht, dan over naar normaal, slotakkoord met klap, afgefloten aan het eind |
| 2 | Spiegel-template (zelfstandige scripts in `rounds/02/`, constanten bovenaan: BPM, KEY_UP, SOFT_PASSES): zacht deel = lowpass 3,2 kHz, zwelt in dB aan van −22 dB tot `SOFT_LEVEL` −28 dBFS; cos²-crossfade 1,4 s eindigend op eerste tel van het normale deel; slotakkoord + klap; klassieke scheidsfluit −9 dB (= intro) 0,9 s na slotakkoord. A 104 BPM, 1 zachte ronde (15,7 s); B 108 BPM + normaal deel toon hoger (15,3 s); C 104 BPM, 2 zachte rondes (20,3 s) | — (wacht op feedback) |

## 3c. Logboek transitie default
Verzoek: snel, goede fades, herkenbaar; zelfde stijl als intro/outro maar niet te veel erop lijken.
Aanpak: zelfde familie (e-piano, zachte fluit, bas, claps, shaker; G groot, 104 BPM), eigen kort motief, ~2,5 s,
inzet zonder klik (`fade` 20 ms), natuurlijke uitklank + `fade_out` ~1 s.

| Ronde | Wat we probeerden | Feedback |
|---|---|---|
| 1 | A opwaarts e-piano-loopje C–D–G + bas, landt met klap (2,7 s); B gefloten handtekening B5–D6–G6 + e-piano/bas/klap, shaker zwelt aan (2,6 s); C tribuneklappen ta-ta-TAM met e-piano-stoten D–D–G + kort gefloten G6-accent (2,4 s) | **B het beste, maar nog niet goed genoeg** → B als referentie, 3 nieuwe |
| 2 | A 4 gefloten noten G5–B5–D6–G6 + akkoordwissel D→G, fluit zachter/ronder (lowpass 2,4 kHz, −6) (2,8 s); B halve maat intro-groove op C (+D-opstap) → handtekening B5–D6–G6 (3,0 s); C kort: D6→G6 + e-piano/bas/klap tegelijk (1,9 s) | **B het beste**; telkens iets zachter, vooral de fluit is heel hard |
| 3 | Alle = ronde-2-B (seed vastgezet op `ord("b")`), eindversterking van ronde-2-B hergebruikt. A fluit −3/geheel −1,5; B fluit −6/geheel −3; C fluit −9/geheel −4,5 dB; fluit steeds ronder (lowpass 2,4→2,0 kHz, minder adem, meer galm). Gemeten fluit −4,3/−9,0/−13,8, backing −1,0/−2,5/−4,0 dB | **C het beste**; moet ook mooi infaden (fadet nu alleen goed uit) |
| 4 | Alle = ronde-3-C met sin²-fade-in (`fade(x, FADE_IN, 1.0)`): A 0,4 s, B 0,7 s, C 1,0 s; na de fade bit-identiek aan ronde-3-C; landing (1,2 s) op vol volume | **B gekozen als definitief** ("de transitie default is nu goed") |

## 3d. Logboek transitie Pad door de Stad
Verzoek: transitie voor de reportage-rubriek "Pad door de Stad", bruikbaar als intro én outro van de reportage;
bij 1 versie echt "Pad door de Stad" laten zingen. Familie: 104 BPM, G groot, e-piano/upright bass/klap/shaker,
plus stadsgeluid (`city`, ~15 dB onder de muziek), fade-in ~0,5 s en uitfade 1 s, landing op G.

| Ronde | Wat we probeerden | Feedback |
|---|---|---|
| 1 | A fietsbel tring-tring + 1 maat groove (wandelbas G–A–B–D, e-piano intro-ritme, klappen) + e-piano-loopje naar G, belletje als staart (4,3 s); B **gezongen** "Pad – door de – Stad" (B2 – D3 D3 – G3; Windows-TTS-stem Frank via `engine/voice.py` op de noten gezet, 3 stemmen) op D → G – C – G, zang 3–5 dB boven de band (3,7 s); C voetstappen L→R + stad met stemmen + shuffle-groove met vingerknippen en e-piano-melodietje (4,4 s). Niveau ≈ default (RMS −21) | **A het beste, maar de melodie klopt niet helemaal** → 3 nieuwe melodieën in de stijl van A |
| 2 | Alle = ronde-1-A (`seed(1000+ord("a"))`, rng-state bewaard rond de melodie → stad/fietsbel/groove gelijk; opening ≤0,7 dB verschil door normalisatie). Akkoorden G–G–G–C–C–D → G; bas tel 2 B→C (botste met C-akkoord): G–B–C–D. Volledige e-piano-melodie (`MELODY`, nootduur = 90 % tot volgende noot), elke noot past bij het akkoord. A D–B–D \| E–G \| E–F# → G5; B B–C–D–G \| E–D–C–A → G4 (terugwandelend); C knipoog naar intro D–B–D–E \| C–E–G \| F# → G5 | **B gekozen**; laatste belletje → fietsbel |
| 3 | Alle = ronde-2-B, tot de bel bit-identiek (normalisatie via referentiemix mét het oude belletje). Slotbelletje vervangen door `bike_bell`, ná de uitfade toegevoegd met eigen uitklank (bestand ~0,6 s langer, `TAIL` 1,3 s): A één tring (tel 5, −17); B tring-tring (tel 4,75, −17); C tring-tring verder weg (−21, lowpass 5 kHz, galm 0,4, pan 0,65) | **C het beste**, maar de bel mag niet in de uitfade van de muziek vallen (klinkt raar) |
| 4 | Alle = ronde-3-C (verre fietsbel), tot tel 4,2 bit-identiek. Bel nooit meer meegefadet, eigen uitklank 2 s. A bel pas ná de volledig uitgefade muziek (muziek = vorige C; 6,6 s); B bel op tel 4½ tijdens de landing op vol volume, muziek-uitfade (1 s) begint pas 0,15 s na de bel (5,6 s); C idem op tel 4¼, direct na de slotklap (5,4 s) | **B gekozen als definitief**; later (2026-11-17): "B voor nu op A, en voor B en C een nieuwe versie waar de fietsbel vervangen is met een zachte toeter van een auto" |
| 5 | A = ronde-4-B (bit-identiek). Nieuw `car_horn` (twee zaagtand-hoorns G4+B4 = grote terts op het G-slotakkoord, drive + filters, `soft`), los van de muziek-fade zoals de bel; muziek bit-identiek aan A. B alleen de **slotbel** → toet-toet (tel 4½, lowpass 3 kHz, galm 0,4, pan 0,65); C ook het **openingsbelletje** → één verre toet (0,1 s, −20; oude bel telt nog mee in de normalisatie-referentie). Gemeten: toeter op −21 (= bel-gain) zat in zijn band ~20 dB onder de piano (bel ~7 dB) → gemaskeerd, dus slottoeter op **−13** | "Toeter bij B en C iets harder, hoor hem bijna niks. Verander niks anders" |
| 6 | Alles = ronde 5; alleen toeters +6 dB: slottoeter −13→**−7**, openingstoet −20→**−14** (A bit-identiek, B/C veranderen alleen waar de toeter klinkt; piek −7,2 dBFS) | "Nog iets harder" |
| 7 | Alles = ronde 6; alleen toeters +4 dB: slottoeter −7→**−3**, openingstoet −14→**−10** (A bit-identiek; piek −5,9 dBFS) | "Toeters iets langer, iets langere pauze tussen de twee toets" |
| 8 | Alles = ronde 7; slottoeter toot_dur 0,16→**0,22** s, gap 0,10→**0,16** s; openingstoet (C) 0,22→**0,30** s (A bit-identiek). Galm (mix 0,4) vult de pauze deels: dip ~6 dB (ronde 7 ~5 dB) | "Nog langer uit laten lopen" (geïnterpreteerd: langere toets die geleidelijk uitsterven) |
| 9 | Alles = ronde 8; `car_horn` kreeg `release` (default 0,035 = oude rondes bit-identiek). Slottoeter toot_dur 0,22→**0,30** s + release **0,15** s, gap 0,16 gelijk; openingstoet (C) 0,30→**0,40** s + release 0,2 (A bit-identiek; piek −5,0). Let op: uitloop eet de pauze grotendeels op (dip ~5 dB) | — (wacht op feedback) |

## 3e. Logboek transitie Shirtje Zoeken
Verzoek: "Nu de transitie voor shirtje zoeken". De rubriek gaat over **een verzamelaar van items van de club vinden**
(niet per se een shirtje); begin én eind van de rubriek.
Familie: 104 BPM, e-piano/bas/klap, 'zoekend' (mineur/staccato) → 'gevonden' (landing op G groot met klap).
Effecten starten direct (fade-in 20 ms, géén fade over een effect) en zijn uitgeklonken vóór de uitfade.

| Ronde | Wat we probeerden | Feedback |
|---|---|---|
| 1 | A kledingrek: 2× hangers schuiven (`rack_slide`) + staccato bas/e-piano Em–C–D, melodie B–E–D–B \| C–E \| D–F# → G (4,2 s); B speurtocht: rommelen in doos (`rummage`) + sluipend pizzicato E–G–B–G \| A–C–B–A in E-mineur, vingerknippen, D7 → G (4,1 s); C gevonden!: kort rommelen + hangertik, e-piano-loopje G–B–D–G–B op D, landing G + kort stadiongejuich dat binnen 1,4 s uitsterft (3,7 s). RMS ≈ −21 | **"Alle 3 helemaal niks"** (mineur/sluipend/zoek-effecten werkt niet) |
| 2 | Terug naar de stijl van Pad door de Stad A: één maat groove G–Em–C–D (akkoord per tel, e-piano + naslag op de 'en', bas grondtoon + octaaf, klappen 2/4, shaker), e-piano-melodie, landing op G met klap. Template met `FX`, `MELODY`, `PICKUP`. A 2× bladzijde omslaan (`page_turn`) vooraf, melodie D–G \| E–B \| C–E \| D–F# → G5; B vaag stadionpubliek als herinnering (weg vóór tel 1,5), melodie B–D \| G–E \| E–C \| D–A → G5; C geen effect, halve maat aanloop + fade-in 0,6 s, syncopische melodie G–D–E \| E–G \| F#–E–D → G5. ~4,4 s, RMS ≈ −21 | **Behoud C**; A en B compleet opnieuw |
| 3 | C = ronde-2-C (`seed(1000+ord("c"))`, bit-identiek). A zachte piano (intro-klank: bright 0,25, lowpass 3,5 kHz) in tertsen over C–D–Em–D → G, 96 BPM, lang aangehouden e-piano, hartslag-kick, aanloop bas+shaker, fade-in 0,25 s (4,7 s). B Em–C–G–D → G, 108 BPM, zacht gefloten melodie B–G \| C–E \| D–B \| A–F# → lange G (breath 0,022, lowpass 2,4 kHz, galm 0,34; ~5–6 dB onder de backing), e-piano syncopisch (tel + 0,75), tamboerijn op de 'en' (4,3 s) | — (wacht op feedback) |

## 4. Geleerde voorkeuren (richting)
- **Kort**: intro maximaal 10 seconden (het "luide" deel); daarna mag het deuntje heel zacht (~13 dB onder, lowpass)
  doorspelen als bed onder de eerste woorden — gebruiker vindt het leuk de intro nog even te horen als de podcast begint.
- **Gefloten melodie + e-piano-groove** (ronde 11 C) bleef 4 rondes staan → serieuze kandidaat naast de zachtere piano.
- **"Zachter, zoals bij de piano"** = een melodie-instrument minder intens maken: ~−4 dB, hoog wegfilteren, minder
  aanslag/adem, iets meer galm, de rest van de mix exact gelijk laten.
- **Fluit/gefloten melodie snel "te hard"**: gebruiker wil die consequent zacht en rond (zoals in de intro:
  lowpass ~2,4 kHz, weinig adem, galm ~0,34, ruim onder de backing-pieken).
- **ALTIJD bij kopiëren naar een andere optieletter:** `seed(1000 + ord("<oude letter>"))` als eerste regel in
  `render()`, anders klinkt de groove (humanize, claps, shaker) anders. Ging al twee keer bijna mis.
- **Losse effecten (bel, fluit) niet in een uitfade laten vallen**: klinkt raar. Zet ze vóór de uitfade (en laat de
  muziek pas daarna uitfaden) of ná de muziek, en laat ze zelf natuurlijk uitklinken.
- **"Net ietsjes"** = echt een kleine stap (~1 dB), niet halverwege. Gebruiker typt snel; lees typo's in context
  ("Niet" = "Net", "anderzom" = "andersom").
- **Rustig maar niet somber**: licht hoopvol (Am–F–C–G), tempo rond 100 BPM; "energieker" betekent tempo/melodie, niet meer lagen.
- **Eenvoudige, "normale" bezetting**: piano + e-piano + zachte pad + subtiele kick. Geen drums, risers, arpeggio's,
  glitch of andere "rare dingen in de achtergrond". Geen retro/radio-effect: modern klinken.
- **Werkte niet**: mineur/sluipend/'detective'-loopjes en zoek-effecten (shirt ronde 1), oude radio, synthetische strijkers, geslagen (harde) gitaar, wind/lege-tribune-concept, fluitachtige lead,
  stadionorgel + handclaps (ronde 11 B).
- **Interpretatie "maak X nu Y"**: kan beide kanten op betekenen (ronde 14 ging mis). Bij twijfel kort in de chat
  benoemen hoe je het leest vóór het renderen, of de gekozen lezing expliciet in de ronde-notitie zetten.
- **Inkorten tot 8 s** zonder karakterverlies: tempo/melodie/fluit gelijk laten, muziek starten tijdens de laatste lange
  fluitstoot (T0 2,0 s), `fade_away(start=2.0, dur=3.0)`, slotakkoord ≥1 s laten uitklinken, niveau compenseren.
  Uitfade niet te kort: wat de gebruiker als "2 seconden fade" hoort, is de **uitklinktijd na het slotakkoord**
  (A/C: slotakkoord ~7,1 s, ~2,2 s tot −20 dB). Een langere fade-instelling helpt niet als het bestand eerder ophoudt;
  dan moet het bestand langer (B werd 9,2 s). Meet dit: tijd van slotakkoord tot −20 dB.
- **"Sneller" kan ook door méér noten** (achtsten in de melodie) bij hetzelfde tempo, i.p.v. BPM omhoog.
- **Werkte wel**: fluitsignaal + juichend publiek dat wegsterft (herkenbaar "logo"), e-piano, warme/zachte piano.
- Kleine, gerichte aanpassingen per ronde; wat goed is ongewijzigd laten staan (kopieer het script naar de nieuwe ronde,
  controleer met `np.array_equal` dat het bit-identiek is).
- **Zang:** `engine/voice.py` kan een gesproken lettergreep laten zingen (LPC-vocoder: klinker opnieuw aangeslagen
  op de noot, medeklinkers origineel). Bron: Windows-TTS **Microsoft Frank (nl-NL)** via WinRT in PowerShell
  (`Windows.Media.SpeechSynthesis`, SSML `prosody rate=-30% pitch=+15%`, één woord per bestand; de stem staat
  alleen in OneCore, niet in System.Speech). Klinkt verstaanbaar maar robot/autotune-achtig. Een eigen opname van
  het team (per lettergreep of hele zin) blijft het echtst; die kan via `load_voice()` + `sing()` op toon worden gezet.
  Per lettergreep `vowel=(t0,t1)` en `hold` handmatig opgeven (automatische stemdetectie is onbetrouwbaar bij TTS).
- **Energiek maar niet "AI"**: voorkeur voor instrumenten die de engine geloofwaardig kan (piano, e-piano, orgel,
  mallets, handclaps/stomps, gefloten melodie, getokkelde bas) + humanizing (timing/velocity-variatie, swing);
  echte drum-/instrumentsamples via `load_wav()` waar synthese tekortschiet (drumkit, gitaar, blazers, strijkers).
- Zelf niet kunnen luisteren → altijd meten: RMS per halve seconde (balans publiek/muziek, eindes), spectrum (helderheid),
  en vergelijk met de vorige ronde.

## 5. Workflow per verzoek
1. Nieuw verzoek → `python studio.py new <id> --title "..." --category intro|transitie|transitie-stad|transitie-shirt|outro|overig --prompt "<verzoek>" --note "..."`
2. Schrijf **3 opties**: `projects/<id>/rounds/NN/a.py`, `b.py`, `c.py` (eerste ronde: duidelijk verschillend).
3. `python studio.py render <id> [ronde] [opties]` → WAV's + metadata in `round.json`. Controleer duur, piek, RMS.
4. Webpagina: `python studio.py serve` (of `start-studio.bat`), http://localhost:8765 — pikt nieuwe rondes automatisch op.
   Na wijzigingen aan `studio.py` de server herstarten; na wijzigingen aan `web/index.html` moet de gebruiker verversen.
5. Feedback lezen: `python studio.py feedback <id> [ronde]` (soms geeft de gebruiker feedback direct in de chat).
6. Volgende ronde: `python studio.py round <id> --note "wat is er veranderd"`, scripts kopiëren/aanpassen. Oude rondes nooit overschrijven.
7. "Kies deze als definitief" op de pagina → `final/<id>.wav` + `.mp3`.
8. **Werk §2–§4 van dit bestand bij.**

Downloadknop levert MP3 (320 kbps, via `lameenc`, endpoint `/mp3/<pad>.wav?name=...`; MP3 wordt naast de WAV gecachet).
Geeft de download "Site was niet beschikbaar"/HTTP 500 → `lameenc` ontbreekt in de huidige Python: `python -m pip install lameenc` (geen serverherstart nodig).

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
  vibraphone, marimba, bell, bass, sub, lead, chip, strum, poly, organ (tonewheel + leslie), whistling (gefloten
  melodie met glijden/vibrato), tambourine, stomp, group_clap, humanize/vel (timing-/aanslagvariatie);
  drums (kick, snare, clap, hat, shaker, crash, tom);
  FX (riser, downlifter, whoosh, impact, reverse_swell, sparkle).
- `engine/ambience.py`: crowd (stadionpubliek, `excitement` 0..1), applause, whistle, pea_whistle (realistischer,
  met balletje), final_whistle (`kind='classic'|'pea'`), wind, crackle,
  old_radio, fade_away (wegsterven met dichtgaand filter), slow_noise,
  bike_bell (fietsbel tring-tring), car_horn (zachte autotoeter toet-toet, gestemd; zit in het piano-register → ~18 dB meer gain nodig dan de bel: −3 i.p.v. −21), footstep, hanger_click, rack_slide (kledingrek), rummage (doos/kleding), page_turn (bladzijde omslaan), city (verkeer, passerende auto, stemmen; normaliseert op piek →
  in de mix rond gain 0 dB zetten en meten, ~15 dB onder de muziek).
- `engine/voice.py`: load_voice (16 kHz mono), sing_syllable, sing(events=[(start, noot, duur, lettergreep)],
  formant, cents, vib, scoop, even). Lettergrepen voor "Pad door de Stad": `projects/transitie-stad/assets/syl_*.wav`.
- Altijd `finalize()` aan het eind (piek −1 dBFS). Synthetische klank is de beperking: geen realistische
  akoestische instrumenten of zang beloven; echte opnames kunnen via `load_wav()` worden ingemengd.
