"""
Sfeergeluiden: stadionpubliek, scheidsrechtersfluit, wind, vinylgekraak, oude radio.
Alles synthetisch — benadert de echte geluiden, maar is geen veldopname.
"""
from __future__ import annotations

import numpy as np

from .core import (SR, _end_fade, _farr, bandpass, drive, filter_env, highpass, lowpass, noise, ns,
                   osc, pan, reverb, rng, to_mono, to_stereo, tvec)


def slow_noise(dur, rate=1.0):
    """Vloeiend willekeurig signaal tussen 0 en 1 dat ~rate keer per seconde van richting verandert."""
    n = ns(dur)
    k = max(4, int(dur * rate) + 3)
    pts = rng().random(k)
    x = np.linspace(0, k - 2, n)
    i = np.floor(x).astype(int)
    f = x - i
    f = (1 - np.cos(np.pi * f)) / 2  # cosinus-interpolatie
    return pts[i] * (1 - f) + pts[i + 1] * f


_VOWELS = [(800, 1200), (500, 900), (450, 1900), (350, 800), (650, 1700), (400, 2100)]


def _babble_voice(dur):
    src = noise(dur)
    f1, f2 = rng().uniform(350, 800), rng().uniform(1000, 2300)
    v = bandpass(src, f1, 4) + 0.6 * bandpass(src, f2, 5)
    syl = np.clip(slow_noise(dur, rng().uniform(3, 6)) * 1.8 - 0.7, 0, 1) ** 2
    talk = np.clip(slow_noise(dur, 0.4) * 2.5 - 0.9, 0, 1)
    return v * syl * talk


def _shout_voice(dur):
    f0 = rng().uniform(110, 330)
    t = tvec(dur)
    fp = f0 * (1 + 0.25 * (slow_noise(dur, 0.7) - 0.5)) * (1 + 0.01 * np.sin(2 * np.pi * rng().uniform(4, 7) * t))
    src = osc('saw', fp, dur, phase=rng().random()) + 0.4 * noise(dur)
    F1, F2 = _VOWELS[rng().integers(len(_VOWELS))]
    v = bandpass(src, F1, 6) + 0.5 * bandpass(src, F2, 8) + 0.2 * bandpass(src, 2700, 8)
    return v * slow_noise(dur, rng().uniform(0.3, 1.0)) ** 1.5


def crowd(dur, excitement=0.5, voices=40, chatter=30, stadium=True):
    """Stadionpubliek (stereo). excitement 0..1 (getal of array per sample): hoeveel er gejuicht wordt.
    0 = geroezemoes, 1 = brullend stadion."""
    n = ns(dur)
    ex = _farr(excitement, n)
    out = np.zeros((n, 2))
    # bed: breed geruis van duizenden mensen
    bed = np.column_stack([highpass(lowpass(noise(dur, 'pink'), 2200), 220) for _ in range(2)])
    bed *= (0.6 + 0.4 * slow_noise(dur, 0.3))[:, None]
    out += bed * (0.25 + 0.5 * ex)[:, None]
    babble = np.zeros((n, 2))
    for _ in range(chatter):
        babble += pan(_babble_voice(dur), rng().uniform(-0.9, 0.9))
    out += babble / np.sqrt(chatter) * 1.2
    shouts = np.zeros((n, 2))
    for _ in range(voices):
        shouts += pan(_shout_voice(dur), rng().uniform(-0.9, 0.9))
    out += shouts / np.sqrt(max(voices, 1)) * (ex ** 1.3 * 2.0)[:, None]
    if stadium:
        out = reverb(out, decay=2.4, mix=0.35, predelay=0.03, tone=5000)[:n]
    return out / (np.max(np.abs(out)) + 1e-9) * 0.9


def applause(dur, density=60, intensity=None):
    """Applaus: veel losse klappen (stereo). intensity = array/getal 0..1 voor het verloop."""
    n = ns(dur)
    inten = _farr(1.0 if intensity is None else intensity, n)
    out = np.zeros((n, 2))
    cl = ns(0.03)
    tt = np.arange(cl) / SR
    count = int(density * dur * 4)
    times = rng().integers(0, max(1, n - cl), count)
    keep = rng().random(count) < inten[times]
    for s in times[keep]:
        c = bandpass(rng().standard_normal(cl), rng().uniform(900, 2500), 1.5) * np.exp(-tt / 0.006)
        p = rng().uniform(-1, 1)
        out[s:s + cl, 0] += c * (1 - p) / 2 * rng().uniform(0.3, 1)
        out[s:s + cl, 1] += c * (1 + p) / 2 * rng().uniform(0.3, 1)
    out = reverb(out, 1.8, 0.3)[:n]
    return out / (np.max(np.abs(out)) + 1e-9) * 0.9


