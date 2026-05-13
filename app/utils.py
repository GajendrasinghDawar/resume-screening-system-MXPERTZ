from pathlib import Path
from uuid import uuid4

RESUME_DIR = Path("storage/resumes")
RESUME_DIR.mkdir(parents=True, exist_ok=True)

TEXT_DIR = Path("storage/text")
TEXT_DIR.mkdir(parents=True, exist_ok=True)


def store_upload(filename: str | None, content: bytes) -> str:
    safe_name = (filename or "resume").replace(" ", "_")
    stored_name = f"{Path(safe_name).stem}_{uuid4().hex}{Path(safe_name).suffix}"
    (RESUME_DIR / stored_name).write_bytes(content)
    return stored_name


def store_text(filename: str, text: str) -> None:
    (TEXT_DIR / f"{Path(filename).stem}.txt").write_text(text, encoding="utf-8")
