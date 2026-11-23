(() => {
  "use strict";
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const state = { dataset: null, inspection: null, analytics: null, charts: null, status: null, report: null, notifications: [] };
  const API = {
    health: "/api/health", status: "/api/status", upload: "/api/upload",
    inspect: "/api/inspect", clean: "/api/clean", analyze: "/api/analyze",
    charts: "/api/visualizations", report: "/api/report"
  };

  function addNotification(message, type = "success") {
    const item = { id: `${Date.now()}-${Math.random()}`, message, type, time: new Date(), read: false };
    state.notifications.unshift(item);
    state.notifications = state.notifications.slice(0, 30);
    renderNotifications();
  }
  function renderNotifications() {
    const list = $("#notification-list");
    const unread = state.notifications.filter(item => !item.read).length;
    $("#notification-dot").classList.toggle("hidden", unread === 0);
    $("#notification-count").textContent = unread ? `${unread} unread notification${unread === 1 ? "" : "s"}` : "You're all caught up";
    list.innerHTML = state.notifications.length ? state.notifications.map(item => `
      <article class="notification-item ${item.read ? "" : "unread"}">
        <span class="notification-symbol">${item.type === "error" ? "!" : "✓"}</span>
        <div><strong>${item.type === "error" ? "NEXUS alert" : "NEXUS update"}</strong><p>${escapeHTML(item.message)}</p><time>${item.time.toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})}</time></div>
      </article>`).join("") : `<div class="notification-empty">No notifications yet.</div>`;
  }
  function togglePopover(panel, button) {
    const willOpen = panel.classList.contains("hidden");
    $("#notification-panel").classList.add("hidden");
    $("#profile-panel").classList.add("hidden");
    $("#notification-button").setAttribute("aria-expanded", "false");
    $("#profile-button").setAttribute("aria-expanded", "false");
    panel.classList.toggle("hidden", !willOpen);
    button.setAttribute("aria-expanded", String(willOpen));
  }
  function toast(message, type = "success") {
    addNotification(message, type);
    const node = document.createElement("div");
    node.className = `toast ${type === "error" ? "error" : ""}`;
    node.textContent = message;
    $("#toast-region").appendChild(node);
    setTimeout(() => node.remove(), 4200);
  }
  function busy(show, title = "Working on your data…", subtitle = "Please wait while NEXUS processes your request.") {
    $("#busy-title").textContent = title;
    $("#busy-subtitle").textContent = subtitle;
    $("#busy-overlay").classList.toggle("hidden", !show);
  }
  async function request(url, options = {}) {
    const response = await fetch(url, options);
    let body;
    try { body = await response.json(); }
    catch { throw new Error(`The server returned an unreadable response (HTTP ${response.status}).`); }
    if (!response.ok || body.success === false) throw new Error(body.error || body.message || `Request failed (HTTP ${response.status}).`);
    return body;
  }
  const post = (url, data = {}) => request(url, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data)
  });
  function showView(name) {
    $$(".view").forEach(v => v.classList.toggle("active", v.id === `view-${name}`));
    $$(".nav-item").forEach(b => b.classList.toggle("active", b.dataset.view === name));
    const label = $(`.nav-item[data-view="${name}"]`)?.textContent.trim() || "Overview";
    $("#breadcrumb-current").textContent = label;
    $("#sidebar").classList.remove("open");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, ch => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[ch]));
  }
  function isTable(value) {
    return value && typeof value === "object" && Array.isArray(value.columns) && Array.isArray(value.data);
  }
  function renderTable(value) {
    if (!isTable(value)) return `<pre>${escapeHTML(JSON.stringify(value, null, 2))}</pre>`;
    const cols = value.columns;
    const rows = value.data || [];
    if (!cols.length) return `<p class="muted">No records to display.</p>`;
    return `<div class="table-wrap"><table class="data-table"><thead><tr>${cols.map(c => `<th>${escapeHTML(c)}</th>`).join("")}</tr></thead><tbody>${rows.slice(0, 100).map(row => `<tr>${cols.map(c => `<td>${escapeHTML(row?.[c] ?? "—")}</td>`).join("")}</tr>`).join("")}</tbody></table>${rows.length > 100 ? `<p class="muted">Showing 100 of ${rows.length} rows.</p>` : ""}</div>`;
  }
  function renderValue(value) {
    if (isTable(value)) return renderTable(value);
    if (Array.isArray(value)) {
      if (!value.length) return `<p class="muted">No results.</p>`;
      if (value.every(x => x && typeof x === "object" && !Array.isArray(x))) {
        const keys = [...new Set(value.flatMap(x => Object.keys(x)))];
        return renderTable({ columns: keys, data: value });
      }
      return `<pre>${escapeHTML(JSON.stringify(value, null, 2))}</pre>`;
    }
    if (value && typeof value === "object") {
      const entries = Object.entries(value);
      if (!entries.length) return `<p class="muted">No results.</p>`;
      return `<div class="nested-results">${entries.map(([key, val]) => `<div class="nested-item"><div class="section-kicker">${escapeHTML(key.replaceAll("_", " "))}</div>${renderValue(val)}</div>`).join("")}</div>`;
    }
    return `<pre>${escapeHTML(value ?? "—")}</pre>`;
  }
  function resultCard(title, value, wide = false) {
    return `<article class="panel result-card ${wide ? "wide" : ""}"><h3>${escapeHTML(title.replaceAll("_", " "))}</h3>${renderValue(value)}</article>`;
  }
  function updateStatus(status) {
    state.status = status || {};
    const loaded = !!status?.dataset_loaded;
    $("#stat-pipeline").textContent = loaded ? (status.dataset_analyzed ? "Analyzed" : "Active") : "Standby";
    $("#stat-pipeline-note").textContent = loaded ? "Dataset loaded in workspace" : "Waiting for a dataset";
    $$(".pipeline-step").forEach(step => {
      const done = !!status?.[step.dataset.step];
      step.classList.toggle("done", done);
      $(".step-state", step).textContent = done ? "Complete" : "Waiting";
    });
    $("#stat-charts").textContent = status?.visualization_count ?? 0;
  }
  async function refreshStatus() {
    const body = await request(API.status);
    updateStatus(body.data);
  }
  async function checkHealth() {
    try {
      const body = await request(API.health);
      $("#connection-label").textContent = body.data?.status === "running" ? "Connected · Flask API" : "Connected";
      return true;
    } catch (error) {
      $("#connection-label").textContent = "Backend unavailable";
      toast(error.message, "error");
      return false;
    }
  }
  function setDatasetInfo(data) {
    state.dataset = data;
    $("#stat-rows").textContent = Number(data.rows || 0).toLocaleString();
    $("#stat-columns").textContent = Number(data.columns || 0).toLocaleString();
    $("#dataset-name").textContent = data.filename || "Active dataset";
    $("#dataset-shape").textContent = `${data.rows} rows · ${data.columns} columns`;
    $("#dataset-empty").classList.add("hidden");
    $("#preview-wrap").classList.remove("hidden");
    const columns = data.column_names || [];
    $("#preview-table").innerHTML = `<thead><tr>${columns.map(c => `<th>${escapeHTML(c)}</th>`).join("")}</tr></thead><tbody><tr><td colspan="${Math.max(columns.length,1)}">Dataset uploaded. Run inspection to review its profile and use analytics to explore the records.</td></tr></tbody>`;
  }
  async function uploadFile(file) {
    if (!file) return;
    const ext = file.name.split(".").pop().toLowerCase();
    if (!["csv", "xlsx", "xls"].includes(ext)) { toast("Choose a CSV, XLSX or XLS file.", "error"); return; }
    if (file.size > 50 * 1024 * 1024) { toast("The selected file exceeds the 50 MB limit.", "error"); return; }
    const form = new FormData();
    form.append("file", file);
    $("#upload-progress").classList.remove("hidden");
    $("#upload-message").textContent = `Uploading ${file.name}…`;
    busy(true, "Uploading your dataset", "NEXUS is loading and validating the file.");
    try {
      const body = await request(API.upload, { method: "POST", body: form });
      setDatasetInfo(body.data);
      $("#upload-message").textContent = `${body.data.filename} uploaded · ${body.data.file_size.toLocaleString()} bytes`;
      await refreshStatus();
      toast("Dataset uploaded successfully.");
      showView("dataset");
    } catch (error) {
      $("#upload-message").textContent = error.message;
      toast(error.message, "error");
    } finally {
      busy(false);
      $("#upload-progress").classList.add("hidden");
      $("#dataset-file").value = "";
    }
  }
  async function runInspection() {
    busy(true, "Inspecting your dataset", "Checking columns, data types, missing values and duplicates.");
    try {
      const body = await post(API.inspect);
      state.inspection = body.data;
      const cards = Object.entries(body.data || {}).map(([key, value]) => resultCard(key, value, ["numerical_statistics", "categorical_statistics"].includes(key)));
      $("#inspection-results").innerHTML = cards.join("") || `<div class="panel empty-state wide-empty">No inspection data returned.</div>`;
      await refreshStatus();
      toast("Data inspection completed.");
    } catch (error) { toast(error.message, "error"); }
    finally { busy(false); }
  }
  async function runCleaning() {
    const operations = [];
    if ($("#clean-duplicates").checked) operations.push({ name: "remove_duplicates", parameters: {} });
    if ($("#clean-whitespace").checked) operations.push({ name: "trim_whitespace", parameters: {} });
    if ($("#clean-missing").checked) operations.push({ name: "handle_missing_values", parameters: { strategy: "drop" } });
    if (!operations.length) { toast("Select at least one cleaning operation.", "error"); return; }
    busy(true, "Cleaning your dataset", "Applying the selected operations to the uploaded source data.");
    try {
      const body = await post(API.clean, { operations });
      const d = body.data || {};
      $("#cleaning-summary").className = "cleaning-summary";
      $("#cleaning-summary").innerHTML = `
        <div class="summary-number">${Number(d.rows || 0).toLocaleString()} <small>rows remaining</small></div>
        <div class="summary-number">${Number(d.columns || 0).toLocaleString()} <small>columns</small></div>
        ${renderValue(d.cleaning_history || {})}`;
      await refreshStatus();
      toast("Cleaning operations completed.");
    } catch (error) { toast(error.message, "error"); }
    finally { busy(false); }
  }
  async function runAnalytics() {
    busy(true, "Analyzing your dataset", "Calculating statistical summaries and patterns.");
    try {
      const body = await post(API.analyze);
      state.analytics = body.data;
      $("#analytics-results").innerHTML = Object.entries(body.data || {}).map(([key, value]) => resultCard(key, value, ["correlation", "descriptive_statistics"].includes(key))).join("") || `<div class="panel empty-state wide-empty">No analytics returned.</div>`;
      await refreshStatus();
      toast("Analytics completed.");
    } catch (error) { toast(error.message, "error"); }
    finally { busy(false); }
  }
  function drawCharts(charts) {
    const entries = Object.entries(charts || {}).filter(([, fig]) => fig && Array.isArray(fig.data));
    if (!entries.length) {
      $("#charts-grid").innerHTML = `<div class="panel empty-state wide-empty"><span>▥</span><strong>No compatible charts returned</strong><p>The backend did not return Plotly figure data for this dataset.</p></div>`;
      return;
    }
    $("#charts-grid").innerHTML = entries.map(([name], index) => `<article class="panel chart-card"><h3>${escapeHTML(name.replaceAll("_", " "))}</h3><div class="chart-canvas" id="chart-${index}"></div></article>`).join("");
    entries.forEach(([name, fig], index) => {
      const layout = { ...(fig.layout || {}), paper_bgcolor: "rgba(255,255,255,0)", plot_bgcolor: "rgba(255,255,255,0)", font: { color: "#334155", family: "DM Sans" }, autosize: true, margin: { l: 45, r: 20, t: 28, b: 45 } };
      Plotly.newPlot(`chart-${index}`, fig.data, layout, { responsive: true, displaylogo: false });
    });
  }
  async function runCharts() {
    busy(true, "Generating visualizations", "Building charts from the active dataset.");
    try {
      const body = await post(API.charts);
      state.charts = body.data;
      drawCharts(body.data);
      await refreshStatus();
      showView("visualizations");
      toast("Visualizations generated.");
    } catch (error) { toast(error.message, "error"); }
    finally { busy(false); }
  }
  async function runReport() {
    busy(true, "Generating your PDF report", "Preparing the dataset profile and analytical findings.");
    try {
      const body = await post(API.report, {});
      state.report = body.data;
      const filename = body.data?.filename;
      $("#report-message").textContent = filename ? `Report created: ${filename} · ${(body.data.file_size_bytes || 0).toLocaleString()} bytes` : "Report generated, but the server did not return a filename.";
      if (filename) {
        const link = $("#report-download");
        link.href = `/api/reports/${encodeURIComponent(filename)}`;
        link.classList.remove("hidden");
      }
      await refreshStatus();
      toast("PDF report generated.");
    } catch (error) { $("#report-message").textContent = error.message; toast(error.message, "error"); }
    finally { busy(false); }
  }
  function bindEvents() {
    $$(".nav-item").forEach(btn => btn.addEventListener("click", () => showView(btn.dataset.view)));
    $$("[data-go]").forEach(btn => btn.addEventListener("click", () => showView(btn.dataset.go)));
    $("#mobile-menu").addEventListener("click", () => $("#sidebar").classList.toggle("open"));
    $("#notification-button").addEventListener("click", () => togglePopover($("#notification-panel"), $("#notification-button")));
    $("#profile-button").addEventListener("click", () => togglePopover($("#profile-panel"), $("#profile-button")));
    $("#mark-notifications-read").addEventListener("click", () => { state.notifications.forEach(item => item.read = true); renderNotifications(); });
    document.addEventListener("click", event => {
      if (!event.target.closest(".topbar-menu-wrap")) {
        $("#notification-panel").classList.add("hidden");
        $("#profile-panel").classList.add("hidden");
        $("#notification-button").setAttribute("aria-expanded", "false");
        $("#profile-button").setAttribute("aria-expanded", "false");
      }
    });
    $("#dataset-upload-trigger").addEventListener("click", () => showView("overview"));
    $("#dataset-file").addEventListener("change", e => uploadFile(e.target.files[0]));
    $("#dropzone").addEventListener("dragover", e => { e.preventDefault(); e.currentTarget.classList.add("dragover"); });
    $("#dropzone").addEventListener("dragleave", e => e.currentTarget.classList.remove("dragover"));
    $("#dropzone").addEventListener("drop", e => { e.preventDefault(); e.currentTarget.classList.remove("dragover"); uploadFile(e.dataTransfer.files[0]); });
    $("#inspect-button").addEventListener("click", runInspection);
    $("#clean-button").addEventListener("click", runCleaning);
    $("#analyze-button").addEventListener("click", runAnalytics);
    $("#charts-button").addEventListener("click", runCharts);
    $("#report-button").addEventListener("click", runReport);
  }
  document.addEventListener("DOMContentLoaded", async () => {
    bindEvents();
    renderNotifications();
    await checkHealth();
    try { await refreshStatus(); } catch { /* Backend health indicator already explains connection state. */ }
  });
})(); 
