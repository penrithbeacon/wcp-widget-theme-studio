"""
WCP Widget: WCP Theme Studio
Theme gallery with 15 built-in themes + custom theme editor.
Each theme is served as a downloadable .pbtheme.json for import into any WCP dashboard.
Port: 3740
Specification: https://widgetcontextprotocol.com
"""

import io, json, os, uuid as uuid_lib, zipfile
from flask import Flask, jsonify, render_template, request, Response

app = Flask(__name__)

PUBLISHED_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'published', 'index.html')

# ── CORS ──────────────────────────────────────────────────────────────────────

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = (
        'Content-Type, Wcp-Instance-Id, Wcp-Dashboard-Id, Wcp-Version, Wcp-Widget-Id, '
        'Wcp-Orchestration-Id, Wcp-Application-Id'
    )
    return response

@app.route('/widget/<path:p>', methods=['OPTIONS'])
@app.route('/widget/', methods=['OPTIONS'])
@app.route('/wcp', methods=['OPTIONS'])
def cors_preflight(p=''):
    return Response('', status=204)

# ── Instance ID helper ────────────────────────────────────────────────────────

def get_instance_id():
    iid = request.headers.get("Wcp-Instance-Id", "").strip()
    if not iid:
        iid = (request.args.get("wcpInstanceId", "") or "").strip()
    return iid

def get_orchestration_id():
    oid = request.headers.get("Wcp-Orchestration-Id", "").strip()
    if not oid:
        oid = (request.args.get("wcpOrchestrationId", "") or "").strip()
    return oid

def get_application_id():
    aid = request.headers.get("Wcp-Application-Id", "").strip()
    if not aid:
        aid = (request.args.get("wcpApplicationId", "") or "").strip()
    return aid

def get_state_key():
    """WCP 1.5.0 compound state key. See widgetcontextprotocol.com — WCP Request Headers."""
    orch_id = get_orchestration_id()
    app_id  = get_application_id()
    if orch_id and app_id: return f"{orch_id}:{app_id}"
    if orch_id:            return orch_id
    return "global"

DATA_FILE = '/app/data/custom_themes.json'
os.makedirs('/app/data', exist_ok=True)

# ── Built-in themes ───────────────────────────────────────────────────────────

