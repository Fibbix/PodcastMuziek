"""
Kern van de synth-engine.

Conventies
- Alle audio is een numpy float-array: mono (n,) of stereo (n, 2), samplerate SR.
- Tijden in seconden, frequenties in Hz.
- Noten als 'A4', 'C#3', 'Eb5' of als MIDI-nummer (60 = C4).
"""
from __future__ import annotations

import re

import numpy as np
from scipy import signal
from scipy.io import wavfile
from scipy.ndimage import minimum_filter1d, uniform_filter1d

SR = 44100
_rng = np.random.default_rng(1)


# ---------------------------------------------------------------- basis
def seed(s: int):
    """Zet de random-generator vast (studio.py doet dit per optie)."""
    global _rng
    _rng = np.random.default_rng(s)


def rng():
    return _rng


def ns(dur):
    """Seconden -> aantal samples."""
    return max(0, int(round(dur * SR)))


def tvec(dur):
    return np.arange(ns(dur)) / SR


def db(v):
    """dB -> lineaire factor."""
    return 10 ** (v / 20)


def silence(dur):
    return np.zeros((ns(dur), 2))


# ---------------------------------------------------------------- noten
_NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def midi(note):
    if isinstance(note, (int, float, np.integer, np.floating)):
        return float(note)
    m = re.fullmatch(r'([A-Ga-g])([#b]*)(-?\d+)', note.strip())
    if not m:
        raise ValueError(f'Onbekende noot: {note!r}')
    acc = m.group(2).count('#') - m.group(2).count('b')
    return float(12 * (int(m.group(3)) + 1) + _NOTE[m.group(1).upper()] + acc)


def freq(note):
    return 440.0 * 2 ** ((midi(note) - 69) / 12)


def transpose(note, semis):
    return midi(note) + semis


CHORDS = {
    'maj': [0, 4, 7], 'min': [0, 3, 7], 'dim': [0, 3, 6], 'aug': [0, 4, 8],
    'sus2': [0, 2, 7], 'sus4': [0, 5, 7], '7': [0, 4, 7, 10],
    'maj7': [0, 4, 7, 11], 'min7': [0, 3, 7, 10], 'add9': [0, 4, 7, 14],
    'maj9': [0, 4, 7, 11, 14], 'min9': [0, 3, 7, 10, 14], '6': [0, 4, 7, 9],
    'min6': [0, 3, 7, 9], 'power': [0, 7, 12],
}

SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11], 'minor': [0, 2, 3, 5, 7, 8, 10],
    'dorian': [0, 2, 3, 5, 7, 9, 10], 'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11], 'pentatonic': [0, 2, 4, 7, 9],
    'minor_pentatonic': [0, 3, 5, 7, 10], 'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
}


def chord(root, kind='maj', inversion=0):
    """Lijst MIDI-noten, bv. chord('C4', 'maj7', inversion=1)."""
    r = midi(root)
    notes = [r + i for i in CHORDS[kind]]
    for _ in range(inversion):
        notes = notes[1:] + [notes[0] + 12]
    return notes


def scale(root, kind='major', octaves=2):
    r = midi(root)
    return [r + 12 * o + i for o in range(octaves) for i in SCALES[kind]] + [r + 12 * octaves]


# ---------------------------------------------------------------- oscillators
def _farr(f, n):
    a = np.asarray(f, dtype=float)
    if a.ndim == 0:
        return np.full(n, float(a))
    if len(a) >= n:
        return a[:n]
    return np.pad(a, (0, n - len(a)), mode='edge')


def _blep(t, dt):
    out = np.zeros_like(t)
    dt = np.maximum(dt, 1e-9)
    m = t < dt
    x = t[m] / dt[m]
    out[m] = 2 * x - x * x - 1
    m = t > 1 - dt
    x = (t[m] - 1) / dt[m]
    out[m] = x * x + 2 * x + 1
    return out


