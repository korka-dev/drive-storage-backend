from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import user, storage, auth
from app.storage import connect_database, disconnect_from_database

from rich.console import Console

console = Console()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    console.print(":banana: [cyan underline]Drive Storage is starting ...[/]")
    connect_database()
    yield
    console.print(":mango: [bold red underline] Drive storage shutting down ...[/]")
    disconnect_from_database()


app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(storage.router)

