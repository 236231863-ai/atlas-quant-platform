# -*- mode: python ; coding: utf-8 -*-
# Atlas Quant Platform - Desktop Executable Spec
# 打包 Atlas.exe（PySide6 桌面客户端，含内置数据）

a = Analysis(
    ['..\\desktop\\main.py'],
    pathex=['..\\desktop'],
    binaries=[],
    datas=[
        ('..\\data\\raw\\dlt_2024_sample.csv', 'data\\raw'),
        ('..\\branding\\logo.ico', 'branding'),
    ],
    hiddenimports=[
        'matplotlib.backends.backend_qtagg',
        'matplotlib.backends.backend_qt5agg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Atlas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='..\\branding\\logo.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
