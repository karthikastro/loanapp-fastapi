from sqlalchemy import Boolean,Column,Integer,ForeignKey,DateTime,String
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime,timedelta

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key = True, index = True)
    email = Column(String,unique = True, index = True)
    username = Column(String, unique = True,index = True )
    first_name = Column(String)
    last_name = Column(String)
    account_no = Column(Integer)
    ifsc_code = Column(String)
    hash_password = Column(String)
    is_active = Column(Boolean,default = True)

    loanlist = relationship("LoanList",back_populates = "loanuser")

class LoanList(Base):
    __tablename__ = "loanlist"
    lid = Column(Integer,primary_key=True, index = True)
    accounter_name = Column(String, unique = True)
    first_name = Column(String)
    last_name = Column(String)
    loan_account_no = Column(Integer,index = True)
    ifsc_code = Column(String)
    loan_type = Column(String)
    loan_amount = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    loanuser = relationship("Users",back_populates="loanlist")
    loan_date = Column(DateTime , default = datetime.utcnow())
    loan_status = Column(Integer,default=0)
    
class LoanOfficer(Base):
    __tablename__= "loanofficer"
    oid = Column(Integer,primary_key=True,index=True)
    officer_name = Column(String,unique=True,index=True)
    first_name = Column(String)
    last_name = Column(String)
    officer_email = Column(String,unique=True,index=True)
    ifsc_code = Column(String)
    hash_password = Column(String)


class LoanType(Base):
    __tablename__="loantypes"
    ltid = Column(Integer,primary_key=True,index=True)
    loan_type_name = Column(String,index=True)

class Admins(Base):
    __tablename__ = "admins"
    adminid = Column(Integer,primary_key=True,index=True)
    admin_name = Column(String)
    admin_password = Column(String)
    