import "./style.css";

const $ = (id) => document.getElementById(id);
const POLL_MS = 2000;

const els = {
  form: $("form"), file: $("file"), drop: $("drop"), preview: $("preview"),
  dropText: $("dropText"), test: $("test"), question: $("question"),
  resolution: $("resolution"), notes: $("notes"), submit: $("submit"),
  formError: $("formError"), statusPanel: $("statusPanel"), statusLabel: $("statusLabel"),
  statusStage: $("statusStage"), statusBadge: $("statusBadge"), statusError: $("statusError"),
  repairs: $("repairs"),
  spinner: $("spinner"), videoPanel: $("videoPanel"), video: $("video"),
  download: $("download"), codePanel: $("codePanel"), code: $("code"),
  history: $("history"), health: $("health"),
};

const BADGE = {
  queued: "border-edge text-slate-300",
  generating: "border-accent/50 text-accent",
  rendering: "border-warn/50 text-warn",
  done: "border-good/50 text-good",
  failed: "border-bad/50 text-bad",
};

// Rendering takes minutes, so say what is happening rather than just spinning
const HUMAN = {
  queued: "Queued",
  generating: "Reading the problem and writing the scene",
  rendering: "Rendering frames",
  done: "Done",
  failed: "Failed",
};

let pollTimer = null;

function showFormError(message) {
  els.formError.textContent = message;
  els.formError.classList.toggle("hidden", !message);
}

function setBusy(busy) {
  els.submit.disabled = busy;
  els.submit.textContent = busy ? "Working…" : "Generate video";
}

function pickFile(file) {
  if (!file) return;
  els.file.files = (() => {
    const dt = new DataTransfer();
    dt.items.add(file);
    return dt.files;
  })();
  els.preview.src = URL.createObjectURL(file);
  els.preview.classList.remove("hidden");
  els.dropText.classList.add("hidden");
}

els.file.addEventListener("change", (event) => pickFile(event.target.files[0]));

["dragenter", "dragover"].forEach((name) =>
  els.drop.addEventListener(name, (event) => {
    event.preventDefault();
    els.drop.classList.add("border-accent");
  }),
);
["dragleave", "drop"].forEach((name) =>
  els.drop.addEventListener(name, (event) => {
    event.preventDefault();
    els.drop.classList.remove("border-accent");
  }),
);
els.drop.addEventListener("drop", (event) => pickFile(event.dataTransfer.files[0]));

// Pasting a screenshot straight from the clipboard is the fastest path in
function onPaste(event) {
  const item = [...(event.clipboardData?.items || [])].find((i) => i.type.startsWith("image/"));
  if (item) pickFile(item.getAsFile());
}
window.addEventListener("paste", onPaste);

function render(job) {
  els.statusPanel.classList.remove("hidden");
  els.statusLabel.textContent = `${job.label} — ${HUMAN[job.status] || job.status}`;
  els.statusStage.textContent = job.stage || "";
  els.statusBadge.textContent = job.status;
  els.statusBadge.className =
    "rounded-full border px-2.5 py-1 text-xs font-medium " + (BADGE[job.status] || BADGE.queued);

  const running = job.status === "queued" || job.status === "generating" || job.status === "rendering";
  els.spinner.classList.toggle("hidden", !running);

  els.repairs.innerHTML = "";
  if (job.repairs?.length) {
    els.repairs.classList.remove("hidden");
    els.repairs.innerHTML =
      `<span class="font-medium text-warn">Fixed automatically:</span> ` +
      job.repairs.map((r) => `<div class="mt-1 font-mono">${r.replace(/</g, "&lt;")}</div>`).join("");
  } else {
    els.repairs.classList.add("hidden");
  }

  const detail = [job.error, job.log_tail].filter(Boolean).join("\n\n");
  els.statusError.textContent = detail;
  els.statusError.classList.toggle("hidden", job.status !== "failed" || !detail);

  if (job.code) {
    els.code.textContent = job.code;
    els.codePanel.classList.remove("hidden");
  }

  if (job.video_url) {
    // Cache-bust so a re-run of the same job id refreshes the player
    els.video.src = `${job.video_url}?v=${encodeURIComponent(job.finished_at || "")}`;
    els.download.href = job.video_url;
    els.videoPanel.classList.remove("hidden");
  }
  return running;
}

async function poll(jobId) {
  clearTimeout(pollTimer);
  let job;
  try {
    const response = await fetch(`/api/jobs/${jobId}`);
    if (!response.ok) throw new Error(`status ${response.status}`);
    job = await response.json();
  } catch (err) {
    els.statusStage.textContent = `lost contact with the backend (${err.message}), retrying…`;
    pollTimer = setTimeout(() => poll(jobId), POLL_MS * 2);
    return;
  }
  const running = render(job);
  if (running) {
    pollTimer = setTimeout(() => poll(jobId), POLL_MS);
  } else {
    setBusy(false);
    loadHistory();
  }
}

els.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showFormError("");
  if (!els.file.files[0]) {
    showFormError("Pick a screenshot of the problem first.");
    return;
  }

  const body = new FormData();
  body.append("image", els.file.files[0]);
  body.append("test", els.test.value.trim());
  body.append("question", els.question.value);
  body.append("notes", els.notes.value);
  body.append("resolution", els.resolution.value);

  setBusy(true);
  els.videoPanel.classList.add("hidden");
  els.codePanel.classList.add("hidden");

  try {
    const response = await fetch("/api/jobs", { method: "POST", body });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || `status ${response.status}`);
    render(data);
    poll(data.id);
  } catch (err) {
    setBusy(false);
    showFormError(err.message);
  }
});

async function loadHistory() {
  try {
    const jobs = await (await fetch("/api/jobs")).json();
    els.history.innerHTML = "";
    if (!jobs.length) {
      els.history.innerHTML = '<li class="text-slate-500">Nothing rendered yet.</li>';
      return;
    }
    for (const job of jobs.slice(0, 12)) {
      const li = document.createElement("li");
      li.className =
        "flex items-center justify-between gap-3 rounded-lg border border-edge px-3 py-2";
      const when = new Date(job.created_at).toLocaleString();
      li.innerHTML = `
        <span><span class="font-semibold text-slate-200">${job.label}</span>
          <span class="ml-2 text-xs text-slate-500">${when}</span></span>
        <span class="text-xs ${job.status === "done" ? "text-good" : job.status === "failed" ? "text-bad" : "text-warn"}">
          ${job.status}</span>`;
      if (job.status === "done") {
        li.classList.add("cursor-pointer", "hover:border-accent");
        li.addEventListener("click", () => {
          render(job);
          els.statusPanel.scrollIntoView({ behavior: "smooth", block: "start" });
        });
      }
      els.history.appendChild(li);
    }
  } catch {
    els.history.innerHTML = '<li class="text-slate-500">Backend unreachable.</li>';
  }
}

async function checkHealth() {
  try {
    const info = await (await fetch("/api/health")).json();
    els.health.textContent = info.api_key_configured
      ? `${info.model} · ${info.resolution}`
      : "ANTHROPIC_API_KEY is not set — generation will fail";
    els.health.className = info.api_key_configured
      ? "text-xs text-slate-500"
      : "text-xs font-medium text-bad";
  } catch {
    els.health.textContent = "backend unreachable";
    els.health.className = "text-xs font-medium text-bad";
  }
}

checkHealth();
loadHistory();
