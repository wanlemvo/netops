"""Build a clean, traceable Windows distribution without reading user data."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
import zipfile


def run(*args):
    subprocess.run(list(args), check=True)


def main():
    root = Path(__file__).resolve().parents[1]
    if Path.cwd() != root:
        raise SystemExit('Run this script from the repository root.')
    if sys.platform != 'win32':
        raise SystemExit('The Windows distribution must be built on Windows.')
    if sys.version_info[:2] != (3, 12):
        raise SystemExit('Use Python 3.12 with requirements/windows-build.txt.')
    dirty = subprocess.check_output(['git', 'status', '--porcelain'], text=True)
    if dirty.strip():
        raise SystemExit('Commit reviewed source changes before building a release.')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    version = '0.2.0'
    output = root / 'dist' / f'netops-{version}-{commit[:8]}'
    output.mkdir(parents=True, exist_ok=False)
    portable = output / 'netops'
    work = root / 'build' / commit[:8]
    for surface in ['gui', 'cli']:
        name = f'netops-{surface}'
        destination = portable / name
        destination.mkdir(parents=True)
        args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--onefile',
                '--windowed' if surface == 'gui' else '--console', '--name', name,
                '--distpath', str(destination), '--workpath', str(work / name), '--specpath', str(work),
                '--add-data', f'{root / "src/netops/gui/static"};netops/gui/static',
                '--collect-all', 'webview', str(root / f'src/netops/portable_{surface}.py')]
        run(*args)
    (portable / '.netops-portable').write_text('NetOps portable root v1\n', encoding='utf-8')
    (portable / 'data/assets/profile_photos').mkdir(parents=True)
    (portable / 'README.txt').write_text(
        'NetOps 0.2.0\nOpen netops-gui/netops-gui.exe. Windows 10/11 and Microsoft Edge WebView2 are required.\n'
        'Records are stored in data/netops.sqlite3, created on first launch. Move this whole folder together.\n'
        'This release contains no database. To use existing data, close all NetOps windows, back up the entire old data folder,\n'
        'and copy it into a separate extracted release. Never overwrite your only copy.\n'
        'Local SQLite storage is not encrypted and does not sync. CLI/TUI is a secondary interface.\n', encoding='utf-8')
    files = {p.relative_to(portable).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in portable.rglob('*') if p.is_file()}
    manifest = {'version': version, 'source_commit': commit, 'source_clean': True,
                'python': platform.python_version(), 'platform': platform.platform(),
                'build': {'format': 'PyInstaller onefile', 'gui': 'pywebview EdgeChromium', 'personal_data': False},
                'dependencies': dict(sorted((d.metadata['Name'], d.version) for d in importlib.metadata.distributions())),
                'sha256': files}
    (portable / 'build-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    archive = output.parent / (output.name + '.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in portable.rglob('*'):
            if p.is_file():
                if p.suffix.lower() in {'.db', '.sqlite', '.sqlite3'}:
                    raise RuntimeError('Unexpected database in release staging.')
                z.write(p, p.relative_to(output))
    archive.with_suffix('.sha256').write_text(hashlib.sha256(archive.read_bytes()).hexdigest() + '  ' + archive.name + '\n', encoding='utf-8')
    print(f'Release: {archive}')


if __name__ == '__main__':
    main()
