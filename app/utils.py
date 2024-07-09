# from flask_redis import FlaskRedis
#
#
# redis_client = FlaskRedis()

import redis
from config import Config

redis_cache = redis.StrictRedis(host='localhost', port=6379, decode_responses=True, encoding='utf-8')
