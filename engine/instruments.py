"""
Instrumenten, drums en transitie-effecten.

Melodische instrumenten nemen een noot ('C4' of MIDI-nummer) en een duur (hoe lang
de noot 'ingedrukt' is); de release komt daar nog achteraan.
Mono-instrumenten geven (n,), stereo-instrumenten (n, 2).
"""
from __future__ import annotations

import numpy as np
from scipy import signal

from .ambience import slow_noise
from .core import (SR, adsr, bandpass, drive, eq, filter_env, freq, haas, highpass, lowpass,
                   noise, ns, osc, pan, ramp, reverb, rng, to_stereo, tvec, vibrato, _end_fade)


def _notes(n):
    return list(n) if isinstance(n, (list, tuple, np.ndarray)) else [n]


def _glide(note, total, glide_from=None, glide_time=0.08):
    f = freq(note)
    if glide_from is None:
        return f
    n = ns(total)
    g = ramp(freq(glide_from), f, glide_time, 'exp')
    return np.concatenate([g, np.full(max(0, n - len(g)), f)])[:n]


# ================================================================ melodisch
def pad(notes, dur, bright=0.5, detune=0.12, attack=0.6, release=1.2, voices=5, width=0.8, motion=0.0):
    """Brede supersaw-pad (stereo). notes = noot of lijst (akkoord).
    bright 0..1 = filteropening, detune in halve tonen, motion 0..1 = langzaam bewegend filter."""
    total = dur + release
    out = np.zeros((ns(total), 2))
    nl = _notes(notes)
    for note in nl:
        f = freq(note)
        for v in range(voices):
            k = v / (voices - 1) * 2 - 1 if voices > 1 else 0.0
            s = osc('saw', f * 2 ** (k * detune / 12), total, phase=rng().random())
            out += pan(s, k * width)
    out /= voices * np.sqrt(len(nl))
    cut = 250 + 9000 * bright ** 2
    if motion > 0:
        cuts = cut * (1 + motion * 0.6 * np.sin(2 * np.pi * 0.12 * tvec(total) - np.pi / 2))
        out = filter_env(out, 'lowpass', cuts, 0.8)
    else:
        out = lowpass(out, cut, 0.8)
    return out * adsr(total, attack, 0.5, 0.85, release)[:, None]


def soft_pad(notes, dur, attack=1.0, release=2.0, bright=0.3):
    """Zachte, ronde pad van driehoeksgolven (stereo) — fijn voor achtergrond."""
    total = dur + release
    out = np.zeros((ns(total), 2))
    nl = _notes(notes)
    for note in nl:
        f = freq(note)
        for k, p in ((-1, -0.6), (1, 0.6)):
            s = osc('triangle', f * 2 ** (k * 0.06 / 12), total, phase=rng().random())
            s += 0.3 * osc('sine', f * 2, total)
            out += pan(s, p)
    out /= 2 * np.sqrt(len(nl))
    out = lowpass(out, 400 + 5000 * bright ** 2)
    return out * adsr(total, attack, 0.5, 0.9, release)[:, None]


def keys(note, dur, bright=0.5, release=0.5, decay=1.6):
    """Elektrische piano (FM), warm en rond. Mono."""
    total = dur + release
    t = tvec(total)
    f = freq(note)
    idx = (0.4 + 2.6 * bright) * np.exp(-t / 0.35) + 0.15
    car = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    tine = 0.25 * bright * np.sin(2 * np.pi * min(f * 7, SR * 0.4) * t) * np.exp(-t / 0.04)
    amp = np.exp(-t / decay) * adsr(total, 0.004, 0.01, 1.0, release)
    return _end_fade((car + tine) * amp * 0.6)


def piano(note, dur, bright=0.5, release=0.4):
    """Simpele 'piano' met meerdere harmonischen en snellere hoge decay. Mono."""
    total = dur + release
    t = tvec(total)
    f = freq(note)
    y = np.zeros_like(t)
    for h in range(1, 9):
        fh = f * h * (1 + 0.0004 * h * h)  # lichte inharmoniciteit
        if fh > SR * 0.45:
            break
        y += (bright ** (h - 1) * 0.9 + 0.1) / h * np.sin(2 * np.pi * fh * t) * np.exp(-t * (0.8 + 0.6 * h))
    y += 0.15 * lowpass(noise(total), 3000) * np.exp(-t / 0.01)
    y *= adsr(total, 0.002, 0.01, 1.0, release)
    return _end_fade(y * 0.5)


