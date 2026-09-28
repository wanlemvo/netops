"""Native Windows launch/persistence smoke check using copied binaries and fictional data."""
import argparse
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time
import urllib.request

from netops.demo import seed_demo


def request(url, payload=None):
    req = urllib.request.Request(url, data=None if payload is None else json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=3) as response:
        return json.load(response)


def native_window(executable):
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    found = []
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def visit(hwnd, _):
        title = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, title, 256)
        if title.value != 'NetworkOps' or not user32.IsWindowVisible(hwnd): return True
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        handle = kernel32.OpenProcess(0x1000, False, pid.value)
        if handle:
            path = ctypes.create_unicode_buffer(32768)
            size = wintypes.DWORD(len(path))
            try:
                if kernel32.QueryFullProcessImageNameW(handle, 0, path, ctypes.byref(size)) and Path(path.value).resolve() == executable.resolve():
                    found.append(int(hwnd))
            finally:
                kernel32.CloseHandle(handle)
        return True
    user32.EnumWindows(callback_type(visit), 0)
    return found[0] if found else None


def launch_check(root, expected_id=None):
    exe = root / 'netops-gui/netops-gui.exe'
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    env = {k: v for k, v in os.environ.items() if k not in {'NETOPS_DB', 'NETOPS_HOME'}}
    log = (root.parent / f'{root.name}-launch.log').open('w', encoding='utf-8')
    process = subprocess.Popen([str(exe), 'gui', '--port', str(port)], env=env, stdout=log, stderr=log)
    hwnd = None
    url = f'http://127.0.0.1:{port}/'
    try:
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if process.poll() is not None: raise RuntimeError(f'Desktop exited with {process.returncode}; inspect launch log.')
            try:
                settings = request(url + 'api/settings')
                hwnd = native_window(exe)
                if hwnd: break
            except (OSError, ValueError):
                pass
            time.sleep(0.25)
        else: raise RuntimeError('No visible native NetworkOps window and API within 60 seconds.')
        assert Path(settings['database_path']).resolve() == (root / 'data/netops.sqlite3').resolve()
        capture = root.parent / (root.name + '-window.png')
        subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                        str(Path(__file__).with_name('capture_window.ps1')), '-WindowHandle', str(hwnd),
                        '-Output', str(capture)], check=True, timeout=55)
        if expected_id is None:
            result = request(url + 'api/people', {'name': 'Native Window Fiction', 'dossier': 'Saved through the packaged application.'})
            expected_id = result['person_id']
        record = request(url + f'api/people/{expected_id}')
        assert record['dossier'] == 'Saved through the packaged application.'
        result = {'visible_native_window': True, 'rendered_controls_verified': True, 'database_path': settings['database_path'],
                  'persistent_record_verified': True, 'interaction_surface': 'Native launch plus HTTP API; GUI clicks verified separately in browser tests.'}
        print(json.dumps(result), flush=True)
        return expected_id, result
    finally:
        if hwnd:
            ctypes.windll.user32.PostMessageW(wintypes.HWND(hwnd), 0x0010, 0, 0)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            # Only this test's process tree, never another NetOps installation.
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
        log.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    initial = output / 'Original portable folder'
    executable = initial / 'netops-gui/netops-gui.exe'
    executable.parent.mkdir(parents=True)
    shutil.copy2(args.exe, executable)
    (initial / '.netops-portable').write_text('NetOps portable root v1\n')
    seed_demo(initial / 'data/netops.sqlite3')
    pid, first = launch_check(initial)
    renamed = output / 'Renamed portable folder with spaces'
    assert initial.resolve().is_relative_to(output) and renamed.resolve().is_relative_to(output)
    shutil.move(str(initial), renamed)
    _, second = launch_check(renamed, pid)
    (output / 'results.json').write_text(json.dumps([first, second], indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
