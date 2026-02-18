from fastapi import FastAPI
from app.auth.router import router as auth_router
from app.config import settings

app = FastAPI(title="Finance Tracker API", version="1.0.0")


# CORS middleware (для фронтенда)


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@app.get("/")
async def root():
    return {"message": "Finance Tracker API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(auth_router)
