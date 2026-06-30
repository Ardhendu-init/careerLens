def chunk_text(text: str, max_len: int = 1500) -> list[str]:
    chunks: list[str] = []
    for para in text.split("\n\n"):
        para = para.strip()
        if len(para) <= 20:
            continue
        # break paragraphs that would overflow the chunks.text column
        for i in range(0, len(para), max_len):
            chunks.append(para[i : i + max_len])
    return chunks
