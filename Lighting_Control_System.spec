# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# 自动收集复杂库的所有依赖和数据点
sounddevice_data, sounddevice_binaries, sounddevice_hidden = collect_all('sounddevice')
numpy_data, numpy_binaries, numpy_hidden = collect_all('numpy')
pythonosc_data, pythonosc_binaries, pythonosc_hidden = collect_all('pythonosc')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=sounddevice_binaries + numpy_binaries + pythonosc_binaries,
    datas=[
        ('config', 'config'), # 只保留文件夹和非代码资源
        *sounddevice_data,
        *numpy_data,
        *pythonosc_data,
    ],
    hiddenimports=[
        'sounddevice',
        'numpy',
        'pythonosc',
        'icmplib',
        'settings',         # 如果报错找不到，手动加在这里
        'fixtures',
        'protocols',
        'console_manager',
        'fixture_manager',
        'audio_processor',
    ],
    # ... 其他保持不变
)
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

# 注意：单文件模式下不需要使用 COLLECT 模块，所以下面这行删掉或注释掉
# coll = COLLECT(...)