def osc(shape, f, dur, phase=0.0, pw=0.5):
    """Band-limited oscillator. shape: sine | saw | square | triangle.
    f mag een getal (Hz) of een array (Hz per sample, voor glides/vibrato)."""
    n = ns(dur)
    f = _farr(f, n)
    dt = np.abs(f) / SR
    ph = (phase + np.concatenate(([0.0], np.cumsum(f[:-1]))) / SR) % 1.0
    if shape == 'sine':
        return np.sin(2 * np.pi * ph)
    if shape == 'saw':
        return 2 * ph - 1 - _blep(ph, dt)
    if shape in ('square', 'pulse'):
        y = np.where(ph < pw, 1.0, -1.0)
        y += _blep(ph, dt)
        y -= _blep((ph - pw) % 1.0, dt)
        return y
    if shape == 'triangle':
        return 1 - 4 * np.abs(ph - 0.5)
    raise ValueError(f'Onbekende vorm: {shape}')


def ramp(v0, v1, dur, curve='lin'):
    """Automatiseringslijn van v0 naar v1. curve: 'lin', 'exp' of een macht (bv. 2)."""
    u = np.linspace(0, 1, ns(dur))
    if curve == 'exp':
        return v0 * (v1 / v0) ** u
    if curve == 'lin':
        return v0 + (v1 - v0) * u
    return v0 + (v1 - v0) * u ** float(curve)


def vibrato(f, dur, rate=5.0, depth=0.2, delay=0.25):
    """Frequentie-array met vibrato (depth in halve tonen), na een korte delay."""
    t = tvec(dur)
    amt = np.clip((t - delay) / 0.3, 0, 1) * depth
    return _farr(f, len(t)) * 2 ** (amt * np.sin(2 * np.pi * rate * t) / 12)


def noise(dur, color='white'):
    """color: white | pink | brown. Piek genormaliseerd op 1."""
    n = ns(dur)
    w = rng().standard_normal(n)
    if color != 'white' and n > 1:
        X = np.fft.rfft(w)
        k = np.arange(len(X), dtype=float)
        k[0] = 1
        X /= k ** (0.5 if color == 'pink' else 1.0)
        w = np.fft.irfft(X, n)
    return w / (np.max(np.abs(w)) + 1e-12)


# ---------------------------------------------------------------- envelopes
def adsr(dur, a=0.01, d=0.1, s=0.8, r=0.2):
    """Envelope met totale lengte dur (inclusief release)."""
    n = ns(dur)
    na = min(ns(a), n)
    nd = min(ns(d), n - na)
    nr = min(ns(r), n - na - nd)
    nsus = n - na - nd - nr
    env = np.concatenate([
        np.linspace(0, 1, na, endpoint=False),
        np.linspace(1, s, nd, endpoint=False),
        np.full(nsus, s),
        np.linspace(s, 0, nr),
    ])
    return env


def perc(dur, attack=0.002, decay=0.3):
    """Percussieve envelope: snelle attack, exponentiële decay (tijdconstante decay)."""
    t = tvec(dur)
    env = np.minimum(t / max(attack, 1e-6), 1.0) * np.exp(-np.maximum(t - attack, 0) / decay)
    return _end_fade(env)


def _end_fade(x, dur=0.005):
    k = min(ns(dur), len(x))
    if k:
        x = x.copy()
        x[-k:] *= np.linspace(1, 0, k).reshape((-1,) + (1,) * (x.ndim - 1))
    return x


# ---------------------------------------------------------------- filters (RBJ biquads)
def _coeffs(kind, f, q=0.707, gain=0.0):
    f = float(np.clip(f, 10, SR * 0.45))
    w0 = 2 * np.pi * f / SR
    c, s = np.cos(w0), np.sin(w0)
    al = s / (2 * q)
    A = 10 ** (gain / 40)
    if kind == 'lowpass':
        b = [(1 - c) / 2, 1 - c, (1 - c) / 2]; a = [1 + al, -2 * c, 1 - al]
    elif kind == 'highpass':
        b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]; a = [1 + al, -2 * c, 1 - al]
    elif kind == 'bandpass':
        b = [al, 0, -al]; a = [1 + al, -2 * c, 1 - al]
    elif kind == 'peak':
        b = [1 + al * A, -2 * c, 1 - al * A]; a = [1 + al / A, -2 * c, 1 - al / A]
    elif kind == 'lowshelf':
        sq = 2 * np.sqrt(A) * al
        b = [A * ((A + 1) - (A - 1) * c + sq), 2 * A * ((A - 1) - (A + 1) * c), A * ((A + 1) - (A - 1) * c - sq)]
        a = [(A + 1) + (A - 1) * c + sq, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - sq]
    elif kind == 'highshelf':
        sq = 2 * np.sqrt(A) * al
        b = [A * ((A + 1) + (A - 1) * c + sq), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - sq)]
        a = [(A + 1) - (A - 1) * c + sq, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - sq]
    else:
        raise ValueError(f'Onbekend filter: {kind}')
    b, a = np.array(b), np.array(a)
    return b / a[0], a / a[0]


