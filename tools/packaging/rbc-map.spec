# PyInstaller onedir specification for the Linux and macOS release jobs.
# Windows uses Nuitka because the project has historically produced fewer
# Defender false positives with that toolchain.

from pathlib import Path

from PyInstaller.utils.hooks import copy_metadata


ROOT = Path(SPECPATH).parent.parent
datas = [
    (str(ROOT / "images"), "images"),
    (str(ROOT / "css"), "css"),
    (str(ROOT / "docs" / "help"), "docs/help"),
]
datas += copy_metadata("keyring")

hiddenimports = [
    "keyring.backends.chainer",
    "keyring.backends.SecretService",
    "keyring.backends.libsecret",
    "keyring.backends.kwallet",
    "keyring.backends.macOS",
    "secretstorage",
    "jeepney",
]

a = Analysis(
    [str(ROOT / "main_1.0.4.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    name="RBC Community Map",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    contents_directory=".",
    exclude_binaries=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="RBC-Map",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="RBC Community Map.app",
        icon=str(ROOT / "tools" / "packaging" / "macos" / "icon.icns"),
        bundle_identifier="com.jelollis.rbcommunitymap",
        info_plist={
            "CFBundleShortVersionString": "1.0.4",
            "CFBundleVersion": "1.0.4",
            "NSHighResolutionCapable": True,
        },
    )
