from fastapi import FastAPI

app = FastAPI(
    title="Industrial AI Onboarding Assistant API",
    description="Backend API for an AI-powered onboarding assistant for industrial engineers.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Industrial AI Onboarding Assistant API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "backend",
    }