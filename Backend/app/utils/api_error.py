# app/utils/api_error.py

from fastapi import HTTPException, status

def not_found(entity: str):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{entity} not found",
    )

def forbidden(msg="Forbidden"):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=msg,
    )

def bad_request(msg="Bad request"):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=msg,
    )