BUILTIN_THEMES = [
  # ── Penrith Beacon WCP native themes — always at the top ──────────
  {"id":"pb-wcp-dark", "uuid":"a1b2c3d4-e5f6-7890-abcd-ef1234567890","name":"Penrith Beacon WCP Dark",          "builtin":True,"vars":{"--wcp-color-bg":"#0d1117","--wcp-color-surface":"#161b22","--wcp-color-surface-raised":"#1c2128","--wcp-color-border":"#30363d","--wcp-color-text":"#e6edf3","--wcp-color-text-muted":"#8b949e","--wcp-color-primary":"#f0883e","--wcp-color-success":"#3fb950","--wcp-color-danger":"#f85149","--wcp-color-warning":"#d29922","--wcp-color-info":"#58a6ff","--wcp-radius-md":"8px","--wcp-shadow-sm":"0 4px 16px rgba(0,0,0,.45)"}},
  {"id":"pb-wcp-light","uuid":"b2c3d4e5-f6a7-8901-bcde-f12345678901","name":"Penrith Beacon WCP Light",         "builtin":True,"vars":{"--wcp-color-bg":"#ffffff","--wcp-color-surface":"#f6f8fa","--wcp-color-surface-raised":"#eaeef2","--wcp-color-border":"#d0d7de","--wcp-color-text":"#1f2328","--wcp-color-text-muted":"#636c76","--wcp-color-primary":"#f0883e","--wcp-color-success":"#1a7f37","--wcp-color-danger":"#cf222e","--wcp-color-warning":"#9a6700","--wcp-color-info":"#0969da","--wcp-radius-md":"8px","--wcp-shadow-sm":"0 4px 8px rgba(0,0,0,.12)"}},
  {"id":"pb-wcp-hc",   "uuid":"c3d4e5f6-a7b8-9012-cdef-123456789012","name":"Penrith Beacon WCP High Contrast", "builtin":True,"vars":{"--wcp-color-bg":"#000000","--wcp-color-surface":"#0d0d0d","--wcp-color-surface-raised":"#1a1a1a","--wcp-color-border":"#ffffff","--wcp-color-text":"#ffffff","--wcp-color-text-muted":"#cccccc","--wcp-color-primary":"#ff8c00","--wcp-color-success":"#00ff41","--wcp-color-danger":"#ff3333","--wcp-color-warning":"#ffff00","--wcp-color-info":"#00b4ff","--wcp-radius-md":"4px","--wcp-shadow-sm":"none"}},
  # ── Community themes ──────────────────────────────────────────────
  {"id":"dracula",   "uuid":"2d9e7698-c49e-482d-87cf-a2d8c03f423d","name":"Dracula",         "builtin":True,"vars":{"--wcp-color-bg":"#282a36","--wcp-color-surface":"#343746","--wcp-color-surface-raised":"#44475a","--wcp-color-border":"#6272a4","--wcp-color-text":"#f8f8f2","--wcp-color-text-muted":"#6272a4","--wcp-color-primary":"#ff79c6","--wcp-color-success":"#50fa7b","--wcp-color-danger":"#ff5555","--wcp-color-warning":"#f1fa8c","--wcp-color-info":"#8be9fd","--wcp-radius-md":"6px","--wcp-shadow-sm":"0 4px 16px rgba(0,0,0,.5)"}},
  {"id":"nord",      "uuid":"6b5bd0ad-39ac-4bcd-8a04-54959b39bef2","name":"Nord",             "builtin":True,"vars":{"--wcp-color-bg":"#2e3440","--wcp-color-surface":"#3b4252","--wcp-color-surface-raised":"#434c5e","--wcp-color-border":"#4c566a","--wcp-color-text":"#eceff4","--wcp-color-text-muted":"#d8dee9","--wcp-color-primary":"#88c0d0","--wcp-color-success":"#a3be8c","--wcp-color-danger":"#bf616a","--wcp-color-warning":"#ebcb8b","--wcp-color-info":"#81a1c1","--wcp-radius-md":"8px","--wcp-shadow-sm":"0 4px 12px rgba(0,0,0,.4)"}},
  {"id":"catppuccin","uuid":"d3a11c29-4dbd-4fa6-a6de-145c13045867","name":"Catppuccin Mocha", "builtin":True,"vars":{"--wcp-color-bg":"#1e1e2e","--wcp-color-surface":"#313244","--wcp-color-surface-raised":"#45475a","--wcp-color-border":"#585b70","--wcp-color-text":"#cdd6f4","--wcp-color-text-muted":"#a6adc8","--wcp-color-primary":"#cba6f7","--wcp-color-success":"#a6e3a1","--wcp-color-danger":"#f38ba8","--wcp-color-warning":"#f9e2af","--wcp-color-info":"#89b4fa","--wcp-radius-md":"8px","--wcp-shadow-sm":"0 4px 20px rgba(0,0,0,.5)"}},
  {"id":"tokyo",     "uuid":"d9ac54b8-622c-4811-b387-5fdc7d1af8aa","name":"Tokyo Night",      "builtin":True,"vars":{"--wcp-color-bg":"#1a1b2e","--wcp-color-surface":"#24253e","--wcp-color-surface-raised":"#2f3154","--wcp-color-border":"#414868","--wcp-color-text":"#c0caf5","--wcp-color-text-muted":"#9aa5ce","--wcp-color-primary":"#7aa2f7","--wcp-color-success":"#9ece6a","--wcp-color-danger":"#f7768e","--wcp-color-warning":"#e0af68","--wcp-color-info":"#7dcfff","--wcp-radius-md":"6px","--wcp-shadow-sm":"0 4px 20px rgba(0,0,0,.6)"}},
  {"id":"gruvbox",   "uuid":"fddd994e-71ad-4006-9c1e-b251e6beb7ac","name":"Gruvbox Dark",     "builtin":True,"vars":{"--wcp-color-bg":"#282828","--wcp-color-surface":"#3c3836","--wcp-color-surface-raised":"#504945","--wcp-color-border":"#665c54","--wcp-color-text":"#ebdbb2","--wcp-color-text-muted":"#a89984","--wcp-color-primary":"#fabd2f","--wcp-color-success":"#b8bb26","--wcp-color-danger":"#fb4934","--wcp-color-warning":"#fabd2f","--wcp-color-info":"#83a598","--wcp-radius-md":"4px","--wcp-shadow-sm":"0 4px 12px rgba(0,0,0,.5)"}},
  {"id":"monokai",   "uuid":"cc0d722b-48ac-495f-b8d2-d9f3304b97f8","name":"Monokai",          "builtin":True,"vars":{"--wcp-color-bg":"#272822","--wcp-color-surface":"#3e3d32","--wcp-color-surface-raised":"#49483e","--wcp-color-border":"#75715e","--wcp-color-text":"#f8f8f2","--wcp-color-text-muted":"#75715e","--wcp-color-primary":"#f92672","--wcp-color-success":"#a6e22e","--wcp-color-danger":"#f92672","--wcp-color-warning":"#e6db74","--wcp-color-info":"#66d9ef","--wcp-radius-md":"6px","--wcp-shadow-sm":"0 4px 16px rgba(0,0,0,.5)"}},
  {"id":"onedark",   "uuid":"ab07c05a-5ff7-445d-ac86-0e5ee6ab1887","name":"One Dark",         "builtin":True,"vars":{"--wcp-color-bg":"#282c34","--wcp-color-surface":"#2c313c","--wcp-color-surface-raised":"#3e4451","--wcp-color-border":"#4b5263","--wcp-color-text":"#abb2bf","--wcp-color-text-muted":"#5c6370","--wcp-color-primary":"#61afef","--wcp-color-success":"#98c379","--wcp-color-danger":"#e06c75","--wcp-color-warning":"#e5c07b","--wcp-color-info":"#61afef","--wcp-radius-md":"6px","--wcp-shadow-sm":"0 4px 16px rgba(0,0,0,.4)"}},
  {"id":"solarized", "uuid":"10ab0dcf-361a-4680-9d10-3d6cbd09c5c8","name":"Solarized Dark",   "builtin":True,"vars":{"--wcp-color-bg":"#002b36","--wcp-color-surface":"#073642","--wcp-color-surface-raised":"#0b4a56","--wcp-color-border":"#586e75","--wcp-color-text":"#839496","--wcp-color-text-muted":"#657b83","--wcp-color-primary":"#268bd2","--wcp-color-success":"#859900","--wcp-color-danger":"#dc322f","--wcp-color-warning":"#b58900","--wcp-color-info":"#268bd2","--wcp-radius-md":"6px","--wcp-shadow-sm":"0 4px 16px rgba(0,0,0,.6)"}},
  {"id":"rosepine",  "uuid":"67637421-bd4d-460d-ba9c-6f5c462feb4e","name":"Rosé Pine",        "builtin":True,"vars":{"--wcp-color-bg":"#191724","--wcp-color-surface":"#1f1d2e","--wcp-color-surface-raised":"#26233a","--wcp-color-border":"#403d52","--wcp-color-text":"#e0def4","--wcp-color-text-muted":"#6e6a86","--wcp-color-primary":"#eb6f92","--wcp-color-success":"#31748f","--wcp-color-danger":"#eb6f92","--wcp-color-warning":"#f6c177","--wcp-color-info":"#9ccfd8","--wcp-radius-md":"8px","--wcp-shadow-sm":"0 4px 20px rgba(0,0,0,.5)"}},
  {"id":"ayu",       "uuid":"ef5178f8-d30d-42b7-aac1-9028eae0811c","name":"Ayu Dark",         "builtin":True,"vars":{"--wcp-color-bg":"#0d1017","--wcp-color-surface":"#131721","--wcp-color-surface-raised":"#1a1f29","--wcp-color-border":"#2d3345","--wcp-color-text":"#bfbdb6","--wcp-color-text-muted":"#565b66","--wcp-color-primary":"#e6b450","--wcp-color-success":"#7fd962","--wcp-color-danger":"#f07178","--wcp-color-warning":"#e6b450","--wcp-color-info":"#39bae6","--wcp-radius-md":"6px","--wcp-shadow-sm":"0 4px 16px rgba(0,0,0,.6)"}},
  {"id":"cyberpunk", "uuid":"e10609cb-2da3-4f28-920c-b7fc51845755","name":"Cyberpunk",        "builtin":True,"vars":{"--wcp-color-bg":"#060010","--wcp-color-surface":"#100025","--wcp-color-surface-raised":"#1a003a","--wcp-color-border":"#ff2d78","--wcp-color-text":"#f0f0f0","--wcp-color-text-muted":"#888888","--wcp-color-primary":"#ff2d78","--wcp-color-success":"#00ff41","--wcp-color-danger":"#ff2d78","--wcp-color-warning":"#ffff00","--wcp-color-info":"#00b4ff","--wcp-radius-md":"2px","--wcp-shadow-sm":"0 0 20px rgba(255,45,120,.3)"}},
  {"id":"forest",    "uuid":"94153276-8395-48df-a4a8-9cadebb605e6","name":"Forest",            "builtin":True,"vars":{"--wcp-color-bg":"#1a2214","--wcp-color-surface":"#22301a","--wcp-color-surface-raised":"#2d4020","--wcp-color-border":"#3d5c2a","--wcp-color-text":"#c8d8c0","--wcp-color-text-muted":"#7a9a6a","--wcp-color-primary":"#5a9e3a","--wcp-color-success":"#5a9e3a","--wcp-color-danger":"#c0392b","--wcp-color-warning":"#d4a017","--wcp-color-info":"#3a7ab8","--wcp-radius-md":"8px","--wcp-shadow-sm":"0 4px 16px rgba(0,0,0,.5)"}},
]

