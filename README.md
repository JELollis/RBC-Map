# RBC Community Map — 0.12.1

> **Archived snapshot.** This branch preserves version 0.12.1 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.12.1: Compass overlay, move countdowns & character switching

This entry was missing from earlier copies of the changelog; it was reconstructed
from the archived `main_0.12.1.py`.

#### ✅ Key changes in v0.12.1
- 🧭 **Compass overlay**: a new `CompassOverlay` dialog lists routes to
  destinations with direction arrows and AP-cost labels.
- ⏳ **Move countdowns**: countdown labels for the next guild and shop moves.
- 👥 **Character switching**: switching characters now sets the login cookie
  and logs in directly (replacing the separate logout step), and restores each
  character's last destination.
- 🎨 **Theming**: themes can be applied to individual widgets and dialogs.
- ✅ **Dialog validation**: dialogs validate input before accepting.

See the [Changelog](Changelog.md#version-0121--compass-overlay-move-countdowns--character-switching) for details and earlier history.

## Requirements

- Python 3
- UI toolkit: PySide6 (Qt 6)

Third-party packages (also listed in [`requirements.txt`](requirements.txt)):
- PySide6
- beautifulsoup4
- requests

## Run

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**macOS / Linux:**
```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

```bash
python main_0.12.1.py
```


## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
