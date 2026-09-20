from fastapi import FastAPI

from benchflow.presentation.lifespan import lifespan
from benchflow.presentation.routes.auth import router as auth_router
from benchflow.presentation.routes.benches import router as benches_router
from benchflow.presentation.routes.users import router as users_router

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(benches_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Return application health status."""

    return {"status": "ok"}
