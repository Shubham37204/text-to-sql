import json
from app.utils.serializer import safe_dumps

def detect_chart_type(columns: list, rows: list) -> str | None:
    """
    Detects best chart type based on data shape.
    """

    # 1. No data or not exactly 2 columns → no chart
    if not rows or len(columns) != 2:
        return None

    # 2. Check if second column is numeric
    is_numeric = True
    for row in rows:
        try:
            float(row[1])
        except (ValueError, TypeError):
            is_numeric = False
            break

    if not is_numeric:
        return None

    # 3. Check if first column is date-like
    first_value = str(rows[0][0])
    is_date_like = "-" in first_value and len(first_value) > 6

    # 4. Decide chart type
    if is_date_like:
        return "line"

    return "bar"


def build_chart_config(columns: list, rows: list, chart_type: str) -> str:
    """
    Builds Chart.js config JSON string.
    """

    # 1. Labels (x-axis)
    labels = [str(row[0]) for row in rows]

    # 2. Data (y-axis)
    data = []
    for row in rows:
        try:
            data.append(float(row[1]))
        except (ValueError, TypeError):
            data.append(0)

    # 3. Config object
    config = {
        "type": chart_type,
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": columns[1],
                    "data": data,
                    "backgroundColor": "#378ADD",
                    "borderColor": "#378ADD",
                    "fill": False if chart_type == "line" else True,
                    "tension": 0.3 if chart_type == "line" else 0
                }
            ]
        },
        "options": {
            "responsive": True,
            "plugins": {
                "legend": {"display": False}
            }
        }
    }

    # 4. Return JSON string
    return safe_dumps(config)