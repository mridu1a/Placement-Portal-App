import redis
import json

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

def get_cache(key):
    """Get data from cache"""
    data = r.get(key)
    if data:
        return json.loads(data)
    return None

def set_cache(key, data, expiry=300):
    """Save data to cache with expiry in seconds (default 5 mins)"""
    r.setex(key, expiry, json.dumps(data))

def delete_cache(key):
    """Delete a specific cache key"""
    r.delete(key)

def clear_pattern(pattern):
    """Delete all keys matching a pattern"""
    keys = r.keys(pattern)
    if keys:
        r.delete(*keys)