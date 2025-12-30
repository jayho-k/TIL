from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from app.core.database import Base

class UserEmail(Base):
    __tablename__ = "user_email"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String, index=True)
    success_or_fail: Mapped[str] = mapped_column(String)
