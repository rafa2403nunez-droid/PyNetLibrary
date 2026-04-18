/** @type {HTMLIFrameElement} */
let viewerIframe;

/** @type {Array} */
let clashData = [];

/** @type {Array} */
let modelFiles = [];

async function initDashboard() {
  viewerIframe = document.getElementById("bim-viewer");

  try {
    const resp = await fetch("/data/clashes.json");
    if (!resp.ok) throw new Error("No clash data found");
    const data = await resp.json();
    clashData = data.clashes || [];
    modelFiles = data.models || [];

    renderCards(data);
    renderClashTable(clashData);
    renderPieChart(clashData);
    renderBarChart(clashData);

    document.getElementById("subtitle").textContent =
      `Zone A — ${clashData.length} clashes | ${countTests(clashData)} active tests | ${modelFiles.length} federated models`;

    // Build viewer URL with all models
    const modelNames = modelFiles.map((m) => m.fileName).join(",");
    viewerIframe.src = `/viewer/?models=${encodeURIComponent(modelNames)}`;
  } catch (e) {
    console.error("Failed to load clash data:", e);
    document.getElementById("subtitle").textContent =
      "No clash data available — export from Navisworks first";
  }
}

function countTests(clashes) {
  return new Set(clashes.map((c) => c.Test)).size;
}

function loadModelsInViewer() {
  const viewer = viewerIframe.contentWindow;
  if (!viewer) return;

  for (const model of modelFiles) {
    const url = `/models/${model.fileName}`;
    // Use postMessage for iframe communication
    viewerIframe.contentWindow.postMessage(
      { type: "viewer-command", action: "loadModel", payload: { url, name: model.name } },
      "*"
    );
  }
}

function renderCards(data) {
  const container = document.getElementById("cards");
  const summary = data.summary || {};
  const cards = [
    { title: "Total Clashes", value: clashData.length, cls: "card-clashes" },
    { title: "Active Tests", value: countTests(clashData), cls: "card-tests" },
    { title: "Federated Models", value: modelFiles.length, cls: "card-models" },
  ];

  container.innerHTML = cards
    .map(
      (c) => `
    <div class="card ${c.cls}">
      <div class="card-title">${c.title}</div>
      <div class="card-value">${c.value}</div>
    </div>
  `
    )
    .join("");
}

function renderClashTable(clashes) {
  const tbody = document.getElementById("clash-tbody");

  tbody.innerHTML = clashes
    .map(
      (c, i) => `
    <tr data-index="${i}">
      <td>${c.Clash || ""}</td>
      <td>${c.Test || ""}</td>
      <td class="${c.Status === "New" ? "status-new" : ""}">${c.Status || ""}</td>
      <td>${c["Distance (m)"] || ""}</td>
      <td title="${c["Element A"] || ""}">${c["Element A"] || ""}</td>
      <td>${c["ID A"] || ""}</td>
      <td title="${c["Element B"] || ""}">${c["Element B"] || ""}</td>
      <td>${c["ID B"] || ""}</td>
    </tr>
  `
    )
    .join("");

  // Click handler for clash navigation
  tbody.addEventListener("click", (e) => {
    const row = e.target.closest("tr");
    if (!row) return;
    const idx = parseInt(row.dataset.index);
    const clash = clashes[idx];
    if (!clash) return;

    // Visual feedback
    tbody.querySelectorAll("tr.selected").forEach((r) => r.classList.remove("selected"));
    row.classList.add("selected");

    // Send highlight command to viewer
    viewerIframe.contentWindow?.postMessage(
      {
        type: "viewer-command",
        action: "highlightElements",
        payload: {
          modelId: clash.modelId || "",
          expressIds: [clash.expressIdA, clash.expressIdB].filter(Boolean),
        },
      },
      "*"
    );
  });
}

function renderPieChart(clashes) {
  const disciplines = {};
  for (const c of clashes) {
    const d = c.Discipline || "Unknown";
    disciplines[d] = (disciplines[d] || 0) + 1;
  }

  Plotly.newPlot(
    "pie-chart",
    [
      {
        type: "pie",
        labels: Object.keys(disciplines),
        values: Object.values(disciplines),
        marker: {
          colors: ["#ff4c4c", "#ffb300", "#3385ff", "#33cc33", "#9933ff"],
          line: { color: "#fff", width: 2 },
        },
        textinfo: "percent+label+value",
      },
    ],
    {
      title: "Clashes por Disciplina",
      height: 250,
      margin: { t: 40, b: 10, l: 10, r: 10 },
      paper_bgcolor: "transparent",
    },
    { responsive: true }
  );
}

function renderBarChart(clashes) {
  const tests = {};
  for (const c of clashes) {
    const t = c.Test || "Unknown";
    tests[t] = (tests[t] || 0) + 1;
  }

  const sorted = Object.entries(tests).sort((a, b) => b[1] - a[1]);

  Plotly.newPlot(
    "bar-chart",
    [
      {
        type: "bar",
        x: sorted.map(([name]) => name),
        y: sorted.map(([, count]) => count),
        marker: {
          color: sorted.map(([, count]) =>
            count > 5 ? "#ff4c4c" : count > 2 ? "#ffb300" : "#3385ff"
          ),
        },
      },
    ],
    {
      title: "Clashes por Test",
      height: 250,
      margin: { t: 40, b: 80, l: 40, r: 20 },
      xaxis: { tickangle: -25 },
      paper_bgcolor: "transparent",
      plot_bgcolor: "transparent",
    },
    { responsive: true }
  );
}

// Listen for events from the viewer
window.addEventListener("message", (event) => {
  if (!event.data || event.data.type !== "viewer-event") return;

  if (event.data.event === "modelsLoaded") {
    console.log("[Dashboard] All models loaded in viewer");
  }
});

document.addEventListener("DOMContentLoaded", initDashboard);