def pluck(note, dur=1.5, bright=0.6, decay=None, release=0.05):
    """Getokkelde snaar (Karplus-Strong). Mono."""
    f = freq(note)
    total = dur + release
    n = ns(total)
    decay = decay or (2.5 if f < 300 else 1.5)
    N = max(2, int(round(SR / f - 0.5)))
    exc = lowpass(rng().uniform(-1, 1, N), 800 + bright * 9000)
    x = np.zeros(n)
    x[:min(N, n)] = exc[:n]
    g = 10 ** (-3 / (decay * f))
    a = np.zeros(N + 2)
    a[0] = 1
    a[N] -= g * 0.5
    a[N + 1] -= g * 0.5
    y = signal.lfilter([1.0], a, x)
    y = highpass(y, 40) * adsr(total, 0.001, 0.01, 1.0, release)
    return _end_fade(y / (np.max(np.abs(y)) + 1e-9) * 0.8)


def guitar(note, dur=1.5, bright=0.5, decay=None, release=0.08):
    """Akoestische gitaar: Karplus-Strong snaar + 'body'-resonantie. Mono."""
    y = pluck(note, dur, bright=bright, decay=decay, release=release)
    y = eq(eq(y, 110, 4, 1.2), 220, 3, 1.0)
    y = highpass(eq(y, 2500, 2 * bright, 0.8), 70)
    return y / (np.max(np.abs(y)) + 1e-9) * 0.8


def upright_bass(note, dur=1.0, bright=0.3, release=0.15):
    """Contrabas (getokkeld). Mono."""
    y = pluck(note, dur, bright=bright, decay=1.2, release=release)
    y = lowpass(eq(y, 90, 3, 1.0), 900 + 1200 * bright)
    return y / (np.max(np.abs(y)) + 1e-9) * 0.8


def strings(notes, dur, attack=0.25, release=0.6, bright=0.45, players=6):
    """Strijkersensemble (violen/altviolen/cello's afhankelijk van ligging). Stereo.
    Elke 'speler' heeft eigen vibrato en lichte ontstemming."""
    total = dur + release
    out = np.zeros((ns(total), 2))
    nl = _notes(notes)
    for note in nl:
        f0 = freq(note)
        for p in range(players):
            f = f0 * 2 ** (rng().uniform(-0.07, 0.07) / 12)
            fv = vibrato(f, total, rate=rng().uniform(4.6, 5.8), depth=rng().uniform(0.06, 0.12),
                         delay=rng().uniform(0.1, 0.3))
            s = osc('saw', fv, total, phase=rng().random())
            out += pan(s, rng().uniform(-0.7, 0.7))
    out /= players * np.sqrt(len(nl))
    out = highpass(lowpass(out, 900 + 3500 * bright, 0.6), 60)
    out = eq(out, 300, -2, 0.8)              # minder 'doos'
    out = eq(out, 1800 + 1000 * bright, 2, 1.0)  # strijk-'glans'
    return out * adsr(total, attack, 0.3, 0.9, release)[:, None]


def pizzicato(note, dur=0.3, bright=0.35):
    """Getokkelde strijker (pizzicato). Mono."""
    y = pluck(note, dur, bright=bright, decay=0.35, release=0.05)
    y = eq(lowpass(y, 2500), 250, 3, 1.0)
    return y / (np.max(np.abs(y)) + 1e-9) * 0.8


def vibraphone(note, dur=0.5, release=1.5, tremolo=0.25, bright=0.4, decay=2.5):
    """Vibrafoon: metalen staven (boventonen 1:4:10), zachte mallet, motor-tremolo. Mono."""
    total = dur + release
    t = tvec(total)
    f = freq(note)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / decay)
    for ratio, amp, dec in ((4.0, 0.3, 0.5), (10.0, 0.12, 0.12)):
        if f * ratio < SR * 0.45:
            y += bright * amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t / dec)
    y += 0.04 * lowpass(noise(total), 2500) * np.exp(-t / 0.004)
    y *= 1 - tremolo * (0.5 + 0.5 * np.sin(2 * np.pi * 5.5 * t))
    y *= np.minimum(t / 0.002, 1) * adsr(total, 0.001, 0.01, 1.0, release)
    return _end_fade(y * 0.6)


