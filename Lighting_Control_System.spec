# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import numpy
import sounddevice
import pythonosc

# 打印调试信息
print(f"DEBUG: Python Path: {sys.executable}")
print(f"DEBUG: NumPy Path: {os.path.dirname(numpy.__file__)}")

block_cipher = None

# 直接获取库的安装目录
numpy_dir = os.path.dirname(numpy.__file__)
sounddevice_dir = os.path.dirname(sounddevice.__file__)
pythonosc_dir = os.path.dirname(pythonosc.__file__)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[], # 后面通过 datas 强制带入
    datas=[
        ('config', 'config'),
        # 暴力法：直接把整个库文件夹塞进去，确保 DLL 不丢失
        (numpy_dir, 'numpy'),
        (sounddevice_dir, 'sounddevice'),
        (pythonosc_dir, 'pythonosc'),
    ],
    hiddenimports=[
        'sounddevice',
        'numpy',
        'pythonosc',
        'icmplib',
        'numpy.core._multiarray_umath',
        'numpy.libs',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

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
