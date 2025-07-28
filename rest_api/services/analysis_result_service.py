import json
from json import JSONEncoder

from bson.objectid import ObjectId
from fastapi import Response

from tradingagents.config.database_manager import (
    get_database_manager,
    get_mongodb_client,
)

db_manager = get_database_manager()
db_client = get_mongodb_client()[db_manager.mongodb_config["database"]]
collection = db_client.analysis_reports

# 查询示例 - 获取所有分析报告
# all_reports = list(collection.find())

# 条件查询 - 获取特定股票的分析报告
# stock_reports = list(collection.find({"stock_code": "601127"}))

# 投影查询 - 只返回需要的字段（排除_id字段）
# projected_reports = list(
#     collection.find(
#         {"stock_code": "601127"}, {"_id": 0, "title": 1, "analysis_date": 1}
#     )
# )

# 排序和限制结果 - 按分析日期降序排列，只取前10条
# sorted_reports = list(collection.find().sort("analysis_date", -1).limit(10))

# 聚合查询示例 - 按股票代码分组统计报告数量
# pipeline = [
#     {"$group": {"_id": "$stock_code", "count": {"$sum": 1}}},
#     {"$sort": {"count": -1}}
# ]
# report_counts = list(collection.aggregate(pipeline))


class MongoJSONEncoder(JSONEncoder):
    """
    自定义JSON编码器，用于处理ObjectId类型
    """

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, bytes):

            return o.decode("utf-8")

        return super().default(o)


def get_report_list_date(analysis_date: str) -> Response:
    """
    获取指定日期的报告列表
    Args:
        analysis_date: 分析日期
    Returns:
        报告列表
    """
    try:
        report_res = list(
            collection.find(
                {"analysis_date": analysis_date, "analysis_type": "markdown"},
                {
                    "_id": 1,
                    "filename": 1,
                    "analysis_date": 1,
                    "symbol": 1,
                    "file_size": 1,
                },
            )
        )
    except Exception as _:
        return Response(
            content="query error!",
            media_type="application/json; charset=utf-8",
            status_code=500,
        )
    return Response(
        content=json.dumps(
            report_res, ensure_ascii=False, indent=2, cls=MongoJSONEncoder
        ),
        media_type="application/json; charset=utf-8",
        status_code=200,
    )


def get_report_ids(ids: [str]):
    """
    获取指定ID的报告内容
    Args:
        ids: 报告ID列表
    Returns:
        报告内容列表
    """
    report_res = list(
        collection.find(
            {"_id": {"$in": [ObjectId(id) for id in ids]}, "analysis_type": "markdown"},
            {"_id": 1, "content": 1},
        )
    )
    content = report_res[0].get("content", b"").decode("utf-8")
    print(content)
    print(json.dumps(report_res, ensure_ascii=False, indent=2, cls=MongoJSONEncoder))


def get_report_id(report_id: str) -> Response:
    """
    获取报告内容
    Args:
        report_id: 报告ID
    Returns:
        报告内容
    """
    try:
        report_res = list(
            collection.find(
                {"_id": ObjectId(report_id), "analysis_type": "markdown"},
                {"_id": 1, "content": 1},
            )
        )
        report_content: dict = report_res[0]

    except Exception as _:
        return Response(
            content="query error!",
            media_type="application/json; charset=utf-8",
            status_code=500,
        )
    return Response(
        content=report_content.get("content", b""),
        media_type="application/json; charset=utf-8",
        status_code=200,
        headers={"X-Id": str(report_content.get("_id"))},
    )


def decode_demo():
    """
    解码示例
    """
    report_res = list(
        collection.find({"analysis_date": "2025-07-22", "analysis_type": "markdown"})
    )
    # 直接进行UTF-8解码
    try:
        content = report_res[0].get("content", b"").decode("utf-8")
    except UnicodeDecodeError:
        content = None  # 处理解码失败的情况
    print(content)


if __name__ == "__main__":

    res = collection.find({"analysis_date": "2025-07-22"})
    print(res)