WCP_MANIFEST = {
  "wcp":"2.1.0","uuid":"87a8413d-28d9-451b-b1ef-7c1763a665ec","name":"WCP Theme Studio","version":"1.6.0",
  "description":"Gallery of 15 built-in themes + custom theme editor. Includes the 3 Penrith Beacon WCP native themes. Each theme shareable as a .pbtheme.json URL.",
  "icon":"/widget/icon.svg","health":"/widget/health",
  "container":{
    "image":            "docker.io/penrithbeacon/wcp-widget-theme-studio",
    "source":           {"type": "registry"},
    "tag":              "1.6.0-wcp2.1.0",
    "port":             3740,
    "volumes":          [{"name": "theme_data", "mountPath": "/app/data"}],
    "defaultLifecycle": "always",
  },
  "components":[
    {"id":"theme-studio",     "uuid":"e27a9086-89ee-498f-98e7-cebd7efb73c9","name":"WCP Theme Studio",      "role":"widget","path":"/widget/",     "icon":"/widget/icon.svg","renderMode":"iframe","defaultSize":{"w":4,"h":6}},
    {"id":"theme-studio-full","uuid":"f38b0197-9aff-5b09-a9f8-dce8f0gc84da","name":"WCP Theme Studio — Full","role":"widget","path":"/widget/full","icon":"/widget/icon.svg","renderMode":"iframe","defaultSize":{"w":12,"h":12}},
    {"id":"theme-studio-guide","uuid":"a49c2e18-73d1-4f5b-b8a2-9e6d0f7c5b31","name":"WCP Theme Studio — Guide","role":"widget","path":"/widget/guide","icon":"/widget/icon.svg","renderMode":"iframe","defaultSize":{"w":12,"h":12}},
  ],
  "pages":[{"id":"full","path":"/widget/full","title":"Theme Studio","description":"Full theme gallery with editor","window":{"width":1100,"height":700}}],
  "actions":[
    {"id":"open-studio","type":"wcp:open-window","label":"Open Theme Studio","page":"full"},
    {"id":"open-tab","type":"wcp:open-tab","label":"Open in New Tab","page":"full","tab":{"title":"Theme Studio","icon":"/widget/icon.svg"},"persist":False},
  ],
}

