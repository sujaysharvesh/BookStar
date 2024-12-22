from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import sessionmaker
from app.DataBase.config import Config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


engine = create_async_engine(
    Config.DATABASE_URL,
    echo=True,
)



async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error during database initialization: {e}")


async def get_session():
    Session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with Session() as session:
        yield session

