import sys 
sys.path.append("..")


from fastapi import Depends,HTTPException,status,APIRouter
from typing import Optional
from pydantic import BaseModel,Field 
import models 
from passlib.context import CryptContext
from sqlalchemy.orm import relationship,Session
from database import engine,SessionLocal
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from datetime import datetime,timedelta
from jose import jwt,JWTError

SECRET_KEY = "mysecretkey20220817loankey$$$$$"
ALGORITHM = "HS256"

router = APIRouter(
    prefix="/api/v2/auth",
    tags = ["Auth"],
    responses = {401 : {"detail" : "not authorized"}}
)

class UserLogin(BaseModel):
    email : Optional[str]
    username : str
    password : str


bcrypt_context = CryptContext(schemes=["bcrypt"],deprecated = "auto")

models.Base.metadata.create_all(bind = engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl = "token")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_hash_password(password):
    return bcrypt_context.hash(password)

def verify_password(plain_password,hash_password):
    return bcrypt_context.verify(plain_password,hash_password)

def authenticate_user(username : str,password : str, db):
    user = db.query(models.Users)\
            .filter(models.Users.username == username).first()
    
    if not user:
        return False
    if not verify_password(password,user.hash_password):
        return False
    
    return user
def authenticate_officer(officername : str,password : str, db):
    officer = db.query(models.LoanOfficer).filter(models.LoanOfficer.officer_name==officername).first()
    if not officer:
        return False
    if not verify_password(password,officer.hash_password):
        return False
    return officer

def authenticate_admin(adminname : str, password : str,db):
    admin = db.query(models.Admins).filter(models.Admins.admin_name==adminname).first()
    if not admin:
        return False
    if not verify_password(password,admin.admin_password):
        return False
    return admin

def create_access_token(username : str,user_id : int, role : str,expires_delta : Optional[timedelta] = None):
    encode = {"sub" : username, "id" : user_id ,"role":role}
    if expires_delta:
        expire = datetime.utcnow()+expires_delta
    else :
        expire = datetime.utcnow()+timedelta(minutes = 60)

    return jwt.encode(encode,SECRET_KEY,algorithm = ALGORITHM)

async def get_current_user(token : str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms = [ALGORITHM,])
        username : str = payload.get("sub")
        user_id : int = payload.get("id")
        role : str = payload.get("role")
        if username is None or user_id is None:
            raise get_user_exception()
        return {"username" : username,"id" : user_id,"role":role}
    except JWTError:
        raise get_user_exception()


@router.post('/userlogin')
async def user_login(form_data : OAuth2PasswordRequestForm= Depends(),db: Session= Depends(get_db)):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise token_exception()
    role = "user"
    token_expires = timedelta(minutes = 20)
    token = create_access_token(user.username,user.id,role,expires_delta=token_expires)

    return {"token" : token}

@router.post('/officerlogin')
async def officer_login(form_data :OAuth2PasswordRequestForm = Depends(),db :Session=Depends(get_db)):
    officer = authenticate_officer(form_data.username,form_data.password,db)
    if not officer:
        raise token_exception()
    role ="loanofficer"
    token_expires = timedelta(minutes=60)
    token = create_access_token(officer.officer_name,officer.oid,role,expires_delta=token_expires)

    return{"token" : token}

@router.post("/adminlogin")
async def admin_login(form_data:OAuth2PasswordRequestForm=Depends(),db : Session = Depends(get_db)):
    admin = authenticate_admin(form_data.username,form_data.password,db)
    if not admin:
        raise token_exception()
    role="admin"
    token_expires=timedelta(minutes=60)
    token = create_access_token(admin.admin_name,admin.adminid,role,expires_delta=token_expires)
    return {"token" : token}





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
    


class CreateAdmin(BaseModel):
    username : str
    password : str
    password2 : str

@router.post("/registration/admin")
async def admin_registration(regadmin : CreateAdmin, db : Session= Depends(get_db)):
    try:
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
    except Exception as e:
        return HTTPException(status_code=501,detail=str(e))


#Exceptions
def get_user_exception():
    credentials_exception = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                                            detail = "could not validate credentials ",
                                            headers = {"WWW=Authenticate" : "Bearer"})
    return credentials_exception

def token_exception():
    token_exception_response = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                                            detail = " invalid  credentials ",
                                            headers = {"WWW=Authenticate" : "Bearer"})
    return token_exception_response
