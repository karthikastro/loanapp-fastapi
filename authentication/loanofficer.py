import sys
sys.path.append("..")

from fastapi import APIRouter,Depends,HTTPException
from database import SessionLocal,engine
from sqlalchemy.orm import Session
import models
from pydantic import BaseModel,Field
from .auth import get_hash_password,get_current_user,get_user_exception,verify_password
from datetime import datetime

router = APIRouter(
                    prefix="/api/v2/loanofficer",
                    tags=["Loan Officer"],
                    responses={404 :{"description" :"incorrect request"}}
)

models.Base.metadata.create_all(bind = engine)

def get_db():
    try:
        db= SessionLocal()
        yield db
    finally:
        db.close()


@router.get('/get-all-loanlist')
async def get_all_loans(user : dict = Depends(get_current_user),db : Session=Depends(get_db)):
    try: 
        if user.get("role") != "loanofficer":
            return {"incorrect request" : "unauthorized"}
        all_loan_model = db.query(models.LoanList).all()
        return all_loan_model
    except Exception as e:
        return HTTPException(status_code=500,detail=str(e))


@router.put('/update/loanstatus')
async def update_loan_status(loan_status : int,user : dict = Depends(get_current_user),db : Session=Depends(get_db)):
    try: 
        user_role =user.get("role")
        if user_role != "loanofficer":
            return {"request failed" : "Unauthorized request"}
        loan_model=db.query(models.LoanList).filter(models.LoanList.user_id==user.get("id")).first()
        if loan_model is not None:
            loan_model.loan_status = loan_status
            db.add(loan_model)
            db.commit()
            if(loan_model.loan_status == 1):
                return {"loan " : "approved"}
            elif(loan_model.loan_status == 2):
                return {"loan" : "declined"}
            else:
                return {"loan status" : "pending"}
        else:
            return {"loan id " : "not found"}
    except Exception as e:
        return HTTPException(status_code=500,detail=str(e))
