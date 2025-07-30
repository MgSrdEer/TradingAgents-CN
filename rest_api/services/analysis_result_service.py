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


def get_report_list_date(analysis_date: str, weixinid: str) -> Response:
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
                {
                    "analysis_date": analysis_date,
                    "analysis_type": "markdown",
                    "weixinid": weixinid,
                },
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


def get_report_id(report_id: str, weixinid: str) -> Response:
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
                {
                    "_id": ObjectId(report_id),
                    "analysis_type": "markdown",
                    "weixinid": weixinid,
                },
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