def filt(x, kind, f, q=0.707, gain=0.0):
    b, a = _coeffs(kind, f, q, gain)
    return signal.lfilter(b, a, x, axis=0)


def lowpass(x, f, q=0.707):
    return filt(x, 'lowpass', f, q)


def highpass(x, f, q=0.707):
    return filt(x, 'highpass', f, q)


def bandpass(x, f, q=1.0):
    return filt(x, 'bandpass', f, q)


def eq(x, f, gain, q=1.0):
    """Piek-EQ: boost/cut van gain dB rond f."""
    return filt(x, 'peak', f, q, gain)


def lowshelf(x, f, gain):
    return filt(x, 'lowshelf', f, 0.707, gain)


def highshelf(x, f, gain):
    return filt(x, 'highshelf', f, 0.707, gain)


def filter_env(x, kind, freqs, q=0.707, block=64):
    """Filter met een cutoff die per sample mag veranderen (freqs = array)."""
    freqs = _farr(freqs, len(x))
    y = np.empty_like(x, dtype=float)
    zi = np.zeros((2,) + x.shape[1:])
    for i in range(0, len(x), block):
        j = min(i + block, len(x))
        b, a = _coeffs(kind, freqs[(i + j) // 2], q)
        y[i:j], zi = signal.lfilter(b, a, x[i:j], axis=0, zi=zi)
    return y


def sweep(x, kind, f0, f1, q=0.707, curve='exp'):
    """Filter-sweep van f0 naar f1 over de hele lengte van x."""
    return filter_env(x, kind, ramp(f0, f1, len(x) / SR, curve), q)


# ---------------------------------------------------------------- stereo
def to_stereo(x):
    x = np.asarray(x, dtype=float)
    return x if x.ndim == 2 else np.column_stack([x, x])


def to_mono(x):
    x = np.asarray(x, dtype=float)
    return x if x.ndim == 1 else x.mean(axis=1)


def pan(x, p=0.0):
    """p van -1 (links) tot 1 (rechts); p mag een array zijn (pan-sweep)."""
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        p = _farr(p, len(x))
        ang = (p + 1) * np.pi / 4
        return np.column_stack([x * np.cos(ang), x * np.sin(ang)]) * np.sqrt(2)
    p = _farr(p, len(x))
    return np.column_stack([x[:, 0] * np.minimum(1, 1 - p), x[:, 1] * np.minimum(1, 1 + p)])


def widen(x, amount=1.5):
    """Mid/side: amount >1 breder, <1 smaller, 0 = mono."""
    x = to_stereo(x)
    mid = (x[:, 0] + x[:, 1]) / 2
    side = (x[:, 0] - x[:, 1]) / 2 * amount
    return np.column_stack([mid + side, mid - side])


def haas(x, ms=12.0):
    """Mono -> breed stereo door één kanaal een paar ms te vertragen."""
    x = to_mono(x)
    d = ns(ms / 1000)
    return np.column_stack([np.concatenate([x, np.zeros(d)]), np.concatenate([np.zeros(d), x])])


# ---------------------------------------------------------------- effecten
def reverb(x, decay=2.0, mix=0.3, predelay=0.02, tone=6000, wet_only=False):
    """Convolutie-galm. decay = RT60 in seconden. Output is langer (galmstaart)."""
    x = to_stereo(x)
    t = tvec(decay * 1.2)
    env = np.exp(-6.9 * t / decay) * np.minimum(t / 0.004, 1)
    ir = np.column_stack([noise(len(t) / SR) * env, noise(len(t) / SR) * env])
    ir = lowpass(ir, tone)
    ir /= np.sqrt(np.sum(ir ** 2) / 2) + 1e-12
    pd = ns(predelay)
    wet = np.column_stack([signal.fftconvolve(x[:, c], ir[:, c]) for c in range(2)])
    wet = np.vstack([np.zeros((pd, 2)), wet])
    if wet_only:
        return wet
    out = np.zeros_like(wet)
    out[:len(x)] = x * (1 - mix * 0.5)
    return out + wet * mix


def delay(x, time=0.375, feedback=0.4, mix=0.3, pingpong=True, tone=4500):
    """Echo. time in seconden (tip: Track.b(0.75) voor een gepunteerde 8e)."""
    x = to_stereo(x)
    d = ns(time)
    k_max = 1
    while feedback ** k_max > 0.01 and k_max < 40:
        k_max += 1
    out = np.zeros((len(x) + d * k_max, 2))
    out[:len(x)] += x
    echo = to_mono(x) if pingpong else x
    for k in range(1, k_max + 1):
        echo = lowpass(echo, tone) * feedback
        seg = pan(echo, -0.8 if k % 2 else 0.8) if pingpong else echo
        out[d * k:d * k + len(x)] += seg * mix
    return out


def chorus(x, depth_ms=2.5, rate=0.7, mix=0.5, base_ms=12.0):
    x = to_stereo(x)
    n = np.arange(len(x))
    out = np.empty_like(x)
    for c in range(2):
        lfo = np.sin(2 * np.pi * rate * n / SR + c * np.pi / 2)
        d = (base_ms + depth_ms * lfo) / 1000 * SR
        out[:, c] = np.interp(n - d, n, x[:, c], left=0)
    return x * (1 - mix) + out * mix


def drive(x, amount=2.0):
    """Zachte saturatie (warmer/vetter)."""
    return np.tanh(x * amount) / np.tanh(amount)


def bitcrush(x, bits=8, downsample=4):
    q = 2 ** (bits - 1)
    y = np.round(x * q) / q
    if downsample > 1:
        idx = (np.arange(len(y)) // downsample) * downsample
        y = y[idx]
    return y


def reverse(x):
    return np.asarray(x)[::-1].copy()


def tape_stop(x, dur=0.5):
    """Laat de laatste dur seconden vertragen tot stilstand (tape-stop effect)."""
    x = to_stereo(x)
    k = min(ns(dur), len(x))
    s0 = len(x) - k
    rate = (1 - np.linspace(0, 1, k)) ** 1.5
    pos = s0 + np.cumsum(rate)
    idx = np.arange(len(x))
    tail = np.column_stack([np.interp(pos, idx, x[:, c]) for c in range(2)])
    return _end_fade(np.vstack([x[:s0], tail]), 0.02)


def stutter(x, slice_dur=0.1, repeats=4, start=0.0):
    """Knip een stukje uit x en herhaal het (glitch/stutter)."""
    x = to_stereo(x)
    a = ns(start)
    piece = _end_fade(x[a:a + ns(slice_dur)], 0.003)
    return np.vstack([piece] * repeats)


def sidechain(x, bpm, depth=0.6, every=1.0, release=0.25):
    """'Pompend' volume op de beat (every in beats)."""
    t = np.arange(len(x)) / SR
    period = 60 / bpm * every
    ph = t % period
    g = 1 - depth * np.exp(-ph / (release * period / 2))
    return x * (g[:, None] if np.asarray(x).ndim == 2 else g)


def gain(x, dbv):
    return np.asarray(x) * db(dbv)


# ---------------------------------------------------------------- arrangeren
class Track:
    """Tijdlijn. Voeg geluiden toe op een tijd (sec) of beat; render() mixt alles stereo.

        song = Track(bpm=110)
        song.add(kick(), beat=0)
        song.add(pad(chord('C4','maj7'), song.b(4)), beat=0, gain=-6, pan=-0.2)
        audio = song.render()
    """

    def __init__(self, bpm=120.0):
        self.bpm = bpm
        self.events = []

    @property
    def beat(self):
        return 60.0 / self.bpm

    def b(self, beats):
        """Beats -> seconden."""
        return beats * 60.0 / self.bpm

    def add(self, audio, at=0.0, beat=None, gain=0.0, pan=0.0):
        """gain in dB, pan -1..1."""
        start = self.b(beat) if beat is not None else at
        self.events.append((ns(start), np.asarray(audio, dtype=float), gain, pan))
        return self

    def render(self, length=None):
        end = max([s + len(a) for s, a, _, _ in self.events], default=0)
        if length is not None:
            end = max(end, ns(length))
        out = np.zeros((end, 2))
        for s, a, g, p in self.events:
            a = globals()['pan'](a, p) if (a.ndim == 1 or p) else a
            out[s:s + len(a)] += a * db(g)
        return out


def mix(*parts):
    """Telt stereo/mono-delen op, allemaal vanaf t=0."""
    parts = [to_stereo(p) for p in parts]
    out = np.zeros((max(len(p) for p in parts), 2))
    for p in parts:
        out[:len(p)] += p
    return out


def concat(*parts):
    return np.vstack([to_stereo(p) for p in parts])


def loopify(x, loop_dur):
    """Maak naadloos loopbaar: alles na loop_dur (bv. galmstaart) wordt over het begin gevouwen."""
    x = to_stereo(x)
    L = ns(loop_dur)
    out = np.zeros((L, 2))
    for i in range(0, len(x), L):
        seg = x[i:i + L]
        out[:len(seg)] += seg
    return out


# ---------------------------------------------------------------- mastering
def fade(x, fade_in=0.0, fade_out=0.0):
    x = np.array(x, dtype=float)
    ki, ko = min(ns(fade_in), len(x)), min(ns(fade_out), len(x))
    shape = (-1,) + (1,) * (x.ndim - 1)
    if ki:
        x[:ki] *= np.sin(np.linspace(0, np.pi / 2, ki)).reshape(shape) ** 2
    if ko:
        x[-ko:] *= np.cos(np.linspace(0, np.pi / 2, ko)).reshape(shape) ** 2
    return x


def trim_end(x, threshold_db=-65, keep=0.05):
    a = np.max(np.abs(to_stereo(x)), axis=1)
    idx = np.nonzero(a > db(threshold_db))[0]
    if len(idx) == 0:
        return x
    return x[:min(len(x), idx[-1] + ns(keep))]


def normalize(x, peak_db=-1.0):
    pk = np.max(np.abs(x))
    return x if pk == 0 else x / pk * db(peak_db)


def limit(x, ceiling_db=-1.0, hold=0.012):
    """Look-ahead peak-limiter."""
    x = to_stereo(x)
    ceil = db(ceiling_db)
    a = np.max(np.abs(x), axis=1)
    g = np.minimum(1.0, ceil / np.maximum(a, 1e-12))
    w = 2 * ns(hold) + 1
    g = minimum_filter1d(g, w, mode='nearest')
    g = uniform_filter1d(g, w, mode='nearest')
    return np.clip(x * g[:, None], -ceil, ceil)


def finalize(x, peak=-1.0, loud=2.0, fade_in=0.0, fade_out=0.0, trim=True, hp=25):
    """Eindbewerking: DC/rommel weg, staart trimmen, luider maken (loud dB in de limiter), fades.
    Voor achtergrondmuziek: loud=0 houdt de dynamiek natuurlijker."""
    x = to_stereo(x)
    x = highpass(x, hp)
    if trim:
        x = trim_end(x)
    x = normalize(x, loud)
    x = limit(x, peak)
    return fade(x, fade_in, fade_out)


def write_wav(path, x):
    x = np.clip(to_stereo(x), -1, 1)
    wavfile.write(str(path), SR, (x * 32767).astype(np.int16))


def load_wav(path):
    """Laad een WAV (bv. een eigen sample) als float stereo op SR."""
    sr, d = wavfile.read(str(path))
    if d.dtype.kind == 'i':
        d = d / float(np.iinfo(d.dtype).max)
    elif d.dtype.kind == 'u':
        d = (d - 128) / 128.0
    d = to_stereo(d.astype(float))
    if sr != SR:
        from math import gcd
        g = gcd(sr, SR)
        d = signal.resample_poly(d, SR // g, sr // g, axis=0)
    return d
