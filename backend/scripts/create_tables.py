from dotenv import load_dotenv
import os
import asyncio
from app.infra.database import engine, Base
import app.modules.usuarios.models
import app.modules.agent_chat.models

load_dotenv()

async def create_tables():
    print("DATABASE_URL usada:", os.getenv("DATABASE_URL"))
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Tabelas criadas")

if __name__ == "__main__":
    asyncio.run(create_tables())