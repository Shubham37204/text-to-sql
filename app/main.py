from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes import query, history, export

app = FastAPI(
    title="Text-to-SQL",
    description="Natural language to SQL using Groq + PostgreSQL",
    version="1.0.0"
)

# Allow frontend (React on port 5173) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route groups
app.include_router(query.router, prefix="/api")
app.include_router(history.router, prefix="/api")   # NEW
app.include_router(export.router,  prefix="/api")   # NEW
# Add after app.include_router(...)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")
