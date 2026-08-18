import "./style.css";
import "katex/dist/katex.min.css";
import { renderLatexFragment } from "./latex-preview.js";

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
  latex: $("latex"), latexPreview: $("latexPreview"),
  musicPanel: $("musicPanel"), musicEmpty: $("musicEmpty"), musicControls: $("musicControls"),
  musicBadge: $("musicBadge"), track: $("track"), trackAudio: $("trackAudio"),
  start: $("start"), setStart: $("setStart"), volume: $("volume"), volLabel: $("volLabel"),
  fadeIn: $("fadeIn"), fadeOut: $("fadeOut"), loop: $("loop"), musicInfo: $("musicInfo"),
  applyMusic: $("applyMusic"), removeMusic: $("removeMusic"), musicError: $("musicError"),
  tabs: [...document.querySelectorAll(".mode-tab")],
  panels: [...document.querySelectorAll("[data-panel]")],
};

// "image" or "latex" -- which input the next job is built from
let mode = "image";

function setMode(next) {
  mode = next;
  for (const tab of els.tabs) {
    const on = tab.dataset.mode === mode;
    tab.className =
      "mode-tab flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition " +
      (on ? "bg-accent text-ink" : "text-slate-400 hover:text-slate-200");
  }
  for (const panel of els.panels) {
    panel.classList.toggle("hidden", panel.dataset.panel !== mode);
  }
  showFormError("");
}

// Problems are written as mixed text + math (prose, inline $...$, display
// environments), so the preview renders them as a document fragment rather
// than one math block. See latex-preview.js.
function renderPreview() {
  const raw = els.latex.value;
  if (!raw.trim()) {
    els.latexPreview.innerHTML =
      '<span class="text-sm text-slate-500">Nothing to preview yet.</span>';
    return;
  }
  try {
    els.latexPreview.innerHTML = renderLatexFragment(raw);
  } catch (err) {
    els.latexPreview.innerHTML =
      `<span class="text-sm text-bad">${err.message}</span>`;
  }
}

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
els.tabs.forEach((tab) => tab.addEventListener("click", () => setMode(tab.dataset.mode)));
els.latex.addEventListener("input", renderPreview);

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
  // Ignore pastes aimed at the LaTeX box
  if (event.target === els.latex) return;
  const item = [...(event.clipboardData?.items || [])].find((i) => i.type.startsWith("image/"));
  if (item) {
    setMode("image");
    pickFile(item.getAsFile());
  }
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
    const src = job.music_video_url || job.video_url;
    // Cache-bust so a re-run of the same job id refreshes the player
    els.video.src = `${src}?v=${encodeURIComponent(job.finished_at || "")}`;
    els.download.href = src;
    els.videoPanel.classList.remove("hidden");
    videoSeconds = 0;             // re-measure for this job
    loadMusicFor(job);
  } else {
    els.musicPanel.classList.add("hidden");
  }
  return running;
}


// ---- Background music -----------------------------------------------------

let currentJob = null;     // the job the video panel is showing
let videoSeconds = 0;      // its duration, read off the <video> element
let tracks = [];           // catalogue from /api/music

const fmt = (s) => {
  if (!s || s < 0) s = 0;
  const m = Math.floor(s / 60);
  const r = Math.round(s % 60);
  return `${m}:${String(r).padStart(2, "0")}`;
};

function selectedTrack() {
  return tracks.find((t) => t.id === els.track.value) || null;
}

function updateMusicInfo() {
  const t = selectedTrack();
  if (!t) {
    els.musicInfo.textContent = "";
    return;
  }
  const shorter = t.duration < videoSeconds - 0.1;
  els.loop.parentElement.classList.toggle("opacity-40", !shorter);
  let verdict;
  if (shorter) {
    verdict = els.loop.checked
      ? "shorter than the video — it will loop to fill."
      : "shorter than the video — it plays once, then silence.";
  } else {
    verdict = `trimmed to ${fmt(videoSeconds)} from your start point.`;
  }
  els.musicInfo.textContent =
    `Track ${fmt(t.duration)} · video ${fmt(videoSeconds)} — ${verdict}`;
}

function onTrackChange() {
  const t = selectedTrack();
  if (!t) return;
  els.trackAudio.src = `/api/music/${encodeURIComponent(t.id)}/audio`;
  els.start.max = Math.max(0, Math.floor(t.duration));
  // Default the loop toggle to on when the track can't cover the video
  els.loop.checked = t.duration < videoSeconds - 0.1;
  updateMusicInfo();
}

