#!/usr/bin/env python3
"""Verify and assemble the five offline archive parts, then extract the ready USB folder."""
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    manifest = json.loads((ROOT / 'tools' / 'parts.json').read_text())
    candidates = [ROOT, ROOT.parent, ROOT.parent.parent]
    folder = next((p for p in candidates if all((p / item['name']).is_file() for item in manifest['parts'])), None)
    if folder is None:
        raise RuntimeError('Hamma 5 qismni bitta papkaga yuklang. Yigish ZIPini shu papkaga oching.\nKerakli nomlar: ' + ', '.join(item['name'] for item in manifest['parts']))
    target = folder / manifest['folder']
    if target.exists():
        raise RuntimeError(str(target) + ' allaqachon bor. Avval uni boshqa joyga kochiring yoki nomini ozgartiring.')
    if shutil.disk_usage(folder).free < 5_100_000_000:
        raise RuntimeError('Kompyuter diskida kamida 5.1 GB bosh joy kerak. Yigishni fleshkada bajarmang.')
    for item in manifest['parts']:
        p = folder / item['name']
        if p.stat().st_size != item['size']:
            raise RuntimeError(item['name'] + ' toliq yuklanmagan. Shu qismni qayta yuklang.')
    print('\nDAVA USB AI — TOLIQ OFLAYN PAKETNI YIGISH\n', flush=True)
    with tempfile.TemporaryDirectory(prefix='Dava_AI_yigilyapti_', dir=folder) as temp:
        staging = Path(temp)
        archive = staging / manifest['archive_name']
        full = hashlib.sha256()
        with archive.open('wb') as out:
            for i, item in enumerate(manifest['parts'], 1):
                print(f'[{i}/5] ' + item['name'] + ' tekshirilyapti va birlashtirilyapti...', flush=True)
                part_hash = hashlib.sha256()
                with (folder / item['name']).open('rb') as stream:
                    for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
                        out.write(chunk)
                        part_hash.update(chunk)
                        full.update(chunk)
                if part_hash.hexdigest() != item['sha256']:
                    raise RuntimeError(item['name'] + ' buzilgan. Faqat shu qismni qayta yuklang.')
        if full.hexdigest() != manifest['archive_sha256']:
            raise RuntimeError('Yigilgan arxiv nazorat summasi mos emas.')
        print('Arxiv togri. Tayyor dastur papkasi chiqarilyapti...', flush=True)
        with zipfile.ZipFile(archive) as z:
            for item in z.infolist():
                resolved = (staging / item.filename).resolve()
                if not resolved.is_relative_to(staging.resolve()):
                    raise RuntimeError('Arxivdagi yol notogri.')
                z.extract(item, staging)
        shutil.move(str(staging / manifest['folder']), str(target))
    print('\nTAYYOR!\n' + str(target), flush=True)
    print('\nEndi shu Dava_USB_AI papkasini butunligicha fleshkaga kochiring.', flush=True)
    print('Kali uchun: papka ichida bash BOSHLASH_KALI.sh', flush=True)
    print('Windows uchun: BOSHLASH_WINDOWS.cmd', flush=True)
    print('5 qismni fleshkaga kochirish shart emas. Model tayyor papkaning ichida.', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as error:
        print('\nXATO: ' + str(error), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print('\nYigish toxtatildi. Qismlar oz joyida; qayta ishga tushirishingiz mumkin.')
        sys.exit(130)
