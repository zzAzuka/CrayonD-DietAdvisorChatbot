from pinecone import Pinecone
import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PC_API_KEY"))
PINECONE_INDEX = pc.Index("diet-bot-index-v2")

CHAT_MODEL = "gemini-1.5-pro"
EMBEDDING_MODEL = "models/text-embedding-004"

EMBEDDER = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    google_api_key=os.getenv("GEM_API_KEY")
)

LLM = ChatGoogleGenerativeAI(
    model=CHAT_MODEL,
    temperature=0.7,
    google_api_key=os.getenv("GEM_API_KEY")
)