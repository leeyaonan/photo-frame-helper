# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['photo_frame_helper.py'],
    pathex=[],
    binaries=[],
    datas=[('application.yml', '.'), ('template/impl', 'template/impl'), ('photo_frame_helper_logo.png', '.'), ('photo_frame_helper_logo_filleted.png', '.'), ('logo', 'logo')],
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
    [],
    exclude_binaries=True,
    name='photo_frame_helper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['photo_frame_helper_logo_filleted.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='photo_frame_helper',
)
app = BUNDLE(
    coll,
    name='photo_frame_helper.app',
    icon='photo_frame_helper_logo_filleted.png',
    bundle_identifier=None,
)
