from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import settings

async_engine = create_async_engine(
    url=settings.db_url,
    echo=True)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)
