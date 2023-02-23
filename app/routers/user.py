from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponseDto)
def create_user(userDto: schemas.CreateUserDto, db: Session = Depends(get_db)):
    
    hashed_password = utils.hash(userDto.password)
    userDto.password = hashed_password
    new_user = models.User(**userDto.dict())
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"user with email: {userDto.email} already exists")
    db.refresh(new_user)
    return new_user

@router.get("/{id}", response_model=schemas.UserResponseDto)
def get_user(id: int, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    print(user)

    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"user with id: {id} was not found")

    return user 