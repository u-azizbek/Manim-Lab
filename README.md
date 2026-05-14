
# Manim Lab

My personal mathematical animation workspace, built on [3b1b/manim](https://github.com/3b1b/manim) (not the community edition).

## Setup

### Prerequisites

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- LaTeX: `brew install --cask mactex` (macOS)

### Install

```sh
# Clone manimgl from source
git clone https://github.com/3b1b/manim.git ~/manim

# Create and activate the conda environment
conda create -n manim python=3.11
conda activate manim

# Install manimgl and its dependencies
pip install -e ~/manim
pip install -r ~/manim/requirements.txt
```

### Configure

Edit `custom_config.yml` to set your output directory:

```yaml
directories:
  base: "/your/output/path/"
```

## Running Scenes

Activate the environment first (every new terminal):

```sh
conda activate manim
```

Run a scene from the project root:

```sh
cd _2026/<project>
manimgl <file>.py <SceneName>
```

| Flag | Effect |
|---|---|
| _(none)_ | Open interactive preview window |
| `-w` | Render to file |
| `-p` | Preview without saving |
| `-se <line>` | Drop into interactive debugger at that line |

## Interactive Development

Drop into a scene at a specific line:

```sh
manimgl <file>.py <SceneName> -se 42
```

In the iPython terminal that opens, use `checkpoint_paste()` to run code from your clipboard:

```python
checkpoint_paste()          # run with animation
checkpoint_paste(skip=True) # run instantly (no animation)
checkpoint_paste(record=True) # render the clip to file
```

## Project Structure

```
_2026/          ← active animation projects
custom/         ← reusable components (characters, backdrops, etc.)
once_useful_constructs/ ← legacy utility classes
sublime_custom_commands/ ← Sublime Text integration
manim_imports_ext.py ← universal import (use at top of every scene file)
custom_config.yml    ← local paths and rendering settings
```

Every scene file should start with:

```python
from manim_imports_ext import *
```