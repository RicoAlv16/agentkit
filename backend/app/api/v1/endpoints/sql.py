import asyncpg

pg_pool = None

async def init_pg_pool():
    global pg_pool
    pg_pool = await asyncpg.create_pool(
        dsn=f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}/{settings.DB_NAME}",
        min_size=5,
        max_size=50,  # Adjust pool size dynamically
        statement_cache_size=1000,  # Enable prepared statements cache
        timeout=5,
    )

async def execute_sql(statement: str):
    """Optimized SQL execution with connection pooling."""
    if not is_sql_query_safe(statement):
        return {"message": "Unsafe SQL detected"}

    async with pg_pool.acquire() as conn:
        async with conn.transaction():
            # Use server-side cursors for large queries
            cursor = await conn.cursor(statement)
            rows = await cursor.fetch(100)  # Stream 100 rows at a time
            columns = [desc[0] for desc in cursor.description]

    return [
        dict(zip(columns, row))
        for row in rows
    ]

# ... existing code ...