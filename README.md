# RBC Community Map Application

**Current development version: 1.0.4** · **Latest stable release: 1.0.0** ([release branch](https://github.com/JELollis/RBC-Map/tree/version/1.0.0)) · [Repository](https://github.com/JELollis/RBC-Map) · [Changelog](Changelog.md)

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in [RavenBlack City](https://quiz.ravenblack.net/blood.pl). It combines an interactive minimap, character management, community-maintained location information, and in-game planning tools.

![Main application](Screenshots/Main%20Application.png)

## Features

### Interactive minimap
- Follow the character's current position using the game's right-hand frame.
- Show routes to the nearest **transit station** (red), **bank** (blue), and **pub** (orange).
- Choose a **3×3** (default), **5×5**, **7×7**, or **9×9** view.
- Recenter by clicking a map cell or choosing a location from the dropdowns and selecting **Go**.
- Use **Set Destination** to mark a destination and display its route in green.
- Customize the minimap theme; fallback rendering helps maintain usability in zoomed views.
- Refresh destination choices when the destination dialog opens.

![Minimap theme](Screenshots/Minimap%20Theme.png)

### Community location data
- Synchronize guild and shop movements and community-supplied buildings, points of interest, arenas, alchemy locations, lairs, and halls.
- Optionally enable **Contribute Discovered Locations** to report newly discovered non-moving locations anonymously. You can turn this setting off at any time.
- Continue using previously synchronized local location data when the update service is unavailable.

### Characters and controls
- Store character login details locally and switch between characters.
- Resize the navigation panel using its divider. The panel has a minimum width to keep the character buttons visible.
- Sign in automatically with a saved password when no session cookie is available.
- Restore destinations, themes, and other preferences between sessions.
- Choose **WASD** or **arrow keys** for movement; movement shortcuts are suppressed while typing into input fields.

![New user dialog](Screenshots/New%20User%20Dialog.png)

### Planning and reference tools

| Tool | What it does |
| --- | --- |
| **Shopping list** | Build item lists, calculate total cost, compare against available coins, and view the countdown to the next shop update. |
| **Damage calculator** | Estimate damage required to bring a target to staking level and compare item combinations. |
| **Power information** | Review game powers, descriptions, costs, effects, and the countdown to the next guild move. |
| **Database viewer** | Inspect and manage underlying data tables (intended for advanced users). |

![Shopping list tool](Screenshots/Shopping%20List%20Tool.png)
![Damage calculator](Screenshots/Damage%20Calculator.png)
![Power information](Screenshots/Power%20Information.png)
![Database viewer](Screenshots/Database%20Viewer.png)

### Appearance customization
- Customize interface and minimap themes.
- Use the CSS customization tool for styling, including fonts, box shadows, and background images, with a live preview.

![CSS customization tool](Screenshots/CSS%20Customization%20Dialog.png)
![Interface theme](Screenshots/Interface%20Theme.png)

## Getting started

### Requirements
The Python runtime dependencies listed in [`requirements.txt`](requirements.txt) are:
- PySide6 (including the Qt WebEngine components used by the embedded browser)
- beautifulsoup4
- keyring
- requests

A working Python 3 installation and an environment capable of running a Qt desktop application are required.

### Install dependencies

From a checkout of this branch, create and activate a virtual environment, then install the declared dependencies:

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

### Run

The instructions in this section run the application from the Python source.
Starting with the 1.0.4 release, each release will publish a packaged build
with an installer on the [releases](https://github.com/JELollis/RBC-Map/releases)
page; installers bundle everything the app needs and require no Python setup.

```bash
python main_1.0.4.py
```

When running the script directly, keep the folders it loads at runtime —
`images/` (interface and minimap artwork), `css/` (optional sample themes you
can import through the CSS dialog), `docs/help/`
(help files), and any existing `sessions/` folder from a previous version —
in the same directory as `main_1.0.4.py`. The per-user data folder
(`%LOCALAPPDATA%\RBC-Map` on Windows, `~/.local/share/RBC-Map` on macOS and
Linux) is created automatically and does not need to sit next to the script.

For a packaged build, check the repository's [releases](https://github.com/JELollis/RBC-Map/releases) for available downloads and release-specific instructions.

Packagers must include the monolithic `main_1.0.4.py` application and the
platform-appropriate `keyring` backend modules. For frozen builds, verify that
the selected backend (for example, Windows Credential Locker) is included and
available at runtime. The release workflow builds Windows with Nuitka and NSIS,
and Linux/macOS artifacts with platform-appropriate onedir packaging. Every
frozen artifact runs a self-check for its version, resource directories, and
keyring backend before it is uploaded.

### Run the auto-login regression checks

Install Node.js and ensure the `node` command is on your PATH before running
`python tools/check_auto_login.py`. The checker uses Node.js to test the generated
login-form JavaScript. Node.js is only needed for this test.

## Code signing policy

Windows release artifacts may use the SignPath Foundation open-source signing
program. **Free code signing provided by SignPath.io, certificate by SignPath
Foundation.** Until acceptance is confirmed, Windows and macOS artifacts are
unsigned and their release notes document the SmartScreen or Gatekeeper steps.

- Committers and reviewers: authorized RBC-Map GitHub collaborators, with
  changes reviewed through pull requests.
- Approver: Jonathan Lollis (`JELollis`), the repository owner, approves each
  signing request and release artifact.
- Privacy: apart from loading the RavenBlack game website and downloading
  public map data from the community update service, the program does not
  transfer information to other networked systems unless the user enables
  **Contribute Discovered Locations**. That feature is opt-in and disclosed
  below.

## Data and privacy

Character information, session metadata, and application preferences are stored in a local SQLite database. Passwords and session-cookie values are stored through the operating system credential store via `keyring` when that store is available; after a successful migration, the database keeps only non-secret metadata. If the credential store is unavailable or locked, migration fails closed and deliberately leaves existing plaintext credentials in SQLite so they are not lost; resolve the credential-store problem and restart the app before treating the data as protected. On first launch, data from an older version kept next to the script (`sessions/` or `testing/sessions/`) is copied into the per-user data folder automatically; the originals are left in place. The app keeps its logs, sessions, and database in a per-user data folder (`%LOCALAPPDATA%\RBC-Map` on Windows, `$XDG_DATA_HOME/RBC-Map`, by default `~/.local/share/RBC-Map`, on macOS and Linux), outside the repository. Don't commit or share that folder.

On Linux, the keyring needs an available, unlocked Secret Service collection. If it does not respond, the app stops waiting and retries the backend only after a restart. If you cannot use a keyring, launch with `RBC_MAP_CREDENTIAL_STORAGE=sqlite python main_1.0.4.py` to use a separate `RBC-Map-SQLite` profile. Add your characters again in that profile. Its SQLite database stores saved passwords and session cookies in plaintext. Launch without the environment variable to return to the original keyring-backed profile. See the [Linux installation guide](docs/help/Linux_Installation.html) for package requirements and workarounds.

After confirming your characters, settings, and sign-in work in the new data folder, consider deleting the old copies in `sessions/` or `testing/sessions/` next to the old installation and any `rbc_map_data.db.pre-migration` backup in the new sessions folder. These backups may contain plaintext passwords or session cookies. Keep them if you still need rollback, and protect any copies you retain.

The documented community reporting feature (**Contribute Discovered Locations**) is **opt-in** and is intended to send only newly discovered non-moving locations, not login credentials. Review the application's settings before enabling reporting, and protect your local database and device as you would other stored credentials.

## Versions and branches

> **Looking for a stable build?** Use [`release`](https://github.com/JELollis/RBC-Map/tree/release) or the latest [release](https://github.com/JELollis/RBC-Map/releases). `dev` is the **beta** branch — it holds the newest work and may be less stable. `release` is the **stable** branch, and every numbered release is based on `release`.

| Branch | Contents |
| --- | --- |
| `dev` | **Beta.** Active development, currently on 1.0.4 (`main_1.0.4.py`); bug fixes and feature work merge here through pull requests. |
| `release` | **Stable.** Receives release candidates from `version/<number>` branches through pull requests; each merge is tagged `v<number>`. All releases are based on `release`. |
| [`version/1.0.0`](https://github.com/JELollis/RBC-Map/tree/version/1.0.0) | Release 1.0.0 (`main_1.0.0.py`). |
| `version/0.7.1` … `version/0.13.3.0` | Archived PySide6 versions. |
| `version/0.3.2` … `version/0.7.0` | Archived PyQt5 versions. |
| `version/0.1.0` … `version/0.3.1` | Archived tkinter prototypes. |
| `version/0.11.2-abandoned` | An alternative 0.11.2 draft that was not continued. |

Each `version/<number>` branch holds that version as `main_<number>.py`, with a
README and changelog for that version. Branches are snapshots for reference and
are not maintained.

The `version/1.0.0` branch is the fixed release snapshot, while `dev` moves on as new work lands in `main_1.0.4.py`. Version tags and [releases](https://github.com/JELollis/RBC-Map/releases) mark published builds from `release`.

## Repository layout

| Path | Purpose |
| --- | --- |
| `main_1.0.4.py` | The current development application, packaged as a single file. |
| `requirements.txt` | Runtime dependencies. |
| `images/`, `css/` | Icons, artwork, and stylesheets used by the app. |
| `docs/help/` | Help documentation (HTML, PDF, CHM, EPUB, DOCX). |
| `Screenshots/` | Screenshots used in this README. |

## Documentation, support, and contributions

- [Changelog](Changelog.md) — release history.
- [Help documentation](docs/help/RBC_Map_Help.html) — application help topics.
- [GitHub issues](https://github.com/JELollis/RBC-Map/issues) — report bugs and suggest improvements.
- [Community Discord](https://discord.gg/rKamEZvK6X) — community discussion (the server has a joining process).

Contributions and feedback are welcome. When reporting a problem, include the application version, operating system, steps to reproduce, and relevant error details; do not include passwords or session credentials.

## License

The project is documented as licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

## Contributors

**Development team**
- **Windows compatibility:** Jonathan Lollis (Nesmuth), Justin Solivan
- **macOS compatibility:** Joseph Lemois
- **Linux compatibility:** Josh "Blaskewitts" Corse, Fern Lovebond
- **Design and layout:** Shuvi, Blair Wilson (Ikunnaprinsess)

**Special thanks**
- [LIAM²](http://liam2.leprichaunproductions.com/home.php) by Cain "Leprechaun" McBride — inspiration for this project.
- [A View in the Dark](https://aviewinthedark.net/) by Cliff Burton — shop and guild data.
- [RavenBlack Wiki](https://ravenblack.city/) contributors.
- Anders — RBNav and ongoing support.
- [Vespertine's City Crawler](https://vampires.terrible.engineering/) — additional shop and guild data.
