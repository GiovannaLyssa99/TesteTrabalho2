from langgraph.graph import StateGraph, END, add_messages
from langgraph.prebuilt import ToolNode
from langgraph.runtime import get_runtime
from pydantic import BaseModel
from typing import Annotated, Any, Optional, TypedDict
from langchain_core.messages import SystemMessage, BaseMessage, HumanMessage, AIMessage
from langgraph.types import interrupt, Command
from langchain.tools import tool
from app.modules.agent_chat.llm import llm
from app.infra.config import Config
from langgraph.runtime import Runtime
from app.infra.core_dependency_container import container
from app.modules.agent_chat.V1_multiagent.prompts import perfil_agent_prompt

# ESTADO DO AGENTE
class State(BaseModel):
    """Estado do agente de perfil do inventor."""
    messages: Annotated[list[BaseMessage], add_messages] = []
    user_profile: dict = {}
    profile_fetched: bool = False

class ContextSchema(TypedDict):
    user_id: str

@tool("buscar_perfil_usuario_logado")
def buscar_perfil_usuario_logado() -> Optional[dict | str]:
    """Busca o perfil do usuário logado."""

    runtime = get_runtime(ContextSchema)
    user_id = runtime.context.user_id
    print("user_id" + user_id)

    if not user_id:
        return "Sem user_id. Sessão anônima"

    # Simula busca
    
    return Command(update={
        "user_profile": {"nome": "Bruna Borges", "area": "Biotecnologia", "nivel_experiencia": "Intermediário"},
        "profile_fetched": True
    })
    

@tool("coletar_perfil_usuario_anonimo")
def coletar_perfil_usuario_anonimo() -> Any:
    """Coleta perfil do usuário anônimo."""
    
    perfil = interrupt( 
        {
            "mensagem": "Por favor, preencha o formulário de perfil do inventor."
        }
    )

    return Command(update={
        "user_profile": perfil,
        "profile_fetched": True
    })


tools = [coletar_perfil_usuario_anonimo, buscar_perfil_usuario_logado]
llm_with_tools = llm.bind_tools(tools)


# NÓ PRINCIPAL DO AGENTE
async def perfil_agent(state: State, runtime: Runtime[ContextSchema]):
    """Agente especializado em coleta e validação de perfis de inventores"""

    user_id = runtime.context["user_id"]
    status: str

    if state.user_profile:
        status = "COLETADO"
    
    elif user_id:
        status = "BUSCAR"
    
    else:
        status = "COLETAR"

    system_prompt = SystemMessage(content=perfil_agent_prompt.format(
        status=status))
    
    response = llm_with_tools.invoke([system_prompt] + state.messages)

    return {"messages": [response]}


# ROTEAMENTO DE TOOLS
def perfil_agent_router(state: State) -> str:
    """Roteia a execução entre o LLM e a ferramenta RAG."""
    if state.messages[-1].tool_calls:
        return "tools"
    return END


# CONSTRUÇÃO DO GRAFO
builder = StateGraph(State)

builder.add_node(perfil_agent)
builder.add_node("tools", ToolNode(tools))

builder.set_entry_point("perfil_agent")

builder.add_conditional_edges(
    "perfil_agent",
    perfil_agent_router,
    {
        "tools": "tools",
        END: END,
    }
)
builder.add_edge("tools", "perfil_agent")

graph = builder.compile()
