import json
from decimal import Decimal


class SafeEncoder(json.JSONEncoder):
    """
    Extends the default JSON encoder to handle types
    PostgreSQL returns that standard json.dumps can't handle.

    Currently handles:
    - Decimal → float  (NUMERIC, MONEY columns)
    - You can add: datetime → str, UUID → str if needed later
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def safe_dumps(data) -> str:
    """Use this everywhere instead of json.dumps()"""
    return json.dumps(data, cls=SafeEncoder)