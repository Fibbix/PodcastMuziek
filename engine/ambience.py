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
    out += shouts / np.sqrt(voices) * (ex ** 1.3 * 2.0)[:, None]
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


def final_whistle(pitch=3000, long=1.3, gap=0.5):
    """Laatste fluitsignaal: kort, kort, laaaang (mono)."""
    parts = [(0.0, 0.28), (gap, 0.28), (2 * gap, long)]
    out = np.zeros(ns(2 * gap + long + 0.1))
    for start, d in parts:
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
