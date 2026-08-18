import { renderLatexFragment } from "./src/latex-preview.js";

const cases = [
  String.raw`Find $\dfrac{2}{3-\sqrt{3}}+\dfrac{2}{3+\sqrt{3}}$\,.`,
  String.raw`Simplify
\begin{equation*}
  \left(\sqrt{2}+\sqrt{5}+\sqrt{7}\right)^{2}
  \left(\sqrt{2}+\sqrt{5}-\sqrt{7}\right)^{2}.
\end{equation*}`,
  String.raw`Find the sum of all natural numbers that satisfy the following
inequality.
\begin{equation*}
  \left(\log_{2}2x\right)\left(\log_{2}4x\right)\leqslant 12
\end{equation*}`,
  String.raw`Let $R(x)$ be the remainder when \\ $P(x)=x^{10}-x^{5}+2$ is divided
by $(x+1)^{2}$. \\ Find $R(-2)$.`,
];

let failed = 0;
cases.forEach((input, k) => {
  let html = "";
  try {
    html = renderLatexFragment(input);
  } catch (err) {
    console.log(`CASE ${k + 1}: THREW ${err.message}`);
    failed++;
    return;
  }
  const errs = (html.match(/katex-error/g) || []).length;
  const mathSpans = (html.match(/class="katex"/g) || []).length;
  console.log(`CASE ${k + 1}: katex-errors=${errs}  math-spans=${mathSpans}  html=${html.length}b`);
  if (errs > 0) {
    failed++;
    // show the offending titles KaTeX embeds
    for (const m of html.matchAll(/katex-error[^>]*title="([^"]*)"/g)) {
      console.log(`   error: ${m[1]}`);
    }
  }
});
console.log(failed ? `\nFAILED: ${failed} case(s) had errors` : "\nALL CASES OK");
process.exit(failed ? 1 : 0);
