import time
import asyncio

from aiohttp import ClientSession
from more_itertools import chunked

from tools.timer import async_timer
from models import init_db, Session, Character

BASE_URL = 'https://swapi.dev/api/people'
RATE = {'requests': 10, 'seconds': 1, 'chunk_size': 20}


async def prepare_character_objects(data: list[dict[str, str]]) \
        -> list[Character]:
    char_objects = [Character(
        person_id=int(char['url'].split('/')[-2]),
        birth_year=char['birth_year'],
        eye_color=char['eye_color'],
        films=', '.join(char['films']),
        gender=char['gender'],
        hair_color=char['hair_color'],
        height=char['height'],
        home_world=char['homeworld'],
        mass=char['mass'],
        name=char['name'],
        skin_color=char['skin_color'],
        species=', '.join(char['species']),
        starships=', '.join(char['starships']),
        vehicles=', '.join(char['vehicles']),
    ) for char in data]
    return char_objects


async def insert_to_db(characters: list[Character]) -> None:
    print('starting to insert characters', flush=True)
    async with Session() as session:
        session.add_all(characters)
        await session.commit()
        print('finished inserting characters', flush=True)


async def fetch_data(session, semaphore, url) \
        -> dict[str, str | dict[str, str]]:
    async with semaphore:
        start = time.time()
        resource_type, idx, _ = url.split('/')[-3:]
        print(f'fetching {resource_type} #{idx}', flush=True)
        async with session.get(url) as response:
            json_data = await response.json()
            print(f'fetched {resource_type} #{idx}', flush=True)
            time_to_fetch = time.time() - start
            if time_to_fetch < RATE['seconds']:
                print(f'sleeping for {RATE["seconds"] - time_to_fetch} '
                      f'seconds', flush=True)
                await asyncio.sleep(RATE['seconds'] - time_to_fetch)
            return {'status_code': response.status, 'data': json_data}


@async_timer
async def main() -> None:
    semaphore = asyncio.Semaphore(RATE['requests'])
    async with ClientSession() as session:

        urls_with_values = {}

        for chunk_of_ids in chunked(range(1, 100), RATE['chunk_size']):
            char_requests = await asyncio.gather(
                *[fetch_data(session, semaphore, f'{BASE_URL}/{i}/')
                  for i in chunk_of_ids]
            )

            chars = [char['data'] for char in char_requests if char['status_code'] == 200]

            linked_fields = {
                'films': 'title',
                'species': 'name',
                'homeworld': 'name',
                'starships': 'name',
                'vehicles': 'name'
            }

            for char in chars:
                for field in linked_fields.keys():
                    if field == 'homeworld':
                        if char[field] not in urls_with_values.keys():
                            retrieve_task = asyncio.create_task(
                                fetch_data(session, semaphore, char[field])
                            )
                            urls_with_values[char[field]] = retrieve_task
                        continue

                    for url in char[field]:
                        if url not in urls_with_values.keys():
                            retrieve_task = asyncio.create_task(
                                fetch_data(session, semaphore, url)
                            )
                            urls_with_values[url] = retrieve_task

            await asyncio.gather(*urls_with_values.values())

            for char in chars:
                for field in linked_fields.keys():
                    if field == 'homeworld':
                        char[field] \
                            = urls_with_values[char[field]].result()['data'][linked_fields[field]]
                        continue
                    for idx, url in enumerate(char[field]):
                        char[field][idx] \
                            = urls_with_values[url].result()['data'][linked_fields[field]]

            char_objects = await prepare_character_objects(chars)
            asyncio.create_task(insert_to_db(char_objects))
        await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})


async def entry_point() -> None:
    await init_db()
    await main()

if __name__ == '__main__':
    asyncio.run(entry_point())
