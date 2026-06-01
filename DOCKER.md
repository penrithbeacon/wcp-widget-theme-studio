# WCP Widget: Theme Studio

A [Widget Context Protocol (WCP)](https://widgetcontextprotocol.com) compliant widget providing
a full theme gallery and custom theme editor for WCP-compatible dashboards. Ships with 15
built-in themes (12 community + 3 Penrith Beacon WCP native) and allows unlimited custom themes,
all shareable via URL. Designed to run alongside any WCP-compatible host dashboard.

**Specification:** [widgetcontextprotocol.com](https://widgetcontextprotocol.com)

## Quick Start

```bash
docker run -d \
  --name wcp-widget-theme-studio \
  -p 3740:3740 \
  -v theme_data:/app/data \
  --restart unless-stopped \
  penrithbeacon/wcp-widget-theme-studio:latest
```

Then add it to your WCP dashboard at the container's network address.

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

## WCP Request Headers

This widget supports the WCP 1.3.1 request headers:

| Header | Required | Description |
|--------|----------|-------------|
| `Wcp-Instance-Id` | Required | UUID identifying this widget instance |
| `Wcp-Dashboard-Id` | Optional | UUID identifying the requesting dashboard |
| `Wcp-Version` | Optional | Protocol version the dashboard speaks |

## WCP Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /widget/` | Compact widget card with theme list |
| `GET /widget/wcp` | WCP 1.3.1 manifest |
| `GET /widget/health` | Health check |
| `GET /widget/icon.svg` | Widget icon (SVG) |
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

## Built-in Themes (15 total)

**Community themes:**

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

**Penrith Beacon WCP native themes:**

| Theme | ID |
|-------|----|
| Penrith Beacon WCP Dark | `pb-wcp-dark` |
| Penrith Beacon WCP Light | `pb-wcp-light` |
| Penrith Beacon WCP High Contrast | `pb-wcp-hc` |

## WCP Compatibility

| Property | Value |
|----------|-------|
| WCP Version | 1.3.1 |
| Widget Version | 1.3.0 |
| Render mode | iframe |
| Auth | none |
| Default card size | 6×4 |
| Multi-instance | Theme storage is global by design |

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
| `1.3.0-wcp1.3.1` | Widget v1.3.0, WCP 1.3.1 — CORS headers, multi-instance support |
| `1.2.0-wcp1.3.0` | Widget v1.2.0, WCP 1.3.0 — mandatory components array |

## Source

- Docker Hub: [penrithbeacon/wcp-widget-theme-studio](https://hub.docker.com/r/penrithbeacon/wcp-widget-theme-studio)
- GitHub: [penrithbeacon/wcp-widget-theme-studio](https://github.com/penrithbeacon/wcp-widget-theme-studio)
- WCP Specification: [widgetcontextprotocol.com](https://widgetcontextprotocol.com)
