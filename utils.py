from datetime import datetime, date, timedelta


def round_float(value: float) -> float:
    return round(value, 2)


def get_current_period() -> tuple:
    now = datetime.utcnow()
    start_date = date(now.year, now.month, 1)
    end_month = 1 if now.month == 12 else now.month + 1
    end_year = now.year + 1 if now.month == 12 else now.year
    end_date = date(end_year, end_month, 1) - timedelta(days=1)
    return start_date, end_date


def get_period(offset_months: int) -> tuple:
    now = datetime.utcnow()
    start_month = offset_months if now.month == 12 and offset_months > 0 else now.month + offset_months
    start_year = now.year + 1 if now.month == 12 and offset_months > 0 else now.year
    start_date = date(start_year, start_month, 1)
    end_month = 1 if start_date.month == 12 else start_date.month + 1
    end_year = start_date.year + 1 if start_date.month == 12 else start_date.year
    end_date = date(end_year, end_month, 1) - timedelta(days=1)
    return start_date, end_date
