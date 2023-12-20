PG_USER = 'api'
PG_PASSWORD = 'secret'
PG_HOST = 'localhost'
PG_PORT = '5431'
PG_NAME = 'pokemon'

PG_DSN = f'postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_NAME}'
