import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.db.models import QueryHistory
from app.db.schema import get_schema_description
from app.services.llm import generate_sql
from app.services.memory import get_history, add_turn
from app.services.chart import detect_chart_type, build_chart_config
from app.models.request import QueryRequest, QueryResponse
from app.utils.html_renderer import render_result
from decimal import Decimal

router = APIRouter()

def error_html(message: str) -> HTMLResponse:
    return HTMLResponse(
        f'<div class="alert alert-error text-sm shadow-md">'
        f'<span>{message}</span></div>'
    )


@router.post("/query", response_class=HTMLResponse)
async def run_query(request: Request, db: Session = Depends(get_db)):
    try:
        # 1. Session
        session_id = request.cookies.get("session_id") or str(uuid.uuid4())

        # 2. Input
        form = await request.form()
        question = form.get("question", "").strip()
        if not question:
            return error_html("Question cannot be empty.")

        # 3. Schema + history
        schema = get_schema_description(db)
        history = get_history(session_id)

        # 4. LLM
        sql = generate_sql(question, schema, history)

        if "INVALID_QUERY" in sql.upper():
            return error_html("This question can't be answered from the available data.")

        if not sql.strip().lower().startswith("select"):
            return error_html("Only SELECT queries are allowed.")

        # 5. Execute
        try:
            result = db.execute(text(sql))
            columns = list(result.keys())
            rows = [list(row) for row in result.fetchall()]
        except Exception as e:
            err = str(e)
            if "does not exist" in err:
                return error_html("This question references data that doesn't exist in the database.")
            return error_html(f"Database error: {err}")

        # 6. Memory
        add_turn(session_id, question, sql)

        # 7. Save to DB
        db.add(QueryHistory(
            session_id=session_id,
            question=question,
            sql=sql,
            row_count=len(rows)
        ))
        db.commit()

        # 8. Chart
        chart_type = detect_chart_type(columns, rows)
        chart_config = build_chart_config(
            columns, rows, chart_type) if chart_type else None

        # 9. Render
        html = render_result(
            question=question,
            sql=sql,
            columns=columns,
            rows=rows,
            chart_config=chart_config
        )

        # 10. Set cookie
        response = HTMLResponse(html)
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=60 * 60 * 24 * 7,
            httponly=True
        )
        return response

    except Exception as e:
        # Catches schema load failures, LLM errors, anything unexpected
        return error_html(f"Unexpected error: {str(e)}")


@router.post("/query/json", response_model=QueryResponse)
def run_query_json(payload: QueryRequest, db: Session = Depends(get_db)):
    schema = get_schema_description(db)
    sql = generate_sql(payload.question, schema)

    if "INVALID_QUERY" in sql.upper():
        raise HTTPException(status_code=400, detail="Invalid query")
    if not sql.strip().lower().startswith("select"):
        raise HTTPException(
            status_code=400, detail="Only SELECT queries allowed")

    try:
        result = db.execute(text(sql))
        columns = list(result.keys())
        # rows = [list(row) for row in result.fetchall()]
        rows = [
            [float(cell) if isinstance(cell, Decimal)
             else cell for cell in row]
            for row in result.fetchall()
        ]
        return QueryResponse(
            question=payload.question,
            sql=sql,
            columns=columns,
            rows=rows
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
