"""
FastAPI web interface for dark pattern detection agent.

Provides web UI for configuring, running, and reviewing explorations.
"""

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from src.agent.orchestrator import DarkPatternOrchestrator
from src.frameworks.ieee_7010 import IEEE7010Framework
from src.frameworks.dsa_article_28 import DSAArticle28Framework
from src.frameworks.attention_economy import AttentionEconomyFramework
from src.frameworks.ico_aadc import ICOAADCFramework
from src.utils.storage import get_storage

# Initialize FastAPI app
app = FastAPI(
    title="Dark Pattern Detection Agent",
    description="Multi-framework dark pattern detection with explainable AI",
    version="0.1.0",
)

# Setup templates and static files
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Available frameworks
FRAMEWORKS = {
    "ieee_7010": IEEE7010Framework,
    "dsa_article_28": DSAArticle28Framework,
    "attention_economy": AttentionEconomyFramework,
    "ico_aadc": ICOAADCFramework,
}


class ExplorationRequest(BaseModel):
    """Request model for starting exploration."""

    url: str
    session_name: Optional[str] = None
    frameworks: list[str] = ["ieee_7010", "dsa_article_28"]
    max_depth: int = 5


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page with exploration configuration."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "available_frameworks": [
                {
                    "id": key,
                    "name": framework.name,
                    "description": framework.description,
                }
                for key, framework in FRAMEWORKS.items()
            ],
        },
    )


@app.post("/api/explore")
async def start_exploration(req: ExplorationRequest):
    """Start a new exploration."""
    try:
        # Validate frameworks
        selected_frameworks = []
        for fw_id in req.frameworks:
            if fw_id not in FRAMEWORKS:
                raise HTTPException(status_code=400, detail=f"Invalid framework: {fw_id}")
            selected_frameworks.append(FRAMEWORKS[fw_id])

        # Initialize storage
        storage = await get_storage()

        # Create orchestrator
        orchestrator = DarkPatternOrchestrator(
            frameworks=selected_frameworks,
            max_depth=req.max_depth,
            storage=storage,
        )

        # Run exploration (async)
        session = await orchestrator.explore(
            url=req.url, session_name=req.session_name
        )

        return {
            "success": True,
            "session_id": session.session_id,
            "patterns_detected": session.total_patterns_detected,
            "pages_visited": len(session.pages_visited),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
async def list_sessions(limit: int = 50, offset: int = 0):
    """List all exploration sessions."""
    storage = await get_storage()
    sessions = await storage.list_sessions(limit=limit, offset=offset)
    return {"sessions": sessions}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get details of a specific session."""
    storage = await get_storage()
    session = await storage.load_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session.model_dump(mode="json")


@app.get("/api/sessions/{session_id}/findings")
async def get_session_findings(session_id: str):
    """Get findings for a session."""
    storage = await get_storage()
    findings = await storage.get_findings_by_session(session_id)

    return {
        "findings": [f.model_dump(mode="json") for f in findings],
        "total": len(findings),
    }


@app.get("/api/statistics")
async def get_statistics():
    """Get overall statistics."""
    storage = await get_storage()
    stats = await storage.get_statistics()
    return stats


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("WEB_PORT", 8000))
    uvicorn.run(
        "src.web.app:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("WEB_RELOAD", "false").lower() == "true",
    )
