import json

from app.services.embedding import client


def analyze_match(jd_text: str, resume_chunks: list[str]) -> dict:
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

    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    return json.loads(response.text)
