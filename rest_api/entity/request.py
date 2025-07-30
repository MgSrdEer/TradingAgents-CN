import datetime

from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    """
    分析请求入参架构
    """

    # stock_symbol 股票代码
    stock_symbol: str
    # str(datetime.date.today()) 分析日期
    analysis_date: str = str(datetime.date.today())
    # 分析师列表 ["market", "social", "news", "fundamentals"] // ["市场分析师", "社交媒体分析", "新闻分析师", "基本面分析师"]
    analysts: list[str]
    # 研究深度 1-5 // 1-5 层深度分析 # 3
    research_depth: int
    # "dashscope", "deepseek", "google" # dashscope
    llm_provider: str = "dashscope"
    # "美股", "A股", "港股"
    market_type: str
    # "dashscope": "qwen-turbo", "qwen-plus-latest", "qwen-max" // qwen-plus-latest
    # deepseek: "deepseek-chat"
    # google: "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"
    llm_model: str = "qwen-plus-latest"
    # 微信id
    weixinid: str
