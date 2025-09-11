from fastapi import HTTPException, status

def assert_role(role: str, allowed: list[str]):
    if role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role clearance")
