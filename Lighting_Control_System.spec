# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    ['main.py'],                    # 主入口文件
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),                    # 打包整个 config 文件夹
        ('settings.py', '.'),
        ('fixtures.py', '.'),
        ('protocols.py', '.'),
        ('console_manager.py', '.'),
        ('fixture_manager.py', '.'),
        ('audio_processor.py', '.'),
    ],
    hiddenimports=[
        'soundcard',
        'soundcard.cffi',
        'numpy',
        'pythonosc',
        'icmplib',
        'pythonosc.udp_client',
        'pythonosc.dispatcher',
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
    console=True,                    # 命令行工具必须 True（保留打印信息）
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
    name='Lighting_Control_System',   # 最终文件夹名字
)