# ── Custom theme persistence ───────────────────────────────────────────────────

def read_custom():
    try:
        with open(DATA_FILE) as f: return json.load(f)
    except: return []

def write_custom(data):
    with open(DATA_FILE,'w') as f: json.dump(data, f, indent=2)

def all_themes():
    return BUILTIN_THEMES + read_custom()

# ── JSON-LD structured data ───────────────────────────────────────────────────

WIDGET_JSONLD = json.dumps({
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": WCP_MANIFEST["name"],
    "softwareVersion": WCP_MANIFEST["version"],
    "description": WCP_MANIFEST["description"],
    "identifier": WCP_MANIFEST["uuid"],
    "applicationCategory": "WCP Widget",
    "operatingSystem": "Web",
    "isBasedOn": {
        "@type": "WebSite",
        "name": "Widget Context Protocol",
        "url": "https://widgetcontextprotocol.com",
    },
    "additionalProperty": [
        {"@type": "PropertyValue", "name": "wcpVersion",      "value": WCP_MANIFEST["wcp"]},
        {"@type": "PropertyValue", "name": "containerImage",  "value": WCP_MANIFEST["container"]["image"]},
        {"@type": "PropertyValue", "name": "containerTag",    "value": WCP_MANIFEST["container"]["tag"]},
        {"@type": "PropertyValue", "name": "containerPort",   "value": str(WCP_MANIFEST["container"]["port"])},
    ],
}, indent=2)