def whistle(dur=0.4, pitch=3000):
    """Eén fluitstoot van een scheidsrechtersfluit (mono)."""
    t = tvec(dur)
    trill = np.sin(2 * np.pi * rng().uniform(38, 48) * t)
    f = pitch * (1 + 0.025 * trill)
    y = osc('sine', f, dur) * (1 - 0.35 * (0.5 + 0.5 * trill))
    y += 0.12 * osc('sine', 2 * f, dur)
    y += 0.08 * bandpass(noise(dur), pitch, 6)
    env = np.minimum(t / 0.015, 1) * np.minimum((dur - t) / 0.04, 1)
    return _end_fade(y * np.clip(env, 0, 1) * 0.6)


def pea_whistle(dur=0.4, pitch=3150, trill=0.8, chiff=0.6):
    """Scheidsrechtersfluit mét balletje (mono): onregelmatig 'ratelen' (toonhoogte + volume),
    een luchtstootje bij de aanzet en een kleine toonhoogtestijging in het begin. Herkenbaarder dan whistle()."""
    t = tvec(dur)
    rate = 34 + 14 * (slow_noise(dur, 8) - 0.5)                  # balletje draait onregelmatig
    tr = (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(rate) / SR)) ** 1.5
    rise = 1 - 0.035 * np.exp(-t / 0.03)                          # toon 'schiet' even omhoog bij aanblazen
    f = pitch * rise * (1 + 0.045 * trill * (tr - 0.5))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + 0.28 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)
    y *= 1 - 0.6 * trill * tr                                     # sterke volume-trilling
    y += 0.18 * bandpass(noise(dur), pitch, 4)                    # lucht door de fluit
    y += chiff * highpass(noise(dur), 2500) * np.exp(-t / 0.018)  # luchtstootje bij de aanzet
    env = np.clip(np.minimum(t / 0.008, 1) * np.minimum((dur - t) / 0.03, 1), 0, 1)
    return _end_fade(y * env * 0.5)


def final_whistle(pitch=3000, long=1.3, gap=0.5, kind='classic'):
    """Laatste fluitsignaal: kort, kort, laaaang (mono). kind='pea' = herkenbaardere fluit met balletje."""
    parts = [(0.0, 0.28), (gap, 0.28), (2 * gap, long)]
    out = np.zeros(ns(2 * gap + long + 0.1))
    for start, d in parts:
        if kind == 'pea':
            w = pea_whistle(d, 3150 * rng().uniform(0.99, 1.01))
            s = ns(start)
            out[s:s + len(w)] += w
            continue
        w = whistle(d, pitch * rng().uniform(0.99, 1.01))
        s = ns(start)
        out[s:s + len(w)] += w
    return out


def wind(dur, strength=0.5, gust_rate=0.15):
    """Wind, bv. over een lege tribune (stereo)."""
    chans = []
    for _ in range(2):
        center = 250 + 900 * slow_noise(dur, gust_rate) * (0.5 + strength)
        w = filter_env(noise(dur, 'pink'), 'bandpass', center, 1.4)
        w *= 0.35 + 0.65 * slow_noise(dur, gust_rate * 1.3)
        w += 0.5 * lowpass(noise(dur, 'brown'), 120)
        chans.append(w)
    out = np.column_stack(chans)
    return out / (np.max(np.abs(out)) + 1e-9) * 0.8 * (0.4 + 0.6 * strength)


def crackle(dur, density=12, hiss=0.04):
    """Vinylgekraak + lichte ruis (stereo)."""
    n = ns(dur)
    out = np.zeros((n, 2))
    count = int(density * dur)
    for s in rng().integers(0, max(1, n - 64), count):
        k = rng().integers(4, 40)
        a = rng().random() ** 3
        click = rng().standard_normal(k) * np.exp(-np.arange(k) / (k / 4)) * a
        c = rng().integers(2)
        out[s:s + k, c] += click
        out[s:s + k, 1 - c] += click * 0.5
    out = highpass(out, 900)
    out += np.column_stack([highpass(noise(dur, 'pink'), 2500) for _ in range(2)]) * hiss
    return out


