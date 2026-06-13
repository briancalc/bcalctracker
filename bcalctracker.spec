# pyinstaller bcalctracker.spec

a = Analysis(
    ['starttracker.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('guiform', 'guiform'),      # Bundle the guiform package
        ('datamenu', 'datamenu'),    # Bundle the datamenu folder
        ('guiform/bcalcnotepadicon.png', 'guiform') # Explicitly bundle icon if it's there
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'PIL.ImageTk',
        'matplotlib.backends.backend_tkagg',
        'ttkbootstrap',
        'pandas'
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
    name='bcalctracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['guiform/bcalcnotepadicon.png'],
)
