import re

CODE_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
URL_RE = re.compile(r"https?://\S+")


def clean_text(text: str | None) -> str:
    if not text:
        return ""
    text = CODE_BLOCK_RE.sub(" ", text)
    text = URL_RE.sub(" ", text)
    return " ".join(text.split())
