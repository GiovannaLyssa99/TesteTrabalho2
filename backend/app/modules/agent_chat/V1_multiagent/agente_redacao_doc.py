from langgraph.graph import StateGraph, END, add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel
from typing import Annotated
from langchain_core.messages import SystemMessage, BaseMessage
from langchain.tools import tool
from app.modules.agent_chat.llm import llm
from app.infra.config import Config
from app.infra.core_dependency_container import container
from app.modules.agent_chat.V1_multiagent.prompts import redacao_agent_prompt

qdrant_service = container.bd_vetorial_service

# ESTADO DO AGENTE
class State(BaseModel):
    """Estado do agente de redação de documentos de patente."""
    messages: Annotated[list[BaseMessage], add_messages] = []


# TOOL DE RAG
@tool
def rag_tool(query: str):
    """Busca informações e exemplos de redação de documentos de patente em uma base RAG.

    Args:
        query: Solicitação do usuário, como 'modelo de reivindicação independente' ou 'estrutura de relatório descritivo'.

    Returns:
        Texto com orientações ou exemplos relevantes sobre a redação solicitada.
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
async def redacao_agent(state: State):
    """Agente responsável por auxiliar na redação de documentos de patente."""

    system_prompt = SystemMessage(content=redacao_agent_prompt)

    response = llm_with_tools.invoke([system_prompt] + state.messages)
    
    return {"messages": [response]}


# ROTEAMENTO DE TOOLS
def redacao_router(state: State) -> str:
    """Roteia a execução entre o LLM e a ferramenta RAG."""
    if state.messages[-1].tool_calls:
        return "tools"
    return END


# CONSTRUÇÃO DO GRAFO
builder = StateGraph(State)

builder.add_node(redacao_agent)
builder.add_node("tools", ToolNode(tools))

builder.set_entry_point("redacao_agent")

builder.add_conditional_edges(
    "redacao_agent",
    redacao_router,
    {
        "tools": "tools",
        END: END,
    }
)
builder.add_edge("tools", "redacao_agent")

graph = builder.compile()
