from redis import Redis, ConnectionPool

# Create a global Redis connection pool
pool = ConnectionPool(host='localhost', port=6379, db=0)
redis_client = Redis(connection_pool=pool)

# ... existing code ...