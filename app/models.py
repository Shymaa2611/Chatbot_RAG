from sqlalchemy import Column, Integer, String
from database import Base

class QA(Base):
    __tablename__ = "qa"

    id = Column(Integer, primary_key=True, index=True)
    question= Column(String, index=True)
    answer = Column(String,index=True)
