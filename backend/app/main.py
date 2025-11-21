from fastapi import FastAPI
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.infra.database import engine
from langgraph.checkpoint.postgres import PostgresSaver
from app.infra.config import Config
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from collections.abc import AsyncGenerator
#from app.modules.agent_chat.V1_multiagent.fluxo_principal import graph
from app.modules.agent_chat.V2_multiagent.graph_workflow import graph


@asynccontextmanager
async def get_postgres_saver():
    """Initialize and return a PostgreSQL saver instance based on a connection pool for more resilent connections."""
    application_name = "chatbotinova-saver"

    async with AsyncConnectionPool(
        Config.DB_URI,
        min_size=1,
        max_size=3,
        # Langgraph requires autocommmit=true and row_factory to be set to dict_row.
        # Application_name is passed so you can identify the connection in your Postgres database connection manager.
        kwargs={"autocommit": True, "row_factory": dict_row, "application_name": application_name},
        # makes sure that the connection is still valid before using it
        check=AsyncConnectionPool.check_connection,
    ) as pool:
        try:
            checkpointer = AsyncPostgresSaver(pool)
            await checkpointer.setup()
            yield checkpointer
        finally:
            await pool.close()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Configurable lifespan that initializes the appropriate database checkpointer, store,
    and agents with async loading - for example for starting up MCP clients.
    """
    try:
        async with get_postgres_saver() as saver:
            if hasattr(saver, "setup"): 
                await saver.setup()
            
            # Set checkpointer for thread-scoped memory (conversation history)
            graph.checkpointer = saver

            yield
    except Exception as e:
        raise

app = FastAPI(lifespan=lifespan)

from app.api.routes.chat_agent_routes import chat_agent_router
from app.api.routes.admin_routes import admin_router
from app.api.routes.users_routes import router as user_router
from app.api.routes.login_auth_routes import auth_router

app.include_router(chat_agent_router)
app.include_router(admin_router)
app.include_router(user_router)
app.include_router(auth_router)