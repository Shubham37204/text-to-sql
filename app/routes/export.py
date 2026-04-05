import csv
import io
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/export")
async def export_csv(request: Request):
    """
    Streams query result as CSV file.
    """

    # 1. Parse JSON body
    data = await request.json()

    columns = data.get("columns", [])
    rows = data.get("rows", [])
    filename = data.get("filename", "query_result")

    # 🔒 Safety: sanitize filename
    filename = filename.replace(" ", "_").replace("/", "")

    # 2. Handle empty data
    if not columns or not rows:
        return StreamingResponse(
            iter(["No data available"]),
            media_type="text/plain"
        )

    # 3. Create buffer
    output = io.StringIO()

    # 4. Write CSV
    writer = csv.writer(output)
    writer.writerow(columns)
    writer.writerows(rows)

    # 5. Reset pointer
    output.seek(0)

    # 6. Return response
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}.csv"'
        }
    )