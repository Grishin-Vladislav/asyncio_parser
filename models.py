import os

from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, \
    AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

PG_USER = os.getenv('PG_USER', 'api')
PG_PASSWORD = os.getenv('PG_PASSWORD', 'secret')
PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = os.getenv('PG_PORT', '5431')
PG_NAME = os.getenv('PG_NAME', 'swapi')

PG_DSN = f'postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_NAME}'

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass


class Character(Base):
    __tablename__ = 'character'

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer, nullable=False)
    birth_year: Mapped[str] = mapped_column(String(100), nullable=False)
    eye_color: Mapped[str] = mapped_column(String(100), nullable=False)
    films: Mapped[str] = mapped_column(String(200), nullable=False)  # list
    gender: Mapped[str] = mapped_column(String(100), nullable=False)
    hair_color: Mapped[str] = mapped_column(String(100), nullable=False)
    height: Mapped[str] = mapped_column(String(100), nullable=False)
    home_world: Mapped[str] = mapped_column(String(100), nullable=False)  # link
    mass: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    skin_color: Mapped[str] = mapped_column(String(100), nullable=False)
    species: Mapped[str] = mapped_column(String(200), nullable=False)  # list
    starships: Mapped[str] = mapped_column(String(200), nullable=False)  # list
    vehicles: Mapped[str] = mapped_column(String(200), nullable=False)  # list


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
