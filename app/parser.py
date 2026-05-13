import io
from pathlib import Path

from pydantic import BaseModel, Field
from pypdf import PdfReader

from .ai_client import CHAT_MODEL, client


class LLMProfile(BaseModel):
    skills: list[str] = Field(default_factory=list)
    experience_years: float | None = None


def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    raise ValueError(f"Unsupported file type: {suffix}")


def parse_profile_with_llm(text: str, kind: str) -> LLMProfile:
    if not text.strip():
        return LLMProfile()

    response = client.responses.parse(
        model=CHAT_MODEL,
        input=[
            {
                "role": "system",
                "content": (
                    f"Extract skills and years of experience from the provided {kind}. "
                    "Use short skill names and omit duplicates."
                ),
            },
            {"role": "user", "content": text},
        ],
        text_format=LLMProfile,
    )

    return response.output_parsed or LLMProfile()
