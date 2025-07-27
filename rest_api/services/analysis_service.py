import datetime
from typing import Any

from rest_api.entity.request import AnalysisRequest
from tradingagents.utils.logging_manager import get_logger
from web.utils.report_exporter import ReportExporter

# 导入日志模块
logger = get_logger("rest_api_analysis")


class AnalysisService:
    """
    分析服务
    """

    def __init__(self) -> None:
        pass

    def validation(self, request: AnalysisRequest) -> bool:
        """
        验证分析参数
        """
        try:
            from web.utils.analysis_runner import validate_analysis_params

            # 验证分析参数
            is_valid, validation_errors = validate_analysis_params(
                stock_symbol=request.stock_symbol,
                analysis_date=request.analysis_date,
                analysts=request.analysts,
                research_depth=request.research_depth,
                market_type=request.market_type,
            )

            if not is_valid:
                # 显示验证错误
                for error in validation_errors:
                    logger.error(error)
                return False
            return True
        except Exception as _:
            return False

    def analysis_stock(self, request: AnalysisRequest) -> None:
        """
        分析股票代码的股票信息
        """
        try:
            from web.utils.analysis_runner import (
                format_analysis_results,
                run_stock_analysis,
            )

            results = run_stock_analysis(
                stock_symbol=request.stock_symbol,
                analysis_date=request.analysis_date,
                analysts=request.analysts,
                research_depth=request.research_depth,
                llm_provider=request.llm_provider,
                market_type=request.market_type,
                llm_model=request.llm_model,
                # progress_callback=request.progress_callback,
            )
            formatted_results = format_analysis_results(results)

            # 导出并保存
            export(formatted_results)
        except Exception as e:
            logger.error(f"❌ 分析股票代码的股票信息失败: {e}")


server = AnalysisService()


def analysis_service() -> AnalysisService:
    """
    分析服务依赖
    """
    return server


report_exporter = ReportExporter()


def export(results: dict[str, Any]) -> None:
    """
    导出分析结果
    """
    if not report_exporter.export_available:
        logger.error("⚠️ 导出功能需要安装额外依赖包")
        raise RuntimeError("❌ 导出功能需要安装额外依赖包")

    # "markdown", "md"
    export_item(results, {"en": "markdown", "ext": "md"})
    export_item(results, {"en": "docx", "ext": "docx"})
    export_item(results, {"en": "pdf", "ext": "pdf"})


def export_item(results: dict[str, Any], extension: dict) -> None:
    """
    导出分析结果的项目。
    """
    try:
        # 生成文件名
        stock_symbol = results.get("stock_symbol", "analysis")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        content = report_exporter.export_report(results, extension.get("en"))
        if content:
            filename = f"{stock_symbol}_analysis_{timestamp}.{extension.get('ext')}"
            logger.info(f"✅ {extension.get('en')}导出成功，文件名: {filename}")
            # save
            save_mongodb(
                filename=filename,
                content=content,
                symbol=stock_symbol,
                analysis_type=extension.get("en"),
                analysis_date=results.get("analysis_date"),
            )
        else:
            logger.error(f"❌ {extension.get('en')}导出失败，content为空")
            raise RuntimeError(f"❌ {extension.get('en')}导出失败，content为空")
    except Exception as e:
        logger.error(f"❌ {extension.get('en')}导出失败: {e}")
        raise e


def save_mongodb(
    filename: str, content: str, symbol: str, analysis_type: str, analysis_date: str
) -> None:
    """
    保存分析结果到MongoDB。
    """
    try:
        from tradingagents.config.database_manager import (
            get_database_manager,
            get_mongodb_client,
        )

        db_manager = get_database_manager()
        db_client = get_mongodb_client()[db_manager.mongodb_config["database"]]
        collection = db_client.analysis_reports
        # 保存数据到集合
        document = {
            "filename": filename,
            "content": content,
            "symbol": symbol,
            "analysis_type": analysis_type,
            "analysis_date": analysis_date,
            "created_at": datetime.datetime.now(),
        }
        collection.insert_one(document)
    except Exception as e:
        logger.error(f"❌ 保存分析结果到MongoDB失败: {e}")
