import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from starlette.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.routes import (users, auth, messages, tags, search, comments, pictures, descriptions, reactions,
                        rating, main_router)
from src.services.secrets_manager import SecretsManager

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://localhost:8000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router.router, tags=["Main"])
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(messages.router, prefix='/api')
app.include_router(search.router, prefix='/api')
app.include_router(pictures.router, prefix='/api')
app.include_router(rating.router, prefix='/api')
app.include_router(descriptions.router, prefix='/api')
app.include_router(tags.router, prefix='/api')
app.include_router(comments.router, prefix='/api')
app.include_router(reactions.router, prefix='/api')

REDIS_HOST = SecretsManager.get_secret("REDIS_HOST")
REDIS_PORT = SecretsManager.get_secret("REDIS_PORT")
REDIS_PASSWORD = SecretsManager.get_secret("REDIS_PASSWORD")


@app.on_event("startup")
async def startup():
    """
    Function to initialize FastAPILimiter on application startup.
    """
    r = await redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(r)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
