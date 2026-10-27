#!/usr/bin/env python3
"""Build the complete, checksum-verified offline release on GitHub's runner."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
ENGINE = ('https://github.com/mozilla-ai/llamafile/releases/download/0.10.6/llamafile-0.10.6-thin', 43856395, '756bf97febae557084e8ced9bde7a1cb0c7f6ce778530d582afa219406237a50')
MODEL = ('https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/bc640142c66e1fdd12af0bd68f40445458f3869b/Qwen3-4B-Q4_K_M.gguf?download=true', 2497280256, '7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def download(spec, destination):
    url, size, expected = spec
    h = hashlib.sha256()
    with urllib.request.urlopen(url, timeout=120) as response, destination.open('wb') as stream:
        for data in iter(lambda: response.read(8 * 1024 * 1024), b''):
            stream.write(data)
            h.update(data)
    if destination.stat().st_size != size or h.hexdigest() != expected:
        raise RuntimeError('Upstream integrity verification failed: ' + destination.name)
    print('Verified upstream:', destination.name, flush=True)


def main():
    DIST.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='dava-release-') as temp:
        temp = Path(temp)
        app = temp / 'Dava_USB_AI'
        app.mkdir()
        for name in ('web', 'tools', 'licenses'):
            shutil.copytree(ROOT / name, app / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for name in ('BOSHLASH_KALI.sh', 'BOSHLASH_WINDOWS.cmd', 'TEKSHIRISH_KALI.sh', 'TEKSHIRISH_WINDOWS.cmd', 'AVVAL_OQING.txt', 'SINOV_NATIJASI.txt'):
            shutil.copyfile(ROOT / name, app / name)
        for name in ('bin', 'models', 'logs'):
            (app / name).mkdir()
        download(ENGINE, app / 'bin/llamafile.exe')
        download(MODEL, app / 'models/Qwen3-4B-Q4_K_M.gguf')
        for name in ('BOSHLASH_KALI.sh', 'TEKSHIRISH_KALI.sh', 'bin/llamafile.exe'):
            (app / name).chmod(0o755)
        entries = sorted(p for p in app.rglob('*') if p.is_file())
        (app / 'SHA256SUMS.txt').write_text(''.join(digest(p) + '  ' + p.relative_to(app).as_posix() + '\n' for p in entries))
        archive = temp / 'Dava_USB_AI_Tayyor.zip'
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1, allowZip64=True) as z:
            z.write(app / 'logs', 'Dava_USB_AI/logs/')
            for p in sorted(app.rglob('*')):
                if p.is_file():
                    z.write(p, p.relative_to(temp).as_posix())
        with zipfile.ZipFile(archive) as z:
            bad = z.testzip()
            if bad:
                raise RuntimeError('ZIP integrity failed: ' + bad)
        parts = []
        full = hashlib.sha256()
        with archive.open('rb') as stream:
            for index in range(1, 100):
                first = stream.read(8 * 1024 * 1024)
                if not first:
                    break
                path = DIST / f'Dava_USB_AI.zip.{index:03d}'
                size = 0
                h = hashlib.sha256()
                with path.open('wb') as output:
                    chunk = first
                    while chunk:
                        output.write(chunk)
                        h.update(chunk)
                        full.update(chunk)
                        size += len(chunk)
                        if size == 500000000:
                            break
                        chunk = stream.read(min(8 * 1024 * 1024, 500000000 - size))
                parts.append({'name': path.name, 'size': size, 'sha256': h.hexdigest()})
                print('Created:', path.name, size, flush=True)
        if len(parts) != 5:
            raise RuntimeError('The installer expects exactly five parts; update before releasing.')
        manifest = {'archive_name': archive.name, 'archive_size': archive.stat().st_size, 'archive_sha256': full.hexdigest(), 'folder': app.name, 'parts': parts}
        (DIST / 'parts.json').write_text(json.dumps(manifest, indent=2) + '\n')
        guide = temp / 'Dava_USB_AI_Yigish'
        shutil.copytree(ROOT / 'installer', guide, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        (guide / 'tools/parts.json').write_text(json.dumps(manifest, indent=2) + '\n')
        with zipfile.ZipFile(DIST / 'Dava_USB_AI_Yigish.zip', 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for p in sorted(guide.rglob('*')):
                if p.is_file():
                    z.write(p, p.relative_to(temp).as_posix())
        (DIST / 'SHA256SUMS.txt').write_text(''.join(digest(p) + '  ' + p.name + '\n' for p in sorted(DIST.iterdir()) if p.is_file() and p.name != 'SHA256SUMS.txt'))
        print('Complete offline release ready.', flush=True)


if __name__ == '__main__':
    main()
