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
                    prefix="/api/v2/user",
                    tags=["User"],
                    responses={404 :{"description" :"incorrect request"}}
)

models.Base.metadata.create_all(bind = engine)

def get_db():
    try:
        db= SessionLocal()
        yield db
    finally:
        db.close()

class LoanList(BaseModel):
    account_no: int
    accounter_name : str
    first_name : str
    last_name : str
    ifsc_code : str
    loan_type : str
    loan_amount : int

@router.post('/apply-loan')
async def loan_registration(loan_register : LoanList, user : dict = Depends(get_current_user),\
                            db: Session= Depends(get_db)):
    try:
        if user is None:
            return "Invalid Token ID"
        
        user_model = db.query(models.Users).filter(models.Users.id == user.get("id")).first()

        if user_model is None:
            return "invalid request or incorrect username or password"

        loan_type_model = db.query(models.LoanType).filter(models.LoanType.loan_type_name==loan_register.loan_type.lower()).first()
        if loan_type_model is None:
            return {"incorrect loan type" : "enter correct loantype"}

        new_loan_model = models.LoanList()

        new_loan_model.accounter_name = loan_register.accounter_name
        new_loan_model.first_name= loan_register.first_name
        new_loan_model.last_name = loan_register.last_name
        new_loan_model.ifsc_code=loan_register.ifsc_code
        new_loan_model.loan_amount = loan_register.loan_amount
        new_loan_model.loan_type = loan_type_model.loan_type_name
        new_loan_model.loan_account_no=loan_register.account_no
        new_loan_model.user_id = user.get("id")

        db.add(new_loan_model)
        db.commit()
        return "loan registered sucessfullly"
    except Exception as e:
        return HTTPException(status_code=500,detail = str(e))


@router.get('/get/loanstatus')
async def get_loan_status(user : dict= Depends(get_current_user), db : Session = Depends(get_db)):
    try:
        loan_model = db.query(models.LoanList).filter(models.LoanList.user_id==user.get("id")).first()
        if(loan_model.loan_status == 1):
                status = "approved"
        elif(loan_model.loan_status == 2):
                status = "declined"
        else:
                status="pending"       
        loan_status_check =[loan_model.accounter_name,loan_model.loan_account_no,loan_model.ifsc_code,loan_model.loan_amount,loan_model.loan_type,status]
        return   loan_status_check
    except Exception as e:
        return HTTPException(status_code=500,detail=str(e))

