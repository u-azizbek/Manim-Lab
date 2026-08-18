from __future__ import annotations

from pathlib import Path

from .settings import settings


# Read the real template and real examples out of the repo at request time, so
# the prompt cannot drift from the code the videos are actually built on.
TEMPLATE_FILE = "custom/mock_tests.py"
STEP_LIST_FILE = "custom/shorts.py"
EXAMPLE_FILES = [
    "Calculus Mock Tests/Foundation Tests/F1/f1_21_matrix_equation.py",
    "Calculus Mock Tests/Foundation Tests/F1/f1_37_integral_equation.py",
]

INSTRUCTIONS = """\
You write ManimGL scene files for a YouTube Shorts channel that solves \
problems from a calculus workbook. You will be shown a photo or screenshot of \
one problem. Work the problem out, then return one Python file that animates \
the solution.

Follow the house template exactly. The reference material below is the real \
source from the repository your file will run inside.

Hard requirements:
- The file starts with `from manim_imports_ext import *` and imports nothing else.
- Define exactly one class, subclassing `MockTestShort`.
- Name the class `{test}Q{question}` with the test id upper-cased, e.g. `F1Q21`.
- Set `test` and `question` to the values given in the user message.
- Set `problem_tex` to the problem statement, restated compactly. Use `\\\\` to \
break lines; the card centres each line. Never include the multiple-choice options.
- `sections` lists your section method names in order and ends with `"outro"`. \
The first entry is `"pose"`, which the base class already implements.
- Every section method other than `pose` and `outro` must be defined on the class \
and must call `self.get_card()` first.
- Finish with `self.conclude(...)` inside the last section before the outro, \
passing the final answer as a tex string.
- Colour roles: `SETUP_COLOR` for restating and naming, `RULE_COLOR` for the key \
identity or trick, and `self.conclude` handles the answer. All three constants \
are already imported.
- Total runtime must stay under 60 seconds. Aim for four to seven steps.

ManimGL details that differ from Manim Community, and things that break:
- Use `Tex(...)` and `TexText(...)`. `MathTex` does not exist.
- Always use raw strings for LaTeX: `R"\\frac{1}{2}"`.
- `Tex` renders inside `align*`. `\\begin{pmatrix}` and friends are available.
- When splitting a long tex string across adjacent Python string literals, make \
sure the join does not weld two commands together: `R"... \\quad "` then `R"B = ..."`, \
never `R"... \\quad"` then `R"B = ..."`.
- Do not pass `color=` to `Tex`; use `.set_color(...)` or the `color=` argument \
of `add_step` / `transform_step`.
- Available step helpers, from the base classes shown below: `self.add_step(tex, \
color=, font_size=, wait=)`, `self.transform_step(source, tex, ...)` which grows a \
line out of an earlier one, and `self.conclude(tex)`.
- `step_buff` controls the gap between steps. Set it as a class attribute so the \
last line lands around 75% of the frame height: use roughly 0.5 for seven steps, \
0.85 for six, and 1.0 for five or fewer.

Output format: return only the contents of the Python file. No markdown fences, \
no commentary before or after.
"""


def _read(relative: str) -> str:
    path = settings.repo_dir / relative
    try:
        return path.read_text()
    except OSError as err:                       # pragma: no cover - setup issue
        return f"# unavailable ({err})"


def _step_list_mixin() -> str:
    """Just the StepListMixin part of custom/shorts.py -- the rest is framing
    detail the model does not need."""
    source = _read(STEP_LIST_FILE)
    marker = "class StepListMixin"
    index = source.find(marker)
    return source[index:] if index != -1 else source


def build_system_prompt() -> str:
    blocks = [
        INSTRUCTIONS,
        f"\n\n# Reference: {TEMPLATE_FILE}\n\n```python\n{_read(TEMPLATE_FILE)}\n```",
        f"\n\n# Reference: StepListMixin from {STEP_LIST_FILE}\n\n"
        f"```python\n{_step_list_mixin()}\n```",
    ]
    for name in EXAMPLE_FILES:
        blocks.append(f"\n\n# Worked example: {name}\n\n```python\n{_read(name)}\n```")
    return "".join(blocks)


def build_user_prompt(test: str, question: int, notes: str = "",
                      problem: str = "") -> str:
    lines = [
        f"This problem is {test}:{question} in the workbook.",
        f"Set `test = \"{test}\"` and `question = {question}`, "
        f"so the card is tagged {test}:{question}.",
    ]
    if problem.strip():
        lines.append(
            "\nThe author typed the problem out rather than sending a photo:"
            f"\n\n{problem.strip()}\n\n"
            "Keep the mathematics exactly as written, but format it into a single "
            "compact `problem_tex` for the card, which is one math-mode `Tex`: wrap "
            "any prose words in `\\text{...}`, replace display environments like "
            "`\\begin{equation*}...\\end{equation*}` with just their inner "
            "expression, use `\\\\` for line breaks, and drop any "
            "multiple-choice options. Do not reword the problem."
        )
    lines.append("Solve it, then write the scene file.")
    if notes.strip():
        lines.append(f"\nExtra direction from the author:\n{notes.strip()}")
    return "\n".join(lines)
