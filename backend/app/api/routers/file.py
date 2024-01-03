from fastapi.responses import StreamingResponse, Response
from fastapi import APIRouter, Depends, HTTPException, Request, status, UploadFile, File

from app.api.routers.bot import STORAGE_DIR

file_router = APIRouter()

@file_router.post("")
async def post_file(
    bot_name: str,
    file: UploadFile = File(...),
):
    with open(STORAGE_DIR+"/"+bot_name, "wb") as f:
        ...