from .meetings import router as meetings_router
from .categories import router as categories_router
from .search import router as search_router
from .health import router as health_router
from .pipeline import router as pipeline_router

__all__ = ["meetings_router", "categories_router", "search_router", "health_router", "pipeline_router"]
