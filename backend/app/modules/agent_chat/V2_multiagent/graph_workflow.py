from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, BaseMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from pydantic import BaseModel
from typing_extensions import TypedDict, Annotated
from langgraph.graph import add_messages
from langgraph.types import Command
from langchain_core.runnables import Runnable, RunnableConfig
from langchain.agents import create_agent
from typing import  Any, Literal, Optional
from langchain_core.tools import tool
from langgraph.runtime import Runtime, get_runtime
from langchain.agents.middleware import wrap_tool_call
from langgraph.types import Command, RunnableConfig
from langgraph_supervisor import create_supervisor, create_handoff_tool
from langgraph_supervisor.handoff import create_forward_message_tool
from app.modules.agent_chat.llm import llm
from app.infra.config import Config
from app.infra.core_dependency_container import container
from app.modules.agent_chat.V1_multiagent.prompts import supervisor_prompt, info_agent_prompt, redacao_agent_prompt

qdrant_service = container.bd_vetorial_service

# STATE

class AgentState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = []
    user_profile: dict = {}
    #profile_fetched: bool = False
    # review_decision: str = ""      # 'valid' ou 'invalid'
    # error_feedback: str = ""       # feedback do revisor

# SCHEMAS

class ContextSchema(TypedDict):
    user_id: str

# TOOLS

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

#MIDDLEWARES

@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        # Return a custom error message to the model
        return ToolMessage(
            content=f"Tool error: Please check your input and try again. ({str(e)})",
            tool_call_id=request.tool_call["id"]
        )

# AGENTS

info_agent = create_agent(
    model=llm,
    tools=[rag_tool],
    system_prompt=info_agent_prompt, 
    context_schema=ContextSchema,
    name="info_agent"
)

redacao_agent = create_agent(
    model=llm,
    tools=[rag_tool],
    system_prompt=redacao_agent_prompt,
    context_schema=ContextSchema,
    name="redacao_agent"
)

def info_agent_node(state: AgentState):
    result = info_agent.invoke(state)
    return Command(
        update={
            "messages": state["messages"] + [
                AIMessage(content=result["messages"][-1].content, name="info_agent_node")
            ]
        },
        goto="supervisor",
    )

def redaco_agent_node(state: AgentState):
    result = redacao_agent.invoke(state)
    return Command(
        update={
            "messages": state["messages"] + [
                AIMessage(content=result["messages"][-1].content, name="redaco_agent_node")
            ]
        },
        goto="supervisor",
    )

# SUPERVISOR

to_info_agent = create_handoff_tool(agent_name="info_agent", 
                    name="transferir_para_info_agent", 
                    description="Transfere tarefa para especialista em Propriedade Intelectual")

to_redacao_agent = create_handoff_tool(agent_name="redacao_agent", 
                    name="transferir_para_redacao_agent", 
                    description="Transfere tarefa para especialista em produção de documentos")

forwarding_tool = create_forward_message_tool("supervisor")

workflow = create_supervisor(
    [redacao_agent, info_agent],
    model=llm,
    prompt=supervisor_prompt,
    tools=[to_info_agent, to_redacao_agent],
    add_handoff_messages=False,
    output_mode="last_message"
)

graph = workflow.compile()

# png_bytes = graph.get_graph(xray=True).draw_mermaid_png()

# with open("graph.png", "wb") as f:
#     f.write(png_bytes)
