from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from app.infra.config import Config

def get_llm(temperature: float = 0.3):
   
    # Para testar local via API
    return ChatGroq(
        model=Config.LLM_MODEL,
        temperature=temperature,
        api_key=Config.GROQ_API_KEY
    )

    # Para rodar o modelo localmente
    # return ChatOllama(
    #     model=Config.LLM_MODEL,
    #     temperature=temperature
    # )