from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.database.models import User

class Auth:
    async def get_current_user(self, token: str, session: Session):

        user = session.query(User).filter(User.token == token).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


        if user.ban_status:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You have been banned")

        return user
