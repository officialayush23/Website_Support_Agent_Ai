from fastapi import HTTPException, status


# -------------------------
# 4xx CLIENT ERRORS
# -------------------------

def not_found(entity: str):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{entity} not found",
    )


def forbidden(msg: str = "Forbidden"):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=msg,
    )


def bad_request(msg: str = "Bad request"):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=msg,
    )


# -------------------------
# 5xx SERVER ERRORS
# -------------------------

def internal_error(msg: str = "Internal server error"):
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=msg,
    )
