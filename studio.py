#!/usr/bin/env python
"""
Podcast Studio — CLI + lokale webserver.

  python studio.py serve                       # start de webpagina (http://localhost:8765)
  python studio.py new <id> --title ... --category intro --prompt "..."
  python studio.py round <id> --note "wat er veranderd is"
  python studio.py render <id> [ronde] [a b c]  # render optie-scripts naar WAV
  python studio.py feedback <id> [ronde]        # toon feedback uit de webpagina

Structuur:
  projects/<id>/project.json
  projects/<id>/rounds/NN/round.json      # notitie + metadata van opties
  projects/<id>/rounds/NN/a.py b.py c.py  # optie-scripts (TITLE, DESCRIPTION, render())
  projects/<id>/rounds/NN/a.wav ...       # gerenderde audio
  projects/<id>/rounds/NN/feedback.json   # feedback vanuit de webpagina
  final/<id>.wav                          # gekozen definitieve versie
"""
from __future__ import annotations

import argparse
import datetime
import importlib.util
import json
import mimetypes
import re
import shutil
import sys
import time
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parent
PROJECTS = ROOT / 'projects'
FINAL = ROOT / 'final'
WEB = ROOT / 'web'
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True  # geen __pycache__ in de rondemappen

ID_RE = re.compile(r'^[a-z0-9][a-z0-9_-]*$')
ROUND_RE = re.compile(r'^\d{2}$')
OPT_RE = re.compile(r'^[a-z]$')
CATEGORIES = ['intro', 'outro', 'transitie', 'achtergrond', 'overig']
STATIC_TYPES = {'.wav', '.mp3', '.html', '.css', '.js', '.json', '.png', '.svg', '.ico'}
MP3_BITRATE = 320


# ---------------------------------------------------------------- helpers
def now():
    return datetime.datetime.now().isoformat(timespec='seconds')


def read_json(p: Path, default):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return default


