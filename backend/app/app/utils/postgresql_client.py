import asyncpg
import asyncio

async def fetch_data():
    conn = await asyncpg.connect(user='user', password='password',
                                 database='database', host='127.0.0.1')
    async with conn.transaction():
        async for record in conn.cursor('SELECT * FROM my_table'):
            print(record)
    await conn.close()

# ... existing code ...