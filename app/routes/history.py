from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from html import escape
from app.db.session import get_db
from app.db.models import QueryHistory
from app.services.memory import clear_history

router = APIRouter()

@router.get("/history", response_class=HTMLResponse)
async def get_history(request: Request, db: Session = Depends(get_db)):

    # 1. Get session_id
    session_id = request.cookies.get("session_id", "default")

    # 2. Fetch last 10 queries
    history = (
        db.query(QueryHistory)
        .filter(QueryHistory.session_id == session_id)
        .order_by(desc(QueryHistory.created_at))
        .limit(10)
        .all()
    )

    # 3. Empty state
    if not history:
        return HTMLResponse(
            '<div class="text-sm opacity-50 p-4">No queries yet</div>'
        )

    # 4. Build HTML
    html_items = ""

    for item in history:
        question = item.question[:60] + \
            ("..." if len(item.question) > 60 else "")
        row_count = item.row_count or 0

        # Format time
        time_str = item.created_at.strftime("%b %d, %H:%M")

        html_items += f"""
        <div class="card bg-base-100 border border-base-200 cursor-pointer hover:border-primary transition"
             hx-post="/api/query"
             hx-vals='{{"question": "{escape(item.question)}"}}'
             hx-target="#chat-container"
             hx-swap="beforeend">

            <div class="card-body p-3 gap-1">
                <p class="text-sm font-medium">{question}</p>

                <div class="flex items-center justify-between text-xs opacity-50">
                    <span>{time_str}</span>
                    <span class="badge badge-outline badge-sm">{row_count} rows</span>
                </div>
            </div>
        </div>
        """

    return HTMLResponse(f"""
    <div class="flex flex-col gap-2">
        {html_items}
    </div>
    """)


@router.post("/history/clear", response_class=HTMLResponse)
async def clear_session_history(request: Request, db: Session = Depends(get_db)):

    # 1. Get session_id
    session_id = request.cookies.get("session_id", "default")

    # 2. Clear in-memory history
    clear_history(session_id)

    # 3. Return success UI
    return HTMLResponse(
        '<div class="badge badge-success badge-sm">Conversation cleared</div>'
    )
