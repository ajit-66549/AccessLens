from datetime import date
from calendar import monthrange

from django.db.models import F

from .models import Plan, OrganizationSubscription, UsageRecord

DEFAULT_FREE_PLAN_CODE = "free"

def _month_window(day: date) -> tuple[date, date]:
    start = day.replace(day=1)    # replace the given date with the first date of month
    end = day.replace(day=monthrange(day.year, day.month)[1]) # last date of that month
    return start, end

def get_or_create_default_plan() -> Plan:
    plan, _ = Plan.objects.get_or_create(
        code=DEFAULT_FREE_PLAN_CODE,
        defaults={"name": "Free", "app_limit": 1, "monthly_request_limit": 10000},
        )
    return plan

def get_or_create_org_subscription(org):
    default_plan = get_or_create_default_plan()
    today = date.today()
    period_start, period_end = _month_window(today)
    subscription, _ = OrganizationSubscription.objects.get_or_create(
        organization=org,
        defaults={
            "plan": default_plan,
            "status": "active",
            "current_period_start": period_start,
            "current_period_end": period_end,
        }
    )
    return subscription

def can_create_app(org) -> bool:
    subscription = get_or_create_org_subscription(org)
    return org.apps.filter(is_active=True).count < subscription.plan.app_limit # total app < allowed app in that plan

# increase usage record
def record_usage(org, metric: str, quantity: int = 1, day: date | None = None) -> UsageRecord:
    tracked_day = day or date.today()
    period_start, period_end = _month_window(tracked_day)
    record, _ = UsageRecord.objects.get_or_create(
        organization=org,
        metric=metric,
        period_start=period_start,
        period_end= period_end,
        defaults={"quanity": 0},
    )
    # increase the quantity count in database
    UsageRecord.objects.filter(id=record.id).update(quantity=F("quantity")+quantity)
    record.refresh_from_db()
    return record