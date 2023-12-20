import time
import asyncio

from aiohttp import ClientSession

from tools.timer import async_timer

BASE_URL = 'https://pokeapi.co/api/v2/pokemon'
RATE = {'requests': 3, 'seconds': 1}


async def get_pokemon(session, pokemon_id, semaphore):
    async with semaphore:
        start = time.time()
        print(f'fetching pokemon {pokemon_id}', flush=True)
        async with session.get(f'{BASE_URL}/{pokemon_id}') as response:
            pokemon = await response.json()
            time_to_fetch = time.time() - start
            if time_to_fetch < RATE['seconds']:
                await asyncio.sleep(RATE['seconds'] - time_to_fetch)
            return pokemon['id'], pokemon['name']


@async_timer
async def main():
    semaphore = asyncio.Semaphore(RATE['requests'])
    async with ClientSession() as session:
        tasks = [get_pokemon(session, i, semaphore) for i in range(1, 21)]
        pokemons = await asyncio.gather(*tasks)
        for pokemon in pokemons:
            print(f'#{pokemon[0]} - {pokemon[1]}', flush=True)


asyncio.run(main())
