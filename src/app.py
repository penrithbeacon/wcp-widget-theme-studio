"""
WCP Widget: WCP Theme Studio
Theme gallery with 15 built-in themes + custom theme editor.
Each theme is served as a downloadable .pbtheme.json for import into any WCP dashboard.
Port: 3740
Specification: https://widgetcontextprotocol.com
"""

import json, os, uuid as uuid_lib
from flask import Flask, jsonify, render_template, request, Response

app = Flask(__name__)

# ── CORS ──────────────────────────────────────────────────────────────────────

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = (
        'Content-Type, Wcp-Instance-Id, Wcp-Dashboard-Id, Wcp-Version'
    )
    return response

@app.route('/widget/<path:p>', methods=['OPTIONS'])
@app.route('/widget/', methods=['OPTIONS'])
def cors_preflight(p=''):
    return Response('', status=204)

DATA_FILE = '/app/data/custom_themes.json'
os.makedirs('/app/data', exist_ok=True)

# ── Built-in themes ───────────────────────────────────────────────────────────

BUILTIN_THEMES = [
  {"id":"dracula",   "uuid":"2d9e7698-c49e-482d-87cf-a2d8c03f423d","name":"Dracula",         "builtin":True,"vars":{"--bg":"#282a36","--surface":"#343746","--surface2":"#44475a","--border":"#6272a4","--text":"#f8f8f2","--muted":"#6272a4","--accent":"#ff79c6","--green":"#50fa7b","--red":"#ff5555","--yellow":"#f1fa8c","--blue":"#8be9fd","--radius":"6px","--shadow":"0 4px 16px rgba(0,0,0,.5)"}},
  {"id":"nord",      "uuid":"6b5bd0ad-39ac-4bcd-8a04-54959b39bef2","name":"Nord",             "builtin":True,"vars":{"--bg":"#2e3440","--surface":"#3b4252","--surface2":"#434c5e","--border":"#4c566a","--text":"#eceff4","--muted":"#d8dee9","--accent":"#88c0d0","--green":"#a3be8c","--red":"#bf616a","--yellow":"#ebcb8b","--blue":"#81a1c1","--radius":"8px","--shadow":"0 4px 12px rgba(0,0,0,.4)"}},
  {"id":"catppuccin","uuid":"d3a11c29-4dbd-4fa6-a6de-145c13045867","name":"Catppuccin Mocha", "builtin":True,"vars":{"--bg":"#1e1e2e","--surface":"#313244","--surface2":"#45475a","--border":"#585b70","--text":"#cdd6f4","--muted":"#a6adc8","--accent":"#cba6f7","--green":"#a6e3a1","--red":"#f38ba8","--yellow":"#f9e2af","--blue":"#89b4fa","--radius":"8px","--shadow":"0 4px 20px rgba(0,0,0,.5)"}},
  {"id":"tokyo",     "uuid":"d9ac54b8-622c-4811-b387-5fdc7d1af8aa","name":"Tokyo Night",      "builtin":True,"vars":{"--bg":"#1a1b2e","--surface":"#24253e","--surface2":"#2f3154","--border":"#414868","--text":"#c0caf5","--muted":"#9aa5ce","--accent":"#7aa2f7","--green":"#9ece6a","--red":"#f7768e","--yellow":"#e0af68","--blue":"#7dcfff","--radius":"6px","--shadow":"0 4px 20px rgba(0,0,0,.6)"}},
  {"id":"gruvbox",   "uuid":"fddd994e-71ad-4006-9c1e-b251e6beb7ac","name":"Gruvbox Dark",     "builtin":True,"vars":{"--bg":"#282828","--surface":"#3c3836","--surface2":"#504945","--border":"#665c54","--text":"#ebdbb2","--muted":"#a89984","--accent":"#fabd2f","--green":"#b8bb26","--red":"#fb4934","--yellow":"#fabd2f","--blue":"#83a598","--radius":"4px","--shadow":"0 4px 12px rgba(0,0,0,.5)"}},
  {"id":"monokai",   "uuid":"cc0d722b-48ac-495f-b8d2-d9f3304b97f8","name":"Monokai",          "builtin":True,"vars":{"--bg":"#272822","--surface":"#3e3d32","--surface2":"#49483e","--border":"#75715e","--text":"#f8f8f2","--muted":"#75715e","--accent":"#f92672","--green":"#a6e22e","--red":"#f92672","--yellow":"#e6db74","--blue":"#66d9ef","--radius":"6px","--shadow":"0 4px 16px rgba(0,0,0,.5)"}},
  {"id":"onedark",   "uuid":"ab07c05a-5ff7-445d-ac86-0e5ee6ab1887","name":"One Dark",         "builtin":True,"vars":{"--bg":"#282c34","--surface":"#2c313c","--surface2":"#3e4451","--border":"#4b5263","--text":"#abb2bf","--muted":"#5c6370","--accent":"#61afef","--green":"#98c379","--red":"#e06c75","--yellow":"#e5c07b","--blue":"#61afef","--radius":"6px","--shadow":"0 4px 16px rgba(0,0,0,.4)"}},
  {"id":"solarized", "uuid":"10ab0dcf-361a-4680-9d10-3d6cbd09c5c8","name":"Solarized Dark",   "builtin":True,"vars":{"--bg":"#002b36","--surface":"#073642","--surface2":"#0b4a56","--border":"#586e75","--text":"#839496","--muted":"#657b83","--accent":"#268bd2","--green":"#859900","--red":"#dc322f","--yellow":"#b58900","--blue":"#268bd2","--radius":"6px","--shadow":"0 4px 16px rgba(0,0,0,.6)"}},
  {"id":"rosepine",  "uuid":"67637421-bd4d-460d-ba9c-6f5c462feb4e","name":"Rosé Pine",        "builtin":True,"vars":{"--bg":"#191724","--surface":"#1f1d2e","--surface2":"#26233a","--border":"#403d52","--text":"#e0def4","--muted":"#6e6a86","--accent":"#eb6f92","--green":"#31748f","--red":"#eb6f92","--yellow":"#f6c177","--blue":"#9ccfd8","--radius":"8px","--shadow":"0 4px 20px rgba(0,0,0,.5)"}},
  {"id":"ayu",       "uuid":"ef5178f8-d30d-42b7-aac1-9028eae0811c","name":"Ayu Dark",         "builtin":True,"vars":{"--bg":"#0d1017","--surface":"#131721","--surface2":"#1a1f29","--border":"#2d3345","--text":"#bfbdb6","--muted":"#565b66","--accent":"#e6b450","--green":"#7fd962","--red":"#f07178","--yellow":"#e6b450","--blue":"#39bae6","--radius":"6px","--shadow":"0 4px 16px rgba(0,0,0,.6)"}},
  {"id":"cyberpunk", "uuid":"e10609cb-2da3-4f28-920c-b7fc51845755","name":"Cyberpunk",        "builtin":True,"vars":{"--bg":"#060010","--surface":"#100025","--surface2":"#1a003a","--border":"#ff2d78","--text":"#f0f0f0","--muted":"#888888","--accent":"#ff2d78","--green":"#00ff41","--red":"#ff2d78","--yellow":"#ffff00","--blue":"#00b4ff","--radius":"2px","--shadow":"0 0 20px rgba(255,45,120,.3)"}},
  {"id":"forest",    "uuid":"94153276-8395-48df-a4a8-9cadebb605e6","name":"Forest",            "builtin":True,"vars":{"--bg":"#1a2214","--surface":"#22301a","--surface2":"#2d4020","--border":"#3d5c2a","--text":"#c8d8c0","--muted":"#7a9a6a","--accent":"#5a9e3a","--green":"#5a9e3a","--red":"#c0392b","--yellow":"#d4a017","--blue":"#3a7ab8","--radius":"8px","--shadow":"0 4px 16px rgba(0,0,0,.5)"}},
  # ── Penrith Beacon WCP built-in themes (match the dashboard's native themes) ──
  {"id":"pb-wcp-dark","uuid":"a1b2c3d4-e5f6-7890-abcd-ef1234567890","name":"Penrith Beacon WCP Dark","builtin":True,"vars":{"--bg":"#0d1117","--surface":"#161b22","--surface2":"#1c2128","--border":"#30363d","--text":"#e6edf3","--muted":"#8b949e","--accent":"#f0883e","--green":"#3fb950","--red":"#f85149","--yellow":"#d29922","--blue":"#58a6ff","--radius":"8px","--shadow":"0 4px 16px rgba(0,0,0,.45)"}},
  {"id":"pb-wcp-light","uuid":"b2c3d4e5-f6a7-8901-bcde-f12345678901","name":"Penrith Beacon WCP Light","builtin":True,"vars":{"--bg":"#ffffff","--surface":"#f6f8fa","--surface2":"#eaeef2","--border":"#d0d7de","--text":"#1f2328","--muted":"#636c76","--accent":"#f0883e","--green":"#1a7f37","--red":"#cf222e","--yellow":"#9a6700","--blue":"#0969da","--radius":"8px","--shadow":"0 4px 8px rgba(0,0,0,.12)"}},
  {"id":"pb-wcp-hc","uuid":"c3d4e5f6-a7b8-9012-cdef-123456789012","name":"Penrith Beacon WCP High Contrast","builtin":True,"vars":{"--bg":"#000000","--surface":"#0d0d0d","--surface2":"#1a1a1a","--border":"#ffffff","--text":"#ffffff","--muted":"#cccccc","--accent":"#ff8c00","--green":"#00ff41","--red":"#ff3333","--yellow":"#ffff00","--blue":"#00b4ff","--radius":"4px","--shadow":"none"}},
]

