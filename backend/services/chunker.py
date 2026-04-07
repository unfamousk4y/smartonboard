import tiktoken

def chunk_text(text: str, max_tokens: int = 512, overlap: int = 50) -> list[str]:
	encoder = tiktoken.get_encoding("cl100k_base")
	tokens = encoder.encode(text)
	chunks = []
	start = 0

	while start < len(tokens):
		end = start + max_tokens
		chunk_tokens = tokens[start:end]
		chunks.append(encoder.decode(chunk_tokens))
		start += max_tokens - overlap

	return chunks