def marimba(note, dur=0.3, release=0.3, bright=0.5):
    """Marimba: houten staven, korte warme toon. Mono."""
    total = dur + release
    t = tvec(total)
    f = freq(note)
    dec = 0.25 + 60 / f
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / dec)
    for ratio, amp, d in ((3.9, 0.35, 0.06), (9.2, 0.1, 0.02)):
        if f * ratio < SR * 0.45:
            y += bright * amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t / d)
    y *= np.minimum(t / 0.002, 1)
    return _end_fade(y * 0.7)


def bell(note, dur=0.5, release=2.0, bright=0.5):
    """Glazen bel / glockenspiel (FM). Mono."""
    total = dur + release
    t = tvec(total)
    f = freq(note)
    idx = (1 + 4 * bright) * np.exp(-t / 0.4)
    y = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * 3.5 * t))
    y += 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.3)
    y *= np.minimum(t / 0.002, 1) * np.exp(-t * 4 / total)
    return _end_fade(y * 0.5)


def bass(note, dur, shape='saw', cutoff=450, env=1400, q=1.0, sub=0.5, release=0.08, glide_from=None):
    """Synth-bas met filter-envelope. Mono."""
    total = dur + release
    t = tvec(total)
    f = _glide(note, total, glide_from)
    s = osc(shape, f, total) + sub * osc('sine', f, total)
    y = filter_env(s, 'lowpass', cutoff + env * np.exp(-t / 0.12), q)
    return _end_fade(y * adsr(total, 0.004, 0.15, 0.8, release) * 0.6)


def sub(note, dur, release=0.1):
    """Pure sub-bas (sinus). Mono."""
    total = dur + release
    return _end_fade(osc('sine', freq(note), total) * adsr(total, 0.005, 0.05, 1.0, release) * 0.8)


def lead(note, dur, shape='square', cutoff=3500, vib=0.15, release=0.15, glide_from=None, pw=0.5):
    """Synth-lead met vibrato. Mono."""
    total = dur + release
    f = vibrato(_glide(note, total, glide_from), total, depth=vib)
    y = lowpass(osc(shape, f, total, pw=pw), cutoff)
    return _end_fade(y * adsr(total, 0.01, 0.1, 0.8, release) * 0.5)


def chip(note, dur, shape='square', pw=0.25, release=0.02):
    """8-bit / chiptune toon (geen filter). Mono."""
    total = dur + release
    y = osc(shape, freq(note), total, pw=pw)
    return _end_fade(y * adsr(total, 0.002, 0.05, 0.7, release) * 0.35)


def strum(notes, dur, spread=0.025, instrument=None, **kw):
    """Speel een akkoord licht na elkaar (gitaar-achtig). Mono."""
    instrument = instrument or pluck
    nl = _notes(notes)
    parts = [instrument(n, dur, **kw) for n in nl]
    L = max(len(p) for p in parts) + ns(spread * len(nl))
    out = np.zeros(L)
    for i, p in enumerate(parts):
        s = ns(spread * i)
        out[s:s + len(p)] += p
    return out / np.sqrt(len(nl))


def poly(instrument, notes, dur, **kw):
    """Speel meerdere noten tegelijk met een mono-instrument (bv. poly(keys, chord('C4','maj7'), 2))."""
    parts = [instrument(n, dur, **kw) for n in _notes(notes)]
    L = max(len(p) for p in parts)
    out = np.zeros((L,) + parts[0].shape[1:])
    for p in parts:
        out[:len(p)] += p
    return out / np.sqrt(len(parts))


