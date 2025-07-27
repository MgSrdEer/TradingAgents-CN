from fastapi import BackgroundTasks, Depends, FastAPI, Response

from rest_api.entity.request import AnalysisRequest
from rest_api.modules.initialze import init
from rest_api.services.analysis_result_service import (
    get_report_id,
    get_report_list_date,
)
from rest_api.services.analysis_service import AnalysisService, analysis_service

# 初始化系统
init()

# 部署api
app = FastAPI()


@app.get("/active")
def active() -> dict:
    """
    controller
    检查服务是否激活
    """
    return {"Hello": "World"}


@app.post("/analysis")
async def analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    service: AnalysisService = Depends(analysis_service),
) -> str:
    """
    controller
    分析股票代码的股票信息
    """

    if not service.validation(request):
        return Response(
            content="invalid request!",
            media_type="application/json; charset=utf-8",
            status_code=400,
        )
    # 后台执行
    background_tasks.add_task(service.analysis_stock, request)
    return Response(
        content="starting, check mongodb!",
        media_type="application/json; charset=utf-8",
        status_code=202,  # 202 Accepted 表示请求已被接受处理
    )


@app.get("/result/filelist")
def analysis_result(date: str) -> dict:
    """
    controller
    获取分析结果

    Args:
        file_id: 文件ID

    /result/filelist?date=2025-07-22
    """

    return get_report_list_date(date)


@app.get("/result/filecontent")
def analysis_result_content(_id: str) -> dict:
    """
    controller
    获取分析结果

    Args:
        _id: 文件ID

    /result/filecontent?_id=659f91367163470000000000
    """

    return get_report_id(_id)
