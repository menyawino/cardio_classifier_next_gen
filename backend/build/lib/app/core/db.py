from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./dev.db")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
