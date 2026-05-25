WEB_UI_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Pixora Creative Engine</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f7fb;
      --panel: #ffffff;
      --panel-2: #f0f3f8;
      --text: #18202f;
      --muted: #617084;
      --line: #d9e0ea;
      --accent: #ff4b4b;
      --accent-dark: #d93636;
      --blue: #2563eb;
      --ok: #0f9f6e;
      --warn: #b7791f;
      --danger: #c53030;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    header {
      background: var(--panel);
      border-bottom: 1px solid var(--line);
      padding: 22px 28px;
      display: flex;
      justify-content: space-between;
      gap: 20px;
      align-items: flex-start;
    }
    h1, h2, h3 { margin: 0; letter-spacing: 0; }
    h1 { font-size: clamp(2rem, 4vw, 3.5rem); line-height: 1.05; }
    h2 { font-size: 1.4rem; margin-bottom: 14px; }
    h3 { font-size: 1rem; margin-bottom: 8px; }
    p { color: var(--muted); line-height: 1.55; }
    a { color: var(--blue); text-decoration: none; }
    .status {
      min-width: 190px;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel-2);
      color: var(--muted);
      font-size: 0.92rem;
    }
    .dot {
      display: inline-block;
      width: 9px;
      height: 9px;
      margin-right: 8px;
      border-radius: 50%;
      background: var(--ok);
    }
    .shell {
      display: grid;
      grid-template-columns: 280px minmax(0, 1fr);
      min-height: calc(100vh - 108px);
    }
    aside {
      background: var(--panel);
      border-right: 1px solid var(--line);
      padding: 22px;
    }
    main {
      width: min(1180px, 100%);
      padding: 24px;
    }
    .about {
      border-radius: 8px;
      background: #e8f2ff;
      color: #254061;
      padding: 12px;
      margin-top: 16px;
      font-size: 0.92rem;
      line-height: 1.5;
    }
    .tabs {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      border-bottom: 1px solid var(--line);
      margin-bottom: 22px;
    }
    .tab {
      border: 0;
      border-bottom: 3px solid transparent;
      background: transparent;
      color: var(--muted);
      padding: 12px 14px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }
    .tab.active {
      color: var(--accent);
      border-color: var(--accent);
    }
    .view { display: none; }
    .view.active { display: block; }
    .card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 18px;
      margin-bottom: 16px;
    }
    .row {
      display: grid;
      grid-template-columns: minmax(0, 2fr) minmax(0, 1fr);
      gap: 16px;
    }
    .two {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }
    .three {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
    }
    label {
      display: block;
      margin: 12px 0 7px;
      color: var(--muted);
      font-size: 0.92rem;
      font-weight: 650;
    }
    input, textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: #ffffff;
      color: var(--text);
      padding: 11px 12px;
      font: inherit;
      outline: none;
    }
    textarea { min-height: 132px; resize: vertical; }
    input:focus, textarea:focus { border-color: var(--accent); }
    button.primary, button.secondary {
      border: 0;
      border-radius: 7px;
      padding: 11px 14px;
      font: inherit;
      font-weight: 750;
      cursor: pointer;
    }
    button.primary {
      width: 100%;
      margin-top: 38px;
      background: var(--accent);
      color: white;
    }
    button.primary:hover { background: var(--accent-dark); }
    button.secondary {
      background: var(--panel-2);
      color: var(--text);
      border: 1px solid var(--line);
    }
    button:disabled { opacity: 0.65; cursor: wait; }
    .metric {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      background: var(--panel);
    }
    .metric span {
      display: block;
      color: var(--muted);
      font-size: 0.84rem;
      margin-bottom: 6px;
    }
    .metric strong { font-size: 1.15rem; overflow-wrap: anywhere; }
    .notice {
      border-radius: 8px;
      padding: 12px;
      margin: 12px 0;
      background: #fff8e6;
      color: #6f4b08;
      border: 1px solid #f1d28a;
    }
    .success {
      background: #e8f8f1;
      color: #075f42;
      border-color: #a4e5ca;
    }
    .error {
      background: #fff0f0;
      color: var(--danger);
      border-color: #f5b5b5;
    }
    .result-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }
    ul { margin: 8px 0 0; padding-left: 20px; color: var(--muted); }
    li { margin: 5px 0; }
    pre {
      background: #111827;
      color: #d7e0ee;
      border-radius: 8px;
      padding: 14px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
    }
    .palette {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 8px;
    }
    .swatch {
      width: 34px;
      height: 34px;
      border-radius: 8px;
      border: 1px solid var(--line);
    }
    .image-tile img {
      width: 100%;
      border-radius: 8px;
      border: 1px solid var(--line);
      background: var(--panel-2);
    }
    .muted { color: var(--muted); }
    .hidden { display: none; }
    @media (max-width: 900px) {
      header, .shell, .row, .two, .three, .result-grid { display: block; }
      aside { border-right: 0; border-bottom: 1px solid var(--line); }
      button.primary { margin-top: 16px; }
      .card, .metric { margin-bottom: 12px; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Pixora Creative Engine</h1>
      <p>AI-powered product creative generation for ecommerce brands.</p>
    </div>
    <div class="status"><span class="dot"></span><span id="health">Checking backend...</span></div>
  </header>

  <div class="shell">
    <aside>
      <h3>Settings</h3>
      <label for="api-base">API Base URL</label>
      <input id="api-base" value="" placeholder="Same deployment" />
      <div class="about">
        <strong>About</strong><br />
        Pixora generates product data, creative strategy, image prompts, video scripts, and quality checks.
      </div>
      <div class="about">
        <strong>Local Streamlit</strong><br />
        The original UI still runs locally with:<br />
        <code>streamlit run frontend/app.py</code>
      </div>
    </aside>

    <main>
      <nav class="tabs">
        <button class="tab active" data-tab="generate">Generate</button>
        <button class="tab" data-tab="bulk">Bulk Upload</button>
        <button class="tab" data-tab="dashboard">Dashboard</button>
        <button class="tab" data-tab="docs">API Docs</button>
      </nav>

      <section id="generate" class="view active">
        <h2>Generate Creatives for Single Product</h2>
        <div class="card">
          <form id="generate-form">
            <div class="row">
              <div>
                <label for="url">Product URL</label>
                <input id="url" type="url" placeholder="https://example.com/product" required />
              </div>
              <div>
                <button id="submit" class="primary" type="submit">Generate</button>
              </div>
            </div>
            <div class="two">
              <div>
                <label for="brand">Brand Override (optional)</label>
                <input id="brand" type="text" placeholder="Custom Brand Name" />
              </div>
              <div>
                <label for="audience">Target Audience (optional)</label>
                <input id="audience" type="text" placeholder="e.g., Young professionals" />
              </div>
            </div>
          </form>
        </div>
        <div id="generate-status"></div>
        <div id="result" class="hidden"></div>
      </section>

      <section id="bulk" class="view">
        <h2>Bulk Processing - Upload CSV</h2>
        <div class="card">
          <p>Upload a CSV file with product URLs. Supported columns: <code>url</code>, <code>brand_override</code>, <code>target_audience</code>, <code>custom_themes</code>.</p>
          <label for="csv-file">CSV file</label>
          <input id="csv-file" type="file" accept=".csv,text/csv" />
          <button id="bulk-submit" class="secondary" type="button">Start Batch Processing</button>
        </div>
        <div id="bulk-status"></div>
      </section>

      <section id="dashboard" class="view">
        <h2>Processing Dashboard</h2>
        <div class="three">
          <div class="metric"><span>Backend</span><strong id="dash-health">Checking...</strong></div>
          <div class="metric"><span>Model</span><strong id="dash-model">-</strong></div>
          <div class="metric"><span>Groq API</span><strong id="dash-groq">-</strong></div>
        </div>
        <div class="card">
          <button id="refresh-health" class="secondary" type="button">Refresh Status</button>
          <p class="muted">Active job tracking is in-memory on this deployment. Serverless instances may not preserve jobs between cold starts.</p>
        </div>
      </section>

      <section id="docs" class="view">
        <h2>API Documentation</h2>
        <div class="card">
          <h3>Single Product Generation</h3>
          <pre>POST /api/v1/generate
{
  "url": "https://product-url.com",
  "brand_override": "Brand Name",
  "target_audience": "Target Description",
  "custom_themes": ["modern", "minimalist"]
}</pre>
        </div>
        <div class="card">
          <h3>Bulk Processing</h3>
          <pre>POST /api/v1/bulk-generate
CSV columns:
url,brand_override,target_audience,custom_themes</pre>
        </div>
        <div class="card">
          <a href="/docs">Open Swagger Docs</a> &nbsp; <a href="/health">Health Check</a> &nbsp; <a href="/openapi.json">OpenAPI JSON</a>
        </div>
      </section>
    </main>
  </div>

  <script>
    const apiBaseInput = document.getElementById("api-base");
    apiBaseInput.value = window.location.origin;

    const tabs = document.querySelectorAll(".tab");
    const views = document.querySelectorAll(".view");
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        tabs.forEach((item) => item.classList.remove("active"));
        views.forEach((item) => item.classList.remove("active"));
        tab.classList.add("active");
        document.getElementById(tab.dataset.tab).classList.add("active");
      });
    });

    function apiBase() {
      return apiBaseInput.value.replace(/\\/$/, "") || window.location.origin;
    }

    function escapeHtml(value) {
      return String(value || "").replace(/[<>&]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[c]));
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
        healthEl.textContent = data.status === "healthy" ? "Backend API is running" : "Backend online";
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
        ${notice("Creatives generated successfully.", "success")}
        <div class="three">
          <div class="metric"><span>Title</span><strong>${escapeHtml(product.title || "N/A")}</strong></div>
          <div class="metric"><span>Price</span><strong>${escapeHtml(product.price ? `${product.currency || "USD"} ${product.price}` : "N/A")}</strong></div>
          <div class="metric"><span>Brand</span><strong>${escapeHtml(product.brand || "N/A")}</strong></div>
        </div>

        <div class="card">
          <h3>Product Information</h3>
          <p>${escapeHtml(product.description || "No product description returned.")}</p>
          ${product.short_summary ? `<p><strong>Summary:</strong> ${escapeHtml(product.short_summary)}</p>` : ""}
          <h3>Key Features</h3>
          ${listItems(product.features || [])}
        </div>

        <div class="two">
          <div class="card">
            <h3>Creative Strategy</h3>
            <p><strong>Target Audience:</strong> ${escapeHtml(brief.target_audience || "N/A")}</p>
            <h3>Visual Themes</h3>
            ${listItems(brief.visual_themes || [])}
            <h3>Color Palette</h3>
            <div class="palette">${palette.map((color) => `<span class="swatch" title="${escapeHtml(color)}" style="background:${escapeHtml(color)}"></span>`).join("") || "<p class='muted'>No palette returned.</p>"}</div>
          </div>
          <div class="card">
            <h3>Marketing Hooks</h3>
            ${listItems(brief.hooks || [])}
            <h3>Marketing Angles</h3>
            ${listItems(brief.marketing_angles || [])}
          </div>
        </div>

        <div class="card">
          <h3>Generated Images</h3>
          <div class="result-grid">
            ${images.map((image, idx) => `
              <div class="image-tile card">
                <h3>Image ${idx + 1}</h3>
                ${image.url ? `<img src="${escapeHtml(image.url)}" alt="Generated image ${idx + 1}" />` : ""}
                <p>${escapeHtml((image.prompt || "").slice(0, 180))}</p>
                <p class="muted">Quality: ${Math.round((image.quality_score || 0) * 100)}%</p>
              </div>
            `).join("") || "<p class='muted'>No images generated.</p>"}
          </div>
        </div>

        <div class="card">
          <h3>Generated Videos</h3>
          ${videos.map((video, idx) => `<p><strong>Video ${idx + 1}:</strong> ${escapeHtml(video.script || "")}</p>`).join("") || "<p class='muted'>No videos generated.</p>"}
        </div>

        <div class="three">
          <div class="metric"><span>Overall Quality</span><strong>${Math.round((review.overall_quality || 0) * 100)}%</strong></div>
          <div class="metric"><span>Accuracy</span><strong>${Math.round((review.hallucination_score || 0) * 100)}%</strong></div>
          <div class="metric"><span>Consistency</span><strong>${Math.round((review.consistency_score || 0) * 100)}%</strong></div>
        </div>
        <div class="card">
          <h3>Suggestions</h3>
          ${listItems(review.suggestions || [])}
        </div>
      `;
    }

    document.getElementById("generate-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const status = document.getElementById("generate-status");
      const submit = document.getElementById("submit");
      const result = document.getElementById("result");
      submit.disabled = true;
      status.innerHTML = notice("Generating creatives. This can take a little while on serverless.");
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
      status.innerHTML = notice("Uploading batch...");
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
