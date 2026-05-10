"""POST /api/pipeline/trigger — manual pipeline trigger (API key required)."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel

from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])
settings = get_settings()


class TriggerResponse(BaseModel):
    status: str
    message: str


@router.post("/trigger", response_model=TriggerResponse)
async def trigger_pipeline(x_api_key: str | None = Header(default=None)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    # Import here to avoid circular imports; pipeline runs in a separate process
    # so we signal it via Redis or simply log that it should be triggered
    try:
        from app.services.cache import cache_publish
        await cache_publish("lcps:pipeline:trigger", {"action": "run_now"})
        return TriggerResponse(status="ok", message="Pipeline trigger signal sent")
    except Exception as exc:
        logger.error("Failed to trigger pipeline: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
