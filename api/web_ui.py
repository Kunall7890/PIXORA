WEB_UI_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Pixora - Creative Engine</title>
  <style>
    :root {
      color-scheme: dark;
      --ink: #f7f4ed;
      --ink-2: #c9c3b7;
      --muted: #878276;
      --paper: #10100e;
      --paper-2: #171713;
      --paper-3: #202017;
      --line: rgba(247, 244, 237, 0.14);
      --line-strong: rgba(247, 244, 237, 0.28);
      --red: #ff4f3e;
      --mint: #70f0b4;
      --cyan: #75d8ff;
      --amber: #ffcf5a;
      --violet: #b99cff;
      --shadow: 0 28px 90px rgba(0, 0, 0, 0.42);
    }

    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px),
        linear-gradient(0deg, rgba(255,255,255,0.03) 1px, transparent 1px),
        radial-gradient(circle at 28% 12%, rgba(255, 79, 62, 0.16), transparent 28rem),
        radial-gradient(circle at 72% 20%, rgba(112, 240, 180, 0.12), transparent 30rem),
        var(--paper);
      background-size: 72px 72px, 72px 72px, auto, auto, auto;
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAQAAAAECAYAAACp8Z5+AAAAHUlEQVR42mP8z8BQz0AEYBxVSFJgYGBgYGBgAAA8cQR7McBHYwAAAABJRU5ErkJggg==");
      opacity: 0.09;
      mix-blend-mode: screen;
    }

    a { color: inherit; text-decoration: none; }
    button, input, textarea { font: inherit; }
    button { cursor: pointer; }
    code { color: var(--mint); }

    .app-shell {
      width: min(1440px, 100%);
      margin: 0 auto;
      min-height: 100vh;
      padding: 18px;
    }

    .topbar {
      position: sticky;
      top: 0;
      z-index: 20;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      padding: 14px 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(16, 16, 14, 0.78);
      backdrop-filter: blur(18px);
      box-shadow: 0 18px 40px rgba(0, 0, 0, 0.28);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 180px;
    }

    .mark {
      width: 38px;
      height: 38px;
      border-radius: 8px;
      display: grid;
      place-items: center;
      color: #140c09;
      font-weight: 900;
      background:
        linear-gradient(135deg, var(--red), var(--amber) 48%, var(--mint));
      box-shadow: 0 12px 34px rgba(255, 79, 62, 0.28);
    }

    .brand strong {
      display: block;
      font-size: 1rem;
      letter-spacing: 0;
    }

    .brand span {
      display: block;
      color: var(--muted);
      font-size: 0.78rem;
    }

    .top-actions {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .health-pill, .text-link {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 36px;
      padding: 8px 10px;
      border-radius: 8px;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.045);
      color: var(--ink-2);
      font-size: 0.86rem;
    }

    .pulse {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--mint);
      box-shadow: 0 0 0 5px rgba(112, 240, 180, 0.12);
    }

    .workspace {
      display: grid;
      grid-template-columns: 310px minmax(0, 1fr);
      gap: 18px;
      margin-top: 18px;
    }

    .sidebar {
      align-self: start;
      position: sticky;
      top: 92px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(23, 23, 19, 0.84);
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    .sidebar-section {
      padding: 18px;
      border-bottom: 1px solid var(--line);
    }

    .sidebar-section:last-child { border-bottom: 0; }

    .kicker {
      margin: 0 0 8px;
      color: var(--red);
      font-size: 0.78rem;
      font-weight: 800;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }

    .sidebar h2 {
      margin: 0;
      font-size: 1.45rem;
      line-height: 1.1;
      letter-spacing: 0;
    }

    .sidebar p, .muted {
      color: var(--muted);
      line-height: 1.58;
    }

    label {
      display: block;
      margin: 14px 0 8px;
      color: var(--ink-2);
      font-size: 0.82rem;
      font-weight: 750;
    }

    input, textarea {
      width: 100%;
      min-height: 44px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.055);
      color: var(--ink);
      outline: none;
      padding: 11px 12px;
      transition: border-color 160ms ease, background 160ms ease, box-shadow 160ms ease;
    }

    textarea {
      min-height: 132px;
      resize: vertical;
    }

    input:focus, textarea:focus {
      border-color: rgba(117, 216, 255, 0.75);
      background: rgba(255, 255, 255, 0.085);
      box-shadow: 0 0 0 4px rgba(117, 216, 255, 0.1);
    }

    .micro-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-top: 14px;
    }

    .micro-card {
      min-height: 78px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.042);
      padding: 12px;
    }

    .micro-card strong {
      display: block;
      font-size: 1.25rem;
    }

    .micro-card span {
      color: var(--muted);
      font-size: 0.78rem;
    }

    .tabs {
      display: grid;
      gap: 8px;
    }

    .tab {
      width: 100%;
      border: 1px solid transparent;
      border-radius: 8px;
      background: transparent;
      color: var(--ink-2);
      padding: 11px 12px;
      text-align: left;
      font-weight: 780;
      transition: 150ms ease;
    }

    .tab:hover {
      color: var(--ink);
      background: rgba(255, 255, 255, 0.052);
    }

    .tab.active {
      color: var(--ink);
      border-color: var(--line-strong);
      background: linear-gradient(135deg, rgba(255, 79, 62, 0.2), rgba(255, 207, 90, 0.09));
    }

    .canvas {
      min-width: 0;
      display: grid;
      gap: 18px;
    }

    .hero {
      position: relative;
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(320px, 430px);
      align-items: end;
      gap: 28px;
      overflow: hidden;
      min-height: 520px;
      padding: clamp(28px, 5vw, 72px);
      border: 1px solid var(--line);
      border-radius: 8px;
      background:
        linear-gradient(90deg, rgba(16, 16, 14, 0.96), rgba(16, 16, 14, 0.55), rgba(16, 16, 14, 0.78)),
        url("https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1800&q=82") center / cover;
      box-shadow: var(--shadow);
    }

    .hero::after {
      content: "";
      position: absolute;
      inset: auto 0 0;
      height: 38%;
      background: linear-gradient(0deg, rgba(16,16,14,1), transparent);
      pointer-events: none;
    }

    .hero-content {
      position: relative;
      z-index: 2;
      width: 100%;
      padding: 0;
    }

    .hero h1 {
      margin: 0;
      font-size: clamp(3rem, 6vw, 5.15rem);
      line-height: 0.88;
      letter-spacing: 0;
      max-width: 7.2ch;
    }

    .hero-copy {
      max-width: 650px;
      margin: 18px 0 0;
      color: var(--ink-2);
      font-size: clamp(1rem, 1.6vw, 1.22rem);
    }

    .hero-actions {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 28px;
    }

    .button-primary, .button-secondary {
      min-height: 46px;
      border-radius: 8px;
      border: 1px solid transparent;
      padding: 12px 16px;
      font-weight: 870;
      transition: transform 160ms ease, background 160ms ease, border-color 160ms ease;
    }

    .button-primary {
      background: var(--red);
      color: #fff;
      box-shadow: 0 18px 42px rgba(255, 79, 62, 0.26);
    }

    .button-secondary {
      background: rgba(255, 255, 255, 0.07);
      color: var(--ink);
      border-color: var(--line-strong);
    }

    .button-primary:hover, .button-secondary:hover { transform: translateY(-1px); }
    .button-primary:disabled { opacity: 0.62; cursor: wait; transform: none; }

    .studio-card {
      position: relative;
      right: auto;
      bottom: auto;
      z-index: 3;
      width: 100%;
      border: 1px solid var(--line-strong);
      border-radius: 8px;
      background: rgba(247, 244, 237, 0.08);
      backdrop-filter: blur(18px);
      box-shadow: 0 22px 80px rgba(0,0,0,0.35);
      overflow: hidden;
    }

    .studio-media {
      aspect-ratio: 16 / 9;
      background:
        linear-gradient(135deg, rgba(255, 79, 62, 0.2), rgba(112, 240, 180, 0.08)),
        url("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80") center / cover;
    }

    .studio-body {
      padding: 14px;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: center;
    }

    .studio-body strong { display: block; }
    .studio-body span { color: var(--ink-2); font-size: 0.85rem; }
    .score {
      width: 58px;
      height: 58px;
      border-radius: 50%;
      display: grid;
      place-items: center;
      background: conic-gradient(var(--mint) 86%, rgba(255,255,255,0.18) 0);
      color: #07120d;
      font-weight: 900;
    }

    .view { display: none; }
    .view.active { display: grid; gap: 18px; }

    .panel {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(23, 23, 19, 0.86);
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    .panel-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 14px;
      padding: 18px;
      border-bottom: 1px solid var(--line);
    }

    .panel-head h2 {
      margin: 0;
      font-size: clamp(1.35rem, 3vw, 2.2rem);
      letter-spacing: 0;
    }

    .panel-body { padding: 18px; }

    .form-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(280px, 0.7fr);
      gap: 18px;
      align-items: start;
    }

    .launch-pad {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      background:
        linear-gradient(135deg, rgba(112,240,180,0.1), rgba(117,216,255,0.08)),
        rgba(255,255,255,0.04);
    }

    .launch-pad button { width: 100%; margin-top: 14px; }

    .checklist {
      display: grid;
      gap: 10px;
      margin-top: 14px;
    }

    .check {
      display: flex;
      gap: 10px;
      color: var(--ink-2);
      font-size: 0.9rem;
    }

    .check::before {
      content: "";
      width: 16px;
      height: 16px;
      flex: 0 0 16px;
      margin-top: 2px;
      border-radius: 50%;
      background: var(--mint);
      box-shadow: inset 0 0 0 5px #173525;
    }

    .notice {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 13px 14px;
      background: rgba(255, 207, 90, 0.1);
      color: #ffe2a0;
    }

    .notice.success {
      background: rgba(112, 240, 180, 0.1);
      color: #b7ffd9;
    }

    .notice.error {
      background: rgba(255, 79, 62, 0.11);
      color: #ffb6ad;
    }

    .result-grid, .two-col, .three-col {
      display: grid;
      gap: 14px;
    }

    .result-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .two-col { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .three-col { grid-template-columns: repeat(3, minmax(0, 1fr)); }

    .metric, .result-card, .doc-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.045);
      padding: 15px;
    }

    .metric span {
      display: block;
      color: var(--muted);
      font-size: 0.78rem;
      margin-bottom: 7px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .metric strong {
      display: block;
      color: var(--ink);
      font-size: clamp(1rem, 1.5vw, 1.25rem);
      overflow-wrap: anywhere;
    }

    .result-card h3, .doc-card h3 {
      margin: 0 0 10px;
      font-size: 1rem;
    }

    ul {
      margin: 8px 0 0;
      padding-left: 18px;
      color: var(--ink-2);
    }

    li { margin: 6px 0; }

    .palette {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 10px;
    }

    .swatch {
      width: 38px;
      height: 38px;
      border-radius: 8px;
      border: 1px solid rgba(255,255,255,0.2);
      box-shadow: inset 0 0 0 1px rgba(0,0,0,0.12);
    }

    .image-tile {
      padding: 0;
      overflow: hidden;
    }

    .image-tile img {
      width: 100%;
      aspect-ratio: 1 / 1;
      object-fit: cover;
      display: block;
      background: var(--paper-3);
    }

    .image-tile div { padding: 13px; }

    pre {
      margin: 0;
      border-radius: 8px;
      border: 1px solid var(--line);
      background: #080807;
      color: #d9f4e8;
      padding: 14px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .empty-state {
      min-height: 240px;
      display: grid;
      place-items: center;
      text-align: center;
      color: var(--muted);
    }

    .hidden { display: none; }

    @media (max-width: 1100px) {
      .workspace { grid-template-columns: 1fr; }
      .sidebar { position: static; }
      .canvas { order: 1; }
      .sidebar { order: 2; }
      .tabs { grid-template-columns: repeat(4, minmax(0, 1fr)); }
      .tab { text-align: center; }
    }

    @media (max-width: 760px) {
      .app-shell { padding: 10px; }
      .topbar, .hero-actions, .panel-head { display: block; }
      .top-actions { justify-content: flex-start; margin-top: 12px; }
      .hero { display: block; min-height: auto; padding: 28px; }
      .hero-content { width: 100%; padding: 0; }
      .hero h1 { font-size: 3.2rem; }
      .studio-card { margin-top: 18px; }
      .tabs, .form-grid, .result-grid, .two-col, .three-col, .micro-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="app-shell">
    <header class="topbar">
      <a class="brand" href="/">
        <div class="mark">P</div>
        <div>
          <strong>Pixora</strong>
          <span>Creative Engine</span>
        </div>
      </a>
      <div class="top-actions">
        <div class="health-pill"><span class="pulse"></span><span id="health">Checking backend...</span></div>
        <a class="text-link" href="/docs">API Docs</a>
        <a class="text-link" href="/health">Health</a>
      </div>
    </header>

    <div class="workspace">
      <aside class="sidebar">
        <div class="sidebar-section">
          <p class="kicker">Senior creative pipeline</p>
          <h2>Turn product URLs into launch-ready ad systems.</h2>
          <p>Research, positioning, prompts, scripts, and QA in one fast workspace.</p>
          <label for="api-base">API Base URL</label>
          <input id="api-base" value="" placeholder="Same deployment" />
        </div>
        <div class="sidebar-section">
          <nav class="tabs" aria-label="Pixora sections">
            <button class="tab active" data-tab="generate">Generate</button>
            <button class="tab" data-tab="bulk">Bulk Upload</button>
            <button class="tab" data-tab="dashboard">Dashboard</button>
            <button class="tab" data-tab="docs">API Docs</button>
          </nav>
        </div>
        <div class="sidebar-section">
          <div class="micro-grid">
            <div class="micro-card"><strong>5</strong><span>image concepts</span></div>
            <div class="micro-card"><strong>2</strong><span>video scripts</span></div>
            <div class="micro-card"><strong>7</strong><span>agent stages</span></div>
            <div class="micro-card"><strong>QA</strong><span>brand checks</span></div>
          </div>
        </div>
        <div class="sidebar-section">
          <p class="muted">The original local UI is still available with <code>streamlit run frontend/app.py</code>. This Vercel surface is a premium web version of the same workflow.</p>
        </div>
      </aside>

      <main class="canvas">
        <section class="hero">
          <div class="hero-content">
            <p class="kicker">Commerce creative that sells</p>
            <h1>From URL to ads.</h1>
            <p class="hero-copy">Drop in a product page and Pixora builds the strategy, visual language, prompt system, scripts, and creative review your team needs before launch.</p>
            <div class="hero-actions">
              <button class="button-primary" type="button" data-jump="generate">Generate creatives</button>
              <button class="button-secondary" type="button" data-jump="docs">View API</button>
            </div>
          </div>
          <div class="studio-card" aria-label="Creative preview">
            <div class="studio-media"></div>
            <div class="studio-body">
              <div>
                <strong>Creative readiness</strong>
                <span>Product truth, hooks, visuals, scripts, QA</span>
              </div>
              <div class="score">86</div>
            </div>
          </div>
        </section>

        <section id="generate" class="view active">
          <div class="panel">
            <div class="panel-head">
              <div>
                <p class="kicker">Generate</p>
                <h2>Build a full creative package.</h2>
              </div>
              <p class="muted">Best with public ecommerce product pages.</p>
            </div>
            <div class="panel-body">
              <form id="generate-form" class="form-grid">
                <div>
                  <label for="url">Product URL</label>
                  <input id="url" type="url" placeholder="https://example.com/product" required />
                  <div class="two-col">
                    <div>
                      <label for="brand">Brand Override</label>
                      <input id="brand" type="text" placeholder="Optional brand name" />
                    </div>
                    <div>
                      <label for="audience">Target Audience</label>
                      <input id="audience" type="text" placeholder="e.g. performance-focused founders" />
                    </div>
                  </div>
                </div>
                <div class="launch-pad">
                  <p class="kicker">Launch pad</p>
                  <h3>What Pixora returns</h3>
                  <div class="checklist">
                    <div class="check">Product data and enriched description</div>
                    <div class="check">Creative hooks, angles, audience, palette</div>
                    <div class="check">Image prompts, video scripts, QA scoring</div>
                  </div>
                  <button id="submit" class="button-primary" type="submit">Generate package</button>
                </div>
              </form>
              <div id="generate-status" style="margin-top:14px"></div>
            </div>
          </div>
          <div id="result" class="hidden"></div>
        </section>

        <section id="bulk" class="view">
          <div class="panel">
            <div class="panel-head">
              <div>
                <p class="kicker">Bulk Upload</p>
                <h2>Process a catalog, not just one product.</h2>
              </div>
            </div>
            <div class="panel-body">
              <div class="two-col">
                <div>
                  <label for="csv-file">CSV file</label>
                  <input id="csv-file" type="file" accept=".csv,text/csv" />
                  <p class="muted">Columns: <code>url</code>, <code>brand_override</code>, <code>target_audience</code>, <code>custom_themes</code>.</p>
                </div>
                <div class="launch-pad">
                  <h3>Batch run</h3>
                  <p class="muted">Upload and queue a set of product pages for creative generation.</p>
                  <button id="bulk-submit" class="button-secondary" type="button">Start batch processing</button>
                </div>
              </div>
              <div id="bulk-status" style="margin-top:14px"></div>
            </div>
          </div>
        </section>

        <section id="dashboard" class="view">
          <div class="panel">
            <div class="panel-head">
              <div>
                <p class="kicker">Dashboard</p>
                <h2>Deployment health and creative engine status.</h2>
              </div>
              <button id="refresh-health" class="button-secondary" type="button">Refresh</button>
            </div>
            <div class="panel-body">
              <div class="three-col">
                <div class="metric"><span>Backend</span><strong id="dash-health">Checking...</strong></div>
                <div class="metric"><span>Groq Model</span><strong id="dash-model">-</strong></div>
                <div class="metric"><span>Groq API</span><strong id="dash-groq">-</strong></div>
              </div>
              <p class="muted">Serverless instances may reset in-memory jobs between cold starts. For production queue durability, connect Redis or a database.</p>
            </div>
          </div>
        </section>

        <section id="docs" class="view">
          <div class="panel">
            <div class="panel-head">
              <div>
                <p class="kicker">API Docs</p>
                <h2>Integrate Pixora anywhere.</h2>
              </div>
              <a class="text-link" href="/docs">Open Swagger</a>
            </div>
            <div class="panel-body two-col">
              <div class="doc-card">
                <h3>Single Product Generation</h3>
                <pre>POST /api/v1/generate
{
  "url": "https://product-url.com",
  "brand_override": "Brand Name",
  "target_audience": "Target Description",
  "custom_themes": ["modern", "minimalist"]
}</pre>
              </div>
              <div class="doc-card">
                <h3>Bulk Processing</h3>
                <pre>POST /api/v1/bulk-generate

CSV columns:
url,brand_override,target_audience,custom_themes</pre>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>

  <script>
    const apiBaseInput = document.getElementById("api-base");
    apiBaseInput.value = window.location.origin;

    const tabs = document.querySelectorAll(".tab");
    const views = document.querySelectorAll(".view");
    const jumpers = document.querySelectorAll("[data-jump]");

    function setTab(name) {
      tabs.forEach((item) => item.classList.toggle("active", item.dataset.tab === name));
      views.forEach((item) => item.classList.toggle("active", item.id === name));
      document.getElementById(name)?.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    tabs.forEach((tab) => tab.addEventListener("click", () => setTab(tab.dataset.tab)));
    jumpers.forEach((button) => button.addEventListener("click", () => setTab(button.dataset.jump)));

    function apiBase() {
      return apiBaseInput.value.replace(/\\/$/, "") || window.location.origin;
    }

    function escapeHtml(value) {
      return String(value || "").replace(/[<>&"]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;" }[c]));
    }

    function listItems(items) {
      if (!items || !items.length) return "<p class='muted'>None returned.</p>";
      return "<ul>" + items.map((item) => `<li>${escapeHtml(item)}</li>`).join("") + "</ul>";
    }

    function notice(message, type = "") {
      return `<div class="notice ${type}">${message}</div>`;
    }

    async function refreshHealth() {
      const healthEl = document.getElementById("health");
      const dashHealth = document.getElementById("dash-health");
      const dashModel = document.getElementById("dash-model");
      const dashGroq = document.getElementById("dash-groq");
      try {
        const response = await fetch(`${apiBase()}/health`);
        const data = await response.json();
        healthEl.textContent = data.status === "healthy" ? "Backend online" : "Backend responding";
        dashHealth.textContent = data.status || "online";
        dashModel.textContent = data.groq_model || "-";
        dashGroq.textContent = data.groq_configured ? "Configured" : "Missing";
      } catch (error) {
        healthEl.textContent = "Backend unavailable";
        dashHealth.textContent = "Unavailable";
        dashModel.textContent = "-";
        dashGroq.textContent = "-";
      }
    }

    function renderResults(data) {
      const result = document.getElementById("result");
      result.classList.remove("hidden");
      if (data.status === "failed") {
        result.innerHTML = notice(`Generation failed: ${escapeHtml(data.error || "Unknown error")}`, "error");
        return;
      }

      const product = data.product_data || {};
      const brief = data.creative_brief || {};
      const prompts = data.prompts || {};
      const review = data.critic_review || {};
      const images = data.images || [];
      const videos = data.videos || [];
      const palette = brief.color_palette || [];

      result.innerHTML = `
        ${notice("Creative package generated. Review the launch assets below.", "success")}
        <div class="three-col">
          <div class="metric"><span>Product</span><strong>${escapeHtml(product.title || "N/A")}</strong></div>
          <div class="metric"><span>Price</span><strong>${escapeHtml(product.price ? `${product.currency || "USD"} ${product.price}` : "N/A")}</strong></div>
          <div class="metric"><span>Quality</span><strong>${Math.round((review.overall_quality || 0) * 100)}%</strong></div>
        </div>

        <div class="two-col">
          <div class="result-card">
            <h3>Product Intelligence</h3>
            <p class="muted">${escapeHtml(product.description || "No product description returned.")}</p>
            ${product.short_summary ? `<p><strong>Summary:</strong> ${escapeHtml(product.short_summary)}</p>` : ""}
            <h3>Key Features</h3>
            ${listItems(product.features || [])}
          </div>
          <div class="result-card">
            <h3>Creative Strategy</h3>
            <p><strong>Audience:</strong> ${escapeHtml(brief.target_audience || "N/A")}</p>
            <h3>Hooks</h3>
            ${listItems(brief.hooks || [])}
          </div>
        </div>

        <div class="two-col">
          <div class="result-card">
            <h3>Visual Direction</h3>
            ${listItems(brief.visual_themes || [])}
            <div class="palette">${palette.map((color) => `<span class="swatch" title="${escapeHtml(color)}" style="background:${escapeHtml(color)}"></span>`).join("") || "<p class='muted'>No palette returned.</p>"}</div>
          </div>
          <div class="result-card">
            <h3>Marketing Angles</h3>
            ${listItems(brief.marketing_angles || [])}
          </div>
        </div>

        <div class="result-card">
          <h3>Generated Images</h3>
          <div class="result-grid">
            ${images.map((image, idx) => `
              <div class="result-card image-tile">
                ${image.url ? `<img src="${escapeHtml(image.url)}" alt="Generated image ${idx + 1}" />` : ""}
                <div>
                  <h3>Image ${idx + 1}</h3>
                  <p class="muted">${escapeHtml((image.prompt || "").slice(0, 190))}</p>
                  <p>Quality: ${Math.round((image.quality_score || 0) * 100)}%</p>
                </div>
              </div>
            `).join("") || "<p class='muted'>No images generated.</p>"}
          </div>
        </div>

        <div class="two-col">
          <div class="result-card">
            <h3>Video Scripts</h3>
            ${videos.map((video, idx) => `<p><strong>Video ${idx + 1}:</strong> ${escapeHtml(video.script || "")}</p>`).join("") || "<p class='muted'>No videos generated.</p>"}
          </div>
          <div class="result-card">
            <h3>Quality Review</h3>
            <p><strong>Accuracy:</strong> ${Math.round((review.hallucination_score || 0) * 100)}%</p>
            <p><strong>Consistency:</strong> ${Math.round((review.consistency_score || 0) * 100)}%</p>
            <p><strong>Branding:</strong> ${Math.round((review.branding_score || 0) * 100)}%</p>
            ${listItems(review.suggestions || [])}
          </div>
        </div>
      `;
    }

    document.getElementById("generate-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const status = document.getElementById("generate-status");
      const submit = document.getElementById("submit");
      const result = document.getElementById("result");
      submit.disabled = true;
      status.innerHTML = notice("Building your campaign system. Pixora is researching, positioning, prompting, and reviewing.");
      result.classList.add("hidden");
      try {
        const response = await fetch(`${apiBase()}/api/v1/generate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            url: document.getElementById("url").value,
            brand_override: document.getElementById("brand").value || null,
            target_audience: document.getElementById("audience").value || null
          })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Generation failed");
        status.innerHTML = "";
        renderResults(data);
      } catch (error) {
        status.innerHTML = notice(`Error: ${escapeHtml(error.message)}`, "error");
      } finally {
        submit.disabled = false;
      }
    });

    document.getElementById("bulk-submit").addEventListener("click", async () => {
      const fileInput = document.getElementById("csv-file");
      const status = document.getElementById("bulk-status");
      if (!fileInput.files.length) {
        status.innerHTML = notice("Please choose a CSV file first.", "error");
        return;
      }
      const formData = new FormData();
      formData.append("file", fileInput.files[0]);
      status.innerHTML = notice("Uploading batch and creating the job.");
      try {
        const response = await fetch(`${apiBase()}/api/v1/bulk-generate`, { method: "POST", body: formData });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Batch upload failed");
        status.innerHTML = notice(`Batch job created: ${escapeHtml(data.job_id)} for ${data.total_urls} products.`, "success");
      } catch (error) {
        status.innerHTML = notice(`Error: ${escapeHtml(error.message)}`, "error");
      }
    });

    document.getElementById("refresh-health").addEventListener("click", refreshHealth);
    refreshHealth();
  </script>
</body>
</html>
"""
