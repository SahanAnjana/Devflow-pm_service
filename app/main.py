# hr-service/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine
from app.api.project import router as project_router      
from app.api.task import router as task_router
from app.api.resource import router as resource_router

app = FastAPI(title="Project Service API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include routers with appropriate prefixes
app.include_router(project_router, prefix="/projects", tags=["projects"])
app.include_router(task_router, prefix="/tasks", tags=["tasks"])
app.include_router(resource_router, prefix="/resources", tags=["resources"])

def create_tables():
    Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    create_tables()

@app.get("/health")
def health_check():
    return {"status": "ok"}