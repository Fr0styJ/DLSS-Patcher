# DLSS Patcher

A standalone Windows utility for updating NVIDIA DLSS, Ray Reconstruction, and Frame Generation DLLs in any game — without waiting for the game developer to ship an update.

Pulls the latest DLL versions directly from [TechPowerUp](https://www.techpowerup.com/download/nvidia-dlss-dll/) and injects them into your game directories with a single click.

---

## Features

- 🔍 **Auto Game Scanner** — Scans all local drives for games containing DLSS DLLs across Steam, Epic Games, GOG, and Xbox Game Pass libraries
- ⬇️ **Latest Version Fetching** — Scrapes TechPowerUp in real time to populate a list of the newest available DLL versions for:
  - DLSS (`nvngx_dlss.dll`)
  - Ray Reconstruction (`nvngx_dlssd.dll`)
  - Frame Generation (`nvngx_dlssg.dll`)
- 💉 **Safe DLL Injection** — Backs up the existing DLL (as `.old`) before injecting the new version
- 🛡️ **On-Screen Indicator Toggle** — Enables or disables the DLSS performance overlay via a registry key (`HKLM\SOFTWARE\NVIDIA Corporation\Global\NGXCore`)
- ⏱️ **Auto-Revert Scheduler** — Optionally schedules a Windows Task Scheduler job to automatically turn the overlay off after 4 hours
- 🔒 **UAC Elevation** — Automatically requests administrator privileges at launch (required for registry writes and DLL injection)

---

## Screenshots

> Launch the app, scan your drives, pick a game, choose which DLSS components to update, and click **Download & Inject**.

---

## Requirements

### Running from Source

- Python 3.10+
- Windows 10 or 11
- Administrator privileges

Install dependencies:

```bash
pip install -r requirements.txt
```

**`requirements.txt`**
```
customtkinter==5.2.2
requests==2.31.0
beautifulsoup4==4.12.3
```

Run:
```bash
python main.py
```

### Running the Standalone EXE

No Python installation needed. Just run:

```
DLSS Patcher.exe
```

Windows will prompt for administrator access via UAC. The app requires admin rights to write to the registry and replace DLL files inside protected game directories.

---

## Building the EXE

PyInstaller is used to produce a single-file Windows executable.

```bash
pip install pyinstaller
pyinstaller --clean dlss_patcher.spec
```

Output: `dist\DLSS Patcher.exe`

The spec file bundles all modules, `customtkinter` theme assets, and the UAC manifest (`dlss_patcher.manifest`) which forces elevation at launch.

---

## How It Works

```
main.py          Entry point — UAC check, re-launches elevated if needed
ui.py            CustomTkinter GUI — all user interaction
scanner.py       Walks drives to find game directories containing DLSS DLLs
scraper.py       Fetches version list and downloads ZIP archives from TechPowerUp
updater.py       Extracts the DLL from the ZIP, backs up the old one, writes the new one
registry_mgr.py  Registry reads/writes for the DLSS indicator; PowerShell task scheduling
```

### DLL Injection Flow

1. User selects a game and one or more DLSS components to update
2. The app fetches the download link for each selected version
3. The ZIP is downloaded to a temp directory with live progress
4. The existing DLL is renamed to `.old` as a backup
5. The new DLL is extracted directly into the game's executable directory
6. The temp ZIP is deleted

### Backup & Recovery

Before any injection, the original DLL is renamed:
```
nvngx_dlss.dll  →  nvngx_dlss.old
```
To roll back, simply rename the `.old` file back to `.dll`.

---

## Supported Game Stores

The scanner checks the following paths on every detected drive:

| Store | Path Pattern |
|---|---|
| Steam | `Steam\steamapps\common` |
| Steam (alt) | `SteamLibrary\steamapps\common` |
| Steam (x86) | `Program Files (x86)\Steam\steamapps\common` |
| Epic Games | `Epic Games` |
| GOG Galaxy | `GOG Galaxy\Games` |
| Xbox / Game Pass | `XboxGames` |

---

## Registry Key Reference

| Key | Path |
|---|---|
| Hive | `HKEY_LOCAL_MACHINE` |
| Path | `SOFTWARE\NVIDIA Corporation\Global\NGXCore` |
| Value | `ShowDlssIndicator` |
| Enabled | `1024` (DWORD) |
| Disabled | `0` (DWORD) |

---

## Disclaimer

This tool modifies game files and Windows registry values. Always ensure your game is **closed** before running an injection. The developer is not responsible for any game instability, anti-cheat bans, or system issues resulting from use of this tool. Use at your own risk.

DLSS and related trademarks are property of NVIDIA Corporation. This project is not affiliated with or endorsed by NVIDIA.
