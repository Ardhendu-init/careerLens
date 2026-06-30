from google import genai
from google.genai import types

from app.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY.get_secret_value())


def embed_text(text: str) -> list[float]:
    result = client.models.embed_content(
        model=settings.EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768),
    )
    return result.embeddings[0].values
