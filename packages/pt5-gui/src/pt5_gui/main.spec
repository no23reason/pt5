# -*- mode: python ; coding: utf-8 -*-

import os

def get_locales_data():
    locales_data = []
    for locale in os.listdir(os.path.join('locales', 'bundles')):
        locales_data.append((
            os.path.join('locales', 'bundles', locale, 'LC_MESSAGES/*.mo'),
            os.path.join('locales', 'bundles', locale, 'LC_MESSAGES')
        ))
    return locales_data

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=get_locales_data(),
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
    name='main',
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
