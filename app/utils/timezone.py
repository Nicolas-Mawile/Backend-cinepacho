# app/utils/timezone.py

from datetime import datetime
from zoneinfo import ZoneInfo

COLOMBIA_TZ = ZoneInfo("America/Bogota")

def nowColombia():
    return datetime.now(COLOMBIA_TZ)