# ── WCP endpoints ─────────────────────────────────────────────────────────────

@app.route('/wcp')
def container_directory():
    return jsonify({
        "type":    "directory",
        "wcp":     "2.1.0",
        "widgets": [{
            "id":          "theme-studio",
            "uuid":        WCP_MANIFEST["uuid"],
            "name":        WCP_MANIFEST["name"],
            "description": WCP_MANIFEST["description"],
            "icon":        WCP_MANIFEST["icon"],
            "manifest":    "/widget/wcp",
        }]
    })

@app.route('/')
def published_spa():
    if os.path.exists(PUBLISHED_PATH):
        with open(PUBLISHED_PATH, 'r', encoding='utf-8') as f:
            return Response(f.read(), mimetype='text/html')
    return Response('Not Found', status=404, mimetype='text/plain')

@app.route('/widget/publish', methods=['POST'])
def publish():
    html = request.get_data(as_text=True)
    if not html:
        return jsonify({'success': False, 'error': 'Empty body'}), 400
    try:
        os.makedirs(os.path.dirname(PUBLISHED_PATH), exist_ok=True)
        with open(PUBLISHED_PATH, 'w', encoding='utf-8') as f:
            f.write(html)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/widget/publish', methods=['DELETE'])
def unpublish():
    try:
        if os.path.exists(PUBLISHED_PATH):
            os.remove(PUBLISHED_PATH)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/widget/')
@app.route('/widget/index.html')
def widget(): return render_template('widget.html', themes=all_themes(), manifest=WCP_MANIFEST, jsonld=WIDGET_JSONLD,
    wcp_instance_id=get_instance_id(),
    wcp_orchestration_id=get_orchestration_id(), wcp_application_id=get_application_id())

@app.route('/widget/wcp')
def wcp():
    manifest = dict(WCP_MANIFEST)
    manifest['web'] = {'published': os.path.exists(PUBLISHED_PATH)}
    return jsonify(manifest)

