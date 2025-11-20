from datetime import datetime
from langgraph.graph import StateGraph, END, add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel
from typing import Annotated
from langchain_core.messages import SystemMessage, BaseMessage
from langchain.tools import tool
from app.modules.agent_chat.llm import llm
from app.infra.config import Config
from app.infra.core_dependency_container import container
from app.modules.agent_chat.V1_multiagent.prompts import editais_prompt

qdrant_service = container.bd_vetorial_service

# ESTADO DO AGENTE
class State(BaseModel):
    """Estado do agente de editais."""
    messages: Annotated[list[BaseMessage], add_messages] = []


# TOOL DE RAG
@tool
async def rag_tool(query: str):
    """Busca informações sobre pedidos de patente em uma base de conhecimento (RAG).

    Args:
        query: Pergunta feita pelo usuário.

    Returns:
        Texto com informações relevantes sobre o tema pesquisado.
    """
    docs = qdrant_service.buscar(query, search_type="hybrid")

    if not docs:
        print("sem docs")
        return "Nenhuma informação relevante encontrada."
    
    results = []
    for i, doc in enumerate(docs.points):
        results.append(f"{doc.payload['page_content']}\n")
    
    return "".join(results)


tools = [rag_tool]
llm_with_tools = llm.bind_tools(tools)


# NÓ PRINCIPAL DO AGENTE
async def editais_agent(state: State):
    """Agente responsável por responder dúvidas sobre editais abertos."""
   
    system_prompt = SystemMessage(content=editais_prompt.format(current_datetime=datetime.now()))

    response = llm_with_tools.invoke([system_prompt] + state.messages)

    return {"messages": [response]}


# ROTEAMENTO DE TOOLS
async def editais_router(state: State) -> str:
    """Roteia a execução entre o LLM e a ferramenta RAG."""
    if state.messages[-1].tool_calls:
        return "tools"
    return END


# CONSTRUÇÃO DO GRAFO
builder = StateGraph(State)

builder.add_node(editais_agent)
builder.add_node("tools", ToolNode(tools))

builder.set_entry_point("editais_agent")

builder.add_conditional_edges(
    "editais_agent",
    editais_router,
    {
        "tools": "tools",
        END: END,
    }
)
builder.add_edge("tools", "editais_agent")

graph = builder.compile()