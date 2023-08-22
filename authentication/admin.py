import sys
sys.path.append("..")

from fastapi import APIRouter,Depends,HTTPException
from database import SessionLocal,engine
from sqlalchemy.orm import Session
import models
from pydantic import BaseModel,Field
from .auth import get_hash_password,get_current_user,get_user_exception
from datetime import datetime

router = APIRouter(
                    prefix="/api/v2/admin",
                    tags=["Admin"],
                    responses={404 :{"description" :"incorrect request"}}
)


models.Base.metadata.create_all(bind = engine)

def get_db():
    try:
        db= SessionLocal()
        yield db
    finally:
        db.close()




@router.get('/all_loans')
async def get_loan_status(user : dict= Depends(get_current_user), db : Session = Depends(get_db)):
    if user.get("role") != "admin":
        return {"incorrect request" : "unauthorized"}
    loan_model = db.query(models.LoanList).all()     
    return   loan_model

   
class RegLoanOfficer(BaseModel):
    officer_name : str
    first_name :str
    last_name : str
    officer_email : str
    ifsc_code : str
    officer_password : str
    officer_password2 : str

@router.post('/create-loanofficer')
async def register_loan_officer(loanoffreg : RegLoanOfficer, user : dict = Depends(get_current_user),db:Session=Depends(get_db)):
    try:
        if user.get("role")!= "admin":
            return {"incorrect request" : "unauthorized"}
        officer_model = models.LoanOfficer()
        check = db.query(models.LoanOfficer).filter(models.LoanOfficer == loanoffreg.officer_name).first()
        checkmail = db.query(models.LoanOfficer).filter(models.LoanOfficer == loanoffreg.officer_email).first()
        if check is not None:
            return {"officer name already taken ": "request failed"}
        if checkmail is not None:
            return{"officer email already taken ": "request failed"}
        if loanoffreg.officer_password != loanoffreg.officer_password2:
            return {"password must be same" : "request failed"}
        officer_model.officer_name = loanoffreg.officer_name
        officer_model.first_name = loanoffreg.first_name
        officer_model.last_name = loanoffreg.last_name
        officer_model.officer_email= loanoffreg.officer_email
        officer_model.ifsc_code = loanoffreg.ifsc_code
        hash_password = get_hash_password(loanoffreg.officer_password)
        officer_model.hash_password=hash_password
        db.add(officer_model)
        db.commit()
        return {201 : "officer registration sucessful"}
    except Exception as e:
        return HTTPException(status_code=500,detail=str(e))


@router.post('/create-loantype')
async def create_loan_type(loantype : str, user : dict = Depends(get_current_user),db : Session = Depends(get_db)):
    try:
        if user.get("role") != "admin":
            return {"incorrect request" : "unauthorized"}
        loan_type_model = db.query(models.LoanType).filter(models.LoanType.loan_type_name==loantype).first()
        if loan_type_model is not None: 
            return {"loan type already exists" : "retry new loan type"}
        loan_type_model1= models.LoanType()
        loan_type_model1.loan_type_name = loantype
        db.add(loan_type_model1)
        db.commit()
        return {201 : "loan type added successfully"}
    except Exception as e:
        return HTTPException(status_code=500,detail=str(e))

@router.get('/get-loantypes')
async def get_all_loantypes( user : dict = Depends(get_current_user),db : Session = Depends(get_db)):
    try:
        if user.get("role") != "admin":
            return {"incorrect request" : "unauthorized"}
        loan_type_model = db.query(models.LoanType).all()
        return loan_type_model
    except Exception as e:
        return HTTPException(status_code=500,detail=str(e))


@router.get('/get-all-loanlist')
async def get_all_loans(user : dict = Depends(get_current_user),db : Session=Depends(get_db)):
    try:
        if user.get("role") != "admin":
            return {"incorrect request" : "unauthorized"}
        all_loan_model = db.query(models.LoanList).all()
        return all_loan_model
    except Exception as e:
        return HTTPException(status_code=500,detail=str(e))


@router.delete('/delete/loanofficer')
async def delete_loanofficer(officer_name : str,user : dict = Depends(get_current_user),db : Session = Depends(get_db)):
    try:
        if user.get("role") != "admin":
            return {"invalid request" : "un authorized"}
        check = db.query(models.LoanOfficer).filter(models.LoanOfficer.officer_name==officer_name).first()
        if check is None:
            return{"invalid request" : "username does not exist"}
        db.query(models.LoanOfficer).filter(models.LoanOfficer.officer_name==officer_name).delete()
        db.commit()
        return {"loan officer account deleted " : "sucessful"}
    except Exception as e:
        return HTTPException(status_code=500,detail=str(e))


@router.delete('/delete/adminaccount')
async def delete_admin_account(admin_name : str,user : dict = Depends(get_current_user),db : Session = Depends(get_db)):
    try:
        if user.get("role") != "admin":
            return {"invalid request" : "un authorized"}
        check = db.query(models.Admins).filter(models.Admins.admin_name==admin_name).first()
        if check is None:
            return {"invalid request" : "admin name does not exist"}
        check2 = user.get("sub")
        if check2 == admin_name:
            return {"could not delete current user" : "invalid request"}
        db.query(models.Admins).filter(models.Admins.admin_name==admin_name).delete()
        db.commit()
        return {"admin acccount deletion" : "sucessful"}
    except Exception as e:
        return HTTPException(status_code=500,detail=str(e))
