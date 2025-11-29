import json
from langchain_core.messages import ToolMessage, AIMessage, BaseMessage
from pydantic import BaseModel
from typing_extensions import Annotated
from langgraph.graph import add_messages
from langgraph.types import Command
from langchain.agents import create_agent
from typing import Any, Literal, Optional
from langchain.agents.middleware import wrap_tool_call
from langgraph.types import Command
from langgraph_supervisor import create_supervisor, create_handoff_tool
from langgraph_supervisor.handoff import create_forward_message_tool
from app.modules.agent_chat.llm import get_llm
from app.infra.core_dependency_container import container
from app.modules.agent_chat.V1_multiagent.prompts import supervisor_prompt, info_agent_prompt, redacao_agent_prompt
from langchain.tools import ToolRuntime, tool
from langmem.short_term import SummarizationNode

qdrant_service = container.bd_vetorial_service

# STATE

class AgentState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = []
    user_profile: dict = {}
    context: dict[str, Any]

# SCHEMAS

class ContextSchema(BaseModel):
    user_profile: dict

class SupervisorResponse(BaseModel):
    message_type: Literal["chat", "checklist_request"]
    content: str
    checklist_type: Optional[Literal["simulador_patenteabilidade", "checklist_ineditismo"]] = None

# TOOLS

@tool
async def rag_tool(query: str):
    """Busca informações sobre pedidos de patente em uma base de conhecimento (RAG).

    Args:
        query: Pergunta feita pelo usuário.

    Returns:
        Texto com informações relevantes sobre o tema pesquisado.
    """
    docs = qdrant_service.buscar(query)

    if not docs:
        print("sem docs")
        return "Nenhuma informação relevante encontrada."
    
    results = []
    for i, doc in enumerate(docs.points):
        results.append(f"{doc.payload['page_content']}\n")
    
    return "".join(results)

@tool("buscar_perfil_usuario_logado")
def buscar_perfil_usuario_logado(runtime: ToolRuntime[AgentState, ContextSchema]) -> Command:
    """Busca o perfil do usuário logado."""

    tool_call_id = runtime.tool_call_id
    
    user_profile = runtime.context.user_profile

    if not user_profile:
        msg_conteudo = "Sem perfil do inventor"
        tool_message = ToolMessage(content=msg_conteudo, tool_call_id=tool_call_id)
        
        return Command(update={
            "messages": [tool_message]
        })

    perfil_para_llm = json.dumps(user_profile, indent=2, ensure_ascii=False)

    tool_message = ToolMessage(
        content=perfil_para_llm, 
        tool_call_id=tool_call_id
    )

    return Command(update={
        "messages": [tool_message],
        "user_profile": user_profile
    })
    
#MIDDLEWARES

@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"Tool error: Please check your input and try again. ({str(e)})",
            tool_call_id=request.tool_call["id"]
        )

# AGENTS

summarization_model = get_llm().bind(max_tokens=512)

summarization_node = SummarizationNode(
    model=summarization_model,
    max_tokens=2048,
    max_tokens_before_summary=20000,
    max_summary_tokens=512,
    output_messages_key="llm_input_messages"
)

info_agent = create_agent(
    model=get_llm(),
    tools=[rag_tool, buscar_perfil_usuario_logado],
    system_prompt=info_agent_prompt, 
    context_schema=ContextSchema,
    name="info_agent"
)

redacao_agent = create_agent(
    model=get_llm(),
    tools=[rag_tool],
    system_prompt=redacao_agent_prompt,
    context_schema=ContextSchema,
    name="redacao_agent"
)

def info_agent_node(state: AgentState):
    result = info_agent.invoke(state)
    return Command(
        update={
            "messages": [
                AIMessage(content=result["messages"][-1].content, name="info_agent_node")
            ]
        },
        goto="supervisor",
    )
# state["messages"] + 

def redaco_agent_node(state: AgentState):
    result = redacao_agent.invoke(state)
    return Command(
        update={
            "messages": [
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

#llm_structure_output = get_llm().with_structured_output(SupervisorResponse)

workflow = create_supervisor(
    [redacao_agent, info_agent],
    model=get_llm(),
    prompt=supervisor_prompt,
    tools=[to_info_agent, to_redacao_agent],
    add_handoff_messages=False,
    output_mode="last_message",
    response_format=SupervisorResponse, 
    pre_model_hook=summarization_node
)

graph = workflow.compile()

# png_bytes = graph.get_graph(xray=True).draw_mermaid_png()

# with open("graph.png", "wb") as f:
#     f.write(png_bytes)
