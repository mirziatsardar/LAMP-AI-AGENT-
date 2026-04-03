# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# 1. 收集依赖（这部分保持不变）
sounddevice_data, sounddevice_binaries, sounddevice_hidden = collect_all('sounddevice')
numpy_data, numpy_binaries, numpy_hidden = collect_all('numpy')
pythonosc_data, pythonosc_binaries, pythonosc_hidden = collect_all('pythonosc')

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
    hiddenimports=['sounddevice', 'numpy', 'pythonosc', 'icmplib'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 2. 核心修改在这里！把所有东西塞进 EXE
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,    # <--- 必须有这个，把 DLL 塞进去
    a.zipfiles,    # <--- 必须有这个，把压缩库塞进去
    a.datas,       # <--- 必须有这个，把数据塞进去
    [],
    name='Lighting_Control_System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,      # 如果 GitHub 环境有 UPX 会自动压缩
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 3. 必须删掉（或注释掉）下面的 COLLECT 部分！！
# 如果留着 COLLECT，PyInstaller 可能会优先生成文件夹模式
# coll = COLLECT( ... )
