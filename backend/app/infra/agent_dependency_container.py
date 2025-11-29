from app.modules.agent_chat.chat_service import ChatAgentService
from app.modules.agent_chat.V1_multiagent.graph_workflow import graph

def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class AgentContainer:
    def __init__(self):
        self.chat_agent_service = ChatAgentService(graph=graph)

agent_container = AgentContainer()