from fastapi.responses import StreamingResponse, Response
from fastapi import APIRouter, Depends, HTTPException, Request, status, UploadFile, File
import base64

from app.api.routers.bot import DATA_DIR
from app.utils.index import add_bot_to_refresh

file_router = APIRouter()

# TODO: complete the route to receive a file
@file_router.post("")
async def post_file(request: Request):
    try:
        data = await request.json()
        filename = data['filename']
        bot_id = data['bot_id']
        file = ""
        if filename.endswith(".pdf"):
            file_base64 = data['file']
            file = base64.b64decode(file_base64)
            with open(DATA_DIR+"/"+bot_id+"/"+filename, "wb") as fh:
                fh.write(file)
        else:
            file = data['file']
            with open(DATA_DIR+"/"+bot_id+"/"+filename, "w") as fh:
                fh.write(file)        
        add_bot_to_refresh(bot_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wrong body format, error {e}",
        )
    return {"ok": True}