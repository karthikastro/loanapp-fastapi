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
                    prefix="/api/v2",
                    tags=["datahandler"],
                    responses={404 :{"description" :"incorrect request"}}
)

models.Base.metadata.create_all(bind = engine)

def get_db():
    try:
        db= SessionLocal()
        yield db
    finally:
        db.close()

class RegisterUser(BaseModel):
    username : str
    first_name : str 
    last_name : str
    email : str
    account_no : int
    ifsc_code : str
    password : str




@router.post("/registration/users")
async def register_user(user : RegisterUser,db : Session = Depends(get_db)):
    try :
        user_model = db.query(models.Users).filter(models.Users.username == user.username).first()
        if user_model is not None:
            return "User name already taken try other username"
    
        new_user_model = models.Users()
        new_user_model.username = user.username
        new_user_model.first_name=user.first_name
        new_user_model.last_name = user.last_name
        new_user_model.email = user.email
        new_user_model.account_no=user.account_no
        new_user_model.ifsc_code = user.ifsc_code
        hashed_password = get_hash_password(user.password)
        new_user_model.hash_password=hashed_password
        new_user_model.is_active = True
        db.add(new_user_model)
        db.commit()
        return {"status" : 201,  "user registeration " : "sucessful"}
    except Exception as e:
        return {"status" : 500 , "user registration " : "failed", "detail" : str(e)}

class LoanList(BaseModel):
    account_no: int
    accounter_name : str
    first_name : str
    last_name : str
    ifsc_code : str
    loan_type : str
    loan_amount : int

@router.post('/registration/loan')
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
    loan_model = db.query(models.LoanList).filter(models.LoanList.user_id==user.get("id")).first()
    if(loan_model.loan_status == 1):
            status = "approved"
    elif(loan_model.loan_status == 2):
            status = "declined"
    else:
            status="pending"       
    loan_status_check =[loan_model.accounter_name,loan_model.loan_account_no,loan_model.ifsc_code,loan_model.loan_amount,loan_model.loan_type,status]
    return   loan_status_check

@router.get('/get-all-loanlist')
async def get_all_loans(user : dict = Depends(get_current_user),db : Session=Depends(get_db)):
    if user.get("role") != "loanofficer":
        return {"incorrect request" : "unauthorized"}
    all_loan_model = db.query(models.LoanList).all()
    return all_loan_model




@router.put('/update/loanstatus')
async def update_loan_status(loan_status : int,user : dict = Depends(get_current_user),db : Session=Depends(get_db)):
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
   
class RegLoanOfficer(BaseModel):
    officer_name : str
    first_name :str
    last_name : str
    officer_email : str
    ifsc_code : str
    officer_password : str
    officer_password2 : str

@router.post('/registration/loanofficer')
async def register_loan_officer(loanoffreg : RegLoanOfficer,db:Session=Depends(get_db)):
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


@router.post('/admin/createloantype')
async def create_loan_type(loantype : str, db : Session = Depends(get_db)):
    loan_type_model = db.query(models.LoanType).filter(models.LoanType.loan_type_name==loantype).first()
    if loan_type_model is not None: 
        return {"loan type already exists" : "retry new loan type"}
    loan_type_model1= models.LoanType()
    loan_type_model1.loan_type_name = loantype
    db.add(loan_type_model1)
    db.commit()
    return {201 : "loan type added successfully"}


class CreateAdmin(BaseModel):
    username : str
    password : str
    password2 : str

@router.post("/registration/admin")
async def admin_registration(regadmin : CreateAdmin, db : Session= Depends(get_db)):
    admin_model = models.Admins()
    check = db.query(models.Admins).filter(models.Admins.admin_name==regadmin.username).first()
    if check is not None:
        return {"username already exists" :"invalid request"}
    if regadmin.password != regadmin.password2:
        return {"incorrect password " : "password mismatch"}
    admin_model.admin_name = regadmin.username
    hash_password = get_hash_password(regadmin.password)
    admin_model.admin_password = hash_password
    db.add(admin_model)
    db.commit()   
    return {201 : "admin id creation sucessful"}

@router.delete('/delete/loanofficer/{officer_name}')
async def delete_loanofficer(officer_name : str,user : dict = Depends(get_current_user),db : Session = Depends(get_db)):
    if user.get("role") != "admin":
        return {"invalid request" : "un authorized"}
    check = db.query(models.LoanOfficer).filter(models.LoanOfficer.officer_name==officer_name).first()
    if check is None:
        return{"invalid request" : "username does not exist"}
    db.query(models.LoanOfficer).filter(models.LoanOfficer.officer_name==officer_name).delete()
    db.commit()
    return {"loan officer account deleted " : "sucessful"}

