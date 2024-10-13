from sqlalchemy.orm import Session
import models

def create_qa(db: Session, question: str, answer: str):
    db_qa = models.QA(question=question, answer=answer)
    db.add(db_qa)
    db.commit()
    db.refresh(db_qa)
    return db_qa

