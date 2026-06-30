import json

from app.config import settings
from app.services.embedding import client


def analyze_match(jd_text: str, resume_chunks: list[str]) -> dict:
    if not resume_chunks:
        return {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [
                "No resume data found. Please upload your resume first."
            ],
            "positioning_advice": "Upload your resume before requesting analysis.",
        }
    chunks_text = "\n\n".join(resume_chunks)

    prompt = f"""You are a career advisor analyzing resume fit for a job description.

    RESUME SECTIONS:
    {chunks_text}

    JOB DESCRIPTION:
    {jd_text}

    Return ONLY a JSON object with these exact fields:
    - match_score: integer 0-100
    - matched_skills: list of strings
    - missing_skills: list of strings
    - positioning_advice: string

    No markdown, no explanation. JSON only."""

    response = client.models.generate_content(model=settings.LLM_MODEL, contents=prompt)

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]  # remove first line (```json)
        text = text.rsplit("```", 1)[0]  # remove last ```
    return json.loads(text)
