# WCP Theme Studio — Specification

## Overview
Gallery of 15 built-in themes + custom theme editor with 81 design tokens. Includes the 3 Penrith Beacon WCP native themes. Each theme shareable as a `.pbtheme.json` URL.

- **Port:** 3740
- **Container:** `wcp-widget-theme-studio`
- **Image:** `docker.io/penrithbeacon/wcp-widget-theme-studio`

## Version
- **Widget:** 1.7.0
- **WCP:** 2.1.0
- **Docker tag:** `1.7.0-wcp2.1.0`

## Controls (HTML Templates)

| Template | Route | Purpose | Default Size |
|----------|-------|---------|--------------|
| widget.html | `/widget/` | Compact theme gallery | 4×6 |
| full.html | `/widget/full` | Full theme editor with 81 tokens | 12×12 (Window: 1100×700) |
| guide.html | `/widget/guide` | Token reference guide | 12×12 |

## Components

| ID | Name | Role | Size |
|----|------|------|------|
| theme-studio | WCP Theme Studio | widget | 4×6 |
| theme-studio-full | WCP Theme Studio — Full | widget | 12×12 |
| theme-studio-guide | WCP Theme Studio — Guide | widget | 12×12 |

## API Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/wcp` | Container directory |
| GET | `/widget/wcp` | Widget manifest |
| GET | `/widget/index` | Widget index directory |
| GET | `/widget/` | Compact gallery |
| GET | `/widget/full` | Full editor |
| GET | `/widget/guide` | Token reference guide |
| GET | `/widget/health` | Health check |
| GET | `/widget/icon.svg` | Widget icon |
| GET | `/widget/manifest` | Lightweight manifest subset |
| GET | `/widget/api/guids` | Component UUIDs |
| GET | `/widget/export.wcp` | WCP export package |
| GET | `/widget/api/themes` | List all themes (built-in + custom) |
| GET | `/widget/themes/<id>.pbtheme.json` | Download theme as shareable JSON |
| GET | `/widget/api/export-wcpt/<id>` | Export theme as WCPT package |
| POST | `/widget/api/custom` | Create/save custom theme |
| DELETE | `/widget/api/custom/<id>` | Delete custom theme |
| POST | `/widget/publish` | Publish SPA |
| DELETE | `/widget/publish` | Remove published SPA |
| GET | `/` | Serve published SPA |

## Features
- 15 built-in themes (3 Penrith Beacon native + 12 community)
- Custom theme editor with 81 WCP design tokens
- Demo tab with live preview of all token effects
- Bullseye search — click editor labels to highlight matching demo elements
- Token reference guide (guide.html)
- Theme export as `.pbtheme.json` URL
- WCPT package export
- Publish to Web support

## Configuration
- Custom themes persisted in container data

## Data Persistence
- Custom themes stored in `./published/` volume mount area
- No named data volume

## Dependencies
- Python: `flask`
- No external API dependencies
