#!/usr/bin/env python
# coding=utf-8

import redis

# redis 地址
REDIS_HOST = "127.0.0.1"
# redis 端口
REDIS_PORT = 6379
# redis 密码
REDIS_PASSWORD = None
# redis 连接池最大连接量
REDIS_MAX_CONNECTION = 20


class RedisClient:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        conn_pool = redis.ConnectionPool(
            host=host,
            port=port,
            password=password,
            max_connections=REDIS_MAX_CONNECTION,
        )
        self.redis = redis.Redis(connection_pool=conn_pool)

    def add_data(self, redis_key, data):
        """
        新增数据
        """
        self.redis.sadd(redis_key, *data)


    def get_data(self, redis_key, count=1):
        """
        返回指定数量的数据
        """
        return self.redis.spop(redis_key, count)
