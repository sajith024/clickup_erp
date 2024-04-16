import re
from datetime import timedelta
from django.utils.timezone import now

from rest_framework.serializers import ValidationError


def check_name(value):
    if not re.match(r"^[a-zA-Z0-9_]{1,20}$", value):
        raise ValidationError(
            "Should only contain alphanumeric characters and underscores, maximum 20 length"
        )


def check_date_range(value):
    today = now()
    one_year = today + timedelta(days=365)
    if value < today or value > one_year:
        raise ValidationError(
            "Date should be today or greater, and less than one year."
        )

def check_date_below(value):
    today = now().date()
    if value < today:
        raise ValidationError(
            "Date should be today or greater"
        )
