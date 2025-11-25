from .core_dependency_container import container
from .agent_dependency_container import agent_container

def get_bd_vetorial_service():
    return container.bd_vetorial_service

def get_minio_service():
    return container.minio_service

def get_admin_service():
    return container.admin_service

def get_chat_service():
    return agent_container.chat_agent_service

def get_crawler_service():
    return container.crawler_service