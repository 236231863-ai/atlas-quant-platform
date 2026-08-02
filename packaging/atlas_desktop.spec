# -*- mode: python ; coding: utf-8 -*-
# Atlas Quant Platform - Desktop Executable Spec
# 打包 Atlas.exe（PySide6 桌面客户端，含真实历史数据 + engine v2 模块）

a = Analysis(
    ['..\\desktop\\main.py'],
    # 加入项目根，使 desktop 能 import engine（data_center_v2/evaluation_v2/export）
    pathex=['..\\desktop', '..'],
    binaries=[],
    datas=[
        # 真实历史数据（520 期大乐透）+ 样例回退
        ('..\\data\\raw\\dlt_history.csv', 'data\\raw'),
        ('..\\data\\raw\\dlt_2024_sample.csv', 'data\\raw'),
        ('..\\data\\raw\\ssq_2024_sample.csv', 'data\\raw'),
        ('..\\branding\\logo.ico', 'branding'),
    ],
    hiddenimports=[
        'matplotlib.backends.backend_qtagg',
        'matplotlib.backends.backend_qt5agg',
        'fpdf',
        'engine.data_center_v2',
        'engine.data_center_v2.sources',
        'engine.data_center_v2.quality',
        'engine.data_center_v2.models',
        'engine.evaluation_v2',
        'engine.evaluation_v2.split',
        'engine.evaluation_v2.baseline',
        'engine.evaluation_v2.metrics',
        'engine.evaluation_v2.disclaimer',
        'engine.export',
        'engine.export.markdown',
        'engine.export.csv',
        'engine.export.png',
        'engine.export.pdf',
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