def organ(notes, dur, drawbars=(8, 8, 8, 0, 0, 0, 0, 0, 0), leslie='slow', click=0.3, release=0.08, grit=1.3):
    """Tonewheel-orgel (Hammond-achtig), stereo. drawbars = 9 registers (16', 5⅓', 8', 4', 2⅔', 2', 1⅗', 1⅓', 1'),
    elk 0..8. leslie: 'slow' | 'fast' | None (draaiende luidspreker)."""
    ratios = (0.5, 1.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0)
    total = dur + release
    t = tvec(total)
    y = np.zeros(len(t))
    nl = _notes(notes)
    for note in nl:
        f = freq(note)
        for r, lvl in zip(ratios, drawbars):
            if lvl and f * r < SR * 0.45:
                y += (lvl / 8) * np.sin(2 * np.pi * f * r * t + rng().random() * 6.28)
    y /= np.sqrt(len(nl)) * max(1.0, sum(d > 0 for d in drawbars) ** 0.5)
    k = ns(0.006)
    if click:
        cl = highpass(noise(0.006), 1500) * np.linspace(1, 0, k) * click
        y[:k] += cl[:k]
    y *= adsr(total, 0.004, 0.01, 1.0, release)
    y = drive(y * 0.6, grit)
    if not leslie:
        return pan(y, 0)
    rate = 6.6 if leslie == 'fast' else 0.8
    n = np.arange(len(y))
    out = np.empty((len(y), 2))
    for c, ph in enumerate((0.0, np.pi / 2)):
        lfo = np.sin(2 * np.pi * rate * n / SR + ph)
        d = (1.2 + 0.6 * lfo) / 1000 * SR  # doppler
        out[:, c] = np.interp(n - d, n, y, left=0) * (1 + 0.25 * lfo)
    return out * 0.8


