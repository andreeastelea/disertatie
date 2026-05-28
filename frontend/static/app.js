/* global state */
let API_BASE = "/api";

/* ── Env loader ────────────────────────────────────────────────── */

function parseEnvText(text) {
  const env = {};
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const idx = line.indexOf("=");
    if (idx < 0) continue;
    const key = line.slice(0, idx).trim();
    let value = line.slice(idx + 1).trim();
    if ((value.startsWith("\"") && value.endsWith("\"")) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    env[key] = value;
  }
  return env;
}

async function loadFrontendEnv() {
  try {
    const resp = await fetch("/.env", { cache: "no-store" });
    if (!resp.ok) return;
    const env = parseEnvText(await resp.text());
    if (env.API_BASE) {
      API_BASE = env.API_BASE;
    }
  } catch {
    // Ignore missing or unreadable env file.
  }
}

function resolveApiBase() {
  if (API_BASE && API_BASE !== "/api") {
    return API_BASE;
  }

  const host = window.location.hostname;
  const port = window.location.port;

  if ((host === "localhost" || host === "127.0.0.1") && port === "8080") {
    return "http://localhost:5000/api";
  }

  return "/api";
}

async function initAppConfig() {
  await loadFrontendEnv();
  API_BASE = resolveApiBase();
}

/* ── Utility ─────────────────────────────────────────────────── */

function showResult(el, type, text) {
  el.className = `result-box ${type}`;
  el.textContent = text;
}

function formatJson(obj) {
  return JSON.stringify(obj, null, 2);
}

async function apiFetch(path, options = {}) {
  const resp = await fetch(API_BASE + path, options);
  const data = await resp.json();
  if (!resp.ok) throw Object.assign(new Error(data.error || "Eroare server"), { data });
  return data;
}

/* ── DB badge ────────────────────────────────────────────────── */

async function initBadge() {
  try {
    const data = await apiFetch("/../health");
    const badge = document.getElementById("db-badge");
    const dbType = data.db_type || "unknown";
    badge.textContent = `DB: ${dbType.toUpperCase()}`;
    badge.classList.add(dbType === "sql" ? "sql" : "nosql");
  } catch {
    /* ignore badge failures */
  }
}

/* ── Submit form ─────────────────────────────────────────────── */

document.getElementById("submitForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const resultEl = document.getElementById("submitResult");
  const btn = e.target.querySelector("button[type=submit]");

  const payload = {
    name: document.getElementById("name").value.trim(),
    surname: document.getElementById("surname").value.trim(),
    code: document.getElementById("code").value.trim(),
    value: parseFloat(document.getElementById("value").value),
    description: document.getElementById("description").value.trim(),
  };

  btn.disabled = true;
  btn.textContent = "Se procesează...";
  resultEl.className = "result-box hidden";

  try {
    const data = await apiFetch("/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    showResult(
      resultEl,
      "success",
      `✔ Salvat cu succes!\n${formatJson(data)}`
    );
    e.target.reset();
    loadRecords();
  } catch (err) {
    showResult(resultEl, "error", `✘ Eroare: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = "Trimite & Calculează";
  }
});

/* ── Benchmark CPU ───────────────────────────────────────────── */

async function runBenchmarkCpu() {
  const value = document.getElementById("cpuValue").value || 42;
  const resultEl = document.getElementById("benchResult");
  showResult(resultEl, "info", "⏳ Se execută test CPU-bound...");

  const t0 = performance.now();
  try {
    const data = await apiFetch(`/benchmark/cpu?value=${encodeURIComponent(value)}`);
    const elapsed = (performance.now() - t0).toFixed(1);
    showResult(
      resultEl,
      "success",
      `✔ CPU-bound completat în ${elapsed} ms (client-side)\n${formatJson(data)}`
    );
  } catch (err) {
    showResult(resultEl, "error", `✘ Eroare: ${err.message}`);
  }
}

/* ── Benchmark I/O ───────────────────────────────────────────── */

async function runBenchmarkIo() {
  const count = document.getElementById("ioCount").value || 10;
  const resultEl = document.getElementById("benchResult");
  showResult(resultEl, "info", "⏳ Se execută test I/O-bound...");

  const t0 = performance.now();
  try {
    const data = await apiFetch(`/benchmark/io?count=${encodeURIComponent(count)}`);
    const elapsed = (performance.now() - t0).toFixed(1);
    showResult(
      resultEl,
      "success",
      `✔ I/O-bound completat în ${elapsed} ms (client-side)\n${formatJson(data)}`
    );
  } catch (err) {
    showResult(resultEl, "error", `✘ Eroare: ${err.message}`);
  }
}

/* ── Load records ────────────────────────────────────────────── */

async function loadRecords() {
  const container = document.getElementById("recordsContainer");
  container.innerHTML = "<p class='hint'>Se încarcă...</p>";

  try {
    const records = await apiFetch("/records");

    if (!records.length) {
      container.innerHTML = "<p class='hint'>Nu există înregistrări.</p>";
      return;
    }

    const cols = ["id", "name", "surname", "code", "value", "result", "created_at"];
    const colLabels = ["ID", "Nume", "Prenume", "Cod", "Valoare", "Rezultat CPU", "Data"];

    const rows = records
      .map((r) => {
        const id = r.id ?? r._id ?? "–";
        const cells = [
          id,
          r.name,
          r.surname,
          r.code,
          r.value,
          typeof r.result === "number" ? r.result.toFixed(4) : r.result,
          r.created_at ? r.created_at.replace("T", " ").substring(0, 19) : "–",
        ]
          .map((v) => `<td>${v ?? "–"}</td>`)
          .join("");
        return `<tr>${cells}</tr>`;
      })
      .join("");

    container.innerHTML = `
      <table>
        <thead><tr>${colLabels.map((l) => `<th>${l}</th>`).join("")}</tr></thead>
        <tbody>${rows}</tbody>
      </table>`;
  } catch (err) {
    container.innerHTML = `<p style="color:#e53e3e">Eroare la încărcare: ${err.message}</p>`;
  }
}

/* ── Init ────────────────────────────────────────────────────── */
(async () => {
  await initAppConfig();
  initBadge();
  loadRecords();
})();
