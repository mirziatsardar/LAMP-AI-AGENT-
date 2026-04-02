# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

sounddevice_data, sounddevice_binaries, sounddevice_hidden = collect_all('sounddevice')
numpy_data, numpy_binaries, numpy_hidden = collect_all('numpy')
pythonosc_data, pythonosc_binaries, pythonosc_hidden = collect_all('pythonosc')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=sounddevice_binaries + numpy_binaries + pythonosc_binaries,
    datas=[
        ('config', 'config'),
        ('settings.py', '.'),
        ('fixtures.py', '.'),
        ('protocols.py', '.'),
        ('console_manager.py', '.'),
        ('fixture_manager.py', '.'),
        ('audio_processor.py', '.'),
        *sounddevice_data,
        *numpy_data,
        *pythonosc_data,
    ],
    hiddenimports=[
        'sounddevice',
        'sounddevice._sounddevice',
        'numpy',
        'pythonosc',
        'pythonosc.udp_client',
        'icmplib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,    # 把 binaries 塞进 exe
    a.zipfiles,    # 把 zipfiles 塞进 exe
    a.datas,       # 把 datas 塞进 exe
    [],
    name='Lighting_Control_System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
