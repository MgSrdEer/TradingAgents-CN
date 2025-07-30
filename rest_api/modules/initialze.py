import sys
from pathlib import Path

from dotenv import load_dotenv

from rest_api.infrastructure.limiter.redis_limiter import get_redis04_manager
from tradingagents.utils.logging_manager import get_logger

# 导入日志模块
logger = get_logger("rest_api_init")

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv(project_root / ".env.local", override=True)


def init() -> None:
    """
    初始化项目。
    包括检查API密钥、检查MongoDB连接等。
    """
    check_api()
    check_mangodb()
    check_redis()
    get_redis04_manager()


def check_api() -> None:
    """
    检查API密钥是否有效。
    若检查失败，会记录错误日志并抛出异常。
    """
    try:
        from web.utils.api_checker import check_api_keys

        api_status = check_api_keys()

        if not api_status["required_configured"]:
            logger.error("❌ API密钥配置异常")
            raise RuntimeError("API密钥配置异常")
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        raise e


def check_mangodb() -> None:
    """
    检查MongoDB连接是否有效。
    若检查失败，会记录错误日志并抛出异常。
    """
    try:
        from tradingagents.config.database_manager import is_mongodb_available

        if not is_mongodb_available():
            logger.error("❌ MongoDB连接失败")
            raise RuntimeError("MongoDB连接失败")
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        raise e


def check_redis() -> None:
    """
    检查Redis连接是否有效。
    若检查失败，会记录错误日志并抛出异常。
    """
    try:
        from tradingagents.config.database_manager import is_redis_available

        if not is_redis_available():
            logger.error("❌ Redis连接失败")
            raise RuntimeError("Redis连接失败")
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        raise e
