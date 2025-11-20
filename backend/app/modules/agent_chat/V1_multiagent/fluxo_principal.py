from pydantic import BaseModel
from typing import Annotated, Any, Literal, TypedDict
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, add_messages, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.checkpoint.memory import MemorySaver
from datetime import datetime
from langgraph.runtime import Runtime
from langgraph.types import Command, RunnableConfig
from langgraph.checkpoint.postgres import PostgresSaver
from app.modules.agent_chat.llm import llm
from app.infra.config import Config
from app.infra.core_dependency_container import container
from app.modules.agent_chat.V1_multiagent.prompts import revisor_prompt, supervisor_prompt

qdrant_service = container.bd_vetorial_service

from app.modules.agent_chat.V1_multiagent.agente_info_gerais import graph as info_agent
from app.modules.agent_chat.V1_multiagent.agente_redacao_doc import graph as redacao_agent
from app.modules.agent_chat.V1_multiagent.agente_perfil_inventor import graph as perfil_agent

class ContextSchema(TypedDict):
    user_id: str

# NOVO STATE DO ROUTER
class RouterState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = []
    user_profile: dict = {}
    profile_fetched: bool = False
    task_description: str | None = None
    review_decision: str = ""      # 'valid' ou 'invalid'
    error_feedback: str = ""       # feedback do revisor


# TOOL DE HANDOFF PARA SUBAGENTES
@tool
def handoff_to_subagent(
    agent_name: Literal["info_agent", "redacao_agent"],
    task_description: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    """Atribui uma tarefa a um subagente."""
    print("task:" + task_description)
    update = {
        "messages": [ToolMessage(
            name=f"handoff_to_{agent_name}",
            content=f"Tarefa atribuída ao agente {agent_name}.",
            tool_call_id=tool_call_id,
        )],
        "task_description": task_description  # guarda a tarefa para que o subagente saiba
    }

    return Command(
        goto=f"call_{agent_name}",
        update=update,
    )


# FUNÇÕES DE CHAMADA DOS SUBAGENTES
async def call_perfil_agent(state: RouterState, runtime: Runtime[ContextSchema]):
    """Invoca o agente de perfil do inventor."""

    perfil_state = {
        "messages": state.messages[-1],
        "user_profile": state.user_profile,
        "profile_fetched": state.profile_fetched
    }

    response = await perfil_agent.ainvoke(
        input=perfil_state,
        context=runtime.context,
    )

    print("response perfil:" + response["messages"][-1].content)
    ai_message = AIMessage(name="agent_answer", content=response["messages"][-1].content)

    return {"messages": [ai_message],
            "user_profile": response["user_profile"],
            "profile_fetched": response["profile_fetched"]}


async def call_info_agent(state: RouterState, runtime: Runtime[ContextSchema]):
    """Invoca o agente de informações sobre patentes."""
    response = await info_agent.ainvoke(
        input={
            "messages": [HumanMessage(content=state.task_description)]
        },
        context=runtime.context,
    )

    ai_message = AIMessage(name="agent_answer", content=response["messages"][-1].content)

    return {"messages": [ai_message]}


async def call_redacao_agent(state: RouterState, runtime: Runtime[ContextSchema]):
    """Invoca o agente de redação de documentos de patente."""
    response = await redacao_agent.ainvoke(
        input={
            "messages": [HumanMessage(content=state.task_description)]
        },
        context=runtime.context,
    )

    ai_message = AIMessage(name="agent_answer", content=response["messages"][-1].content)

    return {"messages": [ai_message]}


# AGENTE ROTEADOR

tools = [handoff_to_subagent]
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)


async def router(state: RouterState):
    """Agente roteador principal."""

    user_query = get_message_by_name(state, "query")
    print("query router:"+user_query)

    response = llm_with_tools.invoke([
        SystemMessage(content=supervisor_prompt.format(perfil= state.user_profile, query=user_query, error_feedback=state.error_feedback))
    ] + state.messages)

    print("response:" + response.content)
    return {"messages": [response]}


def to_tool_router(state: RouterState) -> str:
    """Roteia para ferramentas se houver tool_call."""
    if state.messages[-1].tool_calls:
        return "tools"
    return END

def get_message_by_name(state: RouterState, name: str) -> str:

    for m in reversed(state.messages):
        if getattr(m, "name", None) == name:
            return m.content

class revisor_answer(BaseModel):
    feedback: str | None = None
    decision: Literal["valid", "invalid"] = "valid"

revisor_llm = llm.with_structured_output(revisor_answer)


# NÓ DE REVISOR
async def revisor(state: RouterState):
    """
    O revisor avalia a resposta do subagente usando LLM:
    - review_decision: 'valid' ou 'invalid'
    - error_feedback: comentário detalhado caso inválido
    """

    user_query = get_message_by_name(state, "query")
    print("query:" + user_query)
    agent_answer = get_message_by_name(state, "agent_answer")
    print("answer" + agent_answer)

    review_prompt = SystemMessage(content=revisor_prompt.format(query=user_query, agent_answer=agent_answer))

    response = revisor_llm.invoke([review_prompt])

    review_message = AIMessage(
        name="reviewer",
        content=f"Decisão: {response.decision}. Feedback: {response.feedback}"
    )

    return {"messages": [review_message], 
            "review_decision": response.decision, 
            "error_feedback": str(response.feedback)}


def revisor_router(state: RouterState) -> str:
    """Roteia para END se válido, ou volta para supervisor se inválido."""
    if state.review_decision == "valid":
        return END
    else:
        return "router"


# CONSTRUÇÃO DO GRAFO
builder = StateGraph(RouterState, context_schema=ContextSchema)

# Nós principais
builder.add_node(router)
builder.add_node("tools", ToolNode(tools))
builder.add_node(call_info_agent)
builder.add_node(call_redacao_agent)
builder.add_node(call_perfil_agent)
builder.add_node(revisor)

# Pontos de entrada
builder.set_entry_point("call_perfil_agent")
builder.add_edge("call_perfil_agent", "router")

# Edges do supervisor
builder.add_conditional_edges(
    "router",
    to_tool_router,
    {
        "tools": "tools",
        END: END,
    }
)

# Após subagentes, sempre ir para o revisor
builder.add_edge("call_info_agent", "revisor")
builder.add_edge("call_redacao_agent", "revisor")
builder.add_edge("router", END)

# Roteamento do revisor
builder.add_conditional_edges(
    "revisor",
    revisor_router,
    {
        "router": "router",
        END: END,
    }
)

graph = builder.compile()

# png_bytes = graph.get_graph(xray=True).draw_mermaid_png()

# with open("graph.png", "wb") as f:
#     f.write(png_bytes)

# def run_graph(query: str, user_id: str | None, thread_id: str):

#     result = graph.invoke(
#         {"messages": [HumanMessage(query, name="query")]},
#         context={"user_id": user_id, "thread_id": thread_id}
#     )

#     return result

# def resume_graph(resume_value: Any, user_id: str | None, thread_id: str):
    
#     result = graph.invoke(
#         Command(resume=resume_value),
#         context={"user_id": user_id, "thread_id": thread_id}
#     )

#     return result


