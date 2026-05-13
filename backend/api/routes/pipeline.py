from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException

from backend.api.schemas import PipelineTriggerResponse
from backend.config import settings

router = APIRouter(tags=["pipeline"])


def _verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.pipeline_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")


@router.post("/pipeline/trigger", response_model=PipelineTriggerResponse)
async def trigger_pipeline(
    background_tasks: BackgroundTasks,
    _: None = Depends(_verify_api_key),
):
    """
    Kick off a pipeline run in the background.
    The pipeline worker is a separate process — this endpoint just signals it
    via Redis so the main event loop is never blocked by LLM calls.
    """
    from backend.cache.client import publish_update

    background_tasks.add_task(publish_update, {"event": "pipeline_triggered"})

    return PipelineTriggerResponse(
        triggered=True,
        message="Pipeline run queued. Check /api/health for status.",
    )
