from fastapi import APIRouter, UploadFile, File, HTTPException
from services.chunker import chunk_text
from services.embedder import get_embedding
import psycopg2
import os
from dotenv import load_dotenv
import pypdf
import io

load_dotenv()

router = APIRouter()

def get_db():
	return psycopg2.connect(
		host="ep-orange-sea-anek5ugr.c-6.us-east-1.aws.neon.tech",
		port=5432,
		dbname="neondb",
		user="neondb_owner",
		password=os.getenv("NEON_PASSWORD"),
		sslmode="require"
	)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
	if not file.filename.endswith(".pdf"):
		raise HTTPException(status_code=400, detail="Only PDF files accepted")

	contents = await file.read()
	pdf = pypdf.PdfReader(io.BytesIO(contents))

	full_text = ""
	for page in pdf.pages:
		full_text += page.extract_text() or ""

	chunks = chunk_text(full_text)

	conn = get_db()
	cur = conn.cursor()

	cur.execute(
		"INSERT INTO documents (name) VALUES (%s) RETURNING id",
		(file.filename,)
	)
	document_id = cur.fetchone()[0]

	for i, chunk in enumerate(chunks):
		cur.execute(
			"INSERT INTO chunks (document_id, content, chunk_index) VALUES (%s, %s, %s) RETURNING id",
			(document_id, chunk, i)
		)
		chunk_id = cur.fetchone()[0]

		embedding = get_embedding(chunk)

		cur.execute(
			"INSERT INTO embeddings (chunk_id, embedding) VALUES (%s, %s)",
			(chunk_id, str(embedding))
		)

	conn.commit()
	cur.close()
	conn.close()

	return {"message": f"Uploaded and indexed {len(chunks)} chunks", "document_id": document_id}




