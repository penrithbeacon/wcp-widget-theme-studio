# WCP Widget: Theme Studio

A [Widget Context Protocol (WCP)](https://github.com/penrithbeacon/wcp-widget-theme-studio)
compliant widget providing a full theme gallery and custom theme editor for WCP-compatible
dashboards. Ships with 12 professionally crafted built-in themes and allows unlimited
custom themes, all shareable via URL.

Designed to run alongside the **Penrith Beacon WCP Dashboard** or any WCP-compatible host.

## Quick Start

```bash
docker run -d \
  --name wcp-widget-theme-studio \
  -p 3740:3740 \
  -v theme_data:/app/data \
  --restart unless-stopped \
  penrithbeacon/wcp-widget-theme-studio:latest
```

Then add it to your WCP dashboard at `http://localhost:3740`.

## Docker Compose

```yaml
services:
  theme-studio:
    image: penrithbeacon/wcp-widget-theme-studio:latest
    container_name: wcp-widget-theme-studio
    ports:
      - "3740:3740"
    restart: unless-stopped
    volumes:
      - theme_data:/app/data

volumes:
  theme_data:
```

## WCP Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /widget/` | Compact widget card with theme list |
| `GET /widget/wcp` | WCP 1.0.0 manifest |
| `GET /widget/health` | Health check |
| `GET /widget/icon.svg` | Widget icon |
| `GET /widget/full` | Full Theme Studio (3-column gallery + editor) |
| `GET /widget/themes/<id>.pbtheme.json` | Download a theme as JSON |
| `GET /widget/api/themes` | List all themes (built-in + custom) |
| `POST /widget/api/custom` | Save a custom theme |
| `DELETE /widget/api/custom/<id>` | Delete a custom theme |

## Theme Format (`.pbtheme.json`)

Themes are shareable JSON files containing CSS custom property values:

```json
{
  "uuid": "2d9e7698-c49e-482d-87cf-a2d8c03f423d",
  "name": "Dracula",
  "vars": {
    "--bg": "#282a36",
    "--surface": "#343746",
    "--surface2": "#44475a",
    "--border": "#6272a4",
    "--text": "#f8f8f2",
    "--muted": "#6272a4",
    "--accent": "#ff79c6",
    "--green": "#50fa7b",
    "--red": "#ff5555",
    "--yellow": "#f1fa8c",
    "--blue": "#8be9fd",
    "--radius": "6px",
    "--shadow": "0 4px 16px rgba(0,0,0,.5)"
  }
}
```

Share a theme by URL: `http://localhost:3740/widget/themes/<id>.pbtheme.json`

## Built-in Themes

| Theme | ID |
|-------|----|
| Dracula | `dracula` |
| Nord | `nord` |
| Catppuccin Mocha | `catppuccin` |
| Tokyo Night | `tokyo` |
| Gruvbox Dark | `gruvbox` |
| Monokai | `monokai` |
| One Dark | `onedark` |
| Solarized Dark | `solarized` |
| Rosé Pine | `rosepine` |
| Ayu Dark | `ayu` |
| Cyberpunk | `cyberpunk` |
| Forest | `forest` |

## WCP Compatibility

| Property | Value |
|----------|-------|
| WCP Version | 1.1.0 |
| Widget Version | 1.0.0 |
| Render mode | iframe |
| Auth | none |
| Default card size | 4×6 |

## Technical Details

- **Base image:** `python:3.12-slim`
- **Port:** `3740`
- **Dependencies:** Flask
- **Persistent storage:** Named Docker volume `theme_data` stores custom themes
- **No external API calls** — fully self-contained, works offline

## Tags

| Tag | Description |
|-----|-------------|
| `latest` | Latest stable release |
| `1.0.0-wcp1.1.0` | Widget v1.0.0, WCP protocol v1.1.0 |

## Source

- Docker Hub: [penrithbeacon/wcp-widget-theme-studio](https://hub.docker.com/r/penrithbeacon/wcp-widget-theme-studio)
- GitHub: [penrithbeacon/wcp-widget-theme-studio](https://github.com/penrithbeacon/wcp-widget-theme-studio)
