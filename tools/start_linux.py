#!/usr/bin/env python3
"""Start the bundled CPU engine without installing Python packages or an LLM service."""
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENGINE_HASH = '756bf97febae557084e8ced9bde7a1cb0c7f6ce778530d582afa219406237a50'
MODEL_SIZE = 2497280256


def choose_port():
    requested = os.environ.get('DAVA_PORT')
    ports = [int(requested)] if requested else range(8765, 8800)
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise RuntimeError('8765-8799 portlar band. Oldingi AI oynasini yoping.')


def main():
    if platform.system() != 'Linux' or platform.machine().lower() not in ('x86_64', 'amd64'):
        raise RuntimeError('Bu boshlash fayli 64-bit Intel/AMD Linux uchun tayyorlangan.')
    model = ROOT / 'models' / 'Qwen3-4B-Q4_K_M.gguf'
    engine = ROOT / 'bin' / 'llamafile.exe'
    if not model.is_file() or model.stat().st_size != MODEL_SIZE:
        raise RuntimeError('Model fayli toliq emas. ZIPni qayta, toliq oching.')
    with model.open('rb') as stream:
        if stream.read(4) != b'GGUF':
            raise RuntimeError('Model formati buzilgan. TEKSHIRISH_KALI.sh ni ishga tushiring.')
    if not engine.is_file() or hashlib.sha256(engine.read_bytes()).hexdigest() != ENGINE_HASH:
        raise RuntimeError('AI dastur fayli buzilgan. ZIPni qayta oching.')
    port = choose_port()
    url = f'http://127.0.0.1:{port}/'
    (ROOT / 'logs').mkdir(exist_ok=True)
    logfile = ROOT / 'logs' / 'linux-server.log'
    threads = str(max(1, min(4, os.cpu_count() or 2)))
    args = ['--server', '-m', str(model), '--host', '127.0.0.1', '--port', str(port),
            '--path', str(ROOT / 'web'), '--alias', 'Dava-USB-AI', '--ctx-size', '4096',
            '--parallel', '1', '--threads', threads, '--batch-size', '256',
            '--ubatch-size', '128', '--n-predict', '1024', '--gpu', 'disable',
            '--n-gpu-layers', '0', '--offline', '--no-slots', '--no-webui-mcp-proxy',
            '--cors-origins', url.rstrip('/'), '--nologo']
    env = dict(os.environ)
    env['LLAMA_ARG_CHAT_TEMPLATE_KWARGS'] = '{"enable_thinking":false}'
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    print('\nDAVA USB AI | Qwen3 4B | Oflayn\n', flush=True)
    print('Model ochilyapti. Fleshka tezligiga qarab bir necha daqiqa ketishi mumkin.', flush=True)
    print('Tayyor bolganda chat brauzerda ochiladi. Toxtatish: Ctrl+C.\n', flush=True)
    process = None
    # Running a temporary local copy also supports USB mounts with the noexec option.
    with tempfile.TemporaryDirectory(prefix='dava-usb-ai-') as temp:
        runtime = Path(temp) / 'llamafile.exe'
        shutil.copyfile(engine, runtime)
        runtime.chmod(0o700)
        env['TMPDIR'] = temp
        try:
            with logfile.open('w', encoding='utf-8') as log:
                process = subprocess.Popen(['bash', str(runtime), *args], cwd=ROOT, env=env,
                                           stdin=subprocess.DEVNULL, stdout=log, stderr=log)
                ready = False
                start = time.monotonic()
                last_notice = start
                while time.monotonic() - start < 600:
                    if process.poll() is not None:
                        break
                    try:
                        with opener.open(url + 'health', timeout=1) as response:
                            ready = response.status == 200 and json.load(response).get('status') == 'ok'
                    except (OSError, ValueError, urllib.error.URLError):
                        pass
                    if ready:
                        break
                    if time.monotonic() - last_notice >= 15:
                        print('Hali yuklanyapti...', flush=True)
                        last_notice = time.monotonic()
                    time.sleep(0.5)
                if not ready:
                    tail = '\n'.join(logfile.read_text(errors='replace').splitlines()[-15:])
                    raise RuntimeError('AI ishga tushmadi. logs/linux-server.log faylini tekshiring.\n' + tail)
                print('TAYYOR: ' + url, flush=True)
                if os.environ.get('DAVA_NO_BROWSER') != '1':
                    try:
                        webbrowser.open(url)
                    except Exception:
                        pass
                print('Bu terminalni ochiq qoldiring. Toxtatish: Ctrl+C.\n', flush=True)
                return process.wait()
        except KeyboardInterrupt:
            print('\nAI toxtatilyapti...', flush=True)
            return 0
        finally:
            if process is not None and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (RuntimeError, OSError, ValueError) as error:
        print('\nXATO: ' + str(error), file=sys.stderr)
        sys.exit(1)