def write_json(p: Path, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    tmp.replace(p)


def project_dir(pid: str) -> Path:
    if not ID_RE.match(pid or ''):
        raise ValueError(f'Ongeldige project-id: {pid!r}')
    return PROJECTS / pid


def round_dirs(pid: str):
    rd = project_dir(pid) / 'rounds'
    if not rd.exists():
        return []
    return sorted(d for d in rd.iterdir() if d.is_dir() and ROUND_RE.match(d.name))


def round_dir(pid: str, rnd: str | None) -> Path:
    if rnd is None:
        rs = round_dirs(pid)
        if not rs:
            raise ValueError(f'Project {pid} heeft nog geen rondes')
        return rs[-1]
    rnd = f'{int(rnd):02d}'
    d = project_dir(pid) / 'rounds' / rnd
    if not d.exists():
        raise ValueError(f'Ronde {rnd} bestaat niet voor {pid}')
    return d


def wav_to_mp3(wav: Path) -> Path:
    """Maak (of hergebruik) een MP3 naast de WAV. Wordt opnieuw gemaakt als de WAV nieuwer is."""
    mp3 = wav.with_suffix('.mp3')
    if mp3.exists() and mp3.stat().st_mtime >= wav.stat().st_mtime:
        return mp3
    import lameenc
    import numpy as np
    from scipy.io import wavfile

    sr, d = wavfile.read(str(wav))
    if d.ndim == 1:
        d = np.column_stack([d, d])
    enc = lameenc.Encoder()
    enc.set_bit_rate(MP3_BITRATE)
    enc.set_in_sample_rate(sr)
    enc.set_channels(d.shape[1])
    enc.set_quality(2)  # 2 = hoge kwaliteit
    data = enc.encode(np.ascontiguousarray(d.astype(np.int16)).tobytes()) + enc.flush()
    tmp = mp3.parent / (mp3.name + '.tmp')
    tmp.write_bytes(bytes(data))
    tmp.replace(mp3)
    return mp3


# ---------------------------------------------------------------- commando's
def cmd_new(a):
    d = project_dir(a.id)
    if (d / 'project.json').exists():
        sys.exit(f'Project {a.id} bestaat al')
    write_json(d / 'project.json', {
        'title': a.title or a.id, 'category': a.category, 'prompt': a.prompt or '',
        'created': now(), 'status': 'open', 'final': None,
    })
    write_json(d / 'rounds' / '01' / 'round.json', {'note': a.note or '', 'created': now(), 'options': {}})
    print(f'Aangemaakt: {d.relative_to(ROOT)} (ronde 01)')


def cmd_round(a):
    rs = round_dirs(a.id)
    nxt = f'{(int(rs[-1].name) + 1) if rs else 1:02d}'
    write_json(project_dir(a.id) / 'rounds' / nxt / 'round.json', {'note': a.note or '', 'created': now(), 'options': {}})
    print(f'Nieuwe ronde: projects/{a.id}/rounds/{nxt}')


def render_option(script: Path):
    import numpy as np
    from engine import core

    core.seed(1000 + ord(script.stem))
    name = f'opt_{script.parent.parent.parent.name}_{script.parent.name}_{script.stem}_{time.time_ns()}'
    spec = importlib.util.spec_from_file_location(name, script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    audio = core.to_stereo(np.asarray(mod.render(), dtype=float))
    if not np.all(np.isfinite(audio)):
        raise ValueError('render() gaf NaN/inf terug')
    pk = float(np.max(np.abs(audio))) if len(audio) else 0.0
    if pk > 1.0:
        print(f'  ! piek {pk:.2f} > 1.0 — genormaliseerd (gebruik finalize())')
        audio = audio / pk * 0.98
        pk = 0.98
    wav = script.with_suffix('.wav')
    core.write_wav(wav, audio)
    dur = len(audio) / core.SR
    rms = float(np.sqrt(np.mean(audio ** 2))) if len(audio) else 0.0
    to_db = lambda v: 20 * np.log10(max(v, 1e-9))  # noqa: E731
    info = {
        'title': getattr(mod, 'TITLE', f'Optie {script.stem.upper()}'),
        'description': getattr(mod, 'DESCRIPTION', '').strip(),
        'duration': round(dur, 2),
        'rendered': now(),
    }
    print(f'  {script.stem}: {info["title"]} — {dur:.2f}s, piek {to_db(pk):.1f} dBFS, RMS {to_db(rms):.1f} dBFS')
    return info


def cmd_render(a):
    if a.round and not a.round.isdigit():  # `render <id> b` = laatste ronde, alleen optie b
        a.options, a.round = [a.round] + a.options, None
    rdir = round_dir(a.id, a.round)
    rj = read_json(rdir / 'round.json', {'note': '', 'created': now(), 'options': {}})
    scripts = sorted(p for p in rdir.glob('*.py') if OPT_RE.match(p.stem))
    if a.options:
        scripts = [s for s in scripts if s.stem in a.options]
    if not scripts:
        sys.exit(f'Geen optie-scripts (a.py, b.py, ...) in {rdir.relative_to(ROOT)}')
    print(f'Renderen: {rdir.relative_to(ROOT)}')
    failed = False
    for s in scripts:
        t0 = time.time()
        try:
            rj.setdefault('options', {})[s.stem] = render_option(s)
            print(f'     ({time.time() - t0:.1f}s)')
        except Exception:
            failed = True
            print(f'  {s.stem}: FOUT')
            traceback.print_exc()
    write_json(rdir / 'round.json', rj)
    sys.exit(1 if failed else 0)


def cmd_feedback(a):
    meta = read_json(project_dir(a.id) / 'project.json', {})
    rdir = round_dir(a.id, a.round)
    rj = read_json(rdir / 'round.json', {})
    fb = read_json(rdir / 'feedback.json', {})
    print(f'# {meta.get("title", a.id)} — ronde {rdir.name}')
    if meta.get('final'):
        f = meta['final']
        print(f'GEKOZEN: ronde {f["round"]} optie {f["option"].upper()}')
    print(f'Algemeen: {fb.get("general") or "-"}')
    for opt, info in sorted(rj.get('options', {}).items()):
        o = fb.get('options', {}).get(opt, {})
        stars = o.get('rating') or 0
        print(f'\n[{opt.upper()}] {info.get("title")}  {"*" * stars}{"." * (5 - stars)}')
        print(f'  {o.get("comment") or "-"}')
    if fb.get('updated'):
        print(f'\n(laatst bijgewerkt {fb["updated"]})')


# ---------------------------------------------------------------- server
def build_state():
    projects = []
    if PROJECTS.exists():
        for d in sorted(PROJECTS.iterdir()):
            if not d.is_dir() or not ID_RE.match(d.name):
                continue
            meta = read_json(d / 'project.json', None)
            if meta is None:
                continue
            rounds = []
            for r in round_dirs(d.name):
                rj = read_json(r / 'round.json', {})
                fb = read_json(r / 'feedback.json', {})
                letters = sorted({p.stem for p in r.glob('*.py') if OPT_RE.match(p.stem)} | set(rj.get('options', {})))
                options = []
                for L in letters:
                    info = rj.get('options', {}).get(L, {})
                    wav = r / f'{L}.wav'
                    has = wav.exists()
                    options.append({
                        'id': L,
                        'title': info.get('title', f'Optie {L.upper()}'),
                        'description': info.get('description', ''),
                        'duration': info.get('duration'),
                        'file': wav.relative_to(ROOT).as_posix() if has else None,
                        'mtime': int(wav.stat().st_mtime * 1000) if has else None,
                    })
                rounds.append({'name': r.name, 'note': rj.get('note', ''), 'created': rj.get('created'),
                               'options': options, 'feedback': fb})
            projects.append({**meta, 'id': d.name, 'rounds': rounds})
    return {'projects': projects}


def save_feedback(d):
    rdir = round_dir(d.get('project'), d.get('round'))
    fb = read_json(rdir / 'feedback.json', {'general': '', 'options': {}})
    fb.setdefault('options', {})
    opt = d.get('option')
    if opt:
        if not OPT_RE.match(opt):
            raise ValueError('Ongeldige optie')
        o = fb['options'].setdefault(opt, {})
        if 'rating' in d:
            o['rating'] = max(0, min(5, int(d['rating'])))
        if 'comment' in d:
            o['comment'] = str(d['comment'])[:5000]
    elif 'comment' in d:
        fb['general'] = str(d['comment'])[:5000]
    fb['updated'] = now()
    write_json(rdir / 'feedback.json', fb)
    return fb


def set_final(d):
    pid = d.get('project')
    pfile = project_dir(pid) / 'project.json'
    meta = read_json(pfile, None)
    if meta is None:
        raise ValueError('Onbekend project')
    target = FINAL / f'{pid}.wav'
    if d.get('clear'):
        meta['final'], meta['status'] = None, 'open'
        for f in (target, target.with_suffix('.mp3')):
            if f.exists():
                f.unlink()
    else:
        rdir = round_dir(pid, d.get('round'))
        opt = d.get('option') or ''
        wav = rdir / f'{opt}.wav'
        if not OPT_RE.match(opt) or not wav.exists():
            raise ValueError('Optie niet gevonden')
        FINAL.mkdir(exist_ok=True)
        shutil.copy2(wav, target)
        wav_to_mp3(target)
        meta['final'] = {'round': rdir.name, 'option': opt, 'at': now()}
        meta['status'] = 'klaar'
    write_json(pfile, meta)
    return meta


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, body: bytes, ctype='application/json; charset=utf-8', filename=None):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        if filename:
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        url = urlparse(self.path)
        path = unquote(url.path)
        if path == '/api/state':
            return self._json(build_state())
        if path.startswith('/mp3/'):  # /mp3/<pad naar .wav>?name=bestandsnaam.mp3
            f = (ROOT / path[len('/mp3/'):]).resolve()
            if ROOT in f.parents and f.is_file() and f.suffix.lower() == '.wav':
                name = parse_qs(url.query).get('name', [f.with_suffix('.mp3').name])[0]
                name = re.sub(r'[^A-Za-z0-9._-]', '_', name)
                if not name.lower().endswith('.mp3'):
                    name += '.mp3'
                try:
                    mp3 = wav_to_mp3(f)
                except ImportError:
                    return self._send(500, b'MP3-encoder ontbreekt: python -m pip install lameenc',
                                      'text/plain; charset=utf-8')
                return self._send(200, mp3.read_bytes(), 'audio/mpeg', filename=name)
            return self._send(404, b'niet gevonden', 'text/plain; charset=utf-8')
        if path in ('/', '/index.html'):
            path = '/web/index.html'
        if path.startswith(('/projects/', '/final/', '/web/')):
            f = (ROOT / path.lstrip('/')).resolve()
            if ROOT in f.parents and f.is_file() and f.suffix.lower() in STATIC_TYPES:
                ctype = mimetypes.guess_type(f.name)[0] or 'application/octet-stream'
                if f.suffix == '.wav':
                    ctype = 'audio/wav'
                elif ctype.startswith('text/') or f.suffix in ('.js', '.json'):
                    ctype += '; charset=utf-8'
                return self._send(200, f.read_bytes(), ctype)
        self._send(404, b'niet gevonden', 'text/plain; charset=utf-8')

    def do_POST(self):
        # Alleen JSON van dezelfde origin (voorkomt dat andere websites hier posten).
        if 'application/json' not in (self.headers.get('Content-Type') or ''):
            return self._json({'error': 'JSON vereist'}, 415)
        origin = self.headers.get('Origin')
        if origin and urlparse(origin).netloc != self.headers.get('Host'):
            return self._json({'error': 'origin geweigerd'}, 403)
        path = urlparse(self.path).path
        try:
            data = json.loads(self.rfile.read(int(self.headers.get('Content-Length') or 0)) or b'{}')
            if path == '/api/feedback':
                return self._json({'ok': True, 'feedback': save_feedback(data)})
            if path == '/api/final':
                return self._json({'ok': True, 'project': set_final(data)})
            return self._json({'error': 'onbekend'}, 404)
        except (ValueError, KeyError, TypeError) as e:
            return self._json({'error': str(e)}, 400)


def cmd_serve(a):
    PROJECTS.mkdir(exist_ok=True)
    srv = ThreadingHTTPServer(('127.0.0.1', a.port), Handler)
    url = f'http://localhost:{a.port}'
    print(f'Podcast Studio draait op {url}  (Ctrl+C om te stoppen)')
    if not a.no_browser:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


# ---------------------------------------------------------------- main
def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description='Podcast Studio')
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('new', help='nieuw verzoek/project')
    p.add_argument('id')
    p.add_argument('--title')
    p.add_argument('--category', choices=CATEGORIES, default='overig')
    p.add_argument('--prompt')
    p.add_argument('--note')
    p.set_defaults(fn=cmd_new)

    p = sub.add_parser('round', help='nieuwe ronde')
    p.add_argument('id')
    p.add_argument('--note')
    p.set_defaults(fn=cmd_round)

    p = sub.add_parser('render', help='render optie-scripts naar WAV')
    p.add_argument('id')
    p.add_argument('round', nargs='?')
    p.add_argument('options', nargs='*')
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser('feedback', help='toon feedback')
    p.add_argument('id')
    p.add_argument('round', nargs='?')
    p.set_defaults(fn=cmd_feedback)

    p = sub.add_parser('serve', help='start de webpagina')
    p.add_argument('--port', type=int, default=8765)
    p.add_argument('--no-browser', action='store_true')
    p.set_defaults(fn=cmd_serve)

    a = ap.parse_args()
    try:
        a.fn(a)
    except ValueError as e:
        sys.exit(str(e))


if __name__ == '__main__':
    main()
