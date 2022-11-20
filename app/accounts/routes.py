"""
    Contains route endpoints to access Accounts

    TODO:
        - See if you can type check account(s) objects
"""

# FastAPI imports
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException

# SQLModel imports
from sqlmodel import Session, select

# Model imports
from .models import Account, AccountCreate, AccountRead, AccountUpdate

# Dependency imports
from ..dependencies import get_session

# Standard library imports
import uuid


# Initializing router
router = APIRouter(prefix="/accounts")


### HTTP GET FUNCTIONS ###

@router.get("/", response_model=list[Account])
def get_all_accounts(
    *,
    session: Session = Depends(get_session),
    offset: int = Query(default=0),
    limit: int = Query(default=100, lte=100),
):

    # Get list of accounts
    accounts = session.exec(select(Account).offset(offset).limit(limit)).all()

    # Return list of accounts
    return accounts


@router.get("/{account_id}", response_model=Account)
def get_account_by_id(
    *,
    session: Session = Depends(get_session),
    account_id: uuid.UUID = Path()
):
    # Get account and check if it exists
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Return back account
    return account


### HTTP POST FUNCTIONS ###

@router.post("/", response_model=AccountRead)
def create_account(
    *,
    session: Session = Depends(get_session),
    account: AccountCreate = Body()
):
    # Create account by using from_orm function
    db_account = Account.from_orm(account)

    # Commit to DBMS
    session.add(db_account)
    session.commit()
    session.refresh(db_account)

    # Return back account
    return db_account


### HTTP PATCH FUNCTIONS ###

@router.patch("/{account_id}", response_model=AccountRead)
def update_account(
    *,
    session: Session = Depends(get_session),
    account_id: uuid.UUID = Path(),
    account: AccountUpdate = Body()
):

    # Check if account exists
    db_account = session.get(Account, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Update account data
    account_data = account.dict(exclude_unset=True)
    for key, value in account_data.items():
        setattr(db_account, key, value)

    # Commit to DBMS
    session.add(db_account)
    session.commit()
    session.refresh(db_account)

    # Return back account
    return db_account


### HTTP DELETE FUNCTIONS ###

@router.delete("/{account_id}")
def delete_account(
    *,
    session: Session = Depends(get_session),
    account_id: uuid.UUID = Path()
):

    # Get account and check if it exists
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Commit to DBMS
    session.delete(account)
    session.commit()

    # Return back an OK response
    return {"ok": True}
