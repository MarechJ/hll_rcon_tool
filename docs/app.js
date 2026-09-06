(function () {
  "use strict";

  const catalog = window.CRCON_DOCS || { endpoints: [], schemas: [] };
  const state = {
    game: localStorage.getItem("crcon-docs-game") === "hllv" ? "hllv" : "hll",
    query: "",
    schemaQuery: "",
  };

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  function route() {
    const raw = location.hash.slice(1) || "overview";
    const [page, ...rest] = raw.split("/");
    return { page: ["overview", "api", "schemas"].includes(page) ? page : "overview", detail: decodeURIComponent(rest.join("/")) };
  }

  function endpointsForGame() {
    return catalog.endpoints.filter((endpoint) => endpoint.games.includes(state.game));
  }

  function endpointSearchText(endpoint) {
    return [endpoint.title, endpoint.name, endpoint.path, endpoint.category, endpoint.summary, ...endpoint.permissions].join(" ").toLowerCase();
  }

  function filteredEndpoints() {
    const query = state.query.trim().toLowerCase();
    return endpointsForGame().filter((endpoint) => !query || endpointSearchText(endpoint).includes(query));
  }

  function setGame(game, navigate) {
    state.game = game;
    document.body.dataset.game = game;
    localStorage.setItem("crcon-docs-game", game);
    $$('[data-game]').forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.game === game)));
    renderEndpointNav();
    const current = route();
    if (current.page === "api") {
      const matching = findEndpoint(current.detail);
      if (navigate && !matching) {
        const first = endpointsForGame()[0];
        location.hash = first ? `api/${first.id}` : "api";
      } else {
        renderEndpoint(matching || endpointsForGame()[0]);
      }
    }
  }

  function findEndpoint(id) {
    const endpoints = endpointsForGame();
    return endpoints.find((endpoint) => endpoint.id === id) || endpoints.find((endpoint) => endpoint.name === id);
  }

  function methodBadge(method) {
    return `<span class="method ${escapeHtml(method.toLowerCase())}">${escapeHtml(method)}</span>`;
  }

  function renderEndpointNav() {
    const endpoints = filteredEndpoints();
    const groups = endpoints.reduce((result, endpoint) => {
      if (!result.has(endpoint.category)) result.set(endpoint.category, []);
      result.get(endpoint.category).push(endpoint);
      return result;
    }, new Map());
    const currentId = route().detail;
    const html = Array.from(groups, ([category, items]) => `
      <section class="endpoint-group">
        <h2>${escapeHtml(category)}</h2>
        ${items.map((endpoint) => `
          <a href="#api/${encodeURIComponent(endpoint.id)}" class="${currentId === endpoint.id || currentId === endpoint.name ? "active" : ""}">
            ${methodBadge(endpoint.methods[0])}<span>${escapeHtml(endpoint.title)}</span>
          </a>`).join("")}
      </section>`).join("");
    $("#endpoint-nav").innerHTML = html || '<p class="not-found">No endpoints match this search.</p>';
    $("#endpoint-result-count").textContent = `${endpoints.length} endpoint${endpoints.length === 1 ? "" : "s"}`;
    $("#clear-search").hidden = !state.query;
  }

  function sampleValue(parameter) {
    const type = parameter.type.toLowerCase();
    const name = parameter.name;
    if (name === "player_id") return "76561198000000000";
    if (name.includes("map")) return name.endsWith("s") ? ["carentan_warfare"] : "carentan_warfare";
    if (name.includes("message") || name === "msg" || name === "reason") return "Server maintenance in 10 minutes";
    if (name.includes("seconds") || name.includes("minutes") || name.includes("length") || type.includes("int")) return 10;
    if (type.includes("bool")) return true;
    if (type.includes("list") || type.includes("iterable") || type.includes("sequence")) return ["example"];
    if (type.includes("dict") || type.includes("object")) return { enabled: true };
    return "example";
  }

  function sampleFromType(type, depth = 0, fieldName = "") {
    if (depth > 3) return null;
    const normalized = String(type || "Any").replaceAll("'", "");
    const referenced = catalog.schemas.find((schema) => new RegExp(`\\b${schema.name}\\b`).test(normalized));
    if (referenced && referenced.name !== "ApiResponse") {
      if (referenced.kind === "Enum") return String(referenced.fields[0]?.type || "example").replace(/^['"]|['"]$/g, "");
      return Object.fromEntries(referenced.fields.map((field) => [field.name, sampleFromType(field.type, depth + 1, field.name)]));
    }
    const lower = normalized.toLowerCase();
    if (lower.includes("list") || lower.includes("iterable") || lower.includes("sequence")) return [];
    if (lower.includes("bool")) return true;
    if (lower.includes("int") || lower.includes("float")) return 0;
    if (lower.includes("dict") || lower.includes("object") || lower === "any") return {};
    if (lower === "none") return null;
    if (fieldName.includes("player_id")) return "76561198000000000";
    if (fieldName.includes("timestamp") || fieldName === "start") return 0;
    return "example";
  }

  function requestData(endpoint) {
    if (endpoint.requestType) return sampleFromType(endpoint.requestType);
    return Object.fromEntries(endpoint.parameters.map((parameter) => [parameter.name, sampleValue(parameter)]));
  }

  function curlExample(endpoint) {
    const method = endpoint.methods[0];
    const data = requestData(endpoint);
    const base = `https://crcon.example.com${endpoint.path}`;
    const auth = endpoint.authenticated ? ' \\\n+  -H "Authorization: Bearer YOUR_API_KEY"' : "";
    if (method === "GET") {
      const query = new URLSearchParams();
      Object.entries(data).forEach(([key, value]) => query.set(key, typeof value === "string" ? value : JSON.stringify(value)));
      return `curl "${base}${query.size ? `?${query}` : ""}"${auth} \\\n+  -H "Accept: application/json"`;
    }
    return `curl -X ${method} "${base}"${auth} \\\n+  -H "Content-Type: application/json" \\\n+  -d '${JSON.stringify(data, null, 2)}'`;
  }

  function resultExample(endpoint) {
    return JSON.stringify(sampleFromType(endpoint.responseType), null, 2);
  }

  function schemaName(type) {
    const names = catalog.schemas.map((schema) => schema.name);
    return names.find((name) => new RegExp(`\\b${name}\\b`).test(type)) || "ApiResponse";
  }

  function schemaShape(type, fallbackFields = []) {
    const name = schemaName(type);
    const schema = catalog.schemas.find((item) => item.name === name && (name !== "ApiResponse" || /ApiResponse/.test(type)));
    const fields = schema?.fields || fallbackFields;
    if (fields.length) {
      return `{
${fields.map((field) => `  ${field.name}${field.required ? "" : "?"}: ${field.type}`).join(",\n")}
}`;
    }
    return type || "Any";
  }

  function requestSchema(endpoint) {
    if (endpoint.requestType) return schemaShape(endpoint.requestType, endpoint.parameters);
    if (!endpoint.parameters.length) return "{}";
    return schemaShape("inline request", endpoint.parameters);
  }

  function resultSchema(endpoint) {
    return schemaShape(endpoint.responseType);
  }

  function parameterTable(parameters) {
    if (!parameters.length) return '<div class="empty-parameters">This endpoint does not accept request parameters.</div>';
    return `<table class="parameter-table">
      <thead><tr><th>Parameter</th><th>Type</th><th>Default</th><th>Presence</th></tr></thead>
      <tbody>${parameters.map((parameter) => `<tr>
        <td><code>${escapeHtml(parameter.name)}</code></td>
        <td><code>${escapeHtml(parameter.type)}</code></td>
        <td>${parameter.default === null ? "—" : `<code>${escapeHtml(parameter.default)}</code>`}</td>
        <td><span class="${parameter.required ? "required" : "optional"}">${parameter.required ? "Required" : "Optional"}</span></td>
      </tr>`).join("")}</tbody>
    </table>`;
  }

  function renderEndpoint(endpoint) {
    const content = $("#endpoint-content");
    if (!endpoint) {
      content.innerHTML = '<div class="not-found">Select an endpoint from the reference.</div>';
      return;
    }
    const responseSchema = schemaName(endpoint.responseType);
    const gameLabels = endpoint.games.map((game) => game === "hll" ? "HLL" : "HLLV");
    content.innerHTML = `
      <article>
        <section class="envelope-intro" aria-labelledby="response-envelope-heading">
          <div>
            <p class="section-label">Shared response format</p>
            <h2 id="response-envelope-heading">Every JSON endpoint uses one envelope</h2>
            <p>The sections below document only the endpoint-specific <code>result</code>. The remaining fields consistently report the command, echoed arguments, failure state, forwarding results, and CRCON version.</p>
            <a href="#schemas/ApiResponse">View the complete envelope schema →</a>
          </div>
          <pre><code>${escapeHtml(`{
  result: T,
  command: string,
  arguments: object | null,
  failed: boolean,
  error: string | object | null,
  forward_results: object | null,
  version: string
}`)}</code></pre>
        </section>
        <header class="endpoint-header">
          <p class="crumb">API reference / ${escapeHtml(endpoint.category)}</p>
          <h1>${escapeHtml(endpoint.title)}</h1>
          <p class="endpoint-name"><code>${escapeHtml(endpoint.name)}</code></p>
          <p class="summary">${escapeHtml(endpoint.summary)}</p>
          <div class="endpoint-badges">
            ${gameLabels.map((label) => `<span class="badge game">${label}</span>`).join("")}
          </div>
          <div class="path-row">
            ${methodBadge(endpoint.methods[0])}
            <code>${escapeHtml(endpoint.path)}</code>
            <button type="button" data-copy-text="${escapeHtml(endpoint.path)}">Copy</button>
          </div>
        </header>
        ${endpoint.permissions.length ? `<section class="reference-section" id="permissions">
          <h2>Required permissions</h2>
          <p>The authenticated CRCON user must have the following permission${endpoint.permissions.length === 1 ? "" : "s"}.</p>
          <div class="permission-list">${endpoint.permissions.map((permission) => `<code>${escapeHtml(permission)}</code>`).join("")}</div>
        </section>` : ""}
        <section class="reference-section" id="parameters">
          <h2>Request schema</h2>
          <p>${endpoint.methods.includes("GET") ? "GET parameters are passed in the query string." : "POST parameters are passed as a JSON object with application/json content type."}</p>
          ${parameterTable(endpoint.parameters)}
          <div class="schema-code">
            <div class="code-title"><span>${endpoint.methods.includes("GET") ? "Query object" : "JSON request body"}</span><button type="button" data-copy-code>Copy</button></div>
            <pre><code>${escapeHtml(requestSchema(endpoint))}</code></pre>
          </div>
        </section>
        <section class="reference-section" id="request-example">
          <h2>Request example</h2>
          <div class="code-window">
            <div class="code-title"><span>cURL</span><button type="button" data-copy-code>Copy</button></div>
            <pre><code>${escapeHtml(curlExample(endpoint))}</code></pre>
          </div>
        </section>
        <section class="reference-section" id="response">
          <h2>Result schema</h2>
          <p>The value placed in the shared response envelope's <code>result</code> field.</p>
          <div class="response-schema"><code>${escapeHtml(endpoint.responseType || "Any")}</code><a href="#schemas/${encodeURIComponent(responseSchema)}">View related schema →</a></div>
          <div class="schema-code" style="margin-top: 14px">
            <div class="code-title"><span>Result shape</span><button type="button" data-copy-code>Copy</button></div>
            <pre><code>${escapeHtml(resultSchema(endpoint))}</code></pre>
          </div>
          <div class="code-window" style="margin-top: 14px">
            <div class="code-title"><span>Example result</span><button type="button" data-copy-code>Copy</button></div>
            <pre><code>${escapeHtml(resultExample(endpoint))}</code></pre>
          </div>
        </section>
        <section class="reference-section" id="errors">
          <h2>Errors</h2>
          <p>Missing parameters return <code>400</code>. Invalid credentials return <code>401</code>, insufficient permissions return <code>403</code>, and unsupported methods return <code>405</code>. Command and validation failures set <code>failed</code> or <code>error</code> in the standard response envelope.</p>
        </section>
      </article>`;
    const tocItems = [
      ...(endpoint.permissions.length ? [["permissions", "Required permissions"]] : []),
      ["parameters", "Request parameters"],
      ["request-example", "Request example"], ["response", "Response"], ["errors", "Errors"],
    ];
    $("#endpoint-toc").innerHTML = tocItems.map(([id, label]) => `<a href="#${id}" data-anchor>${label}</a>`).join("");
    $$('[data-anchor]', $("#endpoint-toc")).forEach((link) => link.addEventListener("click", (event) => {
      event.preventDefault();
      $(link.getAttribute("href"), content)?.scrollIntoView({ behavior: "smooth" });
    }));
    renderEndpointNav();
    document.title = `${endpoint.title} · CRCON API`;
  }

  function renderSchemas(targetName) {
    const query = state.schemaQuery.trim().toLowerCase();
    const schemas = catalog.schemas.filter((schema) => {
      const text = [schema.name, schema.kind, schema.description, ...schema.fields.flatMap((field) => [field.name, field.type])].join(" ").toLowerCase();
      return !query || text.includes(query);
    });
    $("#schema-list").innerHTML = schemas.map((schema) => `
      <details class="schema-card" id="schema-${escapeHtml(schema.name)}" ${targetName === schema.name ? "open" : ""}>
        <summary><h2>${escapeHtml(schema.name)}</h2><span class="schema-kind">${escapeHtml(schema.kind)}</span></summary>
        <div class="schema-body">
          ${schema.description ? `<p class="schema-description">${escapeHtml(schema.description)}</p>` : ""}
          <table class="schema-table">
            <thead><tr><th>Field</th><th>Type / value</th><th>Presence</th></tr></thead>
            <tbody>${schema.fields.map((field) => `<tr>
              <td><code>${escapeHtml(field.name)}</code></td><td><code>${escapeHtml(field.type)}</code></td>
              <td><span class="${field.required ? "required" : "optional"}">${field.required ? "Required" : "Optional"}</span></td>
            </tr>`).join("")}</tbody>
          </table>
        </div>
      </details>`).join("") || '<p class="not-found">No schemas match this search.</p>';
    if (targetName) requestAnimationFrame(() => $(`#schema-${CSS.escape(targetName)}`)?.scrollIntoView({ block: "start" }));
  }

  function showRoute() {
    const current = route();
    $$('[data-route]').forEach((page) => { page.hidden = page.dataset.route !== current.page; });
    $$('[data-route-link]').forEach((link) => link.classList.toggle("active", link.dataset.routeLink === current.page));
    if (current.page === "api") {
      renderEndpoint(findEndpoint(current.detail) || endpointsForGame()[0]);
      document.title = current.detail ? document.title : "API reference · CRCON Docs";
    } else if (current.page === "schemas") {
      renderSchemas(current.detail);
      document.title = "Schemas · CRCON API";
    } else {
      document.title = "CRCON Documentation";
    }
    window.scrollTo({ top: 0, behavior: "auto" });
  }

  async function copy(text) {
    try {
      await navigator.clipboard.writeText(text);
    } catch (_) {
      const area = document.createElement("textarea");
      area.value = text;
      document.body.appendChild(area);
      area.select();
      document.execCommand("copy");
      area.remove();
    }
    const toast = $("#copy-toast");
    toast.classList.add("visible");
    clearTimeout(copy.timer);
    copy.timer = setTimeout(() => toast.classList.remove("visible"), 1400);
  }

  document.addEventListener("click", (event) => {
    const gameButton = event.target.closest('[data-game]');
    if (gameButton) setGame(gameButton.dataset.game, true);
    const openGame = event.target.closest('[data-open-game]');
    if (openGame) {
      setGame(openGame.dataset.openGame, false);
      const first = endpointsForGame()[0];
      location.hash = first ? `api/${first.id}` : "api";
    }
    const targetCopy = event.target.closest('[data-copy-target]');
    if (targetCopy) copy($(`#${CSS.escape(targetCopy.dataset.copyTarget)}`).textContent);
    const textCopy = event.target.closest('[data-copy-text]');
    if (textCopy) copy(textCopy.dataset.copyText);
    const codeCopy = event.target.closest('[data-copy-code]');
    if (codeCopy) copy(codeCopy.closest(".code-window").querySelector("code").textContent);
  });

  $("#endpoint-search").addEventListener("input", (event) => { state.query = event.target.value; renderEndpointNav(); });
  $("#clear-search").addEventListener("click", () => { state.query = ""; $("#endpoint-search").value = ""; renderEndpointNav(); });
  $("#schema-search").addEventListener("input", (event) => { state.schemaQuery = event.target.value; renderSchemas(); });
  window.addEventListener("hashchange", showRoute);

  $("#hero-endpoint-count").textContent = new Set(catalog.endpoints.map((endpoint) => endpoint.name)).size;
  $("#hero-schema-count").textContent = catalog.schemas.length;
  setGame(state.game, false);
  showRoute();
})();
