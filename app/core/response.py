from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Any, Optional, Dict


def ok(data=None, message="OK", code=0) -> Dict[str, Any]:

    return {"code": code, "message": message, "data": data}


def err(message="Bad Request", code=40000, status_code=400, data=None):

    payload = {"code": code, "message": message, "data": data}
    return JSONResponse(content=jsonable_encoder(payload), status_code=status_code)

