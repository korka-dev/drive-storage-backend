from mongoengine import connect, disconnect_all, GridFSProxy
from app.config import settings


def connect_database():
    connect(host=settings.mongo_database_url)


def disconnect_from_database():
    disconnect_all()


def iter_chunks(file: GridFSProxy, chunk_size: int = 1024):
    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            break
        yield chunk
