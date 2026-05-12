from fastapi import APIRouter
from app.api.stations import router as stations_router
from app.api.postgre_api import router as postgre_api_router
from app.api.model_api import router as model_api_router


router = APIRouter()

router.include_router(stations_router, prefix="/stations", tags=["stations"])
router.include_router(postgre_api_router, prefix="/postgre", tags=["postgre"])
router.include_router(model_api_router, prefix="/model", tags=["model"])