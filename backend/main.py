from dotenv import load_dotenv
load_dotenv()

import logging
import os
import uvicorn
from app.api.routers.chat import chat_router
from app.api.routers.bot import bot_router
from app.api.routers.file import file_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from milvus import default_server
from pymilvus import connections
from app.utils.index import initialize_vector_store

app = FastAPI()


environment = os.getenv("ENVIRONMENT", "dev")  # Default to 'development' if not set


if environment == "dev":
    logger = logging.getLogger("uvicorn")
    logger.warning("Running in development mode - allowing CORS for all origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(chat_router, prefix="/api/chat")
app.include_router(bot_router, prefix="/api/bot")
app.include_router(file_router, prefix="/api/file")


if __name__ == "__main__":
    default_server.start()
    connections.connect("default", host="0.0.0.0")
    initialize_vector_store()
    uvicorn.run(app="main:app", host="0.0.0.0", port=37331,reload=True)
