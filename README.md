# WCP Widget — Theme Studio

A [Widget Context Protocol (WCP)](https://widgetcontextprotocol.com) widget providing
a full theme gallery and custom theme editor. Ships with 15 built-in themes and supports
unlimited custom themes, all shareable via URL.

**Specification:** [widgetcontextprotocol.com](https://widgetcontextprotocol.com)  
**Part of the** [Penrith Beacon WCP](https://penrithbeacon.com) widget suite.

> **WCP 1.4.0 certified.** This widget implements the full
> [Widget Context Protocol 1.4.0](https://widgetcontextprotocol.com) specification,
> including server UUID, Container Directory (`GET /wcp`), and all four `Wcp-*` request headers.

**Port:** 3740

## Quick Start

```bash
docker compose up --build -d
```

Open in Natterjack WCP Pinboard, or visit `http://localhost:3740/widget/full`

## Sharing Themes

Each theme has a **Copy URL** button. The URL looks like:
```
http://localhost:3740/widget/themes/dracula.njtheme.json
```

In Natterjack WCP: Settings → Themes → ↓ Import from URL → paste → Fetch → Save.

## Built-in Themes

Dracula · Nord · Catppuccin Mocha · Tokyo Night · Gruvbox Dark ·
Monokai · One Dark · Solarized Dark · Rosé Pine · Ayu Dark · Cyberpunk · Forest

## Custom Themes

Create your own via the full studio editor. Custom themes are also shareable via Copy URL.
