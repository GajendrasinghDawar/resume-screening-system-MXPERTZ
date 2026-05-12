# Smart Resume Screening System (AI-Powered)

This project screens resumes against a job description, returns a match score,
matched/missing skills, and a short explanation.

## Step-by-step setup (uv)

1. Create the environment and install dependencies:

```bash
uv sync
```

2. Run the API:

```bash
uv run uvicorn main:app --reload
```

4. Open the docs:

```
http://127.0.0.1:8000/docs
```

## Environment

Set these variables for Azure OpenAI access:

- AZURE_API_KEY
- AZURE_ENDPOINT (optional if using the default in ai_client.py)
- AZURE_CHAT_DEPLOYMENT (default: gpt-5.1-codex-mini)
- AZURE_EMBEDDING_DEPLOYMENT (default: text-embedding-3-large)

## API

Endpoint: `POST /screening`

### Request body (multipart form)

Use a multipart form with a text field and one or more PDF files:

```bash
curl -X POST "http://127.0.0.1:8000/screening" \
  -F "job_description=We need a Python developer with FastAPI, SQL, and AWS." \
  -F "resumes=@/path/to/resume_1.pdf" \
  -F "resumes=@/path/to/resume_2.pdf"
```

### Response (example)

```json
{
  "job_description_preview": "We need a Python developer with FastAPI, SQL, and AWS.",
  "total_resumes": 2,
  "matcher_mode": "embedding",
  "results": [
    {
      "filename": "resume_1.pdf",
      "score": 78.0,
      "matched_skills": ["python", "fastapi", "aws"],
      "missing_skills": ["sql"],
      "experience_years": 3,
      "explanation": "Similarity score is 78.0/100 based on JD vs resume text. Matched skills: python, fastapi, aws. Missing skills: sql."
    }
  ]
}
```

## Approach

1. **Skill extraction (mandatory):**

- Azure OpenAI extracts skills from both the job description and resumes.

2. **Experience (optional):**

- Azure OpenAI extracts years of experience when stated.

3. **Matching logic:**

- Embeddings + cosine similarity on JD vs resume text.

4. **Explanation:**

- 2-3 line summary including score and skill gaps.

## Code walkthrough

See [docs/implementation.md](docs/implementation.md) for a short explanation of how the
modules work together.

## Timeline

- 1-2 hours: basic API + schema + TF-IDF matching
- 1 hour: skill extraction and explanation
- 30 min: README and sample request
