# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# 暴力收集所有库
soundcard_data, soundcard_binaries, soundcard_hidden = collect_all('soundcard')
numpy_data, numpy_binaries, numpy_hidden = collect_all('numpy')
pythonosc_data, pythonosc_binaries, pythonosc_hidden = collect_all('pythonosc')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=soundcard_binaries + numpy_binaries + pythonosc_binaries,
    datas=[
        ('config', 'config'),
        ('settings.py', '.'),
        ('fixtures.py', '.'),
        ('protocols.py', '.'),
        ('console_manager.py', '.'),
        ('fixture_manager.py', '.'),
        ('audio_processor.py', '.'),
        *soundcard_data,
        *numpy_data,
        *pythonosc_data,
        ('soundcard_pkg', 'soundcard'),     # ←←← 关键！强制把手动复制的包整个塞进去
    ],
    hiddenimports=[
        'soundcard', 'soundcard.cffi', 'soundcard.soundcard',
        'soundcard._soundcard', 'soundcard.soundcard_cffi',
        'numpy', 'pythonosc', 'pythonosc.udp_client',
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
    [],
    exclude_binaries=True,
    name='Lighting_Control_System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Lighting_Control_System',
)
