from datetime import datetime, timedelta
from django.db.models import Count
from .models import Transaction


DAILY = "daily"
WEEKLY = "weekly"
MONTHLY = "monthly"
DATE = "date"


def report(report=None, sort_by=DATE):
    today = datetime.now().date()
    if sort_by is None:
        sort_by = DATE
    if sort_by == DATE:
        sort_by = f"-{DATE}"
    if report is None and sort_by is not None:
        print("&&&&& Report called: ", sort_by)
        return Transaction.objects.all().order_by(f"{sort_by}")

    if report is None and sort_by is None:
        return Transaction.objects.all().order_by(f"{sort_by}")
    
    if report == DAILY:
        data = Transaction.objects.filter(date__date=today).order_by(f"{sort_by}")
        return data

    elif report == WEEKLY:
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        data = Transaction.objects.filter(
            date__date__range=[start_of_week, end_of_week]
        ).order_by(f"{sort_by}")
        return data

    elif report == MONTHLY:
        start_of_month = today.replace(day=1)
        end_of_month = start_of_month.replace(day=28) + timedelta(days=4)
        data = Transaction.objects.filter(
            date__date__range=[start_of_month, end_of_month]
        ).order_by(f"{sort_by}")
        return data

    


# def weekly_report():
#     start_of_week = today - timedelta(days=today.weekday())
#     today = datetime.now().date()
#     end_of_week = start_of_week + timedelta(days=6)
#     data = Transaction.objects.filter(date__date__range=[start_of_week, end_of_week])
#     return data
#
#
# def monthly_report():
# today = datetime.now().date()
# start_of_month = today.replace(day=1)
# end_of_month = start_of_month.replace(day=28) + timedelta(days=4)
# data = Transaction.objects.filter(date__date__range=[start_of_month, end_of_month])
# return data
