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
uv run uvicorn app.main:app --reload
```

3. Open the docs:

```
http://127.0.0.1:8000/docs
```

## Environment

Set these variables for Azure OpenAI access (reviewers should provide their own key):

- AZURE_API_KEY
- AZURE_ENDPOINT (optional if using the default in ai_client.py)
- AZURE_CHAT_DEPLOYMENT (default: gpt-5.1-codex-mini)
- AZURE_EMBEDDING_DEPLOYMENT (default: text-embedding-3-large)

## API

Endpoint: `POST /screening`

### Request body (multipart form)

Use a multipart form with a text field and one PDF file:

```bash
curl -X POST "http://127.0.0.1:8000/screening" \
  -F "job_description=We need a Python developer with FastAPI, SQL, and AWS." \
  -F "resumes=@/path/to/resume.pdf"
```

### Response (example)

```json
{
  "job_description_preview": "We need a Python developer with FastAPI, SQL, and AWS.",
  "total_resumes": 1,
  "results": [
    {
      "filename": "resume.pdf",
      "score": 78.0,
      "matched_skills": ["python", "fastapi", "aws"],
      "missing_skills": ["sql"],
      "experience_years": 3,
      "explanation": "Embedding similarity 78.0/100 between job description and resume. Matched skills: python, fastapi, aws. Missing skills: sql."
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

The code is organized into `app/main.py`, `app/parser.py`, and `app/matcher.py` with
short comments explaining each step.

## Timeline

- 1-2 hours: basic API + PDF parsing + LLM extraction
- 1 hour: embeddings + scoring logic
- 30 min: README and sample request
