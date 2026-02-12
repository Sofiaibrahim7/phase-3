from fastapi import FastAPI
from .database import create_db_and_tables
from .mcp_tools import router as mcp_tools_router
from .chat_endpoint import router as chat_router
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    create_db_and_tables()
    yield


# Create FastAPI app
app = FastAPI(
    title="Hackathon Todo App API",
    description="A comprehensive todo application featuring task management, AI-powered chatbot assistance, and real-time collaboration capabilities.",
    version="1.0.0",
    lifespan=lifespan
)


# Include routers
app.include_router(mcp_tools_router, prefix="/api/v1", tags=["mcp-tools"])
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])


@app.get("/")
async def root():
    return {"message": "Welcome to the Hackathon Todo App API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend-api"}
