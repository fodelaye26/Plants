from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.family_member import FamilyMemberCreate, FamilyMemberDB, FamilyMemberResponse

router = APIRouter(prefix="/family", tags=["family"])


@router.get("/", response_model=list[FamilyMemberResponse])
def list_members(db: Session = Depends(get_db)):
    return db.query(FamilyMemberDB).all()


@router.post("/", response_model=FamilyMemberResponse, status_code=201)
def add_member(member_in: FamilyMemberCreate, db: Session = Depends(get_db)):
    member = FamilyMemberDB(**member_in.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("/{member_id}", response_model=FamilyMemberResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(FamilyMemberDB).filter(FamilyMemberDB.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Family member not found")
    return member
