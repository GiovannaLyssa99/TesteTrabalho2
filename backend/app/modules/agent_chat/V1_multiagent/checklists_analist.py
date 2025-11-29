from langchain_core.messages import SystemMessage, AIMessage
from pydantic import BaseModel
from app.modules.agent_chat.llm import get_llm
from langchain.tools import tool
from langchain.agents import create_agent
from app.infra.core_dependency_container import container

qdrant_service = container.bd_vetorial_service

# prompt = """Você é um agente especialista em Propriedade Intelectual com ênfase em avaliação de patenteabilidade e análise de ineditismo. 
# Seu papel é analisar as respostas do checklist preenchido pelo usuário e gerar um parecer técnico detalhado e fundamentado.

# Você possui acesso à seguinte ferramenta:

# - rag_tool(query: str): busca e retorna trechos relevantes de documentos sobre Propriedade Intelectual 
#   (LPI, diretrizes do INPI, guias, manuais, jurisprudência, documentos técnicos, requisitos legais e boas práticas).

# REGRAS DO AGENTE:
# 1. Sua análise DEVE ser baseada exclusivamente em:
#    - respostas do checklist fornecido pelo usuário
#    - informações recuperadas pela ferramenta rag_tool

# 2. Você NÃO pode inventar informações, conceitos técnicos, fundamentos jurídicos ou interpretações não suportadas.
#    Caso os documentos recuperados NÃO contenham informação suficiente, você deve declarar isso explicitamente.
# 3. Sempre que precisar explicar um conceito jurídico ou técnico, você DEVE consultar rag_tool com uma query apropriada.
# 4. Não cite a ferramenta rag_tool na resposta, utilize apenas para contexto.
# 5. Você deve produzir um parecer técnico estruturado, preciso e claro, seguindo o formato abaixo:

# ### Resumo Geral
# (3-5 linhas sobre a situação do usuário com base no checklist e nos documentos recuperados)

# ### Recomendações Técnicas e Jurídicas
# - ações específicas recomendadas, documentação necessária, próximos passos práticos
# - utilize a ferramenta rag_tool para buscar as recomendações. Mande uma query com as informações desejadas.

# 6. Nunca responda com conhecimento pessoal ou externo. 
# 7. Você deve realizar quantas chamadas à ferramenta rag_tool forem necessárias até reunir informação suficiente para fundamentar a análise.
# 8. Se a pergunta do usuário for vaga em algum ponto, você deve indicar explicitamente as limitações da análise.

# ## Checklist com respostas do usuário: {checklist}

# Comportamento esperado: profissional, técnico, fundamentado, claro e seguro.
# """
prompt = """Você é um agente especialista em Propriedade Intelectual com ênfase em avaliação de patenteabilidade e análise de ineditismo. 
Seu papel é analisar as respostas do checklist preenchido pelo usuário e gerar um parecer técnico detalhado e fundamentado.

REGRAS DO AGENTE:
1. Sua análise DEVE ser baseada exclusivamente em:
   - respostas do checklist fornecido pelo usuário

2. Você NÃO pode inventar informações, conceitos técnicos, fundamentos jurídicos ou interpretações não suportadas.
   Caso os documentos recuperados NÃO contenham informação suficiente, você deve declarar isso explicitamente.
3. Não cite a ferramenta rag_tool na resposta, utilize apenas para contexto.
4. Você deve produzir um parecer técnico estruturado, preciso e claro, seguindo o formato abaixo:

### Resumo Geral
(3-5 linhas sobre a situação do usuário com base no checklist e nos documentos recuperados)

### Recomendações Técnicas e Jurídicas
- ações específicas recomendadas, documentação necessária, próximos passos práticos
- utilize a ferramenta rag_tool para buscar as recomendações. Mande uma query com as informações desejadas.

6. Nunca responda com conhecimento pessoal ou externo. 

## Checklist com respostas do usuário: {checklist}

Comportamento esperado: profissional, técnico, fundamentado, claro e seguro.
"""

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
    
agent = create_agent(
    model=get_llm(),
    #tools=[rag_tool],
    name="agent"
)

async def analise_patenteabilidade_checklist(answers: str) -> str:
    full_prompt = prompt.format(checklist=answers)

    response = await agent.ainvoke({"messages":[SystemMessage(content=full_prompt)]})

    for m in reversed(response["messages"]):
                if m.content and isinstance(m, AIMessage) and not m.response_metadata.get("__is_handoff_back"):
                    answer = {"content": m.content}
                    break
    print(f"answer: {response}")

    return answer