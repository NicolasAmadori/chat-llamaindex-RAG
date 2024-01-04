from fastapi.responses import StreamingResponse, Response
from fastapi import APIRouter, Depends, HTTPException, Request, status, UploadFile, File

from app.api.routers.bot import STORAGE_DIR

file_router = APIRouter()

@file_router.post("")
async def post_file(request: Request):
    try:
        data = await request.json()
        file = data['pdf']
        bot_id = data['bot_id']
        return {"file_received":bot_id}
        #with open(STORAGE_DIR+"/"+bot_id, "wb") as f:
        #    ...
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wrong body format, error {e}",
        )