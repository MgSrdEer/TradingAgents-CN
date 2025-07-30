import logging
import os
from datetime import datetime, timedelta

import redis


class Radis04:
    """
    reatapi 模块缓存
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.client = None
        self.connect_kwargs = {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", "6379")),
            "db": 4,
            "socket_timeout": 2,
            "socket_connect_timeout": 2,
        }
        # 初始化连接
        self._initialize_connections()

    def _initialize_connections(self):
        """初始化Redis连接"""
        try:

            # 如果有密码，添加密码
            if os.getenv("REDIS_PASSWORD"):
                self.connect_kwargs["password"] = os.getenv("REDIS_PASSWORD")
            # 打印连接参数
            self.client = redis.Redis(**self.connect_kwargs)
            # 测试连接
            self.client.ping()
            self.logger.info("✅ Redis 04连接成功")
        except Exception as e:
            self.logger.error("❌ Redis 04连接失败: %s", e)
            self.client = None


_redis04_manager = None


def get_redis04_manager() -> Radis04:
    """获取Redis 04管理器实例"""
    global _redis04_manager
    if _redis04_manager is None:
        _redis04_manager = Radis04()
    return _redis04_manager


def get_redis04_client() -> redis.Redis:
    """获取Redis 04客户端实例"""
    manager = get_redis04_manager()
    return manager.client


# 全局访问限制
GLOBAL_ACCESS_LIMIT = 10
# 用户访问限制
USER_ACCESS_LIMIT = 1

# Lua脚本实现原子操作：检查并更新计数,单个lua脚本会被当成一个命令来处理,确保原子性
LUA_SCRIPT = """
local global_key = KEYS[1]
local user_key = KEYS[2]
local global_limit = tonumber(ARGV[1])
local user_limit = tonumber(ARGV[2])
local ttl = tonumber(ARGV[3])

-- 检查全局计数
local global_count = tonumber(redis.call('get', global_key) or "0")
if global_count >= global_limit then
    return 0  -- 拒绝访问
end

-- 检查用户计数
local user_count = tonumber(redis.call('get', user_key) or "0")
if user_count >= user_limit then
    return 0  -- 拒绝访问
end

-- 原子更新计数
redis.call('incr', global_key)
redis.call('incr', user_key)

-- 仅在键不存在时设置过期时间（避免重复刷新）
if global_count == 0 then
    redis.call('expire', global_key, ttl)
end
if user_count == 0 then
    redis.call('expire', user_key, ttl)
end

return 1  -- 允许访问
"""


def get_seconds_to_midnight() -> int:
    """计算当前时间到次日0点的剩余秒数"""
    now = datetime.now()
    # 次日0点时间（今天的时间 + 1天，然后时/分/秒设为0）
    midnight = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    # 计算时间差（秒）
    seconds = int((midnight - now).total_seconds())
    return seconds


def access_limiter(user_wx: str) -> bool:
    """
    Redis 访问限制
    :param user_wx: 用户微信ID
    :return: 是否允许访问
    """
    # 白名单直接通过
    if user_wx in get_whitelist_users():
        return True

    client = get_redis04_client()
    if client is None:
        return False  # 连接失败，拒绝访问

    today = datetime.now().strftime("%Y-%m-%d")
    # 全局计数器键
    global_key = f"access:global:{today}"
    # 用户计数器键
    user_key = f"access:user:{user_wx}:{today}"

    try:
        # 计算到次日0点的剩余秒数
        ttl = get_seconds_to_midnight()
        # 执行Lua脚本（确保原子性）
        result = client.eval(
            LUA_SCRIPT,
            2,  # 键的数量
            global_key,
            user_key,  # 键列表
            GLOBAL_ACCESS_LIMIT,
            USER_ACCESS_LIMIT,
            ttl,  # 参数列表
        )
        return bool(result)
    except Exception as e:
        print(f"❌ Redis操作失败: {str(e)}")
        return False  # 出错时默认拒绝访问，可根据业务调整


def get_global_count() -> int:
    """
    获取Redis中的全局访问次数
    :return: 访问次数
    """
    client = get_redis04_client()
    if client is None:
        return 0  # 连接失败，返回0

    today = datetime.now().strftime("%Y-%m-%d")
    # 全局计数器键
    global_key = f"access:global:{today}"
    try:
        # 获取计数
        count = int(client.get(global_key) or "0")
        return count
    except Exception as e:
        print(f"Redis操作失败: {str(e)}")
        return 0  # 出错时返回0


def get_whitelist_users() -> list:
    """
    获取白名单用户列表
    :return: 白名单用户列表
    """
    client = get_redis04_client()
    if client is None:
        return []  # 连接失败，返回空列表
    whitelist_users_key = "whitelist:users"
    try:
        # 获取白名单用户列表
        whitelist_users = client.smembers(whitelist_users_key)
        return [user.decode("utf-8") for user in whitelist_users if user]  # 过滤空字节串
    except Exception as e:
        print(f"Redis操作失败: {str(e)}")
        return []  # 出错时返回空列表
