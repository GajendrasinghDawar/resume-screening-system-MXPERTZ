"""
Smart Resume Screening System - FastAPI app.

Single endpoint:
    POST /screening
        Form fields:
            job_description: str   (required)
            resumes:        files  (one or more PDF only)
        Returns: ranked list of matches with score, matched/missing skills,
                 and a short explanation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException
from fastapi import UploadFile as FastAPIUploadFile
from pydantic import BaseModel, WithJsonSchema

from .matcher import score_resume
from .parser import extract_text, parse_profile_with_llm

load_dotenv()

RESUME_DIR = Path("storage/resumes")
TEXT_DIR = Path("storage/text")
RESUME_DIR.mkdir(parents=True, exist_ok=True)
TEXT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Smart Resume Screening System",
    description="AI-powered resume screening (Azure OpenAI embeddings).",
    version="1.0.0",
)

UploadFileBinary = Annotated[
    FastAPIUploadFile,
    WithJsonSchema({"type": "string", "format": "binary"}),
]


class ResumeMatch(BaseModel):
    filename: str
    score: float
    matched_skills: list[str]
    missing_skills: list[str]
    experience_years: float | None
    explanation: str


class ScreenResponse(BaseModel):
    job_description_preview: str
    total_resumes: int
    results: list[ResumeMatch]


def _store_upload(filename: str | None, content: bytes) -> str:
    safe_name = (filename or "resume").replace(" ", "_")
    stored_name = f"{Path(safe_name).stem}_{uuid4().hex}{Path(safe_name).suffix}"
    (RESUME_DIR / stored_name).write_bytes(content)
    return stored_name


def _store_text(filename: str, text: str) -> None:
    (TEXT_DIR / f"{Path(filename).stem}.txt").write_text(text, encoding="utf-8")


@app.get("/")
def root() -> dict:
    return {
        "service": "Smart Resume Screening System",
        "endpoint": "POST /screening",
        "docs": "/docs",
    }


@app.post("/screening", response_model=ScreenResponse)
async def screen_resumes(
    job_description: Annotated[
        str, Form(..., description="Plain-text job description.")
    ],
    resumes: Annotated[
        list[UploadFileBinary], File(..., description="Resume files (PDF only).")
    ],
) -> ScreenResponse:
    if not job_description.strip():
        raise HTTPException(400, "job_description must not be empty.")
    if not resumes:
        raise HTTPException(400, "At least one resume file is required.")

    jd_profile = parse_profile_with_llm(job_description, kind="job description")

    results: list[ResumeMatch] = []

    for upload in resumes:
        if not (upload.filename or "").lower().endswith(".pdf"):
            raise HTTPException(400, "Only PDF resumes are supported.")

        content = await upload.read()
        if not content:
            continue

        stored_name = _store_upload(upload.filename, content)

        try:
            text = extract_text(upload.filename or "resume", content)
        except ValueError as exc:
            raise HTTPException(400, f"Failed to parse {upload.filename}: {exc}")
        if not text.strip():
            continue

        _store_text(stored_name, text)

        resume_profile = parse_profile_with_llm(text, kind="resume")

        match = score_resume(
            jd_text=job_description,
            resume_text=text,
            filename=upload.filename or stored_name,
            jd_skills=jd_profile.skills,
            resume_skills=resume_profile.skills,
            experience_years=resume_profile.experience_years,
        )

        results.append(ResumeMatch(**match.__dict__))

    results.sort(key=lambda r: r.score, reverse=True)

    preview = (
        (job_description[:200] + "...")
        if len(job_description) > 200
        else job_description
    )
    return ScreenResponse(
        job_description_preview=preview,
        total_resumes=len(results),
        results=results,
    )
