# -*- mode: python ; coding: utf-8 -*-
# Atlas Quant Platform - Worker Executable Spec
# 打包 Atlas_Worker.exe（后台数据服务）

a = Analysis(
    ['..\\tools\\atlas_worker.py'],
    pathex=['..\\tools', '..\\desktop'],
    binaries=[],
    datas=[
        ('..\\data\\raw\\dlt_2024_sample.csv', 'data\\raw'),
    ],
    hiddenimports=[],
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
    name='Atlas_Worker',
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