def whistling(events, total=None, vib=0.3, breath=0.05, glide=0.035):
    """Menselijk gefloten melodie, stereo-klaar mono. events = [(start_sec, noot, duur_sec), ...].
    Glijdt tussen de noten (zoals echte fluiters), met vibrato en wat adem."""
    events = sorted(events)
    total = total or (events[-1][0] + events[-1][2] + 0.3)
    n = ns(total)
    f = np.zeros(n)
    a = np.zeros(n)
    for start, note, dur in events:
        s, e = ns(start), min(n, ns(start + dur))
        f[s:e] = freq(note)
        L = e - s
        att, rel = min(ns(0.03), L // 3), min(ns(0.05), L // 3)
        env = np.ones(L)
        env[:att] = np.linspace(0, 1, att)
        if rel:
            env[-rel:] = np.linspace(1, 0.15, rel)
        a[s:e] = np.maximum(a[s:e], env * rng().uniform(0.85, 1.0))
    # gaten opvullen met vorige toonhoogte (zodat er geglijd wordt) en glijden via log-smoothing
    idx = np.where(f > 0, np.arange(n), 0)
    np.maximum.accumulate(idx, out=idx)
    f = f[idx]
    f[f == 0] = freq(events[0][1])
    coef = np.exp(-1 / (glide * SR))
    lf = signal.lfilter([1 - coef], [1, -coef], np.log(f), zi=[np.log(f[0]) * coef])[0]
    t = np.arange(n) / SR
    drift = 2 ** ((slow_noise(total, 1.5) - 0.5) * 0.12 / 12)
    vib_curve = 2 ** (vib * np.sin(2 * np.pi * 5.6 * t) / 12 * np.clip(a, 0, 1))
    fr = np.exp(lf) * drift * vib_curve
    a = signal.lfilter([1 - np.exp(-1 / (0.006 * SR))], [1, -np.exp(-1 / (0.006 * SR))], a)
    y = osc('sine', fr, total) + 0.04 * osc('sine', fr * 2, total)
    y += breath * filter_env(noise(total), 'bandpass', fr, 6) * 3
    return _end_fade(y * a * 0.6)


def tambourine(decay=0.14, shake=0.0):
    """Tamboerijn-tik (mono). shake > 0 = korte schudbeweging ervoor."""
    dur = decay * 1.6 + shake
    t = tvec(dur)
    jingles = sum(np.sin(2 * np.pi * rng().uniform(5200, 9800) * t + rng().random() * 6) for _ in range(6)) / 6
    y = (0.6 * highpass(noise(dur), 6000) + 0.5 * jingles)
    env = np.exp(-np.maximum(t - shake, 0) * 5 / decay) * np.minimum(t / (shake + 0.002), 1)
    return _end_fade(y * env * 0.7)


def stomp(people=4, spread=0.012):
    """Groep die op de vloer/tribune stampt (mono)."""
    out = np.zeros(ns(0.5 + spread * people))
    for _ in range(people):
        k = kick(punch=0.15, decay=0.22, tone=rng().uniform(55, 75), click=0.0)
        thud = lowpass(noise(0.12), 500) * np.exp(-tvec(0.12) / 0.02) * 0.6
        k[:len(thud)] += thud
        s = ns(rng().uniform(0, spread * people))
        out[s:s + len(k)] += k * rng().uniform(0.7, 1.0)
    return out / np.sqrt(people)


def group_clap(people=5, spread=0.01):
    """Meerdere mensen die tegelijk (net niet helemaal) klappen (mono)."""
    out = np.zeros(ns(0.4 + spread * people))
    for _ in range(people):
        dur = 0.18
        t = tvec(dur)
        c = bandpass(noise(dur), rng().uniform(900, 2200), 1.4) * np.exp(-t / rng().uniform(0.008, 0.015))
        s = ns(rng().uniform(0, spread * people))
        out[s:s + len(c)] += c * rng().uniform(0.6, 1.0)
    return _end_fade(out / np.sqrt(people) * 2.0)


def humanize(beat, timing=0.012, bpm=None):
    """Kleine timingvariatie (in beats als bpm gegeven, anders in seconden) zodat het minder 'machinaal' klinkt."""
    j = rng().normal(0, timing)
    return beat + (j * bpm / 60 if bpm else j)


def vel(spread_db=1.5):
    """Willekeurige aanslagsterkte-variatie in dB."""
    return rng().normal(0, spread_db)


# ================================================================ drums
def kick(punch=1.0, decay=0.4, tone=48, click=0.3):
    dur = decay * 1.5
    t = tvec(dur)
    f = tone + tone * 3.5 * punch * np.exp(-t / 0.035)
    body = drive(osc('sine', f, dur) * np.exp(-t * 5 / decay), 1.5)
    cl = highpass(noise(dur), 2000) * np.exp(-t / 0.003) * click
    return _end_fade((body + cl) * 0.9)


def snare(tone=185, decay=0.2, snappy=0.7):
    dur = decay * 1.5
    t = tvec(dur)
    body = (np.sin(2 * np.pi * tone * t) + 0.5 * np.sin(2 * np.pi * tone * 1.6 * t)) * np.exp(-t * 5 / (decay * 0.5))
    nz = bandpass(highpass(noise(dur), 1200), 5000, 0.5) * np.exp(-t * 5 / decay) * snappy * 3
    return _end_fade((body * 0.6 + nz) * 0.7)


def clap(decay=0.25):
    dur = 0.04 + decay
    t = tvec(dur)
    env = np.zeros_like(t)
    for off in (0.0, 0.011, 0.022, 0.031):
        tt = t - off
        env += np.where(tt >= 0, np.exp(-np.maximum(tt, 0) / 0.004), 0)
    tt = t - 0.031
    env += np.where(tt >= 0, 0.6 * np.exp(-np.maximum(tt, 0) * 5 / decay), 0)
    return _end_fade(bandpass(noise(dur), 1300, 1.2) * env * 2.5)


def _metal(dur):
    return sum(osc('square', 40 * r, dur) for r in (2, 3, 4.16, 5.43, 6.79, 8.21)) / 6


def hat(open=False, decay=None, tone=1.0):
    decay = decay or (0.35 if open else 0.05)
    dur = decay * 1.5
    t = tvec(dur)
    y = highpass(_metal(dur) * 0.6 + noise(dur) * 0.5, 7000 * tone)
    return _end_fade(y * np.exp(-t * 5 / decay) * 0.6)


def shaker(decay=0.08):
    dur = decay * 1.6
    t = tvec(dur)
    env = np.minimum(t / 0.015, 1) * np.exp(-t * 5 / decay)
    return _end_fade(bandpass(noise(dur), 7000, 0.8) * env * 0.8)


def crash(decay=2.0):
    dur = decay * 1.2
    t = tvec(dur)
    y = highpass(noise(dur) * 0.7 + _metal(dur) * 0.4, 4000)
    return _end_fade(haas(y * np.exp(-t * 5 / decay) * 0.5, 9))


def tom(note='G2', decay=0.3):
    dur = decay * 1.5
    t = tvec(dur)
    f0 = freq(note)
    f = f0 * (1 + 0.6 * np.exp(-t / 0.05))
    return _end_fade(osc('sine', f, dur) * np.exp(-t * 5 / decay) * 0.8)


# ================================================================ transitie-FX (stereo)
def riser(dur=2.0, start=300, end=6000, tone=0.3, note=None, q=2.0, curve=2.0):
    """Opbouwende 'riser': gefilterde ruis die omhoog sweept (+ optioneel stijgende toon)."""
    t = tvec(dur)
    freqs = ramp(start, end, dur, 'exp')
    parts = []
    for _ in range(2):  # L en R verschillende ruis -> breed
        parts.append(filter_env(noise(dur), 'bandpass', freqs, q))
    y = np.column_stack(parts)
    y /= np.max(np.abs(y)) + 1e-9
    if tone > 0:
        f0 = freq(note) if note is not None else start / 2
        s = osc('saw', ramp(f0, f0 * 4, dur, 'exp'), dur)
        s = filter_env(s, 'lowpass', freqs * 1.5, 1.0)
        y += to_stereo(s / (np.max(np.abs(s)) + 1e-9)) * tone
    y *= ((t / dur) ** curve)[:, None]
    return _end_fade(y / (np.max(np.abs(y)) + 1e-9) * 0.9, 0.01)


def downlifter(dur=1.5, start=5000, end=150, q=1.5):
    """Omlaag-sweep die uitsterft (na een drop/impact)."""
    t = tvec(dur)
    freqs = ramp(start, end, dur, 'exp')
    y = np.column_stack([filter_env(noise(dur), 'bandpass', freqs, q) for _ in range(2)])
    y *= (np.exp(-t * 3 / dur) * np.minimum(t / 0.01, 1))[:, None]
    return _end_fade(y / (np.max(np.abs(y)) + 1e-9) * 0.9)


def whoosh(dur=1.0, peak=0.55, low=250, high=4500, q=1.2, pan_from=-0.8, pan_to=0.8, color='pink'):
    """Swoosh: ruis die aanzwelt, langs vliegt (filter + pan) en wegsterft."""
    t = tvec(dur)
    u = t / dur
    bump = np.where(u < peak, u / peak, (1 - u) / (1 - peak))
    bump = np.sin(np.pi / 2 * np.clip(bump, 0, 1))
    freqs = low * (high / low) ** bump
    y = filter_env(noise(dur, color), 'bandpass', freqs, q)
    y = y / (np.max(np.abs(y)) + 1e-9) * bump ** 2
    return _end_fade(pan(y, ramp(pan_from, pan_to, dur)) * 0.8)


def impact(decay=2.0, low=40, brightness=0.5):
    """Dikke klap/boom met galm (begin van een intro, of eind van een riser)."""
    k = kick(punch=1.6, decay=1.0, tone=low, click=0.6)
    dur = len(k) / SR
    t = tvec(dur)
    nz = lowpass(noise(dur), 1500 + 6000 * brightness) * np.exp(-t / 0.08) * 0.6
    y = reverb(k + nz, decay=decay, mix=0.45, tone=3000 + 5000 * brightness)
    return _end_fade(y / (np.max(np.abs(y)) + 1e-9) * 0.95, 0.05)


def reverse_swell(x, decay=2.5, tone=6000):
    """Omgekeerde galm van x: zwelt aan naar het moment waarop x begint.
    Plaats hem zo dat hij eindigt waar x start: start = t_x - len(swell)/SR."""
    wet = reverb(x, decay=decay, mix=1.0, tone=tone, wet_only=True)
    y = wet[::-1].copy()
    return y / (np.max(np.abs(y)) + 1e-9) * 0.8


def sparkle(root='C6', kind='major', count=8, step=0.06, decay=1.2):
    """Snelle glinsterende arpeggio van belletjes (stereo)."""
    from .core import scale
    notes = scale(root, kind, 1)
    out = np.zeros((ns(step * count + decay + 1), 2))
    for i in range(count):
        b = pan(bell(notes[(i * 2) % len(notes)], 0.1, decay, 0.3), np.sin(i * 1.3) * 0.7)
        s = ns(step * i)
        out[s:s + len(b)] += b * (1 - i / (count * 1.5))
    return out
