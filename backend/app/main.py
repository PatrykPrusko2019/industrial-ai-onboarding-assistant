from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.db.base import Base
from app.db.session import engine
from app.models import incident_report, user


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Industrial AI Onboarding Assistant API",
    description="AI-powered onboarding assistant for industrial engineers.",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "name": "Industrial AI Onboarding Assistant",
        "status": "running",
        "version": "0.1.0",
    }



@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "backend",
    }