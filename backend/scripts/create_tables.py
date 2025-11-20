from dotenv import load_dotenv
import os

load_dotenv()

from app.infra.database import engine, Base
import app.modules.usuarios.models

def main():
    print("DATABASE_URL usada:", os.getenv("DATABASE_URL"))
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas")

if __name__ == "__main__":
    main()