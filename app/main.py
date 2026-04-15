from fastapi import FastAPI
from app.api.router import router
from app.exceptions import ExternalAPIError
from fastapi.responses import JSONResponse
from fastapi import Request
from app.db.db import engine, Base
import app.db.models 

app = FastAPI()

@app.on_event("startup")
def _create_tables():
    Base.metadata.create_all(bind=engine)

@app.exception_handler(ExternalAPIError)
async def handle_external_api_error(request: Request, exc: ExternalAPIError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "external_api_error",
            "message": exc.message,
            "source": exc.url
        }
    )

app.include_router(router)