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

from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException
from fastapi import UploadFile as FastAPIUploadFile
from pydantic import BaseModel, WithJsonSchema

from app.utils import store_text, store_upload

from .matcher import score_resume
from .parser import extract_text, parse_profile_with_llm

load_dotenv()


app = FastAPI(
    title="Smart Resume Screening System",
    description="AI-powered resume screening (Azure OpenAI embeddings).",
    version="1.0.0",
)


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


# type alias to fix swagger ui multiple file upload bug.
UploadFileBinary = Annotated[
    FastAPIUploadFile,
    WithJsonSchema({"type": "string", "format": "binary"}),
]


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

        stored_name = store_upload(upload.filename, content)

        try:
            text = extract_text(upload.filename or "resume", content)
        except ValueError as exc:
            raise HTTPException(400, f"Failed to parse {upload.filename}: {exc}")
        if not text.strip():
            continue

        store_text(stored_name, text)

        resume_profile = parse_profile_with_llm(text, kind="resume")

        match = score_resume(
            jd_text=job_description,
            resume_text=text,
            filename=upload.filename or stored_name,
            jd_skills=jd_profile.skills,
            resume_skills=resume_profile.skills,
            experience_years=resume_profile.experience_years,
        )

        results.append(ResumeMatch(**match))

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
