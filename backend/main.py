from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from agent.core import run_agent
from agent.schemas import AnalysisResult

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="FinAgent API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# In-memory store for analysis results (fine for a demo)
results_store: dict[str, AnalysisResult] = {}


@app.post("/api/upload")
async def upload_csv(file: UploadFile) -> dict:
    """Accept a CSV upload, save it, return an analysis_id."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    analysis_id = uuid.uuid4().hex[:12]
    file_path = UPLOAD_DIR / f"{analysis_id}.csv"

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    file_path.write_bytes(contents)

    results_store[analysis_id] = AnalysisResult(
        analysis_id=analysis_id, status="pending"
    )

    return {"analysis_id": analysis_id, "status": "pending"}


@app.post("/api/analyze/{analysis_id}")
async def analyze(analysis_id: str) -> dict:
    """Kick off the agent analysis for the given upload."""
    csv_path = UPLOAD_DIR / f"{analysis_id}.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="Upload not found")

    if analysis_id in results_store and results_store[analysis_id].status == "completed":
        return {"analysis_id": analysis_id, "status": "completed"}

    results_store[analysis_id] = AnalysisResult(
        analysis_id=analysis_id, status="running"
    )

    try:
        result = await run_agent(analysis_id, str(csv_path))
        results_store[analysis_id] = result
    except Exception as e:
        logging.error(f"Agent failed: {e}")
        results_store[analysis_id] = AnalysisResult(
            analysis_id=analysis_id,
            status="failed",
            error=str(e),
        )

    return {"analysis_id": analysis_id, "status": results_store[analysis_id].status}


@app.get("/api/results/{analysis_id}")
async def get_results(analysis_id: str) -> AnalysisResult:
    """Return the analysis results."""
    if analysis_id not in results_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return results_store[analysis_id]


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}