async function loadMusicFor(job) {
  currentJob = job;
  els.musicPanel.classList.remove("hidden");
  els.musicError.classList.add("hidden");

  try {
    tracks = await (await fetch("/api/music")).json();
  } catch {
    tracks = [];
  }

  if (!tracks.length) {
    els.musicEmpty.classList.remove("hidden");
    els.musicControls.classList.add("hidden");
    return;
  }
  els.musicEmpty.classList.add("hidden");
  els.musicControls.classList.remove("hidden");

  const applied = job.has_music ? job.music_track : els.track.value;
  els.track.innerHTML = tracks
    .map((t) => `<option value="${t.id}">${t.name} · ${fmt(t.duration)}</option>`)
    .join("");
  if (applied && tracks.some((t) => t.id === applied)) els.track.value = applied;

  // Reflect an already-applied mix back into the controls
  const cfg = job.music_settings || {};
  if (job.has_music) {
    els.start.value = cfg.start ?? 0;
    els.volume.value = Math.round((cfg.volume ?? 0.6) * 100);
    els.fadeIn.value = cfg.fade_in ?? 0.5;
    els.fadeOut.value = cfg.fade_out ?? 1.5;
    els.loop.checked = !!cfg.loop;
  }
  els.volLabel.textContent = `${els.volume.value}%`;
  els.musicBadge.classList.toggle("hidden", !job.has_music);
  els.musicBadge.textContent = job.has_music ? `♪ ${job.music_track}` : "";
  els.removeMusic.classList.toggle("hidden", !job.has_music);

  onTrackChange();
  if (job.has_music) { els.track.value = applied; updateMusicInfo(); }
}

async function applyMusic() {
  if (!currentJob) return;
  els.musicError.classList.add("hidden");
  els.applyMusic.disabled = true;
  els.applyMusic.textContent = "Mixing…";
  try {
    const body = new FormData();
    body.append("track", els.track.value);
    body.append("start", els.start.value || "0");
    body.append("volume", String((Number(els.volume.value) || 0) / 100));
    body.append("fade_in", els.fadeIn.value || "0");
    body.append("fade_out", els.fadeOut.value || "0");
    body.append("loop", els.loop.checked ? "true" : "false");
    const res = await fetch(`/api/jobs/${currentJob.id}/music`, { method: "POST", body });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `status ${res.status}`);
    currentJob = data;
    // Swap the preview to the mixed version
    els.video.src = `${data.music_video_url}?v=${Date.now()}`;
    els.download.href = data.music_video_url;
    els.musicBadge.classList.remove("hidden");
    els.musicBadge.textContent = `♪ ${data.music_track}`;
    els.removeMusic.classList.remove("hidden");
    els.video.play?.().catch(() => {});
  } catch (err) {
    els.musicError.textContent = err.message;
    els.musicError.classList.remove("hidden");
  } finally {
    els.applyMusic.disabled = false;
    els.applyMusic.textContent = "Apply music";
  }
}

async function removeMusic() {
  if (!currentJob) return;
  try {
    const res = await fetch(`/api/jobs/${currentJob.id}/music`, { method: "DELETE" });
    currentJob = await res.json();
  } catch { /* ignore */ }
  els.video.src = `${currentJob.video_url}?v=${Date.now()}`;
  els.download.href = currentJob.video_url;
  els.musicBadge.classList.add("hidden");
  els.removeMusic.classList.add("hidden");
}

els.track.addEventListener("change", onTrackChange);
els.setStart.addEventListener("click", () => {
  els.start.value = (els.trackAudio.currentTime || 0).toFixed(1);
});
els.volume.addEventListener("input", () => { els.volLabel.textContent = `${els.volume.value}%`; });
els.loop.addEventListener("change", updateMusicInfo);
els.applyMusic.addEventListener("click", applyMusic);
els.removeMusic.addEventListener("click", removeMusic);
els.video.addEventListener("loadedmetadata", () => {
  if (els.video.duration && isFinite(els.video.duration)) {
    // The mixed video shares the silent one's length; capture it once.
    if (!videoSeconds) videoSeconds = els.video.duration;
    updateMusicInfo();
  }
});

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
  if (mode === "image" && !els.file.files[0]) {
    showFormError("Pick a screenshot of the problem first.");
    return;
  }
  if (mode === "latex" && !els.latex.value.trim()) {
    showFormError("Type the problem in LaTeX first.");
    return;
  }

  const body = new FormData();
  if (mode === "image") body.append("image", els.file.files[0]);
  else body.append("problem", els.latex.value.trim());
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
          <span class="ml-2 rounded border border-edge px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-slate-500">${job.source || "image"}</span>
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

setMode("image");
renderPreview();
checkHealth();
loadHistory();
