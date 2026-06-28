def chunk_text(text: str) -> list[str]:
    chunks = text.split("\n\n")

    final_chunks = [chunk.strip() for chunk in chunks if len(chunk.strip()) > 20]

    return final_chunks
