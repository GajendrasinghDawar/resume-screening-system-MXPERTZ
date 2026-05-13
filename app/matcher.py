import re

from .ai_client import EMBEDDING_MODEL, client


def _normalize(skills: list[str]) -> list[str]:
    out: list[str] = []
    for s in skills:
        cleaned = re.sub(r"\s+", " ", str(s or "").strip().lower())
        if cleaned:
            out.append(cleaned)
    return sorted(set(out))


def _embed(text: str) -> list[float]:
    # Generate a semantic embedding vector using Azure OpenAI.
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


def _cosine(a: list[float], b: list[float]) -> float:
    # Cosine similarity: (a · b) / (||a|| * ||b||)

    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def score_resume(
    jd_text: str,
    resume_text: str,
    filename: str,
    jd_skills: list[str],
    resume_skills: list[str],
    experience_years: float | None,
) -> dict:
    # Semantic similarity score between job description and resume text, scaled to 0-100.
    similarity = _cosine(_embed(jd_text), _embed(resume_text))
    score = round(max(0.0, min(1.0, similarity)) * 100, 2)

    # Normalize skill lists for case-insensitive matching and compute gaps.
    jd_norm = _normalize(jd_skills)
    resume_norm = set(_normalize(resume_skills))
    matched = [s for s in jd_norm if s in resume_norm]
    missing = [s for s in jd_norm if s not in resume_norm]

    # Short explanation for the API response.
    matched_preview = ", ".join(matched[:5]) or "no direct skill matches"
    missing_preview = ", ".join(missing[:5]) or "no missing skills"
    explanation = (
        f"Embedding similarity {score}/100 between job description and resume. "
        f"Matched skills: {matched_preview}. Missing skills: {missing_preview}."
    )

    return {
        "filename": filename,
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "experience_years": experience_years,
        "explanation": explanation,
    }