@app.route('/widget/manifest')
def manifest():
    m = WCP_MANIFEST
    return jsonify({k:m[k] for k in ['wcp','name','version','description','icon','health','widget']})

@app.route('/widget/health')
def health():
    return jsonify({"status": "ok", "name": "WCP Theme Studio",
                    "container": os.environ.get("CONTAINER_NAME", "unknown")})

@app.route('/widget/full')
def full(): return render_template('full.html', themes=all_themes(), manifest=WCP_MANIFEST, jsonld=WIDGET_JSONLD,
    wcp_instance_id=get_instance_id(),
    wcp_orchestration_id=get_orchestration_id(), wcp_application_id=get_application_id())

@app.route('/widget/guide')
def guide(): return render_template('guide.html', manifest=WCP_MANIFEST, jsonld=WIDGET_JSONLD,
    wcp_instance_id=get_instance_id(),
    wcp_orchestration_id=get_orchestration_id(), wcp_application_id=get_application_id())

ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <path fill="#f0883e" d="M15.825.12a.5.5 0 0 1 .132.584c-1.53 3.43-4.743 8.17-7.095 10.64a6.067 6.067 0 0 1-2.373 1.534c-.018.227-.06.538-.16.868-.201.659-.667 1.479-1.708 1.74a8.118 8.118 0 0 1-3.078.132 3.659 3.659 0 0 1-.562-.135 1.382 1.382 0 0 1-.466-.247.714.714 0 0 1-.204-.288.622.622 0 0 1 .004-.443c.095-.245.316-.38.461-.452.394-.197.625-.453.867-.826.095-.144.184-.297.287-.472l.117-.198c.151-.255.326-.54.546-.848.528-.739 1.153-.926 1.616-.896.765.05 1.313.548 1.562 1.237a5.83 5.83 0 0 1 1.616-1.128c2.353-2.454 5.557-7.187 7.09-10.62.133-.3.438-.42.728-.32z"/>
</svg>"""

@app.route('/widget/icon.svg')
def icon():
    return Response(ICON_SVG, mimetype='image/svg+xml')

@app.route('/widget/api/guids')
def api_guids():
    return jsonify({
        "uuid": WCP_MANIFEST["uuid"],
        "components": [
            {"id": c["id"], "uuid": c["uuid"], "name": c["name"]}
            for c in WCP_MANIFEST.get("components", [])
        ]
    })

@app.route('/widget/export.wcp')
def export_wcp():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(WCP_MANIFEST, indent=2))
        z.writestr("icon.svg", ICON_SVG)
        z.writestr("DOCKER.md", f"""# {WCP_MANIFEST['name']} — WCP Container

## Pull
```
docker pull penrithbeacon/wcp-widget-theme-studio
```

## Run
```
docker compose up -d
```

