"""Zang uit spraak: een gesproken lettergreep (bv. Windows-TTS of een eigen opname) laten 'zingen' op een noot.

Werkwijze (LPC-vocoder): per 5 ms wordt de klankkleur (het spectrale filter van mond/keel) geanalyseerd.
Medeklinkers (stemloos: p, t, s) blijven het originele restsignaal houden en klinken dus natuurlijk;
het stemhebbende deel (klinker, d, r) wordt opnieuw aangeslagen met een stembandpuls op de gewenste toonhoogte
en uitgerekt tot de nootduur. Resultaat: verstaanbaar, precies zuiver ("autotune"-achtig) gezongen.
"""
import numpy as np
from scipy import signal

from .core import SR, freq, ns, rng

VSR = 16000          # analyse-/synthesesnelheid (TTS levert 16 kHz)
HOP = 80             # 5 ms
WIN = 400            # 25 ms
ORDER = 18
PRE = 0.95


def load_voice(path):
    """Laad een WAV als mono float op 16 kHz (voor sing())."""
    from scipy.io import wavfile
    sr, d = wavfile.read(str(path))
    d = d.astype(float) / (np.iinfo(d.dtype).max if d.dtype.kind == 'i' else 1.0)
    if d.ndim > 1:
        d = d.mean(axis=1)
    if sr != VSR:
        from math import gcd
        g = gcd(sr, VSR)
        d = signal.resample_poly(d, VSR // g, sr // g)
    return d


def _levinson(r, order):
    a = np.zeros(order + 1)
    a[0] = 1.0
    k = np.zeros(order)
    err = r[0]
    for i in range(1, order + 1):
        acc = r[i] + np.dot(a[1:i], r[i - 1:0:-1])
        ki = -acc / err
        k[i - 1] = ki
        a[1:i + 1] = a[1:i + 1] + ki * np.concatenate([a[i - 1:0:-1], [1.0]])
        err *= (1 - ki * ki)
    return k


def _k2a(k):
    a = np.array([1.0])
    for ki in k:
        a = np.concatenate([a, [0.0]]) + ki * np.concatenate([[0.0], a[::-1]])
    return a


def _analyze(x):
    """Per frame: reflectiecoëfficiënten, restsignaal-RMS, stemhebbend ja/nee, en het restsignaal zelf."""
    WIN2 = 640  # langer venster voor de stem-detectie (lage mannenstem)
    xr = np.concatenate([np.zeros(WIN // 2), x, np.zeros(WIN + WIN2)])
    x = signal.lfilter([1, -PRE], [1], x)
    x = np.concatenate([np.zeros(WIN // 2), x, np.zeros(WIN)])
    nf = (len(x) - WIN) // HOP
    win = np.hanning(WIN)
    lag = np.exp(-0.5 * (2 * np.pi * 60 / VSR * np.arange(ORDER + 1)) ** 2)  # lag window (stabiel)
    K, G, V = np.zeros((nf, ORDER)), np.zeros(nf), np.zeros(nf, bool)
    res = np.zeros(nf * HOP + WIN)
    zi = np.zeros(ORDER)
    lp = signal.butter(4, 900, 'low', fs=VSR, output='sos')
    for i in range(nf):
        fr = x[i * HOP:i * HOP + WIN] * win
        r = np.correlate(fr, fr, 'full')[WIN - 1:WIN + ORDER] * lag
        r[0] = r[0] * 1.0001 + 1e-12
        K[i] = _levinson(r, ORDER)
        A = _k2a(K[i])
        c = i * HOP + WIN // 2
        seg = x[c - HOP // 2:c + HOP // 2]
        e, zi = signal.lfilter(A, [1], seg, zi=zi)
        res[c - HOP // 2:c + HOP // 2] = e
        G[i] = np.sqrt(np.mean(e ** 2) + 1e-14)
        # stemhebbend: periodiek (genormaliseerde autocorrelatie, 60-320 Hz) of energie vooral laag (klinker)
        raw = xr[i * HOP:i * HOP + WIN2]
        f = signal.sosfilt(lp, raw)
        f = f - f.mean()
        ac = np.correlate(f, f, 'full')[len(f) - 1:]
        ac = ac / (len(f) - np.arange(len(f))) * len(f)
        lo, hi = VSR // 320, VSR // 60
        per = ac[lo:hi].max() / (ac[0] + 1e-12)
        low = np.sum(f ** 2) / (np.sum((raw - raw.mean()) ** 2) + 1e-12)
        V[i] = per > 0.6 or low > 0.8
    # alleen echte stukken stem (min. 4 frames), kleine gaten dichten
    v = V.copy()
    for i in range(1, nf - 1):
        if not v[i] and V[i - 1] and V[i + 1]:
            v[i] = True
    return K, G, v, res[WIN // 2:WIN // 2 + nf * HOP]


def _pulses(f, breath):
    """Bandbegrensde stembandpuls (vlak spectrum) met continue fase, frequentiecurve f (Hz) per sample."""
    ph = np.cumsum(f) / VSR
    n_h = int(VSR / 2 / f.min())
    y = np.zeros(len(f))
    for h in range(1, n_h + 1):
        mask = (h * f) < VSR / 2 * 0.95
        y += np.where(mask, np.cos(2 * np.pi * h * ph), 0.0)
    y /= np.sqrt(np.mean(y ** 2) + 1e-12)
    return y + breath * rng().standard_normal(len(f))


def sing_syllable(x, note, dur, vowel=None, hold=None, vib=0.25, scoop=0.6, formant=1.0, breath=0.12, cents=0.0):
    """Laat één gesproken lettergreep `x` (16 kHz mono) zingen op `note` gedurende `dur` s (vanaf klinkerstart).
    vowel = (t0, t1) in s: het stemhebbende deel dat gezongen wordt (anders automatisch gezocht);
    hold = tijdstip (s) in de klinker dat wordt aangehouden (standaard het midden).
    Geeft (audio op SR, mono; aanloop_seconden) terug: de aanloop = medeklinkers vóór de klinker,
    die horen vóór de tel te klinken. formant < 1 = donkerdere/grotere stem, > 1 = lichter."""
    K, G, V, res = _analyze(x)
    act = G > G.max() * 10 ** (-45 / 20)
    idx = np.where(act)[0]
    first, last = idx[0], idx[-1]
    if vowel is not None:
        v0, v1 = int(vowel[0] * VSR / HOP), min(int(vowel[1] * VSR / HOP), len(K) - 1)
        first, last = min(first, v0), max(last, v1)
    else:
        vi = np.where(V[first:last + 1])[0] + first
        if len(vi) == 0:
            raise ValueError('geen stemhebbend deel gevonden in lettergreep')
        v0, v1 = vi[0], vi[-1]
    coda = list(range(v1 + 1, last + 1))
    onset = list(range(first, v0))
    hop_out = HOP  # synthese op VSR
    n_voiced = max(v1 - v0 + 1, int(round(dur * VSR / hop_out)) - len(coda))
    # frame-map: aanloop 1:1; in het stemhebbende deel wordt `hold` aangehouden (met een klein beetje beweging),
    # wat ervoor/erna komt (overgang naar klinker, bv. 'r') klinkt op normale snelheid; coda 1:1
    h = (v0 + v1) / 2 if hold is None else hold * VSR / HOP
    pre, post = h - v0, v1 - h
    sus = n_voiced - pre - post
    if sus <= 0:
        vmap = np.linspace(v0, v1, n_voiced)
    else:
        q = np.arange(n_voiced, dtype=float)
        wob = 1.5 * np.sin(np.linspace(0, np.pi, n_voiced))
        vmap = np.where(q < pre, v0 + q, np.where(q < pre + sus, h + wob * np.sin(q / 9.0) * 0.5, h + (q - pre - sus)))
        vmap = np.clip(vmap, v0, v1)
    frames = [(float(i), False) for i in onset] + [(float(i), True) for i in vmap] + [(float(i), False) for i in coda]

    n = len(frames) * hop_out
    # toonhoogte: scoop van onder naar de noot, vertraagd vibrato
    f_target = freq(note) * 2 ** (cents / 1200) / formant
    t = np.arange(n_voiced * hop_out) / VSR
    sc = 2 ** (-scoop / 12 * np.exp(-t / 0.045))
    vb = 2 ** (vib / 12 * np.sin(2 * np.pi * 5.3 * t) * np.clip((t - 0.25) / 0.25, 0, 1))
    drift = 2 ** (np.cumsum(rng().standard_normal(len(t))) / np.sqrt(len(t)) * 0.08 / 12)
    pulses = _pulses(f_target * sc * vb * drift, breath)

    y = np.zeros(n)
    zi = np.zeros(ORDER)
    pv = 0
    for j, (fi, voiced) in enumerate(frames):
        i0 = int(np.floor(fi))
        i1 = min(i0 + 1, len(K) - 1)
        w = fi - i0
        k = (1 - w) * K[i0] + w * K[i1]
        g = (1 - w) * G[i0] + w * G[i1]
        if voiced:
            ex = pulses[pv * hop_out:(pv + 1) * hop_out] * g
            pv += 1
        else:
            ex = res[i0 * HOP:i0 * HOP + HOP]
            if len(ex) < hop_out:
                ex = np.pad(ex, (0, hop_out - len(ex)))
        out, zi = signal.lfilter([1], _k2a(k), ex, zi=zi)
        y[j * hop_out:(j + 1) * hop_out] = out
    y = signal.lfilter([1], [1, -PRE], y)
    y = np.clip(y, -4, 4)
    # naar SR; formant-verschuiving door af te spelen op een andere snelheid
    from math import gcd
    rate = VSR * formant
    up, down = SR, int(round(rate))
    g_ = gcd(up, down)
    y = signal.resample_poly(y, up // g_, down // g_)
    fade = min(len(y) // 4, ns(0.01))
    y[-fade:] *= np.linspace(1, 0, fade)
    lead_in = len(onset) * hop_out / rate
    return y, lead_in


def _loudest(y, win=0.1):
    h = ns(win)
    e = np.convolve(y ** 2, np.ones(h) / h, 'valid')
    return np.sqrt(e.max() + 1e-12)


def sing(events, total=None, even=True, **kw):
    """Gezongen regel. events = [(start_sec, noot, duur_sec, lettergreep), ...]; lettergreep = 16k-array of
    {'x': array, 'vowel': (t0, t1), 'hold': t}; start = klinkerstart (op de tel).
    even=True maakt alle lettergrepen even luid. Extra keyword-argumenten gaan naar sing_syllable (vib, scoop, formant, breath, cents)."""
    parts = []
    for start, note, dur, syl in events:
        if isinstance(syl, dict):  # {'x': array, 'vowel': (t0, t1), 'hold': t}
            y, lead = sing_syllable(syl['x'], note, dur, vowel=syl.get('vowel'), hold=syl.get('hold'), **kw)
        else:
            y, lead = sing_syllable(syl, note, dur, **kw)
        if even:  # elke lettergreep even luid (TTS-woorden verschillen in sterkte)
            y = y / _loudest(y) * 0.2
        parts.append((start - lead, y))
    end = max(s + len(y) / SR for s, y in parts)
    total = total or end + 0.05
    out = np.zeros(ns(total))
    for s, y in parts:
        a = max(0, ns(s))
        y = y[max(0, -ns(s)):]
        m = min(len(y), len(out) - a)
        out[a:a + m] += y[:m]
    pk = np.max(np.abs(out)) + 1e-12
    return out / pk * 0.7