def old_radio(x, low=450, high=3200, grit=2.5):
    """Klinkt als een oude radio-uitzending (mono, smalle band, licht vervormd)."""
    y = to_mono(x)
    y = lowpass(highpass(y, low, 0.9), high, 0.9)
    y = drive(y / (np.max(np.abs(y)) + 1e-9), grit)
    return to_stereo(y * 0.8)


def fade_away(x, start, dur, cutoff=500, reverb_mix=0.0):
    """Laat x vanaf `start` in `dur` seconden wegsterven alsof het steeds verder weg klinkt:
    volume omlaag én het filter dicht (hoog verdwijnt eerst)."""
    x = to_stereo(x)
    n = len(x)
    t = np.arange(n) / SR
    u = np.clip((t - start) / dur, 0, 1)
    freqs = 16000 * (cutoff / 16000) ** u
    y = filter_env(x, 'lowpass', freqs, 0.7)
    amp = np.cos(u * np.pi / 2) ** 2
    y = y * amp[:, None]
    if reverb_mix:
        y = reverb(y, 3.0, reverb_mix)[:n]
    return y


# ================================================================ stad
def bike_bell(rings=2, ring_dur=0.2, gap=0.1, pitch=2950, rate=26.0):
    """Hollandse fietsbel 'tring-tring' (mono): een slagpin raakt de koepel snel achter elkaar.
    rings = aantal 'trings', ring_dur = lengte van elke tring (s)."""
    ratios = [1.0, 1.004, 1.58, 2.16, 2.89, 3.62]
    decays = [0.9, 0.85, 0.45, 0.3, 0.18, 0.12]
    amps = [1.0, 0.7, 0.5, 0.35, 0.22, 0.15]
    ir_dur = 1.4
    t = tvec(ir_dur)
    ir = sum(a * np.sin(2 * np.pi * pitch * r * t + rng().random() * 6.28) * np.exp(-t / d)
             for r, d, a in zip(ratios, decays, amps))
    total = rings * (ring_dur + gap) + ir_dur
    hits = np.zeros(ns(total))
    for k in range(rings):
        t0 = k * (ring_dur + gap)
        n_hits = max(1, int(ring_dur * rate))
        for h in range(n_hits):
            th = t0 + h / rate + rng().normal(0, 0.003)
            hits[ns(max(th, 0))] += rng().uniform(0.5, 1.0) * (1 - 0.4 * h / n_hits)
    click = highpass(noise(0.004), 3000) * np.linspace(1, 0, ns(0.004))
    exc = np.convolve(hits, click)[:len(hits)] + hits * 0.2
    y = np.convolve(exc, ir)[:len(hits)]
    return _end_fade(y / (np.max(np.abs(y)) + 1e-9) * 0.8)


def footstep(hard=0.6):
    """Eén voetstap op straat (mono): hak-tik + doffe dreun + wat geschuifel."""
    dur = 0.25
    t = tvec(dur)
    thud = lowpass(noise(dur, 'brown'), 180) * np.exp(-t / 0.035) * 3
    heel = bandpass(noise(dur), rng().uniform(1800, 2600), 1.5) * np.exp(-t / 0.006) * hard
    scuff = bandpass(noise(dur), 3500, 0.8) * np.clip((t - 0.02) / 0.02, 0, 1) * np.exp(-t / 0.05) * 0.12
    return _end_fade((thud + heel + scuff) * 0.7)


def city(dur, traffic=0.6, voices=0.4, cars=1):
    """Stadsgeluid (stereo): verkeersgeruis, af en toe een passerende auto en wat stemmen in de verte."""
    n = ns(dur)
    out = np.zeros((n, 2))
    rumble = np.column_stack([lowpass(noise(dur, 'brown'), 350) for _ in range(2)])
    rumble *= (0.6 + 0.4 * slow_noise(dur, 0.25))[:, None]
    out += rumble * traffic * 2.0
    hiss = np.column_stack([bandpass(noise(dur, 'pink'), 1200, 0.5) for _ in range(2)]) * 0.08 * traffic
    out += hiss
    t = tvec(dur)
    for _ in range(cars):
        tc = rng().uniform(0.3, 0.8) * dur
        w = rng().uniform(0.7, 1.2)
        env = np.exp(-((t - tc) / w) ** 2)
        fc = 600 + 900 * env
        car = filter_env(noise(dur, 'pink'), 'bandpass', fc, 0.9) * env * 0.5 * traffic
        p = np.clip((t - tc) / (2 * w), -0.8, 0.8)
        out[:, 0] += car * np.sqrt((1 - p) / 2)
        out[:, 1] += car * np.sqrt((1 + p) / 2)
    if voices > 0:
        out += crowd(dur, excitement=0.0, voices=0, chatter=8, stadium=False) * voices * 0.25
    out = reverb(out, decay=1.2, mix=0.15, tone=4000)[:n]
    return out / (np.max(np.abs(out)) + 1e-9) * 0.8


