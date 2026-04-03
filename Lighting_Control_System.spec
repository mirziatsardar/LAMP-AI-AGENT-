# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# 自动收集复杂库的所有依赖和数据点
sounddevice_data, sounddevice_binaries, sounddevice_hidden = collect_all('sounddevice')
numpy_data, numpy_binaries, numpy_hidden = collect_all('numpy')
pythonosc_data, pythonosc_binaries, pythonosc_hidden = collect_all('pythonosc')
# ... 前面的 collect_all 部分保持不变 ...

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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    cipher=block_cipher,
)

# ... 后面的 PYZ 和 EXE 部分保持不变 ...

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,       # <--- 核心修改：将二进制库塞进 EXE
    a.zipfiles,      # <--- 核心修改：将压缩包塞进 EXE
    a.datas,         # <--- 核心修改：将数据文件塞进 EXE
    [],
    name='Lighting_Control_System', # 生成的文件名
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,        # 使用 UPX 压缩体积（如果环境中没有 UPX 会自动跳过）
    upx_exclude=[],
    runtime_tmpdir=None, # 运行时的临时解压目录
    console=True,    # 保持黑窗口开启，方便看报错和菜单
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
