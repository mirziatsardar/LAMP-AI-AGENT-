# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all

# 打印一下当前的 Python 路径，确保库安装到了正确的地方
print(f"DEBUG: Current Python executable: {sys.executable}")

block_cipher = None

# 1. 收集依赖
sounddevice_data, sounddevice_binaries, sounddevice_hidden = collect_all('sounddevice')
numpy_data, numpy_binaries, numpy_hidden = collect_all('numpy')
pythonosc_data, pythonosc_binaries, pythonosc_hidden = collect_all('pythonosc')

# 监控点：看看收集到了多少二进制文件
print(f"DEBUG: NumPy binaries count: {len(numpy_binaries)}")
print(f"DEBUG: SoundDevice binaries count: {len(sounddevice_binaries)}")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=sounddevice_binaries + numpy_binaries + pythonosc_binaries,
    datas=[
        ('config', 'config'),
        *sounddevice_data,
        *numpy_data,
        *pythonosc_data,
    ],
    hiddenimports=[
        'sounddevice', 
        'numpy', 
        'pythonosc', 
        'icmplib',
        'numpy.core._multiarray_umath' # 强制拉入 NumPy 核心
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# 再次监控：Analysis 最终抓到了多少东西
print(f"DEBUG: Final binaries in Analysis: {len(a.binaries)}")

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Lighting_Control_System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