WCP_MANIFEST = {
  "wcp":"1.3.1","name":"WCP Theme Studio","version":"1.3.0",
  "description":"Gallery of 15 built-in themes + custom theme editor. Includes the 3 Penrith Beacon WCP native themes. Each theme shareable as a .pbtheme.json URL.",
  "icon":"/widget/icon.svg","health":"/widget/health",
  "components":[
    {"id":"theme-studio","uuid":"e27a9086-89ee-498f-98e7-cebd7efb73c9","name":"WCP Theme Studio","role":"widget","path":"/widget/","icon":"/widget/icon.svg","renderMode":"iframe","defaultSize":{"w":6,"h":4}}
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

# ── WCP endpoints ─────────────────────────────────────────────────────────────

@app.route('/widget/')
@app.route('/widget/index.html')
def widget(): return render_template('widget.html', themes=all_themes(), manifest=WCP_MANIFEST, wcp_instance_id=request.headers.get('Wcp-Instance-Id',''))

@app.route('/widget/wcp')
def wcp(): return jsonify(WCP_MANIFEST)

@app.route('/widget/manifest')
def manifest():
    m = WCP_MANIFEST
    return jsonify({k:m[k] for k in ['wcp','name','version','description','icon','health','widget']})

@app.route('/widget/health')
def health(): return jsonify({"status":"ok","name":"WCP Theme Studio"})

@app.route('/widget/full')
def full(): return render_template('full.html', themes=all_themes(), manifest=WCP_MANIFEST, wcp_instance_id=request.headers.get('Wcp-Instance-Id',''))

@app.route('/widget/icon.svg')
def icon():
    svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <path fill="#f0883e" d="M15.825.12a.5.5 0 0 1 .132.584c-1.53 3.43-4.743 8.17-7.095 10.64a6.067 6.067 0 0 1-2.373 1.534c-.018.227-.06.538-.16.868-.201.659-.667 1.479-1.708 1.74a8.118 8.118 0 0 1-3.078.132 3.659 3.659 0 0 1-.562-.135 1.382 1.382 0 0 1-.466-.247.714.714 0 0 1-.204-.288.622.622 0 0 1 .004-.443c.095-.245.316-.38.461-.452.394-.197.625-.453.867-.826.095-.144.184-.297.287-.472l.117-.198c.151-.255.326-.54.546-.848.528-.739 1.153-.926 1.616-.896.765.05 1.313.548 1.562 1.237a5.83 5.83 0 0 1 1.616-1.128c2.353-2.454 5.557-7.187 7.09-10.62.133-.3.438-.42.728-.32z"/>
</svg>"""
    return Response(svg, mimetype='image/svg+xml')

# ── Theme file endpoint ────────────────────────────────────────────────────────

@app.route('/widget/themes/<theme_id>.pbtheme.json')
def get_theme_file(theme_id):
    theme = next((t for t in all_themes() if t['id'] == theme_id), None)
    if not theme: return jsonify({"error":"not found"}), 404
    payload = {"uuid": theme.get('uuid', str(uuid_lib.uuid4())),
               "name": theme['name'], "vars": theme['vars']}
    resp = Response(json.dumps(payload, indent=2), mimetype='application/json')
    resp.headers['Content-Disposition'] = f'attachment; filename="{theme_id}.pbtheme.json"'
    return resp

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
