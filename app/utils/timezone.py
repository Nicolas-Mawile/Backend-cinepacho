# app/utils/timezone.py

from datetime import datetime
from zoneinfo import ZoneInfo

COLOMBIA_TZ = ZoneInfo("America/Bogota")

def nowColombia():
    """Aware datetime Colombia. Usar solo para JWT (exp claim)."""
    return datetime.now(COLOMBIA_TZ)

def nowNaive():
    """Naive datetime en hora Colombia. Usar para comparaciones y almacenamiento en BD."""
    return datetime.now(COLOMBIA_TZ).replace(tzinfo=None)

