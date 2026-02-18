from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta
from app.crud import report as report_crud
from app.schemas.report import (
    FinancialSummary
)

class ReportService:

    @staticmethod
    async def get_daily_report(
            db: AsyncSession,
            user_id: int,
            date: str | None = None
    ) -> dict:

        report_date = None
        if date:
            report_date = datetime.fromisoformat(date.replace("Z", "+00:00"))
            if report_date.tzinfo is None:
                report_date = report_date.replace(tzinfo=timezone.utc)

        report = await report_crud.get_daily_report(
            db=db,
            user_id=user_id,
            date=report_date
        )
        return report

    @staticmethod
    async def get_weekly_report(
            db: AsyncSession,
            user_id: int,
            week_start: str | None = None
    ) -> dict:

        start_date = None
        if week_start:
            start_date = datetime.fromisoformat(week_start.replace("Z", "+00:00"))
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)

        report = await report_crud.get_weekly_report(
            db=db,
            user_id=user_id,
            week_start=start_date
        )
        return report

    @staticmethod
    async def get_monthly_report(
            db: AsyncSession,
            user_id: int,
            month: str | None = None
    ) -> dict:

        report_month = None
        if month:
            report_month = datetime.fromisoformat(month.replace("Z", "+00:00"))
            if report_month.tzinfo is None:
                report_month = report_month.replace(tzinfo=timezone.utc)

        report = await report_crud.get_monthly_report(
            db=db,
            user_id=user_id,
            month=report_month
        )
        return report

    @staticmethod
    async def get_custom_report(
            db: AsyncSession,
            user_id: int,
            start_date: str,
            end_date: str
    ) -> dict:

        start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)

        report = await report_crud.get_custom_report(
            db=db,
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt
        )
        return report

    @staticmethod
    async def get_overall_statistics(
            db: AsyncSession,
            user_id: int
    ) -> FinancialSummary:

        stats = await report_crud.get_statistics(db, user_id)

        today = datetime.now(timezone.utc)
        last_30_days_start = today - timedelta(days=30)

        last_30_stats = await report_crud._get_transaction_statistics(
            db=db,
            user_id=user_id,
            start_date=last_30_days_start,
            end_date=today
        )

        return FinancialSummary(
            total_income=stats["total_income"],
            total_expense=stats["total_expense"],
            net_balance=stats["net_balance"],
            last_30_days_income=last_30_stats["total_income"],
            last_30_days_expense=last_30_stats["total_expense"],
            top_categories=stats["top_categories"]
        )























