# UA Alert

A Python 3.12+ desktop monitoring dashboard for Alerts.in.ua. Status is **UNKNOWN** until the first successful API response, and becomes UNKNOWN again when the feed is unavailable or stale. Threat labels are shown only when the API explicitly supplies a recognized threat type; other active alerts are reported as `AIR RAID ALERT — TYPE UNKNOWN`.

## Install and run

Linux (Ubuntu): install Python 3.12+, `python3-venv`, and an audio backend supported by Qt Multimedia (`pipewire` or PulseAudio). On minimal systems install `libxcb-cursor0` and `libegl1` for Qt.

```bash
cd /path/to/files-pasted-by-the-user-project
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ua_alert.main
```

Windows PowerShell:

```powershell
cd /path/to/files-pasted-by-the-user-project
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ua_alert.main
```

Configure an Alerts.in.ua API token in **Settings**. Without a valid token/connection, the dashboard remains UNKNOWN. The token is persisted through the operating system keyring; settings and event data are stored in `~/.ua-alert/history.sqlite3`.

Closing the window hides it in the tray by default. Use the tray menu's **Exit** command to stop monitoring. Use History to search and export CSV. Settings include polling interval, sound toggles, volume, and test tones.

## Packaging

The app uses Qt's cross-platform widgets and multimedia. To package on each target OS, install PyInstaller in the same environment and build from that OS:

```bash
python -m pip install pyinstaller
pyinstaller --noconfirm --windowed --name UA-Alert --paths . --add-data "ua_alert/assets:ua_alert/assets" run_ua_alert.py
```

For Windows, use `;` instead of `:` in `--add-data`. Linux desktop entry template: `ua_alert/packaging/ua-alert.desktop`.

Run the development simulation with `python -m ua_alert.main --simulate`. The title labels it as simulation, it never contacts the live API, and it cycles through safe, drone, missile, unclassified alert, and connection failure states.

## Data behavior

The client calls the documented `GET https://api.alerts.in.ua/v1/alerts/active.json` endpoint and sends the app token as a Bearer header. The app does not query history endpoints. Feed values are validated and unknown threat kinds remain unclassified. The Map page draws Ukraine's oblast boundaries (internationally recognized borders, including Crimea) from `ua_alert/assets/ukraine_regions.json`, a simplified extract of OpenStreetMap data (© OpenStreetMap contributors, ODbL). Hover an oblast to see its status, click it to open it on the dashboard. Sevastopol is outlined for completeness but is not a monitored region.

## Limitations

This initial desktop build includes live monitoring, transition history, configurable sounds, tray notifications, dashboard, region selection, and CSV export. It does not currently implement language/theme switching, favorites persistence, date/category filters, or OS startup registration. Desktop notifications depend on the host desktop environment. The application is supplementary and is not an emergency warning system.
