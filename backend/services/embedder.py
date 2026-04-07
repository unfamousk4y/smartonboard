import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_API_KEY")
API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

def get_embedding(text: str) -> list[float]:
response = requests.post(
API_URL,
headers={"Authorization": f"Bearer {HF_TOKEN}"},
json={"inputs": text}
)
return response.json()[0]
