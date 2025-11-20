from langchain_groq import ChatGroq
from app.infra.config import Config

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    api_key=Config.GROQ_API_KEY
)


#llama-3.1-8b-instant