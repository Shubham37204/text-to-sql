from sqlalchemy import Column, Integer, Text, DateTime, func
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class QueryHistory(Base):
    """
    Stores every successful query run by a user.
    One row = one query execution.
    """
    __tablename__ = "query_history"

    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(Text, nullable=False, index=True)  # browser session
    question   = Column(Text, nullable=False)              # user's NL question
    sql        = Column(Text, nullable=False)              # generated SQL
    row_count  = Column(Integer, default=0)                # how many rows returned
    created_at = Column(DateTime, server_default=func.now())