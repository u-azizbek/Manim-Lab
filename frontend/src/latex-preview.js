import katex from "katex";

// A small renderer for mixed text + math LaTeX, the way a workbook problem is
// actually written: prose with inline `$...$`, display `$$...$$` / `\[...\]`,
// and amsmath environments. KaTeX only renders math, so this splits the input
// into text and math runs and renders each appropriately.

// Environments KaTeX understands natively -- rendered whole.
const KATEX_ENVS = new Set([
  "align", "align*", "aligned", "alignat", "alignat*", "gather", "gather*",
  "gathered", "matrix", "pmatrix", "bmatrix", "Bmatrix", "vmatrix", "Vmatrix",
  "smallmatrix", "cases", "dcases", "rcases", "array", "split", "subarray", "CD",
]);

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// A run of ordinary (non-math) LaTeX text, cleaned up enough to read.
function renderText(text) {
  let out = escapeHtml(text);
  out = out
    .replace(/\\textbf\{([^{}]*)\}/g, "<strong>$1</strong>")
    .replace(/\\textit\{([^{}]*)\}/g, "<em>$1</em>")
    .replace(/\\emph\{([^{}]*)\}/g, "<em>$1</em>")
    .replace(/\\text(?:rm|sf|tt)?\{([^{}]*)\}/g, "$1");
  out = out.replace(/\\\\/g, "<br>");          // line breaks
  out = out.replace(/\\[,;:! ]/g, " ").replace(/~/g, "&nbsp;"); // spacing
  out = out.replace(/\\([.,&%#_$])/g, "$1");   // escaped punctuation
  out = out.replace(/\s*\n\s*/g, " ");         // source newline = space
  return out;
}

function renderMath(tex, display) {
  // throwOnError:false so half-typed input shows KaTeX's own red marker rather
  // than blanking the whole preview.
  return katex.renderToString(tex, {
    displayMode: display,
    throwOnError: false,
    errorColor: "#ff6b6b",
    trust: false,
  });
}

function renderEnv(name, inner) {
  if (KATEX_ENVS.has(name)) {
    return renderMath(`\\begin{${name}}${inner}\\end{${name}}`, true);
  }
  // equation, equation*, multline, displaymath... : KaTeX has no such
  // environment, so drop the wrapper and render the body as display math.
  const body = /\\\\/.test(inner) ? `\\begin{gathered}${inner}\\end{gathered}` : inner;
  return renderMath(body, true);
}

export function renderLatexFragment(raw) {
  let out = "";
  let text = "";
  let i = 0;
  const n = raw.length;
  const flush = () => {
    if (text) {
      out += renderText(text);
      text = "";
    }
  };

  while (i < n) {
    const two = raw.substr(i, 2);

    if (raw.startsWith("\\begin{", i)) {
      const match = /^\\begin\{([^}]+)\}/.exec(raw.slice(i));
      const name = match[1];
      const endToken = `\\end{${name}}`;
      const end = raw.indexOf(endToken, i + match[0].length);
      if (end !== -1) {
        flush();
        out += `<div class="my-1">${renderEnv(name, raw.slice(i + match[0].length, end))}</div>`;
        i = end + endToken.length;
        continue;
      }
    }
    if (two === "$$") {
      const end = raw.indexOf("$$", i + 2);
      if (end !== -1) {
        flush();
        out += renderMath(raw.slice(i + 2, end), true);
        i = end + 2;
        continue;
      }
    }
    if (two === "\\[" || two === "\\(") {
      const close = two === "\\[" ? "\\]" : "\\)";
      const end = raw.indexOf(close, i + 2);
      if (end !== -1) {
        flush();
        out += renderMath(raw.slice(i + 2, end), two === "\\[");
        i = end + 2;
        continue;
      }
    }
    if (raw[i] === "$" && raw[i - 1] !== "\\") {
      let j = i + 1;
      while (j < n && !(raw[j] === "$" && raw[j - 1] !== "\\")) j++;
      if (j < n) {
        flush();
        out += renderMath(raw.slice(i + 1, j), false);
        i = j + 1;
        continue;
      }
    }

    text += raw[i];
    i++;
  }
  flush();
  return out;
}
