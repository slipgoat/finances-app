from datetime import datetime, date, timedelta

from dateutil.relativedelta import relativedelta


def round_float(value: float) -> float:
    return round(value, 2)


def get_current_period() -> tuple:
    return get_period(offset_months=0)


def get_period(offset_months: int) -> tuple:
    now = datetime.utcnow()
    start_date = date(now.year, now.month, 1) + relativedelta(months=offset_months)
    end_date = start_date + relativedelta(months=1) - timedelta(days=1)
    return start_date, end_date
