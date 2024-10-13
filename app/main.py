from fastapi import FastAPI, Depends
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy.orm import Session
import crud
import models
from database import SessionLocal, engine
from model.qa import get_answer
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/')
def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def save_qa(query: str, db: Session = Depends(get_db)):
    answer = get_answer(query)
    existing_doc = db.query(models.QA).filter(models.QA.question == query).first()     
    if not existing_doc: 
            db_qa = crud.create_qa(db, question=query,answer=answer)
            print("success is Saved")


@app.get('/get_answer/')
def get_answer(query: str, db: Session = Depends(get_db)):
    save_qa(query,db)  
    
    qa_record = db.query(models.QA).first()  
    
    if qa_record:
        response = {
            "answer": qa_record.answer 
        }
    else:
        response = {
            "answer": "No answer found in the database."
        }

    return response



