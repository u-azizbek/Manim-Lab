from __future__ import annotations

import json
import os
import re

from manimlib import *

from custom.outro import PURPLE_LIGHT


# Highlight keys usable in captions: "Obviously, this divides {y:the circle into two}"
CAPTION_COLORS = {
    "y": "#FFE14D",          # yellow: the key phrase of the line
    "b": "#58C4DD",          # blue: the second idea, or the object being named
    "p": PURPLE_LIGHT,       # neuro purple: the twist, or the channel's own words
    "g": "#5BD98A",
    "r": "#FF6B6B",
    "w": WHITE,
}
MARKUP = re.compile(r"\{([a-z]):([^{}]*)\}")


def parse_caption(text: str) -> list[tuple[str, str | None]]:
    """Split marked-up text into (word, colour key) pairs."""
    words = []
    position = 0
    for match in MARKUP.finditer(text):
        words += [(w, None) for w in text[position:match.start()].split()]
        words += [(w, match.group(1)) for w in match.group(2).split()]
        position = match.end()
    words += [(w, None) for w in text[position:].split()]
    return words


def plain_text(text: str) -> str:
    """The caption without its markup, as a sentence."""
    return " ".join(word for word, _ in parse_caption(text))


def srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


class NarrationMixin:
    """NARRATED shorts: big two-line captions that an AI voice will later read.

    `self.say(text, *animations)` shows a caption, plays any animations under
    it, and holds the caption for as long as a voice needs to read it.  Every
    line is logged with its start and end time, and after a render three files
    are written next to the video:

        <Scene>.txt    the voice script, one line per caption
        <Scene>.srt    the same with timings (players load it as subtitles)
        <Scene>.json   everything, for scripting the voice-over

    Mix it in first:  class MyShort(NarrationMixin, BrandOutroMixin, ShortsScene)
    """

    caption_font = "Avenir Next"
    caption_weight = "HEAVY"
    caption_font_size = 62
    caption_y = -3.4             # centre of the caption block
    caption_max_width = 7.2
    caption_chars_per_line = 24  # longest line; more than two lines logs a warning
    caption_upper = True
    caption_backstroke = 8       # black outline, so captions read over a figure

    speech_wps = 2.6             # words per second of the voice (about 155 wpm)
    speech_pad = 0.35            # breath after each line
    min_caption_time = 1.2

    # Spoken over the outro badge; no caption.  Empty to stay quiet.
    outro_line = "Follow for a new math puzzle every day."

    # Building captions

    def make_caption(self, text: str) -> Text:
        words = parse_caption(text)
        lines = self.balance_lines(words)
        if len(lines) > 2:
            log.warning(f"Caption runs to {len(lines)} lines, split it in two: {plain_text(text)!r}")

        # Lay the string out and remember which character spans get colours
        string, t2c = "", {}
        for i, line in enumerate(lines):
            if i > 0:
                string += "\n"
            for j, (word, key) in enumerate(line):
                if j > 0:
                    string += " "
                if self.caption_upper:
                    word = word.upper()
                if key is not None:
                    t2c[(len(string), len(string) + len(word))] = CAPTION_COLORS[key]
                string += word

        caption = Text(
            string, font=self.caption_font, weight=self.caption_weight,
            font_size=self.caption_font_size, alignment="CENTER", t2c=t2c,
        )
        caption.set_max_width(self.caption_max_width)
        caption.set_backstroke(BLACK, self.caption_backstroke)
        return caption

    def balance_lines(self, words):
        """Break words into as few lines as the width allows, all about the
        same length, so no word hangs on a line of its own.  A highlighted
        phrase stays on one line whenever it fits, as in the references."""
        limit = self.caption_chars_per_line
        units = []
        for word, key in words:
            if units and key is not None and units[-1][-1][1] == key:
                units[-1].append((word, key))
            else:
                units.append([(word, key)])
        units = [
            piece for unit in units
            for piece in ([unit] if self.width_of(unit) <= limit else [[w] for w in unit])
        ]

        total = self.width_of([w for unit in units for w in unit])
        count = max(1, -(-total // limit))
        target = total / count
        lines, line = [], []
        for unit in units:
            grown = self.width_of(line + unit)
            if line and len(lines) < count - 1 and grown - target > target - self.width_of(line):
                lines.append(line)
                line = []
            line = line + unit
        lines.append(line)
        return lines

    @staticmethod
    def width_of(words) -> int:
        return sum(len(word) for word, _ in words) + max(len(words) - 1, 0)

    def speech_time(self, spoken: str) -> float:
        words = len(spoken.split())
        return max(self.min_caption_time, words / self.speech_wps + self.speech_pad)

    # The transcript

    def transcript(self) -> list[dict]:
        if not hasattr(self, "_transcript"):
            self._transcript = []
        return self._transcript

    def open_line(self, text: str, speak: str | None, caption: bool) -> dict:
        entry = dict(
            text=plain_text(text), speak=speak or plain_text(text),
            start=round(self.time, 3), end=None, caption=caption,
        )
        self.transcript().append(entry)
        return entry

    def close_line(self, entry: dict | None, at: float | None = None):
        if entry is not None and entry["end"] is None:
            entry["end"] = round(self.time if at is None else at, 3)

    # Saying things

    def say(self, text: str, *animations, speak: str | None = None,
            run_time: float | None = None, wait: bool = True,
            y: float | None = None, fade_time: float = 0.3) -> Text:
        """Show `text` as the caption (replacing the last one), play
        `animations` under it, then hold until the voice would be done.

        Mark highlights with {y:...}, {b:...}, {p:...} (see CAPTION_COLORS).
        Write the caption as it should be *read*; when the screen should
        show something else (digits, symbols), pass the spoken form as
        `speak="two to the fifth is thirty-two"`.
        """
        caption = self.make_caption(text)
        caption.move_to((self.caption_y if y is None else y) * UP)

        start = self.time
        old = getattr(self, "_caption", None)
        self.close_line(getattr(self, "_caption_line", None))
        entry = self.open_line(text, speak, caption=True)

        fades = [FadeIn(caption, 0.12 * UP)]
        if old is not None:
            fades.append(FadeOut(old, 0.12 * UP))
        self.play(*fades, run_time=fade_time)
        if animations:
            kwargs = {} if run_time is None else dict(run_time=run_time)
            self.play(*animations, **kwargs)

        remaining = self.speech_time(entry["speak"]) - (self.time - start)
        if wait and remaining > 0:
            self.wait(remaining)

        self._caption, self._caption_line = caption, entry
        return caption

    def hold(self, extra: float = 0.0):
        """Wait until the voice would finish the current caption.  Pairs with
        `say(..., wait=False)` when a line covers several separate plays."""
        entry = getattr(self, "_caption_line", None)
        if entry is None:
            return
        remaining = entry["start"] + self.speech_time(entry["speak"]) - self.time + extra
        if remaining > 0:
            self.wait(remaining)

    def unsay(self, run_time: float = 0.3):
        """Clear the current caption."""
        caption = getattr(self, "_caption", None)
        if caption is not None:
            self.play(FadeOut(caption, 0.12 * UP), run_time=run_time)
        self.close_line(getattr(self, "_caption_line", None))
        self._caption, self._caption_line = None, None

    def narrate(self, speak: str, wait: bool = True):
        """A voice-only line: logged in the transcript, nothing on screen.
        For moments when the screen already shows what is being said."""
        self.close_line(getattr(self, "_caption_line", None))
        entry = self.open_line(speak, speak, caption=False)
        duration = self.speech_time(speak)
        if wait:
            self.wait(duration)
            self.close_line(entry)
        else:
            entry["end"] = round(self.time + duration, 3)
        return entry

    # Hooks into the rest of the scene

    def outro(self):
        if getattr(self, "_caption", None) is not None:
            self.unsay()
        if self.outro_line:
            self.narrate(self.outro_line, wait=False)
        super().outro()

    def write_sidecars(self):
        super().write_sidecars()
        video = self.get_video_path()
        lines = self.transcript()
        if video is None or not lines:
            return
        self.close_line(getattr(self, "_caption_line", None))
        for entry in lines:
            if entry["end"] is None:
                entry["end"] = round(self.time, 3)

        stem = os.path.splitext(video)[0]
        with open(stem + ".txt", "w") as file:
            file.write("\n".join(entry["speak"] for entry in lines) + "\n")
        with open(stem + ".srt", "w") as file:
            for i, entry in enumerate(lines, 1):
                file.write(f"{i}\n{srt_time(entry['start'])} --> {srt_time(entry['end'])}\n{entry['speak']}\n\n")
        with open(stem + ".json", "w") as file:
            json.dump(dict(
                scene=type(self).__name__,
                video=os.path.basename(video),
                duration=round(self.time, 3),
                partial=bool(os.environ.get("SECTIONS", "").strip()),
                speech_wps=self.speech_wps,
                lines=lines,
            ), file, indent=2)
