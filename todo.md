- handle edge case like json file size.
- not handling times pdf parsing in hot path,
  Deliverables
  GitHub repo with working code
  README with:
  Setup steps
  How to run API
  Approach explanation

simplify open azure ok

why i havent used: TF-IDF (Term Frequency-Inverse Document Frequency) co

We use embeddings to measure **semantic similarity** between the job description and the resume, not just exact keyword overlap.

**How it works:**

1. `_embed(jd_text)` and `_embed(resume_text)` call Azure OpenAI to turn each text into a vector.
2. `_cosine(...)` compares the two vectors and returns a similarity score.

**Why we do it:**

- It captures meaning (e.g., “LLM integrations” ≈ “OpenAI API experience”).
- It’s more robust than exact keyword matching.
- The spec allows embeddings as the matching method.

So embeddings power the **score**, while skill lists power **matched/missing skills**.