Port: 3740 | Spec: https://widgetcontextprotocol.com
""")
    buf.seek(0)
    name = WCP_MANIFEST["name"].lower().replace(" ", "-")
    resp = Response(buf.read(), mimetype="application/zip")
    resp.headers["Content-Disposition"] = f'attachment; filename="{name}.wcp"'
    return resp

# ── Theme file endpoint ────────────────────────────────────────────────────────

@app.route('/widget/themes/<theme_id>.pbtheme.json')
def get_theme_file(theme_id):
    theme = next((t for t in all_themes() if t['id'] == theme_id), None)
    if not theme: return jsonify({"error":"not found"}), 404
    payload = {"uuid": theme.get('uuid', str(uuid_lib.uuid4())),
               "name": theme['name'], "vars": _resolve_all_vars(theme['vars'])}
    resp = Response(json.dumps(payload, indent=2), mimetype='application/json')
    resp.headers['Content-Disposition'] = f'attachment; filename="{theme_id}.pbtheme.json"'
    return resp

# ── Export .wcpt ──────────────────────────────────────────────────────────────

@app.route('/widget/api/export-wcpt/<theme_id>')
def export_wcpt(theme_id):
    theme = next((t for t in all_themes() if t['id'] == theme_id), None)
    if not theme: return jsonify({"error":"not found"}), 404
    t_uuid = theme.get('uuid', str(uuid_lib.uuid4()))
    t_vars = _resolve_all_vars(theme['vars'])
    manifest = {
        "format": "wcpt", "formatVersion": "1.0",
        "id": str(uuid_lib.uuid4()), "collectionName": theme['name'],
        "themeCount": 1, "author": "", "authorEmail": "", "authorUrl": "",
        "created": __import__('datetime').datetime.utcnow().isoformat() + 'Z',
    }
    themes_payload = [{"id": theme['id'], "uuid": t_uuid, "name": theme['name'],
                       "vars": t_vars, "author": "", "authorEmail": "", "authorUrl": ""}]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, indent=2))
        z.writestr("themes.json", json.dumps(themes_payload, indent=2))
    buf.seek(0)
    safe_name = theme['name'].replace(' ', '_')
    resp = Response(buf.read(), mimetype='application/octet-stream')
    resp.headers['Content-Disposition'] = f'attachment; filename="{safe_name}.wcpt"'
    return resp

def _hex2rgba(h, a):
    if not h or not h.startswith('#') or len(h) < 7: return f'rgba(0,0,0,{a})'
    r, g, b = int(h[1:3],16), int(h[3:5],16), int(h[5:7],16)
    return f'rgba({r},{g},{b},{a})'

def _resolve_all_vars(tv):
    # All keys use --wcp-* names directly — no old seed names.
    bg  = tv.get('--wcp-color-bg','#0d1117')
    sur = tv.get('--wcp-color-surface','#161b22')
    sr2 = tv.get('--wcp-color-surface-raised','#1c2128')
    bdr = tv.get('--wcp-color-border','#30363d')
    txt = tv.get('--wcp-color-text','#e6edf3')
    mut = tv.get('--wcp-color-text-muted','#8b949e')
    acc = tv.get('--wcp-color-primary','#f0883e')
    grn = tv.get('--wcp-color-success','#3fb950')
    red = tv.get('--wcp-color-danger','#f85149')
    yel = tv.get('--wcp-color-warning','#d29922')
    blu = tv.get('--wcp-color-info','#58a6ff')
    rad = tv.get('--wcp-radius-md','8px')
    shd = tv.get('--wcp-shadow-sm','0 4px 16px rgba(0,0,0,.45)')
    tokens = {
        '--wcp-color-bg':bg,'--wcp-color-surface':sur,
        '--wcp-color-surface-raised':sr2,'--wcp-color-surface-sunken':bg,
        '--wcp-color-overlay':_hex2rgba(bg,0.75),
        '--wcp-color-border':bdr,'--wcp-color-border-strong':_hex2rgba(txt,0.25),
        '--wcp-color-text':txt,'--wcp-color-text-muted':mut,
        '--wcp-color-text-disabled':_hex2rgba(mut,0.5),'--wcp-color-text-inverse':bg,
        '--wcp-color-link':blu,
        '--wcp-color-primary':acc,'--wcp-color-primary-dim':_hex2rgba(acc,0.15),
        '--wcp-color-primary-on':tv.get('--wcp-color-primary-on','#ffffff'),
        '--wcp-color-success':grn,'--wcp-color-success-on':tv.get('--wcp-color-success-on','#ffffff'),
        '--wcp-color-success-surface':_hex2rgba(grn,0.12),
        '--wcp-color-warning':yel,'--wcp-color-warning-surface':_hex2rgba(yel,0.12),
        '--wcp-color-danger':red,'--wcp-color-danger-surface':_hex2rgba(red,0.12),
        '--wcp-color-info':blu,'--wcp-color-info-surface':_hex2rgba(blu,0.12),
        '--wcp-font-family':"-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif",
        '--wcp-font-mono':"ui-monospace,'SF Mono','Fira Code',monospace",
        '--wcp-font-size-xs':'0.70rem','--wcp-font-size-sm':'0.80rem','--wcp-font-size-md':'0.875rem',
        '--wcp-font-size-lg':'1rem','--wcp-font-size-xl':'1.125rem','--wcp-font-size-2xl':'1.375rem',
        '--wcp-font-size-3xl':'1.75rem',
        '--wcp-font-weight-normal':'400','--wcp-font-weight-medium':'500',
        '--wcp-font-weight-semibold':'600','--wcp-font-weight-bold':'700',
        '--wcp-line-height-tight':'1.2','--wcp-line-height-normal':'1.5','--wcp-line-height-relaxed':'1.75',
        '--wcp-space-1':'4px','--wcp-space-2':'8px','--wcp-space-3':'12px','--wcp-space-4':'16px',
        '--wcp-space-5':'24px','--wcp-space-6':'32px','--wcp-space-7':'48px','--wcp-space-8':'64px',
        '--wcp-radius-sm':'4px','--wcp-radius-md':rad,'--wcp-radius-lg':'12px',
        '--wcp-radius-xl':'16px','--wcp-radius-round':'9999px',
        '--wcp-shadow-sm':shd,'--wcp-shadow-md':'0 4px 12px rgba(0,0,0,.2)',
        '--wcp-shadow-lg':'0 8px 24px rgba(0,0,0,.25)','--wcp-shadow-xl':'0 16px 40px rgba(0,0,0,.3)',
        '--wcp-duration-fast':'100ms','--wcp-duration-normal':'200ms','--wcp-duration-slow':'350ms',
        '--wcp-easing-standard':'ease','--wcp-easing-out':'ease-out','--wcp-easing-in':'ease-in',
        '--wcp-easing-spring':'cubic-bezier(0.34,1.56,0.64,1)',
        '--wcp-z-base':'0','--wcp-z-raised':'10','--wcp-z-dropdown':'1000','--wcp-z-sticky':'1100',
        '--wcp-z-modal':'1200','--wcp-z-toast':'1300','--wcp-z-tooltip':'1400',
        '--wcp-focus-ring-width':'2px','--wcp-focus-ring-offset':'2px',
        '--wcp-focus-ring-color':acc,'--wcp-touch-target-min':'44px',
        '--wcp-widget-bg':sur,'--wcp-widget-border':bdr,
        '--wcp-widget-radius':rad,'--wcp-widget-padding':'16px',
        '--wcp-widget-gap':'12px','--wcp-widget-shadow':shd,
    }
    for k, v in tv.items():
        if k.startswith('--wcp-'): tokens[k] = v
    return tokens

# ── Theme list API ────────────────────────────────────────────────────────────

@app.route('/widget/api/themes')
def api_themes(): return jsonify(all_themes())

@app.route('/widget/api/custom', methods=['POST'])
def api_add_custom():
    data = request.get_json(force=True) or {}
    name = str(data.get('name','')).strip()
    vars_ = data.get('vars')
    if not name or not isinstance(vars_, dict):
        return jsonify({"success":False,"error":"name and vars required"}), 400
    custom = read_custom()
    tid = data.get('id') or str(uuid_lib.uuid4())[:8]
    # Assign a permanent UUID if not already present
    if 'uuid' not in data: data['uuid'] = str(uuid_lib.uuid4())
    existing = next((i for i,t in enumerate(custom) if t['id']==tid), None)
    entry = {"id":tid,"uuid":data.get('uuid', str(uuid_lib.uuid4())),"name":name,"builtin":False,"vars":vars_}
    if existing is not None: custom[existing] = entry
    else: custom.append(entry)
    write_custom(custom)
    return jsonify({"success":True,"id":tid})

@app.route('/widget/api/custom/<tid>', methods=['DELETE'])
def api_del_custom(tid):
    custom = [t for t in read_custom() if t['id'] != tid]
    write_custom(custom)
    return jsonify({"success":True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3740, debug=False)