# ================================================================ zoeken (kledingrek, doos)
def hanger_click(bright=0.6):
    """Eén metalen kleerhanger die tegen de stang/andere hanger tikt (mono)."""
    dur = 0.25
    t = tvec(dur)
    f = rng().uniform(2600, 4200)
    ring = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d)
               for r, a, d in ((1.0, 1.0, 0.05), (1.53, 0.5, 0.03), (2.37, 0.3, 0.02)))
    tick = highpass(noise(dur), 3000) * np.exp(-t / 0.002)
    return _end_fade((ring * bright * 0.5 + tick * 0.6) * 0.7)


def rack_slide(dur=0.6, hangers=7, direction=1):
    """Kleerhangers die langs een kledingrek worden geschoven (mono): metaal-geschraap, tikjes en stofgeruis.
    direction=1 versnelt, -1 vertraagt."""
    n = ns(dur + 0.3)
    out = np.zeros(n)
    t = tvec(dur + 0.3)
    env = np.clip(t / 0.05, 0, 1) * np.clip((dur - t) / 0.12, 0, 1)
    scrape = bandpass(noise(dur + 0.3), 5200, 3.0) * env * 0.12
    swish = bandpass(noise(dur + 0.3, 'pink'), 1400, 0.7) * env * 0.35
    out += scrape + swish
    for i in range(hangers):
        u = max(0.0, (i + rng().uniform(-0.2, 0.2)) / hangers)
        u = u ** 0.7 if direction > 0 else u ** 1.4
        c = hanger_click(rng().uniform(0.4, 0.9))
        s = ns(np.clip(u, 0, 1) * dur)
        m = min(len(c), n - s)
        out[s:s + m] += c[:m] * rng().uniform(0.5, 1.0)
    return _end_fade(out)


def rummage(dur=0.8, density=14):
    """Rommelen in een kartonnen doos / stapel kleding (mono): doffe kraakjes en stofgeruis."""
    n = ns(dur + 0.2)
    out = np.zeros(n)
    for _ in range(int(density * dur)):
        d = rng().uniform(0.03, 0.09)
        t = tvec(d)
        b = bandpass(noise(d), rng().uniform(500, 1800), 1.2) * np.exp(-t / (d / 3))
        s = ns(rng().uniform(0, dur))
        m = min(len(b), n - s)
        out[s:s + m] += b[:m] * rng().uniform(0.3, 1.0)
    t = tvec(dur + 0.2)
    out += bandpass(noise(dur + 0.2, 'pink'), 900, 0.6) * np.clip(t / 0.1, 0, 1) * np.clip((dur - t) / 0.2, 0, 1) * 0.15
    return _end_fade(out * 0.8)


def page_turn(dur=0.35, paper=0.6):
    """Bladzijde omslaan in een album/plakboek (mono): papier-zwiep + knisper + klapje op het eind."""
    n = ns(dur + 0.15)
    t = tvec(dur + 0.15)
    u = np.clip(t / dur, 0, 1)
    env = np.sin(np.pi * u) ** 1.5 * (t < dur)
    fc = 900 + 2600 * np.sin(np.pi * u)
    swish = filter_env(noise(dur + 0.15, 'pink'), 'bandpass', fc, 0.8) * env * 0.6
    crk = np.zeros(n)
    for _ in range(int(25 * dur * paper)):
        s = ns(rng().uniform(0, dur * 0.9))
        d = ns(0.004)
        crk[s:s + d] += rng().uniform(-1, 1) * np.linspace(1, 0, d)
    crk = highpass(crk, 2500) * 0.5
    flap = lowpass(noise(dur + 0.15, 'brown'), 300) * np.exp(-np.maximum(t - dur * 0.92, 0) / 0.03) * (t >= dur * 0.92)
    return _end_fade((swish + crk + flap * 1.5) * 0.8)
