/* 4SureERP Universal Viewport v0.2 (auto-refresh)
   - Loads registry
   - Mints embed token
   - Creates sandboxed iframe
   - postMessage handshake: base:init, base:refresh; listens for dashboard:ready, dashboard:resize
*/

const BASE_API = `${location.origin.replace(/\/$/,"")}/api`; // unified front door
const DEFAULT_TENANT = "demo";
const THEME = "holo-dark";

async function fetchJSON(url, opts = {}) {
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error(`HTTP ${res.status} — ${url}`);
  return res.json();
}

async function getRegistryDashboards(tenant = DEFAULT_TENANT) {
  const url = `${BASE_API}/registry/dashboards?tenant=${encodeURIComponent(tenant)}`;
  return fetchJSON(url);
}

async function mintEmbedToken({ tenant, userId, dashboardId, scopes }) {
  const url = `${BASE_API}/embed-token`;
  return fetchJSON(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tenant, user_id: userId, dashboardId, scopes }),
  });
}

// Schedules a refresh ~60s before exp and returns a cancel function
function scheduleTokenRefresh({ iframe, tenant, userId, entry, current }) {
  const now = Math.floor(Date.now() / 1000);
  const refreshIn = Math.max(10, (current.exp || now + 300) - now - 60); // seconds
  let timer = setTimeout(async () => {
    try {
      const next = await mintEmbedToken({
        tenant, userId, dashboardId: entry.dashboardId, scopes: entry.scopesRequired || [],
      });
      // Notify module
      iframe.contentWindow?.postMessage(
        { type: "base:refresh", payload: { token: next.token, exp: next.exp } },
        "*"
      );
      // Re-arm another refresh cycle
      cancel(); // clear previous
      cancel = scheduleTokenRefresh({ iframe, tenant, userId, entry, current: next });
    } catch (e) {
      console.error("embed token refresh failed:", e);
    }
  }, refreshIn * 1000);

  function cancel() { if (timer) { clearTimeout(timer); timer = null; } }
  return cancel;
}

export async function loadDashboardIntoViewport({ container, tenant, userId, entry }) {
  const tokenResp = await mintEmbedToken({
    tenant, userId, dashboardId: entry.dashboardId, scopes: entry.scopesRequired || [],
  });

  const iframe = document.createElement("iframe");
  iframe.src = entry.embed.url;
  iframe.title = entry.label;
  iframe.width = "100%";
  iframe.height = String(entry.embed.height || 560);
  iframe.setAttribute("sandbox", "allow-scripts allow-forms allow-same-origin");
  iframe.style.border = "0";
  iframe.style.borderRadius = "16px";
  iframe.style.boxShadow = "0 0 30px rgba(0,255,200,0.25)";
  iframe.dataset.dashboardId = entry.dashboardId;

  container.innerHTML = "";
  container.appendChild(iframe);

  let cancelRefresh = () => {};
  iframe.addEventListener("load", () => {
    // Send base:init
    iframe.contentWindow?.postMessage(
      {
        type: "base:init",
        payload: {
          token: tokenResp.token,
          exp: tokenResp.exp,
          theme: THEME,
          capabilities: entry.embed.capabilities || [],
        },
      },
      "*"
    );
    // Schedule token auto-refresh
    cancelRefresh = scheduleTokenRefresh({ iframe, tenant, userId, entry, current: tokenResp });
  });

  function onMessage(ev) {
    const { data } = ev || {};
    if (!data || typeof data !== "object" || !data.type) return;
    switch (data.type) {
      case "dashboard:ready":
        // optional: set UI state
        break;
      case "dashboard:resize": {
        const newH = Number(data.payload?.height);
        if (!Number.isNaN(newH) && newH > 300 && newH < 5000) iframe.height = String(newH);
        break;
      }
      default: break;
    }
  }
  window.addEventListener("message", onMessage);

  // Return disposer
  return () => { window.removeEventListener("message", onMessage); cancelRefresh(); };
}

export async function initOwnerShell() {
  const picker = document.querySelector("#dashboard-picker");
  const viewport = document.querySelector("#viewport");
  const debug = document.querySelector("#debug");
  const tenant = DEFAULT_TENANT;
  const userId = "owner_demo"; // change when auth is wired

  let dashboards = [];
  try { dashboards = await getRegistryDashboards(tenant); }
  catch (e) { debug.textContent = `Registry error: ${e.message}`; return; }

  dashboards.forEach((d) => {
    const opt = document.createElement("option");
    opt.value = d.dashboardId;
    opt.textContent = d.label;
    picker.appendChild(opt);
  });

  let dispose = null;
  async function loadSelected(id) {
    const entry = dashboards.find((d) => d.dashboardId === id);
    if (!entry) { debug.textContent = `Unknown dashboard: ${id}`; return; }
    if (dispose) dispose();
    try {
      dispose = await loadDashboardIntoViewport({ container: viewport, tenant, userId, entry });
      debug.textContent = `Loaded ${entry.label}`;
    } catch (e) { debug.textContent = `Load error: ${e.message}`; }
  }

  if (dashboards[0]) { picker.value = dashboards[0].dashboardId; loadSelected(dashboards[0].dashboardId); }
  picker.addEventListener("change", (e) => loadSelected(e.target.value));
}

if (document.currentScript?.dataset?.auto === "1") { initOwnerShell(); }

// --- simple embed handshake v0.1 ---
async function getEmbedToken({ tenant, dashboardId, scopes=[] }) {
  const res = await fetch(`${BASE_API}/embed-token`, {
    method: 'POST',
    headers: { 'Content-Type':'application/json' },
    body: JSON.stringify({ tenant, dashboardId, scopes })
  });
  if (!res.ok) throw new Error(`embed-token ${res.status}`);
  return res.json(); // {token, exp}
}

export async function loadIntoMiniViewer({ iframe, dashboard }) {
  // dashboard = { dashboardId, embed:{url,height,capabilities}, scopesRequired }
  const { token, exp } = await getEmbedToken({
    tenant: 'demo', 
    dashboardId: dashboard.dashboardId,
    scopes: dashboard.scopesRequired || []
  });

  // point the iframe at the module URL
  iframe.src = dashboard.embed.url;

  // when it loads, send base:init
  const onceLoad = () => {
    try {
      iframe.contentWindow?.postMessage({
        type: 'base:init',
        token,
        exp,
        theme: 'holo',
        capabilities: dashboard.embed.capabilities || []
      }, '*');
    } catch(e) { console.error(e); }
    iframe.removeEventListener('load', onceLoad);
  };
  iframe.addEventListener('load', onceLoad);
}
