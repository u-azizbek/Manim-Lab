from __future__ import annotations

import ast
import base64
import re

from anthropic import Anthropic

from .prompt import build_system_prompt, build_user_prompt
from .settings import settings


FENCE = re.compile(r"^\s*```(?:python)?\s*\n(.*?)\n```\s*$", re.DOTALL)


class GenerationError(RuntimeError):
    pass


def _client() -> Anthropic:
    if not settings.anthropic_api_key:
        raise GenerationError(
            "ANTHROPIC_API_KEY is not set. Put it in your shell or in a .env "
            "file next to docker-compose.yml, then restart the stack."
        )
    return Anthropic(api_key=settings.anthropic_api_key)


def strip_fences(text: str) -> str:
    """Models sometimes wrap the file in a code fence despite being asked not
    to; unwrap it rather than failing to compile."""
    match = FENCE.match(text.strip())
    return match.group(1) if match else text.strip()


def find_scene_class(code: str) -> str:
    """The name of the scene to render, read out of the generated source."""
    try:
        tree = ast.parse(code)
    except SyntaxError as err:
        raise GenerationError(f"generated file is not valid Python: {err}") from err

    names = [
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and any(getattr(base, "id", "") == "MockTestShort" for base in node.bases)
    ]
    if not names:
        raise GenerationError("generated file defines no MockTestShort subclass")
    return names[0]


def generate_scene(
    image_bytes: bytes,
    media_type: str,
    test: str,
    question: int,
    notes: str = "",
) -> str:
    """Turn a photo of a problem into a scene file."""
    message = _client().messages.create(
        model=settings.model,
        max_tokens=settings.max_tokens,
        system=build_system_prompt(),
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": base64.b64encode(image_bytes).decode(),
                    },
                },
                {"type": "text", "text": build_user_prompt(test, question, notes)},
            ],
        }],
    )
    text = "".join(block.text for block in message.content if block.type == "text")
    if not text.strip():
        raise GenerationError("model returned no code")
    return strip_fences(text)


def repair_scene(code: str, error: str, test: str, question: int) -> str:
    """Second pass: hand back the traceback and ask for a corrected file."""
    message = _client().messages.create(
        model=settings.model,
        max_tokens=settings.max_tokens,
        system=build_system_prompt(),
        messages=[
            {"role": "user", "content": build_user_prompt(test, question)},
            {"role": "assistant", "content": code},
            {
                "role": "user",
                "content": (
                    "Rendering that file failed. Fix the cause and return the "
                    "complete corrected file, code only.\n\n"
                    f"```\n{error[-4000:]}\n```"
                ),
            },
        ],
    )
    text = "".join(block.text for block in message.content if block.type == "text")
    if not text.strip():
        raise GenerationError("model returned no code on the repair attempt")
    return strip_fences(text)
